# Gazebo 仿真任务：直角弯

本目录是一个 ROS 2 Humble 工作区，后续调试默认都在本机 WSL 中完成，不切换到其他 ROS 2 发行版。

目标链路：

`Gazebo 赛道/车辆 -> 传感器 -> localization -> perception -> mapping -> planning -> control -> /cmd_vel`

当前保留三套 Humble 调试路线：

- `right_angle_wsl_headless.launch.py`：Gazebo Sim + `ros_gz_sim`/`ros_gz_bridge`，专门用于 WSL headless 调试，禁用相机和 GPU 雷达等渲染传感器。
- `right_angle_sim.launch.py`：Gazebo Classic + `gazebo_ros`，适合 Humble 默认 Classic 仿真回退。
- `right_angle_harmonic.launch.py`：Gazebo Sim + `ros_gz_sim`/`ros_gz_bridge`。文件名保留 `harmonic` 是历史命名；在当前 Humble 环境中通常实际运行的是 Ignition Gazebo / Gazebo Fortress。

## 坐标系约定

- 全局坐标系：`world`，ENU 东北天，`x` 向东，`y` 向北，`z` 向上。
- 车辆底盘坐标系：`base_link`，FLU 前左上，`x` 向前，`y` 向左，`z` 向上。
- 起点：`(0, -15)`，车辆朝北，因此初始 yaw 为 `pi/2`。
- 经纬度原点定义在 world 文件的 `<spherical_coordinates>` 中。

## 包结构

- `fsd_common_msgs`：最小消息包，包含 `Cone`、`ConeDetections`、`Map`。
- `right_angle_track`：赛道 world、锥桶模型和 mesh。
- `right_angle_stack`：车辆模型、launch、RViz、定位、建图、规划、控制节点。
- `sim_perception`：老师提供的加密感知包，保留不改。

## 传感器与话题

- 相机：`/sensors/camera/image_raw`，只在 Classic 路线和完整 Gazebo Sim 路线中启用。
- 激光雷达：`/sensors/lidar/scan`，只在 Classic 路线和完整 Gazebo Sim 路线中启用。
- GPS：`/sensors/gps/fix`
- IMU：`/sensors/imu/data_raw`
- 轮速里程计：`/sensors/wheel_odom`
- 磁力计：`/sensors/magnetic_field`
- 融合定位输出：`/localization/odom`、`/localization/pose`、TF `world -> base_link`
- 建图输出：`/estimation/slam/map`、`/visualization/cone_map`
- 规划输出：`/planning/centerline`
- 控制输出：`/cmd_vel`

定位节点会把 GPS 经纬度用局部切平面转换成 ENU 米制坐标，再结合轮速、IMU z 轴角速度和磁力计航向做互补融合。实现见 `right_angle_stack/right_angle_stack/localization_fusion.py`。

## WSL 工作区约定

建议只在 WSL ext4 文件系统中编译，例如：

```bash
/home/furina/ros_ws/percep_node+track
```

不要直接在 `/mnt/c`、`/mnt/e`、OneDrive 或 Windows 同步目录中编译。CMake/colcon 会大量创建中间文件和符号链接，Windows 挂载盘更容易出现权限、大小写、符号链接和文件锁问题。

从 Windows 工程同步到 WSL 时，不要复制旧编译产物：

```bash
mkdir -p /home/furina/ros_ws/percep_node+track
rsync -a --exclude build --exclude install --exclude log \
  "/mnt/e/Mech_Engineering/SCUT_Racing_Tasks/vscode/percep_node+track/" \
  /home/furina/ros_ws/percep_node+track/
```

## 环境检查

```bash
source /opt/ros/humble/setup.bash
printenv ROS_DISTRO
lsb_release -a
```

预期：

```text
humble
Ubuntu 22.04
```

安装基础依赖：

```bash
sudo apt update
sudo apt install python3-colcon-common-extensions \
  ros-humble-desktop \
  ros-humble-xacro \
  ros-humble-robot-state-publisher \
  ros-humble-rviz2 \
  ros-humble-gazebo-ros-pkgs
```

如果要跑 Gazebo Sim / `ros_gz` 路线，还需要确认：

```bash
sudo apt install ros-humble-ros-gz
source /opt/ros/humble/setup.bash
ros2 pkg prefix ros_gz_sim
ros2 pkg prefix ros_gz_bridge
```

如果 `ros-humble-ros-gz` 在你的 apt 源中不可用，先查看可用包名：

```bash
apt-cache search ros-humble-ros-gz
```

## 干净构建

每次删除 `build/install/log` 后都要重新构建整个工作区。不要只构建 `right_angle_stack`，因为它依赖 `fsd_common_msgs` 和 `right_angle_track`。

```bash
cd /home/furina/ros_ws/percep_node+track
rm -rf build install log
source /opt/ros/humble/setup.bash
colcon build --symlink-install --event-handlers console_direct+
source install/setup.bash
```

如果当前终端曾经 source 过旧的 `install/setup.bash`，构建前可能出现不存在路径的 `AMENT_PREFIX_PATH` 警告。最简单的处理方式是打开新 WSL 终端，只执行：

```bash
cd /home/furina/ros_ws/percep_node+track
source /opt/ros/humble/setup.bash
colcon build --symlink-install
```

## 调试路线 1：无 Gazebo 算法链路

先不启动 Gazebo，用内置锥桶感知替身验证定位、感知、建图、规划、控制节点是否能跑通。

```bash
cd /home/furina/ros_ws/percep_node+track
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch right_angle_stack right_angle_sim.launch.py \
  use_gazebo:=false \
  use_sim_time:=false \
  use_rviz:=false
```

另开终端检查：

```bash
source /opt/ros/humble/setup.bash
source /home/furina/ros_ws/percep_node+track/install/setup.bash

ros2 topic echo /localization/odom --once
ros2 topic echo /perception/cones --once
ros2 topic echo /estimation/slam/map --once
ros2 topic echo /planning/centerline --once
ros2 topic echo /cmd_vel --once
```

这些话题能输出，说明上层算法链路基本正常。

## 调试路线 2：Humble + Gazebo Sim headless

这是 WSL 中优先使用的 Gazebo 路线。它会启动 Gazebo Sim server、生成车辆、桥接 `/clock`、`/cmd_vel`、轮速里程计、GPS、IMU 和磁力计，但不加载相机、GPU 雷达和 `gz-sim-sensors-system`，用于避开 WSLg/OpenGL/OGRE2 的渲染传感器崩溃。

启动：

```bash
cd /home/furina/ros_ws/percep_node+track
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch right_angle_stack right_angle_wsl_headless.launch.py
```

检查桥接和控制链路：

```bash
source /opt/ros/humble/setup.bash
source /home/furina/ros_ws/percep_node+track/install/setup.bash

ros2 topic list
ros2 topic echo /clock --once
ros2 topic echo /sensors/wheel_odom --once
ros2 topic echo /sensors/imu/data_raw --once
ros2 topic echo /sensors/gps/fix --once
ros2 topic echo /sensors/magnetic_field --once
ros2 topic echo /localization/odom --once
ros2 topic echo /cmd_vel --once
```

确认 Gazebo Transport 侧话题：

```bash
gz topic -l | grep sensors
gz topic -l | grep cmd_vel
```

headless 路线不会发布 `/sensors/camera/image_raw` 和 `/sensors/lidar/scan`。如果这条路线可以稳定运行，说明车辆动力学、基础传感器、定位、规划和控制链路是通的；相机/GPU 雷达问题再单独处理。

## 调试路线 3：Humble + Gazebo Classic

Classic 路线使用：

- `gazebo_ros`
- `spawn_entity.py`
- `libgazebo_ros_diff_drive.so`
- `libgazebo_ros_camera.so`
- `libgazebo_ros_ray_sensor.so`
- `libgazebo_ros_imu_sensor.so`
- `libgazebo_ros_gps_sensor.so`
- `libgazebo_ros_magnetometer.so`

启动：

```bash
cd /home/furina/ros_ws/percep_node+track
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch right_angle_stack right_angle_sim.launch.py use_rviz:=false
```

检查 Gazebo Classic 关键服务和话题：

```bash
ros2 service list | grep spawn
ros2 topic echo /clock --once
ros2 topic echo /sensors/wheel_odom --once
ros2 topic echo /sensors/imu/data_raw --once
ros2 topic echo /sensors/gps/fix --once
ros2 topic echo /sensors/magnetic_field --once
ros2 topic echo /cmd_vel --once
```

如果需要 RViz：

```bash
ros2 launch right_angle_stack right_angle_sim.launch.py use_rviz:=true
```

WSL 中 RViz 闪退时先用软件渲染：

```bash
LIBGL_ALWAYS_SOFTWARE=1 rviz2 -d install/right_angle_stack/share/right_angle_stack/rviz/right_angle.rviz
```

## 调试路线 4：完整 Gazebo Sim / ros_gz

完整 Gazebo Sim 路线使用：

- `ros_gz_sim`
- `ros_gz_bridge`
- `right_angle_stack/launch/right_angle_harmonic.launch.py`
- `tracks/worlds/right_angle_harmonic.sdf`
- `right_angle_stack/models/right_angle_car_harmonic/model.sdf`

文件名中的 `harmonic` 是历史命名。当前 Humble 环境中如果日志显示 `Ignition Gazebo Server v6.x`，说明实际运行的是 Gazebo Fortress / Ignition Gazebo 6，这是 Humble 的常见组合。

这条路线包含相机和 `gpu_lidar`，即使使用 server-only 模式也会进入 Gazebo 的渲染传感器线程。WSL 中如果已经出现 `Ogre::UnimplementedException` 或 `GL3PlusTextureGpu::copyTo`，先不要用这条路线做主调试。

如果直接运行这条 launch 后 RViz 报 `frame [world] does not exist`，通常不是 `world` 坐标系配置错了，而是 Gazebo 已经先崩溃，导致车辆、`/clock`、传感器和 TF 都没有发布。此时 RViz 黑屏只是后果，应该回到 `right_angle_wsl_headless.launch.py` 验证非渲染链路。

启动：

```bash
cd /home/furina/ros_ws/percep_node+track
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch right_angle_stack right_angle_harmonic.launch.py use_rviz:=false
```

默认 `use_rviz:=false`，`gz_args` 是 `-r -s -v 4 <world>`，即只启动 Gazebo Sim server，不启动 Gazebo GUI。注意：server-only 不等于不渲染，camera 和 `gpu_lidar` 仍可能触发 OGRE2。

检查桥接和控制链路：

```bash
source /opt/ros/humble/setup.bash
source /home/furina/ros_ws/percep_node+track/install/setup.bash

ros2 topic list
ros2 topic echo /clock --once
ros2 topic echo /sensors/wheel_odom --once
ros2 topic echo /sensors/imu/data_raw --once
ros2 topic echo /sensors/gps/fix --once
ros2 topic echo /sensors/magnetic_field --once
ros2 topic echo /localization/odom --once
ros2 topic echo /cmd_vel --once
```

确认 Gazebo Transport 侧话题：

```bash
gz topic -l | grep sensors
gz topic -l | grep cmd_vel
```

如果需要打开 Gazebo GUI，再显式覆盖 `gz_args`：

```bash
ros2 launch right_angle_stack right_angle_harmonic.launch.py \
  use_rviz:=false \
  gz_args:="-r -v 4 $(ros2 pkg prefix right_angle_track)/share/right_angle_track/worlds/right_angle_harmonic.sdf"
```

WSL 图形栈不稳定时，不建议一开始就打开 Gazebo GUI 或 RViz。

## 常见问题

### 只构建 right_angle_stack 失败

如果清理了 `build/install/log` 后执行：

```bash
colcon build --packages-select right_angle_stack
```

可能会报：

```text
Failed to find ... install/fsd_common_msgs/share/fsd_common_msgs/package.sh
```

原因是 `right_angle_stack` 依赖 `fsd_common_msgs`，但依赖包还没有重新构建。处理方式：

```bash
rm -rf build install log
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

### CMakeCache 路径不匹配

如果从 `/mnt/e/...` 复制工程到 WSL 后出现：

```text
The current CMakeCache.txt directory ... is different than the directory ...
The source ".../CMakeLists.txt" does not match the source ".../CMakeLists.txt" used to generate cache.
```

说明旧的 `build/` 也被复制了。不要手改 `CMakeCache.txt`，直接删除编译产物：

```bash
cd /home/furina/ros_ws/percep_node+track
rm -rf build install log
source /opt/ros/humble/setup.bash
colcon build --symlink-install
```

### Operation not permitted

如果构建时出现：

```text
CMake Error at ... CMakeDetermineSystem.cmake:193 (configure_file):
  Operation not permitted
```

常见原因是工程在 Windows 挂载盘、同步目录，或之前用 `sudo colcon build` 产生了 root 拥有的文件。处理：

```bash
cd /home/furina/ros_ws/percep_node+track
sudo chown -R "$USER:$USER" .
chmod -R u+rwX .
rm -rf build install log
source /opt/ros/humble/setup.bash
colcon build --symlink-install
```

不要用 `sudo colcon build`。

### package gazebo_ros not found

说明你启动了 Classic launch，但 Humble 环境缺少 Classic Gazebo ROS 包：

```bash
sudo apt install ros-humble-gazebo-ros-pkgs
source /opt/ros/humble/setup.bash
```

或者改用 Gazebo Sim 路线：

```bash
ros2 launch right_angle_stack right_angle_wsl_headless.launch.py
```

### package ros_gz_sim not found

说明你启动了 Gazebo Sim launch，但缺少 `ros_gz`：

```bash
sudo apt install ros-humble-ros-gz
source /opt/ros/humble/setup.bash
ros2 pkg prefix ros_gz_sim
ros2 pkg prefix ros_gz_bridge
```

### gz_spawn_model.launch.py 不存在

Humble 中常见的 `ros_gz_sim` 版本没有新版 `gz_spawn_model.launch.py`。当前 launch 已经使用兼容 Humble 的 `ros_gz_sim create` 方式。同步源码并重新构建：

```bash
rsync -a --exclude build --exclude install --exclude log \
  "/mnt/e/Mech_Engineering/SCUT_Racing_Tasks/vscode/percep_node+track/" \
  /home/furina/ros_ws/percep_node+track/

cd /home/furina/ros_ws/percep_node+track
rm -rf build install log
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

### Gazebo Sim / OGRE2 在 WSL 中崩溃

如果日志出现：

```text
Ogre::UnimplementedException
GL3PlusTextureGpu::copyTo
libignition-rendering-ogre2
```

这是 WSLg/OpenGL/OGRE2 渲染层问题，通常不是 ROS 节点错误。处理顺序：

1. 先切到 WSL headless 路线，验证非渲染传感器和算法链路：

   ```bash
   ros2 launch right_angle_stack right_angle_wsl_headless.launch.py
   ```

2. 如果必须调完整 Gazebo Sim 相机/GPU 雷达，再尝试软件渲染：

   ```bash
   LIBGL_ALWAYS_SOFTWARE=1 MESA_GL_VERSION_OVERRIDE=3.3 \
     ros2 launch right_angle_stack right_angle_harmonic.launch.py use_rviz:=false
   ```

3. 如果仍然崩溃，继续用 `right_angle_wsl_headless.launch.py` 或 Gazebo Classic 路线验证课程算法链路。相机和 GPU 雷达属于渲染传感器，在 WSL 图形栈不稳定时最容易触发 OGRE 问题。

### xacro pi warning

如果看到：

```text
warning: redefining global symbol: pi
```

说明 WSL 副本还没有同步最新源码，或 install 中仍是旧文件。同步后重新构建：

```bash
rsync -a --exclude build --exclude install --exclude log \
  "/mnt/e/Mech_Engineering/SCUT_Racing_Tasks/vscode/percep_node+track/" \
  /home/furina/ros_ws/percep_node+track/

cd /home/furina/ros_ws/percep_node+track
rm -rf build install log
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## 使用老师给的感知节点

默认使用内置 `track_perception`，从赛道 SDF 读取锥桶，在 `base_link` 前方范围内发布带噪声观测。

如果要改用老师给的 `sim_perception`，在当前 WSL headless 路线中可以这样启动：

```bash
ros2 launch right_angle_stack right_angle_wsl_headless.launch.py \
  use_builtin_perception:=false \
  use_sim_perception:=true
```

建图节点默认订阅：

- `fsd_common_msgs/msg/Map`：`/perception/cones`
- `fsd_common_msgs/msg/ConeDetections`：`/perception/cone_detections`

如果老师节点发布的话题不同：

```bash
ros2 launch right_angle_stack right_angle_wsl_headless.launch.py \
  use_builtin_perception:=false \
  use_sim_perception:=true \
  perception_map_topic:=/your/map/topic \
  perception_detections_topic:=/your/detections/topic
```

## 当前建议

WSL 调试优先顺序：

1. 无 Gazebo 算法链路。
2. Gazebo Sim WSL headless，检查 spawn、bridge、`/cmd_vel` 和定位输出。
3. Gazebo Classic 回退路线。
4. 最后再尝试完整 Gazebo Sim、Gazebo GUI 和 RViz。

如果调试目标是课程演示的完整相机/雷达画面，WSL 图形栈可能成为主要不稳定因素；先保证 server-only 链路可运行，再单独处理图形显示。
