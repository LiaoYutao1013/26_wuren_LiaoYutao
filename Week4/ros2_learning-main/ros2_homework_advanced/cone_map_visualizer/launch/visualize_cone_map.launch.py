import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import ExecuteProcess
from launch.actions import TimerAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_share = get_package_share_directory('cone_map_visualizer')
    default_bag_path = os.path.join(package_share, 'map_to_visualize')
    default_rviz_config = os.path.join(package_share, 'rviz', 'cone_map.rviz')

    input_topic = LaunchConfiguration('input_topic')
    marker_topic = LaunchConfiguration('marker_topic')
    frame_override = LaunchConfiguration('frame_override')
    marker_scale = LaunchConfiguration('marker_scale')
    z_offset = LaunchConfiguration('z_offset')
    bag_path = LaunchConfiguration('bag_path')
    play_bag = LaunchConfiguration('play_bag')
    use_rviz = LaunchConfiguration('use_rviz')

    visualizer_node = Node(
        package='cone_map_visualizer',
        executable='cone_map_visualizer',
        name='cone_map_visualizer',
        output='screen',
        parameters=[{
            'input_topic': input_topic,
            'marker_topic': marker_topic,
            'frame_override': frame_override,
            'marker_scale': marker_scale,
            'z_offset': z_offset,
        }],
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', default_rviz_config],
        condition=IfCondition(use_rviz),
    )

    static_tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='world_frame_publisher',
        output='screen',
        arguments=[
            '--x', '0',
            '--y', '0',
            '--z', '0',
            '--roll', '0',
            '--pitch', '0',
            '--yaw', '0',
            '--frame-id', 'world',
            '--child-frame-id', 'map',
        ],
    )

    delayed_bag_play = TimerAction(
        period=2.0,
        actions=[
            ExecuteProcess(
                cmd=['ros2', 'bag', 'play', '--loop', bag_path],
                output='screen',
                condition=IfCondition(play_bag),
            )
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument('input_topic', default_value='/estimation/slam/map'),
        DeclareLaunchArgument('marker_topic', default_value='/visualization/cone_markers'),
        DeclareLaunchArgument('frame_override', default_value=''),
        DeclareLaunchArgument('marker_scale', default_value='0.45'),
        DeclareLaunchArgument('z_offset', default_value='0.18'),
        DeclareLaunchArgument('bag_path', default_value=default_bag_path),
        DeclareLaunchArgument('play_bag', default_value='true'),
        DeclareLaunchArgument('use_rviz', default_value='true'),
        visualizer_node,
        static_tf_node,
        rviz_node,
        delayed_bag_play,
    ])
