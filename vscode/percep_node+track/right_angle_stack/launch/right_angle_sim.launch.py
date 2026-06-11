import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, EnvironmentVariable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    stack_share = get_package_share_directory('right_angle_stack')
    track_share = get_package_share_directory('right_angle_track')
    gazebo_share = get_package_share_directory('gazebo_ros')

    robot_xacro = os.path.join(stack_share, 'urdf', 'right_angle_car.urdf.xacro')
    rviz_config = os.path.join(stack_share, 'rviz', 'right_angle.rviz')
    stack_config = os.path.join(stack_share, 'config', 'right_angle_stack.yaml')
    track_sdf = os.path.join(track_share, 'models', 'shixi', 'model.sdf')

    model_name = LaunchConfiguration('model_name')
    use_rviz = LaunchConfiguration('use_rviz')
    use_gazebo = LaunchConfiguration('use_gazebo')
    use_builtin_perception = LaunchConfiguration('use_builtin_perception')
    use_sim_perception = LaunchConfiguration('use_sim_perception')
    use_synthetic_sensors = LaunchConfiguration('use_synthetic_sensors')
    perception_map_topic = LaunchConfiguration('perception_map_topic')
    perception_detections_topic = LaunchConfiguration('perception_detections_topic')

    robot_description = {
        'robot_description': Command(['xacro', ' ', robot_xacro])
    }

    gazebo_models = PathJoinSubstitution([FindPackageShare('right_angle_track'), 'models'])
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gazebo_share, 'launch', 'gazebo.launch.py')),
        launch_arguments={
            'world': os.path.join(track_share, 'worlds', 'right_angle.world'),
            'verbose': 'true',
        }.items(),
        condition=IfCondition(use_gazebo),
    )

    return LaunchDescription([
        DeclareLaunchArgument('model_name', default_value='racecar'),
        DeclareLaunchArgument('use_gazebo', default_value='true'),
        DeclareLaunchArgument('use_rviz', default_value='true'),
        DeclareLaunchArgument('use_builtin_perception', default_value='true'),
        DeclareLaunchArgument('use_sim_perception', default_value='false'),
        DeclareLaunchArgument('use_synthetic_sensors', default_value='false'),
        DeclareLaunchArgument('perception_map_topic', default_value='/perception/cones'),
        DeclareLaunchArgument('perception_detections_topic', default_value='/perception/cone_detections'),
        SetEnvironmentVariable(
            name='GAZEBO_MODEL_PATH',
            value=[gazebo_models, ':', EnvironmentVariable('GAZEBO_MODEL_PATH', default_value='')],
        ),
        gazebo_launch,
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[robot_description, {'use_sim_time': True}],
        ),
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-topic', 'robot_description',
                '-entity', model_name,
                '-x', '0.0',
                '-y', '-15.0',
                '-z', '0.02',
                '-Y', '1.57079632679',
            ],
            output='screen',
            condition=IfCondition(use_gazebo),
        ),
        Node(
            package='right_angle_stack',
            executable='sim_sensor_bridge',
            name='sim_sensor_bridge',
            output='screen',
            parameters=[stack_config, {
                'model_name': model_name,
                'use_sim_time': True,
            }],
            condition=IfCondition(use_synthetic_sensors),
        ),
        Node(
            package='right_angle_stack',
            executable='localization_fusion',
            name='localization_fusion',
            output='screen',
            parameters=[stack_config, {'use_sim_time': True}],
        ),
        Node(
            package='right_angle_stack',
            executable='track_perception',
            name='track_perception',
            output='screen',
            parameters=[stack_config, {
                'track_sdf': track_sdf,
                'map_topic': perception_map_topic,
                'detections_topic': perception_detections_topic,
                'use_sim_time': True,
            }],
            condition=IfCondition(use_builtin_perception),
        ),
        Node(
            package='sim_perception',
            executable='sim_node',
            name='sim_perception',
            output='screen',
            condition=IfCondition(use_sim_perception),
        ),
        Node(
            package='right_angle_stack',
            executable='cone_mapper',
            name='cone_mapper',
            output='screen',
            parameters=[stack_config, {
                'perception_map_topic': perception_map_topic,
                'perception_detections_topic': perception_detections_topic,
                'use_sim_time': True,
            }],
        ),
        Node(
            package='right_angle_stack',
            executable='right_angle_planner',
            name='right_angle_planner',
            output='screen',
            parameters=[stack_config, {'use_sim_time': True}],
        ),
        Node(
            package='right_angle_stack',
            executable='pure_pursuit_controller',
            name='pure_pursuit_controller',
            output='screen',
            parameters=[stack_config, {'use_sim_time': True}],
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            output='screen',
            condition=IfCondition(use_rviz),
        ),
    ])
