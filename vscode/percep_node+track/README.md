# Gazebo 仿真任务：直角弯

本目录是一个 ROS 2 + Gazebo Classic 工作区，完成直角弯任务的仿真链路：

`Gazebo 赛道/车辆 -> 传感器 -> localization -> perception -> mapping -> planning -> control -> /cmd_vel`

## 坐标系约定

- 全局坐标系：`world`，采用 ENU 东北天坐标系，`x` 向东，`y` 向北，`z` 向上。
- 车辆底盘坐标系：`base_link`，采用 FLU 前左上坐标系，`x` 向前，`y` 向左，`z` 向上。
- 起点：`(0, -15)`，车辆朝北，因此 Gazebo 初始 yaw 为 `pi/2`。
- world 经纬度原点在 `tracks/worlds/right_angle.world` 的 `<spherical_coordinates>` 中定义。

## 包结构

- `fsd_common_msgs`：最小消息包，包含 `Cone`、`ConeDetections`、`Map`。
- `right_angle_track`：赛道 world、锥桶模型和 mesh。
- `right_angle_stack`：车辆 URDF/xacro、launch、RViz、定位、建图、规划、控制节点。
- `sim_perception`：老师提供的加密感知包，保留不改。

## 传感器与话题

- 相机：`/sensors/camera/image_raw`
- 激光雷达：`/sensors/lidar/scan`
- GPS：`/sensors/gps/fix`
- IMU：`/sensors/imu/data_raw`
- 轮速里程计：`/sensors/wheel_odom`
- 磁力计：`/sensors/magnetic_field`
- 融合定位输出：`/localization/odom`、`/localization/pose`、TF `world -> base_link`
- 建图输出：`/estimation/slam/map`、`/visualization/cone_map`
- 规划输出：`/planning/centerline`
- 控制输出：`/cmd_vel`

定位节点会把 GPS 经纬度用局部切平面转换成 ENU 米制坐标，再结合轮速、IMU z 轴角速度和磁力计航向做互补融合。具体实现见 `right_angle_stack/right_angle_stack/localization_fusion.py`。

## 构建与运行

在 Linux/WSL 的 ROS 2 + Gazebo Classic 环境中运行。Jazzy 示例：

```bash
cd /SCUT_Racing_Tasks/vscode/percep_node+track
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
ros2 launch right_angle_stack right_angle_sim.launch.py
```

如果你使用 Humble，把第一行 source 改成：

```bash
source /opt/ros/humble/setup.bash
```

默认会启动内置感知替身 `track_perception`。它从赛道 SDF 读取锥桶，在 `base_link` 前方范围内发布带噪声的锥桶观测，用于跑通建图、规划和控制链路。

## Jazzy 编译注意事项

ROS 2 Jazzy 对 `.msg -> .idl` 转换更严格。若直接用 `.msg` 生成接口，可能出现类似错误：

```text
list index: 1 out of range
Target dependency .../rosidl_adapter/fsd_common_msgs/msg/Cone.idl does not exist
```

本项目已经为 `fsd_common_msgs` 提供了 `.idl` 文件，并在 `fsd_common_msgs/CMakeLists.txt` 中直接使用：

```cmake
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Cone.idl"
  "msg/ConeDetections.idl"
  "msg/Map.idl"
  DEPENDENCIES geometry_msgs std_msgs
)
```

如果你之前已经编译失败过，需要清理旧缓存后重新编译：

```bash
cd /SCUT_Racing_Tasks/vscode/percep_node+track
rm -rf build/fsd_common_msgs install/fsd_common_msgs log
colcon build --packages-select fsd_common_msgs --cmake-clean-cache
source install/setup.bash
colcon build
```

如果仍有缓存问题，清整个工作区：

```bash
rm -rf build install log
colcon build --symlink-install
```

## 使用老师给的感知节点

如果使用 `sim_perception`：

```bash
ros2 launch right_angle_stack right_angle_sim.launch.py \
  use_builtin_perception:=false \
  use_sim_perception:=true
```

建图节点默认订阅：

- `fsd_common_msgs/msg/Map`：`/perception/cones`
- `fsd_common_msgs/msg/ConeDetections`：`/perception/cone_detections`

如果老师节点发布的话题不同，可以在 launch 中指定：

```bash
ros2 launch right_angle_stack right_angle_sim.launch.py \
  use_builtin_perception:=false \
  use_sim_perception:=true \
  perception_map_topic:=/your/map/topic \
  perception_detections_topic:=/your/detections/topic
```

## 调试命令

```bash
ros2 topic list
ros2 topic echo /localization/odom --once
ros2 topic echo /estimation/slam/map --once
ros2 topic echo /planning/centerline --once
ros2 topic echo /cmd_vel --once
```

RViz 配置在 `right_angle_stack/rviz/right_angle.rviz`，相机和雷达可直接在 RViz 中查看。

## 说明

- 车辆模型使用 Gazebo `diff_drive` 插件接收 `/cmd_vel`，项目重点是传感器位姿、定位、建图、规划、控制链路。
- 如果队友要求 Ackermann 模型，可以替换 URDF 驱动插件，并相应修改控制节点输出接口。
- 如果 Gazebo 环境缺少 GPS 或磁力计插件，可以启动时加 `use_synthetic_sensors:=true`，用 `/gazebo/model_states` 生成同名传感器话题调试上层算法。
- 本项目按 Gazebo Classic 写法组织。如果课程环境是 `gz sim`/Gazebo Harmonic，需要把 launch 和 Gazebo 插件迁移到 `ros_gz_sim`/`ros_gz_bridge`。
