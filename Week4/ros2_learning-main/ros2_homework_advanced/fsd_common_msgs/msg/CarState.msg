# 车辆位姿和速度状态。
std_msgs/Header header              # 状态时间戳和坐标系。

geometry_msgs/Pose2D car_state      # 车辆二维位姿：x、y、theta。
fsd_common_msgs/CarStateDt car_state_dt # 车辆状态变化率/速度信息。
