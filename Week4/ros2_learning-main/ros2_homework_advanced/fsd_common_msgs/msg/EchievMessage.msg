# Echiev 感知/惯导结果消息。
std_msgs/Header header              # 标准消息头，记录时间戳和坐标系。
uint64 frame_id_num                 # 数据帧序号。
uint64 ull_timestamp                # 设备原始时间戳。
float64 lat                         # 纬度。
float64 lon                         # 经度。
float32 h                           # 高程/高度。
float32 vn                          # 北向速度。
float32 ve                          # 东向速度。
float32 vh                          # 垂向速度或高度方向速度。
float32 roll                        # 横滚角。
float32 pitch                       # 俯仰角。
float32 yaw                         # 航向/偏航角。
float32 acc_x                       # x 轴加速度。
float32 acc_y                       # y 轴加速度。
float32 acc_z                       # z 轴加速度。
float32 gyro_x                      # x 轴角速度。
float32 gyro_y                      # y 轴角速度。
float32 gyro_z                      # z 轴角速度。
uint8 state                         # 设备综合状态。
uint8 gps_state                     # GPS 状态。
