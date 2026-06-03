# 进阶作业

本功能包用于完成 ROS2 进阶作业：播放给定的map_to_visualize bag，订阅其中的/estimation/slam/map地图话题，并把红色、蓝色、未知颜色锥桶显示到RViz中。

## 思路

bag中需要可视化的话题是/estimation/slam/map

消息类型是fsd_common_msgs/msg/Map

Map中包含四类锥桶数组，分别是

cone_yellow
cone_blue
cone_red
cone_unknown

理论上节点订阅Map后，把每类锥桶的position转换成RViz的visualization_msgs/msg/MarkerArray。
输出话题是/visualization/cone_markers
RViz的Fixed Frame使用world，因为给定bag中Map.header.frame_id是world。为了避免RViz报Frame [world] does not exist，让launch文件额外发布一个静态TF，使world frame确实出现在TF树中。

## 编译

在 ROS2 Jazzy 环境中执行

```bash
cd Week4/ros2_learning-main/ros2_homework_advanced
source /opt/ros/jazzy/setup.bash
colcon build --packages-select fsd_common_msgs cone_map_visualizer
source install/setup.bash
```

## 启动方式

编译成功并source后，直接运行

```bash
ros2 launch cone_map_visualizer visualize_cone_map.launch.py
```

预期在RViz中看到蓝色、红色和灰色锥桶点云式marker。

## 手动启动（run和play）

第一个终端播放bag

```bash
cd Week4/ros2_learning-main/ros2_homework_advanced
source install/setup.bash
ros2 bag play --loop map_to_visualize
```

第二个终端启动可视化节点

```bash
cd Week4/ros2_learning-main/ros2_homework_advanced
source install/setup.bash
ros2 run cone_map_visualizer cone_map_visualizer
```

第三个终端发布静态TF

```bash
cd Week4/ros2_learning-main/ros2_homework_advanced
source install/setup.bash
ros2 run tf2_ros static_transform_publisher --x 0 --y 0 --z 0 --roll 0 --pitch 0 --yaw 0 --frame-id world --child-frame-id map
```

第四个终端打开RViz

```bash
cd Week4/ros2_learning-main/ros2_homework_advanced
source install/setup.bash
rviz2 -d install/cone_map_visualizer/share/cone_map_visualizer/rviz/cone_map.rviz
```

## Launch 参数

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| input_topic | /estimation/slam/map | 订阅的地图话题 |
| marker_topic | /visualization/cone_markers | 发布给RViz的MarkerArray话题 |
| frame_override | 空字符串 | 为空时使用Map.header.frame_id；非空时强制覆盖marker坐标系 |
| marker_scale | 0.45 | 锥桶marker的显示尺寸 |
| z_offset | 0.18 | 把marker稍微抬高，这样更显眼 |
| bag_path | 安装后的map_to_visualize | launch自动播放的bag路径 |
| play_bag | true | 是否由launch自动播放bag |
| use_rviz | true | 是否由launch自动打开RViz |

## 问题修复

进阶作业里只用到了fsd_common_msgs/msg/Map和fsd_common_msgs/msg/Cone。为了适配ROS2 Jazzy，我让现在的fsd_common_msgs只生成这两个接口，避免其他原因导致运行失败。
此外，msg的解析疑似存在兼容性问题，故这部分让AI直接生成了msg的最终产物文件，防止依赖报错。
（还要确认是不是jazzy和humble确实存在兼容问题/(ㄒoㄒ)/~~）
最终可视化一开始没看到锥桶的位置，排查后发现MarkerArray未激活，在RViz里启动后遂正常看到锥桶。

## 学习笔记

### rosbag2的作用

本作业给出的map_to_visualize是一个rosbag2数据包，可以理解为提前录制好的ROS2话题数据。运行bag后，它会重新发布录制时保存的话题，本作业主要使用其中的/estimation/slam/map；
常用检查命令如下。

```bash
ros2 bag info map_to_visualize
ros2 bag play map_to_visualize
ros2 topic list
ros2 topic echo /estimation/slam/map --once
```

### bag话题和消息类型的关系

bag只负责回放数据，决定数据结构的是消息类型。例如/estimation/slam/map使用了fsd_common_msgs/msg/Map
所以必须先正确编译并source fsd_common_msgs，否则ROS2无法解析bag里的自定义消息。

### Map 和 Cone 消息结构

可视化锥桶地图时主要用到两个接口

- fsd_common_msgs/msg/Map
- fsd_common_msgs/msg/Cone

Map表示一帧锥桶地图，里面按颜色保存多组锥桶，例如蓝色、黄色、橙色、未知颜色等。Cone表示单个锥桶，核心字段是空间位置geometry_msgs/Point position;
可视化节点订阅Map后，会遍历不同颜色的锥桶数组，把每个锥桶的position.x,position.y,position.z转换成 RViz中的marker。

### ROS2 Jazzy下的接口生成问题

（这部分主要是靠AI解决了兼容的问题，不然真没法做了😭）
完成作业不必把fsd_common_msgs的消息全部用上，而且其中部分消息在ROS2 Jazzy的.msg转换阶段容易触发兼容性报错，所以让AI给到了最终生成的文件，跳过高风险步骤；
最终解决方案应该是重装ROS的版本······

### 调试方法

一开始没看到锥桶的时候，我用这些命令的返回内容推测锥桶是否正常播放了：

```bash
source install/setup.bash
ros2 topic list
ros2 topic echo /estimation/slam/map --once
ros2 topic echo /visualization/cone_markers --once
```

然后确认 RViz：

```text
Fixed Frame = world
Display 类型 = MarkerArray
Topic = /visualization/cone_markers
```

当然结果上面说过了，虚惊一场（
