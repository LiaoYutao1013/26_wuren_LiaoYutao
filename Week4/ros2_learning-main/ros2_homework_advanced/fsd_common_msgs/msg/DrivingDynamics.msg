# 发送给 CAN_send 节点并转发到 canB 总线的车辆动力学数据。
std_msgs/Header header              # 动力学数据时间戳。

float32 speed_target                # 目标车速。
float32 speed_actual                # 实际车速。
float32 steering_angle_target       # 目标转角。
float32 steering_angle_actual       # 实际转角。
float32 brake_hydr_target           # 目标液压制动压力。
float32 brake_hydr_actual           # 实际液压制动压力。
float32 motor_moment_target         # 目标电机扭矩。
float32 motor_moment_actual         # 实际电机扭矩。

float32 acceleration_longitudinal   # 车辆纵向加速度。
float32 acceleration_lateral        # 车辆横向加速度。
float32 yaw_rate                    # 横摆角速度。
