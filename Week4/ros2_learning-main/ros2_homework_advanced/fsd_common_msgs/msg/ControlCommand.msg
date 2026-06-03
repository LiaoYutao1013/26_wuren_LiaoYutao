# 控制模块输出给车辆执行层的归一化控制指令。
std_msgs/Header header              # 控制指令时间戳。

std_msgs/Float32 throttle           # 油门/驱动请求，范围通常为 [-1, 1]。
std_msgs/Float32 steering_angle     # 转向请求，范围通常为 [-1, 1]，左转为负、右转为正。
