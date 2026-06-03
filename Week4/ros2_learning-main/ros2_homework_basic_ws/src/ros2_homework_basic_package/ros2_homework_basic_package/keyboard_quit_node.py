import select
import sys
import termios
import tty

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool


class KeyboardQuitNode(Node):
    """监听终端按键，按下 q 后发布退出信号。"""

    def __init__(self):
        super().__init__('keyboard_quit_node')

        self.declare_parameter('quit_key', 'q')
        self.quit_key = (
            self.get_parameter('quit_key').get_parameter_value().string_value
        )

        self.quit_publisher = self.create_publisher(Bool, 'quit_signal', 10)
        self.get_logger().info(
            f'键盘监听节点已启动，按 "{self.quit_key}" 发布退出信号。'
        )

    def run(self):
        """进入键盘监听循环，收到退出按键后发布一次 Bool 消息。"""
        if not sys.stdin.isatty():
            self.get_logger().error(
                '当前 stdin 不是 TTY，请用 ros2 run 在交互终端中启动 keyboard_quit_node。'
            )
            return

        previous_settings = termios.tcgetattr(sys.stdin)

        try:
            tty.setcbreak(sys.stdin.fileno())

            while rclpy.ok():
                readable, _, _ = select.select([sys.stdin], [], [], 0.1)
                if not readable:
                    continue

                key = sys.stdin.read(1)
                if key.lower() == self.quit_key.lower():
                    self.publish_quit_signal()
                    break
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, previous_settings)

    def publish_quit_signal(self):
        """发布退出信号，通知控制节点停止小海龟并退出。"""
        msg = Bool()
        msg.data = True
        self.quit_publisher.publish(msg)
        self.get_logger().info('已发布退出信号。')


def main(args=None):
    """ROS2 节点入口函数。"""
    rclpy.init(args=args)
    node = KeyboardQuitNode()

    try:
        node.run()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
