# ROS 2 launch 文件常见用法速查

这份文档整理 ROS 2 Python launch 文件里最常见的写法：启动节点、传入参数、读取配置文件、执行指令，以及常见参数类型和格式。下面的示例和你当前的 [param_case.launch.py](launch/param_case.launch.py) 风格保持一致。

## 1. 基本骨架

ROS 2 的 Python launch 文件通常都以 `generate_launch_description()` 为入口，最后返回一个 `LaunchDescription`。

```python
from launch import LaunchDescription


def generate_launch_description():
    return LaunchDescription([
        # 在这里放各种 launch action
    ])
```

常见导入包括：

```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
```

## 2. 启动节点

启动节点最常用的是 `Node`。

```python
Node(
    package='turtlesim',
    executable='turtlesim_node',
    name='turtlesim',
    namespace='',
    output='screen',
)
```

### 常见字段

- `package`：节点所在包名。
- `executable`：可执行文件名。
- `name`：节点名。
- `namespace`：命名空间。
- `output`：输出方式，常用 `screen`。
- `emulate_tty`：是否模拟终端，常用于需要键盘输入的程序。
- `parameters`：传入参数，支持字典、YAML 文件路径、LaunchConfiguration 等。
- `remappings`：话题或服务重映射。
- `arguments`：给可执行程序传命令行参数。
- `condition`：条件执行。
- `respawn`：节点退出后是否自动重启。

## 3. 传入参数

ROS 2 launch 里通常先声明参数，再读取参数。

### 3.1 声明参数

```python
DeclareLaunchArgument(
    'use_sim_time',
    default_value='false',
    description='是否使用仿真时间',
)
```

### 3.2 读取参数

```python
use_sim_time = LaunchConfiguration('use_sim_time')
```

### 3.3 传给节点

```python
Node(
    package='demo_nodes_cpp',
    executable='talker',
    parameters=[
        {'use_sim_time': use_sim_time},
    ],
)
```

### 常见格式

- 启动参数声明时，`default_value` 通常写成字符串。
- 节点参数可以来自 launch 参数、固定字面量、YAML 文件或它们的组合。
- 如果需要把 launch 参数明确转换成布尔、整数或浮点数，通常要配合 `ParameterValue` 使用。

示例：

```python
Node(
    package='demo_nodes_cpp',
    executable='talker',
    parameters=[
        {
            'use_sim_time': ParameterValue(LaunchConfiguration('use_sim_time'), value_type=bool),
            'rate': ParameterValue(LaunchConfiguration('rate'), value_type=int),
        }
    ],
)
```

## 4. 读取配置文件

最常见的是读取 YAML 参数文件。常见写法是先找到包路径，再拼接配置文件路径，最后传给节点。

```python
param_file = PathJoinSubstitution(
    [FindPackageShare('param_case_package'), 'config', 'param_case.yaml']
)

Node(
    package='param_case_package',
    executable='param_case',
    name='param_case',
    output='screen',
    parameters=[param_file],
)
```

### YAML 参数文件格式

```yaml
param_case:
  ros__parameters:
    background_r: 255
    background_g: 0
    background_b: 0
```

### YAML 里常见数据类型

- 字符串：`hello`
- 整数：`1`
- 浮点数：`0.5`
- 布尔值：`true` / `false`
- 列表：`[1, 2, 3]`

### 常见节点参数写法

```python
Node(
    package='param_case_package',
    executable='param_case',
    parameters=[
        param_file,
        {'background_r': 255, 'background_g': 0, 'background_b': 0},
    ],
)
```

## 5. 执行指令

如果你要在 launch 阶段真正启动一个外部命令，常用 `ExecuteProcess`。

```python
ExecuteProcess(
    cmd=['ros2', 'topic', 'list'],
    output='screen',
)
```

### `ExecuteProcess` 和 `Command` 的区别

- `ExecuteProcess`：真的执行一个进程。
- `Command`：执行命令并把结果作为字符串返回，通常用于生成参数或动态内容。

### `Command` 示例

```python
robot_description = Command([
    'xacro ',
    PathJoinSubstitution([
        FindPackageShare('my_robot_description'),
        'urdf',
        'robot.urdf.xacro',
    ])
])
```

## 6. 条件执行

有些节点只在满足条件时启动，可以用 `IfCondition` 或 `UnlessCondition`。

```python
Node(
    package='turtlesim',
    executable='turtle_teleop_key',
    name='turtle_teleop_key',
    output='screen',
    emulate_tty=True,
    condition=IfCondition(LaunchConfiguration('enable_teleop')),
)
```

## 7. 重映射

话题重映射常见写法如下：

```python
Node(
    package='demo_nodes_cpp',
    executable='talker',
    remappings=[
        ('/chatter', '/my_chatter'),
    ],
)
```

## 8. 常见参数类型和格式

### 8.1 Launch 参数类型

`DeclareLaunchArgument` 声明的值通常先作为字符串处理。

```python
DeclareLaunchArgument('rate', default_value='10')
DeclareLaunchArgument('use_sim_time', default_value='false')
```

### 8.2 节点参数类型

`Node(parameters=[...])` 里常见的类型有：

- 字典：`{'foo': 'bar'}`
- YAML 文件路径：`param_file`
- `LaunchConfiguration`
- `ParameterValue`
- 列表：`[1, 2, 3]`

### 8.3 `ParameterValue` 的常见用途

当你需要把 launch 参数明确转换为某种类型时，常用它。

```python
ParameterValue(LaunchConfiguration('use_sim_time'), value_type=bool)
ParameterValue(LaunchConfiguration('rate'), value_type=int)
ParameterValue(LaunchConfiguration('scale'), value_type=float)
ParameterValue(LaunchConfiguration('frame_id'), value_type=str)
```

## 9. 结合你当前文件的一个完整示例

下面这个例子对应你现在的 launch 写法：先启动 `turtlesim`，再启动键盘控制节点，最后加载参数客户端节点的 YAML 配置。

```python
from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    turtlesim_node = Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='turtlesim',
        output='screen',
    )

    turtle_teleop_key_node = Node(
        package='turtlesim',
        executable='turtle_teleop_key',
        name='turtle_teleop_key',
        output='screen',
        emulate_tty=True,
    )

    param_case_config = PathJoinSubstitution(
        [FindPackageShare('param_case_package'), 'config', 'param_case.yaml']
    )

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
```

## 10. 一句话记忆

- 启动节点用 `Node`。
- 启动参数用 `DeclareLaunchArgument` + `LaunchConfiguration`。
- 配置文件常用 `FindPackageShare` + `PathJoinSubstitution` + `parameters=[yaml]`。
- 真执行命令用 `ExecuteProcess`。
- 要把命令结果当字符串用，用 `Command`。
