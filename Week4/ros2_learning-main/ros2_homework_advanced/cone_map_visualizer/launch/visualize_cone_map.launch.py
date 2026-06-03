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
    """生成 launch 描述，统一启动可视化节点、RViz、静态 TF 和 bag 播放。"""

    package_share = get_package_share_directory('cone_map_visualizer')
    default_bag_path = os.path.join(package_share, 'map_to_visualize')
    default_rviz_config = os.path.join(package_share, 'rviz', 'cone_map.rviz')

    # LaunchConfiguration表示运行时参数
    input_topic = LaunchConfiguration('input_topic')
    marker_topic = LaunchConfiguration('marker_topic')
    frame_override = LaunchConfiguration('frame_override')
    marker_scale = LaunchConfiguration('marker_scale')
    z_offset = LaunchConfiguration('z_offset')
    bag_path = LaunchConfiguration('bag_path')
    play_bag = LaunchConfiguration('play_bag')
    use_rviz = LaunchConfiguration('use_rviz')

    #主可视化节点,订阅地图topic，发布RViz MarkerArray。
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

    #RViz节点,加载预配置视图，订阅/visualization/cone_markers。
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', default_rviz_config],
        condition=IfCondition(use_rviz),
    )

    #静态TF,把map固定到world，保证RViz的Fixed Frame能找到地图坐标。
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

    # 延迟播放，让可视化节点,RViz和TF先启动。
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
        #输入地图topic。
        DeclareLaunchArgument('input_topic', default_value='/estimation/slam/map'),
        #MarkerArray输出topic。
        DeclareLaunchArgument('marker_topic', default_value='/visualization/cone_markers'),
        #强制坐标系；空字符串表示使用header.frame_id或节点默认回退值。
        DeclareLaunchArgument('frame_override', default_value=''),
        #RViz中每个锥桶点的显示大小。
        DeclareLaunchArgument('marker_scale', default_value='0.45'),
        #锥桶点相对原始地图坐标的显示高度偏移。
        DeclareLaunchArgument('z_offset', default_value='0.18'),
        #rosbag路径。
        DeclareLaunchArgument('bag_path', default_value=default_bag_path),
        #自动循环播放bag。
        DeclareLaunchArgument('play_bag', default_value='true'),
        #自动启动RViz。
        DeclareLaunchArgument('use_rviz', default_value='true'),
        visualizer_node,
        static_tf_node,
        rviz_node,
        delayed_bag_play,
    ])
