import math
import os
import sys
import threading
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


class FigureEightTurtle(Node):
    """Publish velocity commands that make turtlesim draw a figure-eight."""

    def __init__(self):
        super().__init__('figure_eight_turtle')

        self.declare_parameter('cmd_vel_topic', '/turtle1/cmd_vel')
        self.declare_parameter('linear_velocity', 2.0)
        self.declare_parameter('angular_velocity', 1.5)
        self.declare_parameter('publish_rate_hz', 30.0)
        self.declare_parameter('initial_delay_sec', 0.8)
        self.declare_parameter('figure_eight_repetitions', 0)
        self.declare_parameter('start_clockwise', False)
        self.declare_parameter('keyboard_quit_enabled', True)
        self.declare_parameter('quit_key', 'q')

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

        self._validate_parameters()

        self.publisher = self.create_publisher(Twist, self.cmd_vel_topic, 10)
        self.circle_duration = 2.0 * math.pi / self.angular_velocity
        self.start_time = time.monotonic()
        self.current_circle_index = -1
        self.finished = False
        self.shutdown_requested = False

        self.timer = self.create_timer(1.0 / self.publish_rate_hz, self._publish_cmd_vel)
        self.keyboard_thread = None
        if self.keyboard_quit_enabled:
            self._start_keyboard_listener()

        radius = self.linear_velocity / self.angular_velocity
        self.get_logger().info(
            'Figure-eight controller started: '
            f'v={self.linear_velocity:.3f} m/s, '
            f'w={self.angular_velocity:.3f} rad/s, '
            f'radius={radius:.3f}, '
            f'circle_period={self.circle_duration:.3f} s'
        )

    def _validate_parameters(self):
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
        if self.shutdown_requested:
            return

        elapsed = time.monotonic() - self.start_time

        if elapsed < self.initial_delay_sec:
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
            self.current_circle_index = circle_index
            direction_name = self._direction_name(circle_index)
            self.get_logger().info(
                f'Starting circle {circle_index + 1}: {direction_name}'
            )

        cmd = Twist()
        cmd.linear.x = self.linear_velocity
        cmd.angular.z = self._angular_direction(circle_index) * self.angular_velocity
        self.publisher.publish(cmd)

    def _angular_direction(self, circle_index):
        direction = -1.0 if self.start_clockwise else 1.0
        if circle_index % 2 == 1:
            direction *= -1.0
        return direction

    def _direction_name(self, circle_index):
        return 'clockwise' if self._angular_direction(circle_index) < 0.0 else 'counterclockwise'

    def _start_keyboard_listener(self):
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
        if os.name == 'nt':
            self._windows_keyboard_listener_loop()
            return

        self._posix_keyboard_listener_loop()

    def _windows_keyboard_listener_loop(self):
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
            tty.setcbreak(fd)
            while rclpy.ok() and not self.shutdown_requested:
                readable, _, _ = select.select([sys.stdin], [], [], 0.05)
                if readable:
                    key = sys.stdin.read(1)
                    if key.lower() == quit_key:
                        self._request_shutdown_by_key()
                        return
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def _request_shutdown_by_key(self):
        if self.shutdown_requested:
            return

        self.shutdown_requested = True
        self.publisher.publish(Twist())
        self.get_logger().info(
            f"Received quit key '{self.quit_key}'. Stopping turtle and exiting."
        )
        rclpy.try_shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = FigureEightTurtle()

    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if rclpy.ok():
            node.publisher.publish(Twist())
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
