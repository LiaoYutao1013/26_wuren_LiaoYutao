import math
import os
import sys
import threading
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Bool


class FigureEightTurtle(Node):
    """周期性发布Twist速度指令，让小海龟绘制8字形轨迹"""

    def __init__(self):
        """初始化节点、读取参数，并创建发布器、订阅器、定时器和键盘监听线程。

        参数表：
        - cmd_vel_topic：发布速度指令的topic，默认/turtle1/cmd_vel。
        - linear_velocity：小海龟前进线速度，单位m/s。
        - angular_velocity：每个圆弧段的角速度，单位rad/s。
        - publish_rate_hz：Twist指令发布频率，频率越高轨迹越平滑。
        - initial_delay_sec：启动后先延时，让turtlesim初始化窗口。
        - figure_eight_repetitions：重复绘制次数，0表示无限循环；
        - start_clockwise：是否先顺时针转弯，False表示先逆时针；
        - keyboard_quit_enabled：是否允许在终端按退出键停止节点；
        - quit_key：触发退出按键，默认q。
        """
        super().__init__('figure_eight_turtle')

        # 声明ROS2参数及其默认值
        self.declare_parameter('cmd_vel_topic', '/turtle1/cmd_vel')
        self.declare_parameter('linear_velocity', 2.0)
        self.declare_parameter('angular_velocity', 1.5)
        self.declare_parameter('publish_rate_hz', 30.0)
        self.declare_parameter('initial_delay_sec', 0.8)
        self.declare_parameter('figure_eight_repetitions', 0)
        self.declare_parameter('start_clockwise', False)
        self.declare_parameter('keyboard_quit_enabled', True)
        self.declare_parameter('quit_key', 'q')

        #将参数对象转换成普通Python类型，方便计算和判断。
        self.cmd_vel_topic = (
            self.get_parameter('cmd_vel_topic').get_parameter_value().string_value
        )
        self.linear_velocity = (
            self.get_parameter('linear_velocity').get_parameter_value().double_value
        )
        self.angular_velocity = abs(
            self.get_parameter('angular_velocity').get_parameter_value().double_value
        )
        self.publish_rate_hz = (
            self.get_parameter('publish_rate_hz').get_parameter_value().double_value
        )
        self.initial_delay_sec = (
            self.get_parameter('initial_delay_sec').get_parameter_value().double_value
        )
        self.figure_eight_repetitions = (
            self.get_parameter('figure_eight_repetitions').get_parameter_value().integer_value
        )
        self.start_clockwise = (
            self.get_parameter('start_clockwise').get_parameter_value().bool_value
        )
        self.keyboard_quit_enabled = (
            self.get_parameter('keyboard_quit_enabled').get_parameter_value().bool_value
        )
        self.quit_key = (
            self.get_parameter('quit_key').get_parameter_value().string_value
        )

        #检查参数
        self._validate_parameters()

        #Twist发布器负责向turtlesim发送速度控制命令。
        self.publisher = self.create_publisher(Twist, self.cmd_vel_topic, 10)

        #画一个圆的用时满足角速度*时间=2*pi。
        #用两个方向相反的圆拼成8字，每画一个圆都切换一次方向。
        self.circle_duration = 2.0 * math.pi / self.angular_velocity
        self.start_time = time.monotonic()
        self.current_circle_index = -1
        self.finished = False
        self.shutdown_requested = False

        #周期性发布速度指令，ROS2定时器回调频率由publish_rate_hz控制。
        self.timer = self.create_timer(1.0 / self.publish_rate_hz, self._publish_cmd_vel)
        self.keyboard_thread = None
        if self.keyboard_quit_enabled:
            #键盘监听放到后台线程，避免阻塞rclpy.spin()的回调处理。
            self._start_keyboard_listener()

        radius = self.linear_velocity / self.angular_velocity
        self.get_logger().info(
            'Figure-eight controller started: '
            f'v={self.linear_velocity:.3f} m/s, '
            f'w={self.angular_velocity:.3f} rad/s, '
            f'radius={radius:.3f}, '
            f'circle_period={self.circle_duration:.3f} s'
        )

        #监听quit_signal
        self.quit_subscription = self.create_subscription(
            Bool,
            'quit_signal',
            self._quit_signal_callback,
            10,
        )

    def _validate_parameters(self):
        """检查参数合法性（虽然这个任务不太可能出岔子）"""
        if not self.cmd_vel_topic:
            raise ValueError('cmd_vel_topic must not be empty')
        if self.linear_velocity <= 0.0:
            raise ValueError('linear_velocity must be greater than 0')
        if self.angular_velocity <= 0.0:
            raise ValueError('angular_velocity must be greater than 0')
        if self.publish_rate_hz <= 0.0:
            raise ValueError('publish_rate_hz must be greater than 0')
        if self.initial_delay_sec < 0.0:
            raise ValueError('initial_delay_sec must be greater than or equal to 0')
        if self.figure_eight_repetitions < 0:
            raise ValueError('figure_eight_repetitions must be greater than or equal to 0')
        if len(self.quit_key) != 1:
            raise ValueError('quit_key must be a single character')

    def _publish_cmd_vel(self):
        """根据当前时间计算所在圆弧段，并发布对应速度"""
        if self.shutdown_requested:
            return

        elapsed = time.monotonic() - self.start_time

        if elapsed < self.initial_delay_sec:
            #启动初期先发布零速度，等待turtlesim完成初始化并保持海龟静止（这个过程实则转瞬即逝）。
            self.publisher.publish(Twist())
            return

        motion_elapsed = elapsed - self.initial_delay_sec
        circle_index = int(motion_elapsed / self.circle_duration)

        max_circles = self.figure_eight_repetitions * 2
        if max_circles > 0 and circle_index >= max_circles:
            if not self.finished:
                self.publisher.publish(Twist())
                self.get_logger().info('Figure-eight motion finished.')
                self.finished = True
            return

        if circle_index != self.current_circle_index:
            #每次绘制新的圆弧段时打印一次方向；
            self.current_circle_index = circle_index
            direction_name = self._direction_name(circle_index)
            self.get_logger().info(
                f'Starting circle {circle_index + 1}: {direction_name}'
            )

        #线速度保持为正，角速度符号决定方向；
        cmd = Twist()
        cmd.linear.x = self.linear_velocity
        cmd.angular.z = self._angular_direction(circle_index) * self.angular_velocity
        self.publisher.publish(cmd)

    def _angular_direction(self, circle_index):
        """根据圆弧序号返回角速度方向
           1表示逆时针，-1表示顺时针"""
        direction = -1.0 if self.start_clockwise else 1.0
        if circle_index % 2 == 1:
            # 奇数段反向，拼8字形
            direction *= -1.0
        return direction

    def _direction_name(self, circle_index):
        """返回顺逆时针方向（而不是角速度），方便读打印信息"""
        return 'clockwise' if self._angular_direction(circle_index) < 0.0 else 'counterclockwise'

    def _start_keyboard_listener(self):
        """启动后台键盘监听线程，按下quit_key(q)后退出。"""
        self.keyboard_thread = threading.Thread(
            target=self._keyboard_listener_loop,
            name='keyboard_quit_listener',
            daemon=True,
        )
        self.keyboard_thread.start()
        self.get_logger().info(
            f"Press '{self.quit_key}' in the launch terminal to stop the turtle."
        )

    def _keyboard_listener_loop(self):
        """根据操作系统选择键盘读取方式"""
        if os.name == 'nt':
            self._windows_keyboard_listener_loop()
            return

        self._posix_keyboard_listener_loop()

    def _windows_keyboard_listener_loop(self):
        """Windows下使用msvcrt读取按键"""
        import msvcrt

        quit_key = self.quit_key.lower()
        while rclpy.ok() and not self.shutdown_requested:
            if msvcrt.kbhit():
                key = msvcrt.getwch()
                if key.lower() == quit_key:
                    self._request_shutdown_by_key()
                    return
            time.sleep(0.05)

    def _posix_keyboard_listener_loop(self):
        """Linux/macOS下把stdin切到cbreak读取单个字符"""
        if not sys.stdin.isatty():
            self.get_logger().warning(
                'Keyboard quit is disabled because stdin is not a TTY. '
                'Run the node in an interactive terminal if you need q-to-quit.'
            )
            return

        import select
        import termios
        import tty

        quit_key = self.quit_key.lower()
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            # cbreak下按键不需要回车即可被read(1)读取。
            tty.setcbreak(fd)
            while rclpy.ok() and not self.shutdown_requested:
                #select留出0.05秒超时，让线程能检查rclpy.ok()和退出标志。
                readable, _, _ = select.select([sys.stdin], [], [], 0.05)
                if readable:
                    key = sys.stdin.read(1)
                    if key.lower() == quit_key:
                        self._request_shutdown_by_key()
                        return
        finally:
            # 无论退出正常与否，都恢复终端设置，避免终端回显状态被破坏。
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def _request_shutdown_by_key(self):
        """按键退出：先发布零速度停止小海龟，再关闭ROS2"""
        if self.shutdown_requested:
            return

        self.shutdown_requested = True
        self.publisher.publish(Twist())
        self.get_logger().info(
            f"Received quit key '{self.quit_key}'. Stopping turtle and exiting."
        )
        rclpy.try_shutdown()

    def _quit_signal_callback(self, msg):
        """收到其他节点发布的quit_signal=True后停止运动并退出。"""
        if msg.data:
            self.publisher.publish(Twist())
            self.get_logger().info('Received quit signal. Stopping turtle and exiting.')
            rclpy.try_shutdown()


def main(args=None):
    """ROS2 可执行入口函数"""
    rclpy.init(args=args)
    node = FigureEightTurtle()

    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if rclpy.ok():
            # 退出前再发一次零速度，确保小海龟停下来。
            node.publisher.publish(Twist())
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
