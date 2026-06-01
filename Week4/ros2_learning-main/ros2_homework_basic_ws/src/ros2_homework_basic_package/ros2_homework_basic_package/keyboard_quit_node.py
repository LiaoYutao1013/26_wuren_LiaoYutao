import sys
import termios
import tty
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool

class KeyboardQuitNode(Node):
    """监听键盘输入，当按下指定的退出键(q)时发布退出信号。"""

    def __init__(self):
        """初始化节点，声明并获取参数，设置发布器和定时器，启动键盘监听线程（用于键盘控制退出）。
           参数表：
           - quit_key: 退出键，默认为q。"""
        
        super().__init__('keyboard_quit_node')

        self.declare_parameter('quit_key', 'q')
        self.quit_key = (
            self.get_parameter('quit_key').get_parameter_value().string_value
        )

        self.quit_publisher = self.create_publisher(Bool, 'quit_signal', 10)
        self.get_logger().info(f'KeyboardQuitNode initialized. Press "{self.quit_key}" to publish quit signal.')
        self.timer = self.create_timer(0.1, self.publish_quit_signal)

    def run(self):
        """启动一个线程监听键盘输入，按下退出键时发布退出信号。"""

        previous_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

        while rclpy.ok():
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                key = sys.stdin.read(1)
                if key.lower() == self.quit_key.lower():
                    self.publish_quit_signal()
                    break
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, previous_settings)

def main(args=None):
    rclpy.init(args=args)
    node = KeyboardQuitNode()
    node.run()
    rclpy.shutdown()

if __name__ == '__main__':
    main()