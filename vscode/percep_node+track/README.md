# Gazebo 仿真任务：直角弯

本目录已经补成一个 ROS 2 + Gazebo Classic 工作区。默认流程为：

`Gazebo 赛道/车辆 -> 传感器 -> localization -> perception -> mapping -> planning -> control -> /cmd_vel`

## 坐标系

- 全局坐标系：`world`，按 ENU 东北天定义，`x` 向东，`y` 向北，`z` 向上。
- 车体坐标系：`base_link`，按 FLU 前左上定义，`x` 向前，`y` 向左，`z` 向上。
- 起点：`(0, -15)`，朝北，所以 Gazebo 初始 yaw 为 `pi/2`。
- world 经纬度原点在 `tracks/worlds/right_angle.world` 的 `<spherical_coordinates>` 中定义。

## 主要包

- `fsd_common_msgs`：最小消息包，包含 `Cone`、`ConeDetections`、`Map`。
- `right_angle_track`：赛道 world、锥桶模型和 mesh。
- `right_angle_stack`：车辆 URDF/xacro、launch、RViz、定位、建图、规划、控制节点。
- `sim_perception`：原始加密感知包，保留不改。

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

定位节点会把 GPS 经纬度用局部切平面转成 ENU 米制坐标，并用轮速、IMU z 轴角速度、磁力计航向做互补融合。磁力计航向计算见 `right_angle_stack/right_angle_stack/localization_fusion.py`。

## 构建与运行

在 Linux/WSL 的 ROS 2 + Gazebo Classic 环境中运行：

```bash
cd 大作业/percep_node+track
source /opt/ros/humble/setup.bash   # 或你的 ROS 2 发行版
colcon build --symlink-install
source install/setup.bash
ros2 launch right_angle_stack right_angle_sim.launch.py
```

默认会启动内置感知替身 `track_perception`，它从赛道 SDF 读取锥桶，在 `base_link` 前方范围内发布带噪声的锥桶观测，用于完整跑通建图-规划-控制链路。

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

## 说明

- 相机和雷达在 RViz 中可视化即可；RViz 配置在 `right_angle_stack/rviz/right_angle.rviz`。
- 车辆模型用 Gazebo `diff_drive` 插件接收 `/cmd_vel`，项目重点放在传感器位姿、定位、建图、规划、控制链路。若队友要求 Ackermann 模型，可替换 URDF 驱动插件，保留上层 `/cmd_vel` 或改控制节点输出接口。
- 如果你的 Gazebo 环境缺少 GPS 或磁力计插件，可加 `use_synthetic_sensors:=true`，用 `/gazebo/model_states` 生成同名传感器话题调试上层算法。
- 本项目按 Gazebo Classic 写法组织。如果课程环境是 `gz sim`/Gazebo Harmonic，需要把 launch 和 Gazebo 插件名迁移到 `ros_gz_sim`/`ros_gz_bridge`。
