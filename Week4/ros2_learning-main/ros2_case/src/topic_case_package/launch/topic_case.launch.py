from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    turtlesim_node = Node(
        package='turtlesim',  #功能包名
        executable='turtlesim_node', #可执行文件名
        name='turtlesim',     #节点名称、
        output='screen',      #输出位置
    )

    topic_publisher_node = Node(
        package='topic_case_package',
        executable='topic_publisher',
        name='topic_publisher',
        output='screen',
    )

    topic_subscriber_node = Node(
        package='topic_case_package',
        executable='topic_subscriber',
        name='topic_subscriber',
        output='screen',
    )

    return LaunchDescription([
        turtlesim_node,
        topic_publisher_node,
        topic_subscriber_node,
    ])