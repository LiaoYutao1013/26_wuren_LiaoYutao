import math
import time

import rclpy
from geometry_msgs.msg import Twist
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

        self._validate_parameters()

        self.publisher = self.create_publisher(Twist, self.cmd_vel_topic, 10)
        self.circle_duration = 2.0 * math.pi / self.angular_velocity
        self.start_time = time.monotonic()
        self.current_circle_index = -1
        self.finished = False

        self.timer = self.create_timer(1.0 / self.publish_rate_hz, self._publish_cmd_vel)

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

    def _publish_cmd_vel(self):
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


def main(args=None):
    rclpy.init(args=args)
    node = FigureEightTurtle()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.publisher.publish(Twist())
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
