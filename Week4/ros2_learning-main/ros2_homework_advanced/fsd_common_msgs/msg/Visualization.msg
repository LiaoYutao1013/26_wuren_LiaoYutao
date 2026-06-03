# 控制与算法调试可视化数据。
std_msgs/Header header              # 可视化数据时间戳。
uint64 frame_id_num                 # 对应数据帧序号。

# 误差数据：用于观察车辆状态与参考轨迹/目标值的偏差。
float32 lat_error_front_axis        # 前轴横向误差。
float32 lat_error_cog               # 质心横向误差。
float32 lat_error_rear_axis         # 后轴横向误差。
float32 yaw_error_front_axis        # 前轴航向误差。
float32 yaw_error_cog               # 质心航向误差。
float32 yaw_error_rear_axis         # 后轴航向误差。
float32 yaw_rate_error              # 横摆角速度误差。
float32 steering_error              # 转向误差。
float32 vx_error                    # 纵向速度误差。
float32 vy_error                    # 横向速度误差。
float32 sideslip_error              # 侧偏角误差。
float32 motor_torq_error_lr         # 左后电机扭矩误差。
float32 motor_torq_error_rr         # 右后电机扭矩误差。
float32 motor_speed_error_lr        # 左后电机转速误差。
float32 motor_speed_error_rr        # 右后电机转速误差。
float32 error1                      # 预留误差字段 1。
float32 error2                      # 预留误差字段 2。
float32 error3                      # 预留误差字段 3。
float32 error4                      # 预留误差字段 4。

# 参考量数据：用于显示控制器或规划器给出的目标状态。
float32 yaw_ref                     # 参考航向角。
float32 yaw_ref_front_axis          # 前轴参考航向角。
float32 yaw_ref_cog                 # 质心参考航向角。
float32 yaw_ref_rear_axis           # 后轴参考航向角。
float32 curvature_ref               # 参考曲率。
float32 curvature_ref_front_axis    # 前轴参考曲率。
float32 curvature_ref_cog           # 质心参考曲率。
float32 curvature_ref_rear_axis     # 后轴参考曲率。
float32 vx_ref                      # 参考纵向速度。
float32 vy_ref                      # 参考横向速度。
float32 ax_ref                      # 参考纵向加速度。
float32 ay_ref                      # 参考横向加速度。
float32 ref1                        # 预留参考字段 1。
float32 ref2                        # 预留参考字段 2。
float32 ref3                        # 预留参考字段 3。
float32 ref4                        # 预留参考字段 4。

# 算法内部变量：用于调试控制器各项计算结果。
float32 steering_without_compensation # 未补偿前的转向输出。
float32 steering_feedback           # 反馈控制转向量。
float32 steering_feedforward        # 前馈控制转向量。
float32 lookforward_length          # 预瞄距离。
float32 yaw_rate_pre                # 预测横摆角速度。
float32 turning_radius              # 转弯半径。
float32 adhesion_coefficient_pre    # 预测附着系数。
float32 sideslip_pre                # 预测侧偏角。
float32 slip_angle_pre_fl           # 左前轮预测侧偏角。
float32 slip_angle_pre_fr           # 右前轮预测侧偏角。
float32 slip_angle_pre_rl           # 左后轮预测侧偏角。
float32 slip_angle_pre_rr           # 右后轮预测侧偏角。
float32 norm_force_pre_fl           # 左前轮预测法向载荷。
float32 norm_force_pre_fr           # 右前轮预测法向载荷。
float32 norm_force_pre_rl           # 左后轮预测法向载荷。
float32 norm_force_pre_rr           # 右后轮预测法向载荷。
float32 algorithm1                  # 预留算法字段 1。
float32 algorithm2                  # 预留算法字段 2。
float32 algorithm3                  # 预留算法字段 3。
float32 algorithm4                  # 预留算法字段 4。
