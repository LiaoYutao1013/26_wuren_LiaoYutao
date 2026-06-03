# 车辆底盘反馈数据。
std_msgs/Header header              # 反馈数据时间戳。
uint64 frame_id_num                 # 反馈帧序号。
float32 wheel_speed_fl              # 左前轮轮速。
float32 wheel_speed_fr              # 右前轮轮速。
float32 wheel_speed_rl              # 左后轮轮速。
float32 wheel_speed_rr              # 右后轮轮速。
float32 motor_command_speed_rl      # 左后电机目标转速。
float32 motor_command_speed_rr      # 右后电机目标转速。
float32 motor_return_speed_rl       # 左后电机实际转速。
float32 motor_return_speed_rr       # 右后电机实际转速。
float32 motor_command_torq_rl       # 左后电机目标扭矩。
float32 motor_command_torq_rr       # 右后电机目标扭矩。
float32 motor_return_torq_rl        # 左后电机实际扭矩。
float32 motor_return_torq_rr        # 右后电机实际扭矩。
