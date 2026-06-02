# 锥桶地图可视化作业

本功能包用于完成 ROS2 进阶作业：播放给定的 `map_to_visualize` bag，订阅其中的 `/estimation/slam/map` 地图话题，并把红色、蓝色、未知颜色锥桶显示到 RViz 中。

## 实现思路

bag 中需要可视化的话题是：

```text
/estimation/slam/map
```

消息类型是：

```text
fsd_common_msgs/msg/Map
```

`Map` 中包含四类锥桶数组：

```text
cone_yellow
cone_blue
cone_red
cone_unknown
```

本节点订阅 `Map` 后，把每类锥桶的 `position` 转换成 RViz 的 `visualization_msgs/msg/MarkerArray`。其中红色、蓝色、未知颜色分别使用不同namespace和颜色显示；黄色锥桶也保留支持。

输出话题是：

```text
/visualization/cone_markers
```

RViz的Fixed Frame使用world，因为给定bag中Map.header.frame_id是world。

## 启动方式

编译成功并source后，运行

```bash
ros2 launch cone_map_visualizer visualize_cone_map.launch.py
```

正常情况下，RViz 中会看到蓝色、红色和灰色锥桶点云式 marker。

## 手动启动

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

第三个终端打开RViz

```bash
cd Week4/ros2_learning-main/ros2_homework_advanced
source install/setup.bash
rviz2 -d install/cone_map_visualizer/share/cone_map_visualizer/rviz/cone_map.rviz
```

## Launch 参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `input_topic` | `/estimation/slam/map` | 订阅的地图话题 |
| `marker_topic` | `/visualization/cone_markers` | 发布给 RViz 的 MarkerArray 话题 |
| `frame_override` | 空字符串 | 为空时使用 `Map.header.frame_id`；非空时强制覆盖 marker 坐标系 |
| `marker_scale` | `0.45` | 锥桶 marker 的显示尺寸 |
| `z_offset` | `0.18` | 把 marker 稍微抬高，避免贴地不明显 |
| `bag_path` | 安装后的 `map_to_visualize` | launch 自动播放的 bag 路径 |
| `play_bag` | `true` | 是否由 launch 自动播放 bag |
| `use_rviz` | `true` | 是否由 launch 自动打开 RViz |

只启动节点和 bag，不打开 RViz：

```bash
ros2 launch cone_map_visualizer visualize_cone_map.launch.py use_rviz:=false
```

只启动节点和 RViz，不自动播放 bag：

```bash
ros2 launch cone_map_visualizer visualize_cone_map.launch.py play_bag:=false
```

使用其它 bag：

```bash
ros2 launch cone_map_visualizer visualize_cone_map.launch.py bag_path:=/path/to/map_to_visualize
```

## 报错修复说明

这个进阶任务只用到了fsd_common_msgs/msg/Map和fsd_common_msgs/msg/Cone。为了适配ROS2 Jazzy，现在的fsd_common_msgs只生成这两个接口。
此外，msg的解析疑似存在兼容性问题，故这部分让AI直接生成了msg的最终产物文件，防止依赖报错。
