from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    figure_eight_config = PathJoinSubstitution(
        [FindPackageShare('ros2_homework_basic_package'), 'config', 'figure_eight.yaml']
    )

    turtlesim_node = Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='turtlesim',
        output='screen',
    )

    figure_eight_node = Node(
        package='ros2_homework_basic_package',
        executable='figure_eight_turtle',
        name='figure_eight_turtle',
        output='screen',
        parameters=[figure_eight_config],
    )

    return LaunchDescription([
        turtlesim_node,
        figure_eight_node,
    ])
