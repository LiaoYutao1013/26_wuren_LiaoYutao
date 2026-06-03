# ROS2 基础作业文档

## 文件说明

（略过路径了，写出来好长）

- figure_eight_turtle.py向/turtle1/cmd_vel话题发布geometry_msgs/msg/Twist速度指令；
- figure_eight.yaml作为参数配置文件；
- figure_eight.launch.py启动turtlesim_node和8字形运动控制节点，并加载YAML参数。

## 编译

在工作空间目录下执行

```bash
cd ros2_homework_basic_ws
colcon build
source install/setup.bash
```

## 运行

在终端执行以下命令启动小海龟

```bash
ros2 launch ros2_homework_basic_package figure_eight.launch.py #终端1
ros2 run ros2_homework_basic_package keyboard_quit_node #终端2
```

程序启动后，小海龟会先沿一个完整圆周运动，然后反转角速度沿另一个完整圆周运动，两个圆相切，形成8字形轨迹。
此外，可在终端2通过按键q退出程序（Ctrl+C感觉不是很优雅啊）

## 学习记录

### 工作空间结构

ROS2工程一般目录结构如下：

```text
ros2_homework_basic_ws
├── src
│   └── ros2_homework_basic_package
├── build
├── install
└── log
```

其中/src用来存放源码包(手动创建)，/build,/install,/log是build自动生成的目录。
功能包中需要包含package.xml,setup.py等文件，用于声明依赖、安装规则和可执行节点。

### 节点

节点是 ROS2 中执行具体功能的基本单位。本作业中包含两个节点：

- figure_eight_turtle：发布速度指令，控制小海龟绘制8字形轨迹；
- keyboard_quit_node：监听键盘输入，按q发布退出信号。

节点之间不直接调用彼此的函数，而是通过话题、服务、参数等 ROS2 通信机制交换信息。
（思考为什么我们车队主要用话题？）

### 话题通信

话题适合连续或异步的数据传输。本作业使用了两个话题：

- /turtle1/cmd_vel：向turtlesim发布geometry_msgs/msg/Twist消息，控制小海龟线速度和角速度；
- /figure_eight/quit：发布退出信号，让控制节点停止运动并退出。

Twist消息中常用字段包括

linear.x   控制前进速度
angular.z  控制绕z轴旋转的角速度

对turtlesim，只需设置linear.x和angular.z就可以实现平面运动控制。

### 参数与 YAML 配置

ROS2节点可以通过参数控制运行行为。将固定参数写入YAML文件的好处是不用修改源码就能调整运动效果。

我使用的YAML参数包括

- linear_velocity：小海龟线速度；
- angular_velocity：小海龟角速度；
- publish_rate_hz：速度指令发布频率；
- initial_delay_sec：启动后的等待时间；
- figure_eight_repetitions：8字重复次数；
- start_clockwise：是否从顺时针方向开始；
- keyboard_quit_enabled：是否启用键盘退出；
- quit_key：退出按键。

我画8字的思路：匀速画完一个圆，回到起点时往另一个方向画圆，然后就拼出一个8字了。
（要先拉一段切线再开始画圆也不是不可以，但稍微有些复杂，就没实施）

### launch文件

launch文件是启动整个工程的入口，运行完整程序时从这启动。如果要调试部分功能的话，用run启动部分节点也是可以的
（全部run起来也差不多达到launch的效果了，但很繁琐）
（但run有run的优势，比如我这次键盘控制就要run启动，但海龟自己好像有键盘事件？）
launch文件查找工程下文件（很像CMakeList?），初始化节点,引导整个项目启动。
例如这次基础任务的launch就用了以下节点和YAML文件：

- turtlesim_node；
- figure_eight_turtle；
- YAML 参数文件。

使用 launch 文件可以减少手动输入命令的次数，也方便统一管理节点名称、参数文件和输出方式。
面试时被问到launch是用什么写的，现在总算搞明白了（

### 键盘退出控制（自己想加的小功能）

最开始尝试让控制节点直接监听键盘输入，但通过ros2 launch启动时，节点总是打印stdin is not a TTY
问AI得到的原因是launch启动的节点通常拿不到真实终端输入。解决方法是把键盘监听也写成一个节点，在交互终端中运行。

```bash
ros2 run ros2_homework_basic_package keyboard_quit_node
```

键盘监听节点收到q后，通过话题发布退出信号。控制节点订阅该话题，收到信号后发布零速度并退出。这样比让运动控制节点直接读取键盘更稳定。

### 常用命令

```bash
#编译工作空间
colcon build

#加载环境
source install/setup.bash

#启动launch文件
ros2 launch

#启动特定节点
ros2 run

#查看节点列表
ros2 node list

#查看话题列表
ros2 topic list

#查看话题消息类型
ros2 topic info 

#对话题手动发布指令，调整参数（后面的根据文件实际要用什么来填）
ros2 topic pub
```
