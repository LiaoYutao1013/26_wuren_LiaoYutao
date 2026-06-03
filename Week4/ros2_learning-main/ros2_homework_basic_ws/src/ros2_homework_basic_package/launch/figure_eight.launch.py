from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    #从已安装包的share目录中查找参数文件
    figure_eight_config = PathJoinSubstitution(
        [FindPackageShare('ros2_homework_basic_package'), 'config', 'figure_eight.yaml']
    )

    #turtlesim_node提供仿真窗口和/turtle1/cmd_vel速度控制接口。
    turtlesim_node = Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='turtlesim',
        output='screen',
    )

    #figure_eight_turtle节点读取YAML参数，向turtlesim发布Twist指令。
    figure_eight_node = Node(
        package='ros2_homework_basic_package',
        executable='figure_eight_turtle',
        name='figure_eight_turtle',
        output='screen',
        #emulate_tty=True让launch终端保持交互
        emulate_tty=True,
        parameters=[figure_eight_config],
    )

    #launch启动时管理的节点列表
    return LaunchDescription([
        turtlesim_node,
        figure_eight_node,
    ])
