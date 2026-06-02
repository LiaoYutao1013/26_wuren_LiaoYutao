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

本节点订阅 `Map` 后，把每类锥桶的 `position` 转换成 RViz 的 `visualization_msgs/msg/MarkerArray`。其中红色、蓝色、未知颜色分别使用不同 namespace 和颜色显示；黄色锥桶也保留支持。

输出话题是：

```text
/visualization/cone_markers
```

RViz 的 Fixed Frame 使用 `world`，因为给定 bag 中 `Map.header.frame_id` 是 `world`。为了避免 RViz 报 `Frame [world] does not exist`，launch 文件会额外发布一个静态 TF，让 `world` frame 出现在 TF 树中。

## 编译

在 ROS2 Jazzy 环境中执行：

```bash
cd Week4/ros2_learning-main/ros2_homework_advanced
source /opt/ros/jazzy/setup.bash
colcon build --packages-select fsd_common_msgs cone_map_visualizer
source install/setup.bash
```

如果之前编译失败过，建议先清理缓存：

```bash
rm -rf build install log
```

然后重新执行上面的编译命令。

## 推荐启动方式

编译成功并 `source install/setup.bash` 后，直接运行：

```bash
ros2 launch cone_map_visualizer visualize_cone_map.launch.py
```

这个 launch 会自动完成四件事：

1. 启动 `cone_map_visualizer` 节点。
2. 发布静态 TF，让 `world` frame 出现在 RViz 的 TF 树中。
3. 打开 RViz，并加载本包自带的 RViz 配置。
4. 循环播放已给的 `map_to_visualize` bag。

正常情况下，RViz 中会看到蓝色、红色和灰色锥桶点云式 marker。

## 手动启动方式

如果想分开观察各个步骤，也可以手动启动。

第一个终端播放 bag：

```bash
cd Week4/ros2_learning-main/ros2_homework_advanced
source install/setup.bash
ros2 bag play --loop map_to_visualize
```

第二个终端启动可视化节点：

```bash
cd Week4/ros2_learning-main/ros2_homework_advanced
source install/setup.bash
ros2 run cone_map_visualizer cone_map_visualizer
```

第三个终端发布静态 TF：

```bash
cd Week4/ros2_learning-main/ros2_homework_advanced
source install/setup.bash
ros2 run tf2_ros static_transform_publisher --x 0 --y 0 --z 0 --roll 0 --pitch 0 --yaw 0 --frame-id world --child-frame-id map
```

第四个终端打开 RViz：

```bash
cd Week4/ros2_learning-main/ros2_homework_advanced
source install/setup.bash
rviz2 -d install/cone_map_visualizer/share/cone_map_visualizer/rviz/cone_map.rviz
```

如果不使用配置文件，也可以手动在 RViz 中设置：

```text
Fixed Frame: world
Display Type: MarkerArray
Marker Topic: /visualization/cone_markers
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

## 常见问题

如果 RViz 没有显示锥桶，按下面顺序检查。

1. 确认已经执行：

```bash
source install/setup.bash
```

2. 确认 bag 正在发布地图话题：

```bash
ros2 topic list
```

应该能看到：

```text
/estimation/slam/map
```

3. 确认可视化节点正在发布 marker：

```bash
ros2 topic echo /visualization/cone_markers --once
```

4. 确认 RViz 的 Fixed Frame 是：

```text
world
```

5. 如果 RViz 报 `Frame [world] does not exist`，说明 TF 树中没有 `world`。手动启动时需要运行：

```bash
ros2 run tf2_ros static_transform_publisher --x 0 --y 0 --z 0 --roll 0 --pitch 0 --yaw 0 --frame-id world --child-frame-id map
```

6. 确认 RViz 中添加的是 `MarkerArray`，话题是：

```text
/visualization/cone_markers
```

## 关于 fsd_common_msgs

本作业只需要 `fsd_common_msgs/msg/Map` 和 `fsd_common_msgs/msg/Cone`。为了适配 ROS2 Jazzy 并避免其它车队消息在接口转换阶段产生无关报错，当前 `fsd_common_msgs` 只生成这两个接口。

`std_msgs` 不能删除，因为 `Map` 中包含：

```text
std_msgs/Header header
```

`geometry_msgs` 也不能删除，因为 `Cone` 中包含：

```text
geometry_msgs/Point position
```

## 报错修复说明

这个进阶任务只用到了fsd_common_msgs/msg/Map和fsd_common_msgs/msg/Cone。为了适配ROS2 Jazzy，现在的fsd_common_msgs只生成这两个接口。
此外，msg的解析疑似存在兼容性问题，故这部分让AI直接生成了msg的最终产物文件，防止依赖报错。
