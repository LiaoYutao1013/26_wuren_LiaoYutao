# ROS2 基础作业使用说明

该文件夹下编写了一个ROS2项目，用于控制turtlesim中的小海龟沿8字形轨迹运动。

## 文件说明

- `src/ros2_homework_basic_package/ros2_homework_basic_package/figure_eight_turtle.py`：控制节点源码，向 `/turtle1/cmd_vel` 话题发布 `geometry_msgs/msg/Twist` 速度指令。
- `src/ros2_homework_basic_package/config/figure_eight.yaml`：控制器使用的固定参数配置文件。
- `src/ros2_homework_basic_package/launch/figure_eight.launch.py`：启动文件，用于同时启动 `turtlesim_node` 和“8”字形运动控制节点，并加载 YAML 参数。

## 编译

在工作空间目录下执行：

```bash
cd ros2_homework_basic_ws
colcon build
source install/setup.bash
```

## 运行

编译并加载环境后，执行：

```bash
ros2 launch ros2_homework_basic_package figure_eight.launch.py
```

程序启动后，小海龟会先沿一个完整圆周运动，然后反转角速度沿另一个完整圆周运动，两个圆相切，形成8字形轨迹。
此外，可通过按键q退出程序（Ctrl+C感觉不是很优雅啊）
