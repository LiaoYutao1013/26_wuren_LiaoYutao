import math

import rclpy
from geometry_msgs.msg import PoseStamped, TransformStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from sensor_msgs.msg import Imu, MagneticField, NavSatFix
from tf2_ros import TransformBroadcaster

from .utils import normalize_angle, yaw_to_quaternion


EARTH_RADIUS_M = 6378137.0


class LocalizationFusion(Node):
    def __init__(self):
        super().__init__('localization_fusion')

        self.declare_parameter('origin_latitude', 23.043055)
        self.declare_parameter('origin_longitude', 113.397222)
        self.declare_parameter('initial_x', 0.0)
        self.declare_parameter('initial_y', -15.0)
        self.declare_parameter('initial_yaw', math.pi / 2.0)
        self.declare_parameter('gps_gain', 0.45)
        self.declare_parameter('mag_gain', 0.30)
        self.declare_parameter('magnetic_declination', 0.0)
        self.declare_parameter('gps_topic', '/sensors/gps/fix')
        self.declare_parameter('imu_topic', '/sensors/imu/data_raw')
        self.declare_parameter('wheel_odom_topic', '/sensors/wheel_odom')
        self.declare_parameter('magnetic_field_topic', '/sensors/magnetic_field')

        self.origin_lat = math.radians(self.get_parameter('origin_latitude').value)
        self.origin_lon = math.radians(self.get_parameter('origin_longitude').value)
        self.gps_gain = float(self.get_parameter('gps_gain').value)
        self.mag_gain = float(self.get_parameter('mag_gain').value)
        self.magnetic_declination = float(self.get_parameter('magnetic_declination').value)

        self.x = float(self.get_parameter('initial_x').value)
        self.y = float(self.get_parameter('initial_y').value)
        self.yaw = float(self.get_parameter('initial_yaw').value)
        self.forward_speed = 0.0
        self.yaw_rate = 0.0
        self.last_time = self.get_clock().now()

        self.pose_pub = self.create_publisher(PoseStamped, '/localization/pose', 10)
        self.odom_pub = self.create_publisher(Odometry, '/localization/odom', 10)
        self.tf_pub = TransformBroadcaster(self)

        self.create_subscription(
            NavSatFix,
            self.get_parameter('gps_topic').value,
            self.on_gps,
            10,
        )
        self.create_subscription(
            Imu,
            self.get_parameter('imu_topic').value,
            self.on_imu,
            50,
        )
        self.create_subscription(
            Odometry,
            self.get_parameter('wheel_odom_topic').value,
            self.on_wheel_odom,
            20,
        )
        self.create_subscription(
            MagneticField,
            self.get_parameter('magnetic_field_topic').value,
            self.on_magnetic_field,
            20,
        )

        self.timer = self.create_timer(0.02, self.on_timer)
        self.get_logger().info('Localization fusion started: GPS + wheel odom + IMU gyro + magnetometer heading.')

    def gps_to_local_xy(self, latitude_deg, longitude_deg):
        lat = math.radians(latitude_deg)
        lon = math.radians(longitude_deg)
        x = EARTH_RADIUS_M * math.cos(self.origin_lat) * (lon - self.origin_lon)
        y = EARTH_RADIUS_M * (lat - self.origin_lat)
        return x, y

    def on_gps(self, msg):
        if math.isnan(msg.latitude) or math.isnan(msg.longitude):
            return
        gps_x, gps_y = self.gps_to_local_xy(msg.latitude, msg.longitude)
        self.x = (1.0 - self.gps_gain) * self.x + self.gps_gain * gps_x
        self.y = (1.0 - self.gps_gain) * self.y + self.gps_gain * gps_y

    def on_imu(self, msg):
        self.yaw_rate = msg.angular_velocity.z

    def on_wheel_odom(self, msg):
        self.forward_speed = msg.twist.twist.linear.x
        if abs(self.yaw_rate) < 1e-4:
            self.yaw_rate = msg.twist.twist.angular.z

    def on_magnetic_field(self, msg):
        mx = msg.magnetic_field.x
        my = msg.magnetic_field.y
        if abs(mx) + abs(my) < 1e-9:
            return
        measured_yaw = math.atan2(mx, my) - self.magnetic_declination
        self.yaw += self.mag_gain * normalize_angle(measured_yaw - self.yaw)
        self.yaw = normalize_angle(self.yaw)

    def on_timer(self):
        now = self.get_clock().now()
        dt = (now - self.last_time).nanoseconds * 1e-9
        self.last_time = now
        if dt <= 0.0 or dt > 0.2:
            dt = 0.02

        self.yaw = normalize_angle(self.yaw + self.yaw_rate * dt)
        self.x += self.forward_speed * math.cos(self.yaw) * dt
        self.y += self.forward_speed * math.sin(self.yaw) * dt

        self.publish_state(now)

    def publish_state(self, stamp):
        quat = yaw_to_quaternion(self.yaw)

        pose = PoseStamped()
        pose.header.stamp = stamp.to_msg()
        pose.header.frame_id = 'world'
        pose.pose.position.x = self.x
        pose.pose.position.y = self.y
        pose.pose.orientation = quat
        self.pose_pub.publish(pose)

        odom = Odometry()
        odom.header = pose.header
        odom.child_frame_id = 'base_link'
        odom.pose.pose = pose.pose
        odom.twist.twist.linear.x = self.forward_speed
        odom.twist.twist.angular.z = self.yaw_rate
        odom.pose.covariance[0] = 0.25
        odom.pose.covariance[7] = 0.25
        odom.pose.covariance[35] = 0.05
        self.odom_pub.publish(odom)

        transform = TransformStamped()
        transform.header = pose.header
        transform.child_frame_id = 'base_link'
        transform.transform.translation.x = self.x
        transform.transform.translation.y = self.y
        transform.transform.translation.z = 0.0
        transform.transform.rotation = quat
        self.tf_pub.sendTransform(transform)


def main(args=None):
    rclpy.init(args=args)
    node = LocalizationFusion()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
