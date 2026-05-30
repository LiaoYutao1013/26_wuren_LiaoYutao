from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # 启动 turtlesim 节点，参数客户端会连接到这个节点的参数服务。
    turtlesim_node = Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='turtlesim',
        output='screen',
    )

    # 启动键盘遥控节点，配合 turtlesim 进行手动控制。
    turtle_teleop_key_node = Node(
        package='turtlesim',
        executable='turtle_teleop_key',
        name='turtle_teleop_key',
        output='screen',
        emulate_tty=True,    #模拟终端输入，使得键盘输入能够被正确识别
    )

    # 读取配置文件，为本节点提供参数化的运行配置（这里是直接在launch文件里加载yaml文件了，如果不想的话可以用PPT上的命令在运行时加载）。
    param_case_config = PathJoinSubstitution(
        [FindPackageShare('param_case_package'), 'config', 'param_case.yaml']
    )

    # 启动参数客户端节点，持续修改 turtlesim 的背景颜色。
    param_case_node = Node(
        package='param_case_package',
        executable='param_case',
        name='param_case',
        output='screen',
        parameters=[param_case_config],
    )

    return LaunchDescription([
        turtlesim_node,
        turtle_teleop_key_node,
        param_case_node,
    ])