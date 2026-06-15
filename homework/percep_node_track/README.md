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
  "/mnt/e/Mech_Engineering/SCUT_Racing_Tasks/大作业/percep_node+track/" \
  /home/furina/ros_ws/percep_node+track/
```

如果你的 Windows 工程实际在 `vscode/percep_node+track` 或其他目录，把上面 rsync 的源路径替换成自己的实际路径。

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

## 入口选择与启用范围

先按目标选择入口，不要一开始就打开所有图形窗口。WSL 中优先用“部分启用”验证链路，再逐步打开相机、雷达、RViz 和 Gazebo GUI。

| 目标 | 启动入口 | 启用内容 | 不启用内容 | 推荐场景 |
| --- | --- | --- | --- | --- |
| 无 Gazebo 算法链路 | `right_angle_sim.launch.py use_gazebo:=false` | 定位、感知替身、建图、规划、控制 | Gazebo、物理车辆、真实传感器 | 先确认 ROS 节点和话题链路 |
| 部分启用 WSL headless | `right_angle_wsl_headless.launch.py` | Gazebo Sim server、车辆、GPS、IMU、轮速里程计、磁力计、算法链路 | 相机、雷达、Gazebo GUI、RViz 默认关闭 | WSL 主调试入口 |
| 全部传感器 Classic | `right_angle_sim.launch.py` | Gazebo Classic、车辆、相机、雷达、GPS、IMU、轮速里程计、磁力计、算法链路、RViz 默认开启 | 无 | WSL 中验证相机/雷达的优先入口 |
| 全部传感器 Gazebo Sim | `right_angle_harmonic.launch.py` | Gazebo Sim、车辆、相机、GPU 雷达、GPS、IMU、轮速里程计、磁力计、算法链路 | RViz 默认关闭，Gazebo GUI 默认关闭 | 原生 Ubuntu 或图形栈稳定后再试 |

`right_angle_harmonic.launch.py` 文件名中的 `harmonic` 是历史命名。在 ROS 2 Humble 中，日志常显示 `Ignition Gazebo Server v6.x`，实际对应 Gazebo Fortress / Ignition Gazebo 6。

## 流程 1：无 Gazebo，算法链路最小验证

这个流程不启动 Gazebo，不生成仿真车辆，也没有相机、雷达、GPS、IMU 等 Gazebo 传感器。它用于先确认 Python 节点、消息类型、感知替身、建图、规划和控制话题能跑通。

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

这些话题能输出，说明上层算法链路基本正常。这个流程不用于验证传感器 URDF/SDF。

## 流程 2：部分启用，WSL headless Gazebo Sim

这是 WSL 中优先使用的 Gazebo 路线。它会启动 Gazebo Sim server、生成车辆、桥接 `/clock`、`/cmd_vel`、轮速里程计、GPS、IMU 和磁力计，并运行定位、建图、规划和控制。它不加载相机、GPU 雷达和 `gz-sim-sensors-system`，用于避开 WSLg/OpenGL/OGRE2 的渲染传感器崩溃。

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

这个流程预期会有：

- `/clock`
- `/cmd_vel`
- `/sensors/wheel_odom`
- `/sensors/imu/data_raw`
- `/sensors/gps/fix`
- `/sensors/magnetic_field`
- `/localization/odom`
- `/planning/centerline`

这个流程预期不会有：

- `/sensors/camera/image_raw`
- `/sensors/camera/camera_info`
- `/sensors/lidar/scan`

如果这条路线可以稳定运行，说明车辆动力学、基础传感器、定位、规划和控制链路是通的；相机/GPU 雷达问题再单独处理。

需要 RViz 只看 TF、轨迹和地图时，可以显式开启：

```bash
ros2 launch right_angle_stack right_angle_wsl_headless.launch.py use_rviz:=true
```

此时 RViz 中相机和雷达显示项会没有数据，这是正常现象。

## 流程 3：全部传感器启用，Gazebo Classic

这是 WSL 中验证相机启用的优先入口。Classic 路线使用 URDF/xacro 和 Gazebo Classic 插件：

- `gazebo_ros`
- `spawn_entity.py`
- `libgazebo_ros_diff_drive.so`
- `libgazebo_ros_camera.so`
- `libgazebo_ros_ray_sensor.so`
- `libgazebo_ros_imu_sensor.so`
- `libgazebo_ros_gps_sensor.so`
- `libgazebo_ros_magnetometer.so`

### 3.1 全部启用，带 RViz

这会启动 Gazebo Classic、Gazebo GUI、车辆、全部传感器、算法链路和 RViz。

```bash
cd /home/furina/ros_ws/percep_node+track
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch right_angle_stack right_angle_sim.launch.py use_rviz:=true
```

### 3.2 全部传感器启用，但不启动 RViz

如果 RViz 闪退或你只想先检查话题，先关闭 RViz：

```bash
ros2 launch right_angle_stack right_angle_sim.launch.py use_rviz:=false
```

这仍然启用相机、雷达、GPS、IMU、轮速里程计和磁力计，只是不打开 RViz。

检查 Classic 关键服务和传感器话题：

```bash
ros2 service list | grep spawn
ros2 topic echo /clock --once
ros2 topic echo /sensors/wheel_odom --once
ros2 topic echo /sensors/imu/data_raw --once
ros2 topic echo /sensors/gps/fix --once
ros2 topic echo /sensors/magnetic_field --once
ros2 topic echo /cmd_vel --once
```

检查相机：

```bash
ros2 topic list | grep camera
ros2 topic echo /sensors/camera/camera_info --once
ros2 topic hz /sensors/camera/image_raw
```

检查雷达：

```bash
ros2 topic echo /sensors/lidar/scan --once
ros2 topic hz /sensors/lidar/scan
```

WSL 中 RViz 闪退时先用软件渲染：

```bash
LIBGL_ALWAYS_SOFTWARE=1 rviz2 -d install/right_angle_stack/share/right_angle_stack/rviz/right_angle.rviz
```

### 3.3 Classic 的部分启用组合

Classic launch 当前没有单独关闭某一个传感器的参数。可以通过 launch 参数做的部分启用主要是：

- `use_rviz:=false`：全部传感器仍启用，只关闭 RViz。
- `use_gazebo:=false use_sim_time:=false use_rviz:=false`：关闭 Gazebo 和所有 Gazebo 传感器，只跑算法链路。
- `use_synthetic_sensors:=true`：在 Gazebo 传感器插件不可用时，用 `/gazebo/model_states` 生成同名基础传感器话题调试上层算法。

示例：

```bash
ros2 launch right_angle_stack right_angle_sim.launch.py \
  use_rviz:=false \
  use_synthetic_sensors:=true
```

## 流程 4：全部传感器启用，Gazebo Sim / ros_gz

完整 Gazebo Sim 路线使用 SDF 车型和 `ros_gz` 桥接：

- `ros_gz_sim`
- `ros_gz_bridge`
- `right_angle_stack/launch/right_angle_harmonic.launch.py`
- `tracks/worlds/right_angle_harmonic.sdf`
- `right_angle_stack/models/right_angle_car_harmonic/model.sdf`

这条路线包含相机和 `gpu_lidar`，即使使用 server-only 模式也会进入 Gazebo 的渲染传感器线程。WSL 中如果已经出现 `Ogre::UnimplementedException` 或 `GL3PlusTextureGpu::copyTo`，先不要用这条路线做主调试。

如果直接运行这条 launch 后 RViz 报 `frame [world] does not exist`，通常不是 `world` 坐标系配置错了，而是 Gazebo 已经先崩溃，导致车辆、`/clock`、传感器和 TF 都没有发布。此时 RViz 黑屏只是后果，应该回到 `right_angle_wsl_headless.launch.py` 验证非渲染链路。

### 4.1 全部传感器启用，但不启动 RViz 和 Gazebo GUI

这是该入口的默认模式。它会启用相机和 GPU 雷达，但不打开 RViz 和 Gazebo GUI。

```bash
cd /home/furina/ros_ws/percep_node+track
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch right_angle_stack right_angle_harmonic.launch.py use_rviz:=false
```

默认 `gz_args` 是 `-r -s -v 4 <world>`，即只启动 Gazebo Sim server，不启动 Gazebo GUI。注意：server-only 不等于不渲染，camera 和 `gpu_lidar` 仍可能触发 OGRE2。

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

检查相机和雷达桥接：

```bash
ros2 topic list | grep -E 'camera|lidar'
ros2 topic echo /sensors/camera/camera_info --once
ros2 topic hz /sensors/camera/image_raw
ros2 topic echo /sensors/lidar/scan --once
```

确认 Gazebo Transport 侧话题：

```bash
gz topic -l | grep sensors
gz topic -l | grep cmd_vel
```

### 4.2 全部启用，带 RViz

只在 Gazebo Sim 不崩溃后再打开 RViz：

```bash
ros2 launch right_angle_stack right_angle_harmonic.launch.py use_rviz:=true
```

### 4.3 全部启用，带 Gazebo GUI

只在 WSL 图形栈或原生 Ubuntu 图形环境稳定后再打开 Gazebo GUI：

```bash
ros2 launch right_angle_stack right_angle_harmonic.launch.py \
  use_rviz:=false \
  gz_args:="-r -v 4 $(ros2 pkg prefix right_angle_track)/share/right_angle_track/worlds/right_angle_harmonic.sdf"
```

### 4.4 Gazebo Sim 的部分启用组合

Gazebo Sim 当前有两个 SDF 入口来做部分启用：

- `right_angle_wsl_headless.launch.py`：禁用相机、GPU 雷达和渲染传感器系统，只保留基础定位传感器。
- `right_angle_harmonic.launch.py use_rviz:=false`：启用全部传感器，但关闭 RViz 和 Gazebo GUI。

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
  "/mnt/e/Mech_Engineering/SCUT_Racing_Tasks/大作业/percep_node+track/" \
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

### 全部启用后小车不动

先不要改控制参数，按链路定位断点。控制节点只有在同时收到 `/localization/odom` 和 `/planning/centerline`，且路径至少有 2 个点时，才会发布非零 `/cmd_vel`；否则会持续发布停车指令。

1. 先确认仿真时间在走：

   ```bash
   ros2 topic hz /clock
   ```

   如果 `/clock` 不发布或频率为 0，说明 Gazebo 暂停、崩溃，或 Gazebo/ROS bridge 没起来。使用 `use_sim_time:=true` 时，很多节点依赖 `/clock` 才会正常运行。

2. 看控制器是否发出非零速度：

   ```bash
   ros2 topic echo /cmd_vel --once
   ros2 topic hz /cmd_vel
   ```

   如果 `linear.x` 和 `angular.z` 都是 0，继续查定位和规划。

3. 查定位输入和输出：

   ```bash
   ros2 topic echo /localization/odom --once
   ros2 topic echo /localization/pose --once
   ros2 topic echo /sensors/wheel_odom --once
   ros2 topic echo /sensors/imu/data_raw --once
   ros2 topic echo /sensors/gps/fix --once
   ros2 topic echo /sensors/magnetic_field --once
   ```

   `/localization/odom` 没有输出时，控制器不会动车。基础传感器没输出时，先回到对应仿真入口检查传感器插件或 bridge。

4. 查规划路径：

   ```bash
   ros2 topic echo /planning/centerline --once
   ros2 topic echo /estimation/slam/map --once
   ```

   `/planning/centerline` 没有输出时，控制器也会停车。当前规划节点默认 `fallback_path:=true`，理论上即使锥桶建图不足，也应该发布解析路径；如果没有输出，优先检查 `right_angle_planner` 是否启动、`/clock` 是否正常。

5. 如果 `/cmd_vel` 非零但车仍不动，查驱动插件或桥接。

   Classic 路线：

   ```bash
   ros2 topic info /cmd_vel -v
   ros2 topic echo /sensors/wheel_odom --once
   ```

   Gazebo Sim 路线：

   ```bash
   gz topic -l | grep cmd_vel
   gz topic -l | grep wheel
   ros2 topic echo /sensors/wheel_odom --once
   ```

判断标准：

- `/cmd_vel` 是 0：上层算法没给速度，查定位和规划。
- `/cmd_vel` 非 0，但 `/sensors/wheel_odom` 仍是 0：驱动插件或 Gazebo bridge 没吃到速度。
- `/sensors/wheel_odom` 非 0，但画面里车不动：优先查 Gazebo GUI 是否卡住、模型状态是否更新，或画面是否看错对象。

如果 Gazebo 和 RViz 都已经打开，Gazebo 里能看到车和锥桶，但 RViz 显示 `No Image` 且车不动，按下面的顺序进一步确认：

1. 确认不是只打开了 Gazebo/RViz，而是完整 ROS 栈都启动了：

   ```bash
   ros2 node list
   ```

   应该至少看到：

   ```text
   /ros_gz_bridge
   /robot_state_publisher
   /localization_fusion
   /track_perception
   /cone_mapper
   /right_angle_planner
   /pure_pursuit_controller
   ```

   如果这些节点缺失，重新用对应 launch 启动完整工程，不要只单独打开 Gazebo 或 RViz。

2. 绕过规划控制，直接测试 Gazebo 车辆能否响应速度：

   ```bash
   ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0}, angular: {z: 0.0}}" -r 10
   ```

   如果 ROS 直发不动，再直接走 Gazebo Transport：

   ```bash
   gz topic -t /cmd_vel -m gz.msgs.Twist -p "linear: {x: 1.0} angular: {z: 0.0}"
   ```

   ROS 直发能动，说明车辆驱动正常，问题在规划控制输出。Gazebo Transport 直发能动但 ROS 直发不动，说明 ROS/Gazebo bridge 或 topic 方向有问题。两者都不动，优先查 SDF/URDF 的 DiffDrive 插件、topic 和车轮关节。

3. 排查 RViz `No Image`：

   ```bash
   ros2 topic list | grep camera
   ros2 topic hz /sensors/camera/image_raw
   ros2 topic echo /sensors/camera/camera_info --once
   gz topic -l | grep camera
   ```

   `gz topic` 有相机但 ROS 没有，说明 camera bridge 没通。Gazebo 侧也没有相机 topic，说明 Gazebo sensor 没发布。ROS 侧有图像频率但 RViz 仍 `No Image`，再检查 RViz Image display 的 topic 是否是 `/sensors/camera/image_raw`。

4. 确认当前终端 source 的发行版和工作区一致：

   ```bash
   printenv ROS_DISTRO
   echo $AMENT_PREFIX_PATH
   ```

   不要在同一个终端混 source 不同 ROS 2 发行版的 `/opt/ros/*/setup.bash` 和旧工作区 `install/setup.bash`。切换发行版或工作区后，打开新终端重新 source。

### xacro pi warning

如果看到：

```text
warning: redefining global symbol: pi
```

说明 WSL 副本还没有同步最新源码，或 install 中仍是旧文件。同步后重新构建：

```bash
rsync -a --exclude build --exclude install --exclude log \
  "/mnt/e/Mech_Engineering/SCUT_Racing_Tasks/大作业/percep_node+track/" \
  /home/furina/ros_ws/percep_node+track/

cd /home/furina/ros_ws/percep_node+track
rm -rf build install log
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## 使用给出的感知节点

默认使用内置 `track_perception`，从赛道 SDF 读取锥桶，在 `base_link` 前方范围内发布带噪声观测。

所有入口默认使用内置 `track_perception`。如果要改用老师给的 `sim_perception`，把对应 launch 的 `use_builtin_perception` 关掉，并打开 `use_sim_perception`。

部分启用 headless：

```bash
ros2 launch right_angle_stack right_angle_wsl_headless.launch.py \
  use_builtin_perception:=false \
  use_sim_perception:=true
```

全部传感器 Classic：

```bash
ros2 launch right_angle_stack right_angle_sim.launch.py \
  use_builtin_perception:=false \
  use_sim_perception:=true
```

全部传感器 Gazebo Sim：

```bash
ros2 launch right_angle_stack right_angle_harmonic.launch.py \
  use_builtin_perception:=false \
  use_sim_perception:=true
```

建图节点默认订阅：

- `fsd_common_msgs/msg/Map`：`/perception/cones`
- `fsd_common_msgs/msg/ConeDetections`：`/perception/cone_detections`

如果发布的话题不同，在对应 launch 上追加话题参数。下面以 headless 为例：

```bash
ros2 launch right_angle_stack right_angle_wsl_headless.launch.py \
  use_builtin_perception:=false \
  use_sim_perception:=true \
  perception_map_topic:=/your/map/topic \
  perception_detections_topic:=/your/detections/topic
```

### sim_perception 跑不通时

`sim_perception` 是 PyArmor 加密包，`sim_node.py` 启动时必须能导入同目录下的 `pyarmor_runtime_000000/pyarmor_runtime.so`。常见问题按下面顺序查：

1. 先确认它真的被启动了，而不是还在跑内置感知：

   ```bash
   ros2 node list | grep perception
   ```

   需要看到 `sim_perception`，并且 launch 参数里 `use_builtin_perception:=false`、`use_sim_perception:=true`。

2. 确认运行时库存在于安装目录：

   ```bash
   find install/sim_perception -name 'pyarmor_runtime.so' -ls
   ```

   如果找不到，先检查源码里是否存在：

   ```bash
   find sim_perception -name 'pyarmor_runtime.so' -ls
   ```

   缺文件时，先把源码同步完整，再重新构建：

   ```bash
   rm -rf build/sim_perception install/sim_perception
   colcon build --symlink-install --packages-select sim_perception
   source install/setup.bash
   ```

3. 确认 `.gitignore` 没有把这个必要库漏掉。
   根目录现在保留了对该运行时库的例外规则，避免 `*.so` 误屏蔽。

4. 确认 Python 和 ROS 发行版没有混用。
   如果你当前环境是 Jazzy，Python 版本通常和 Humble 不同；加密包对 ABI 更敏感，不能混 source 不同发行版的工作区。

   ```bash
   printenv ROS_DISTRO
   python3 --version
   ```

5. 直接测试加密运行时能否导入：

   ```bash
   python3 -c "from sim_perception.pyarmor_runtime_000000 import __pyarmor__; print('pyarmor ok')"
   ```

6. 如果模块能导入但节点仍起不来，再看依赖和运行时报错：

   ```bash
   ros2 run sim_perception sim_node
   ```

   常见依赖包括 `rclpy`、`tf2_ros`、`tf2_geometry_msgs`、`geometry_msgs`、`std_msgs`、`fsd_common_msgs`。

## 当前建议

WSL 调试优先顺序：

1. 无 Gazebo 算法链路。
2. Gazebo Sim WSL headless，检查 spawn、bridge、`/cmd_vel` 和定位输出。
3. Gazebo Classic 回退路线。
4. 最后再尝试完整 Gazebo Sim、Gazebo GUI 和 RViz。

如果调试目标是课程演示的完整相机/雷达画面，WSL 图形栈可能成为主要不稳定因素；先保证 server-only 链路可运行，再单独处理图形显示。

## 本次日志对应的问题与处理

日志说明当前 Gazebo Sim 8 已经正常启动，车辆实体也已经成功生成：

- `Entity creation successful`：车辆已经被 `ros_gz_sim create` 加入世界。
- `DiffDrive subscribing to twist messages on [/cmd_vel]`：Gazebo 车辆驱动插件已经订阅速度命令。
- `Passing message from ROS geometry_msgs/msg/Twist to Gazebo gz.msgs.Twist`：ROS 到 Gazebo 的 `/cmd_vel` 桥接已经工作。
- `Camera images ... advertised on [/sensors/camera/image_raw]`、`Laser scans ... advertised on [/sensors/lidar/scan]`：Gazebo 端相机和雷达传感器已经发布数据。

这说明问题已经不是 Gazebo 启动失败，而是下面几个更高层的问题：

1. 锥桶显示为圆柱体。
   之前为了绕开缺失 mesh 时的加载失败，锥桶 visual 临时改成了 cylinder。现在已经改回 mesh 外观，collision 仍保留 cylinder，避免 DART 对 mesh collision 的不稳定问题。

2. RViz 中相机/雷达可视化不明显。
   当前 RViz 配置已经包含：
   - `/sensors/camera/image_raw`：Image 显示项。
   - `/sensors/lidar/scan`：LaserScan 显示项。
   - `/sensors/lidar/scan/points`：PointCloud2 显示项。
   - `/visualization/cone_map`：建图锥桶 MarkerArray。
   - `/visualization/planning`、`/planning/centerline`：规划可视化。

3. 小车开始阶段不转向。
   起点是 `(0, -15)`，朝北。当前默认 fallback 规划路径前半段本来就是沿 `x=0` 直行，到接近 `y=0` 后才进入右角弯。如果车还没跑到弯道入口，只走直线是正常的。若到 `y=0` 附近仍不转，需要检查规划路径和角速度命令。

## 完整可视化启动流程

先清理旧进程和旧环境：

```bash
pkill -INT -f "gz sim|ign gazebo|gazebo|gzserver|gzclient|rviz2|ros_gz_bridge|parameter_bridge|spawn_entity|create" || true
sleep 2
pkill -9 -f "gz sim|ign gazebo|gazebo|gzserver|gzclient|rviz2|ros_gz_bridge|parameter_bridge|spawn_entity|create" || true

unset PYTHONPATH
unset LD_LIBRARY_PATH
unset AMENT_PREFIX_PATH
unset CMAKE_PREFIX_PATH
unset COLCON_PREFIX_PATH
```

同步到 WSL 后重新构建。注意不要把 Windows 侧旧的 `build/ install/ log/` 同步进去：

```bash
cd ~/文档/SCUT_Racing_Tasks/homework/percep_node_track
rm -rf build install log
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --event-handlers console_direct+
source install/setup.bash

ros2 pkg prefix right_angle_track
ros2 pkg prefix right_angle_stack
```

上面两个 prefix 必须指向 `homework/percep_node_track/install/...`，不能再出现旧的 `大作业/percep_node+track/install/...`。

全部传感器、Gazebo GUI、RViz 一起启动：

```bash
ros2 launch right_angle_stack right_angle_harmonic.launch.py \
  use_rviz:=true \
  gz_args:="-r -v 4 $(ros2 pkg prefix right_angle_track)/share/right_angle_track/worlds/right_angle_harmonic.sdf"
```

如果 RViz 或 Gazebo GUI 不稳定，分两步启动更容易定位问题：

```bash
# 终端 1：只开 Gazebo GUI 和完整传感器，不开 RViz
ros2 launch right_angle_stack right_angle_harmonic.launch.py \
  use_rviz:=false \
  gz_args:="-r -v 4 $(ros2 pkg prefix right_angle_track)/share/right_angle_track/worlds/right_angle_harmonic.sdf"

# 终端 2：确认话题有数据后再单独开 RViz
source /opt/ros/jazzy/setup.bash
source ~/文档/SCUT_Racing_Tasks/homework/percep_node_track/install/setup.bash
rviz2 -d ~/文档/SCUT_Racing_Tasks/homework/percep_node_track/install/right_angle_stack/share/right_angle_stack/rviz/right_angle.rviz
```

## 相机和雷达可视化验证

Gazebo 侧先看传感器是否存在：

```bash
gz topic -l | grep -E 'camera|lidar|sensors'
```

ROS 侧看 bridge 后的话题：

```bash
ros2 topic list | grep -E 'camera|lidar'
ros2 topic echo /sensors/camera/camera_info --once
ros2 topic hz /sensors/camera/image_raw
ros2 topic echo /sensors/lidar/scan --once
ros2 topic hz /sensors/lidar/scan
ros2 topic echo /sensors/lidar/scan/points --once
```

判断方法：

- `gz topic` 有数据、ROS 没有：优先查 `right_angle_harmonic.launch.py` 里的 `ros_gz_bridge` 参数。
- ROS 有数据、RViz 没显示：检查 RViz Fixed Frame 是否为 `world`，Image topic 是否为 `/sensors/camera/image_raw`，LaserScan topic 是否为 `/sensors/lidar/scan`，PointCloud2 topic 是否为 `/sensors/lidar/scan/points`。
- RViz 报 transform/frame 错误：先确认 `/tf`、`/localization/odom` 和 `/robot_description` 存在。

## 不转向时的最小排查流程

不要只看 Gazebo 画面，按 topic 一层一层确认：

```bash
ros2 topic echo /localization/pose --once
ros2 topic echo /perception/cones --once
ros2 topic echo /estimation/slam/map --once
ros2 topic echo /planning/centerline --once
ros2 topic echo /cmd_vel --once
ros2 topic echo /sensors/wheel_odom --once
```

重点看：

- `/planning/centerline` 是否包含右角弯路径。如果只有直线路径或为空，问题在感知/建图/规划。
- `/cmd_vel.angular.z` 是否在接近 `y=0` 后明显非零。如果一直为 0，问题在规划或 pure pursuit 目标点选择。
- `/cmd_vel.angular.z` 非零但 Gazebo 中车不转，问题在车辆驱动模型或 Gazebo 侧 `/cmd_vel` 接收。
- `/sensors/wheel_odom` 非零但画面里车像在闪烁，优先考虑 Gazebo GUI 渲染问题；以 `/localization/pose` 和 `/sensors/wheel_odom` 判断真实运动。

当前默认感知链路不是从相机/雷达识别锥桶，而是 `track_perception` 根据赛道 SDF 发布带噪声的锥桶位置。相机和雷达用于满足传感器仿真与 RViz 可视化要求，不直接参与当前控制决策。
