# Asensing 组合惯导输出消息，包含定位、姿态、速度、加速度和状态信息。
std_msgs/Header header              # 标准消息头，记录时间戳和坐标系。
uint64 frame_id_num                 # 设备或驱动输出的帧序号。

# 经纬高定位结果。
float64 lat                         # 纬度。
float64 lon                         # 经度。
float64 h                           # 高程/高度。

# 北东地速度分量。
float64 vn                          # 北向速度。
float64 ve                          # 东向速度。
float64 vh                          # 垂向速度或高度方向速度。

# 姿态角。
float64 roll                        # 横滚角。
float64 pitch                       # 俯仰角。
float64 heading_angle               # 航向角。

# 陀螺仪角速度。
float64 gyro_x                      # x 轴角速度。
float64 gyro_y                      # y 轴角速度。
float64 gyro_z                      # z 轴角速度。

# 加速度计输出。
float64 acc_x                       # x 轴加速度。
float64 acc_y                       # y 轴加速度。
float64 acc_z                       # z 轴加速度。

# 定位标准差，用于评估定位结果可信度。
float32 std_lat                     # 纬度标准差。
float32 std_lon                     # 经度标准差。
float32 std_local_height            # 本地高度标准差。

# 速度标准差。
float32 north_velocity_std          # 北向速度标准差。
float32 east_velocity_std           # 东向速度标准差。
float32 ground_velocity_std         # 地面速度标准差。

# 姿态标准差。
float32 roll_std                    # 横滚角标准差。
float32 pitch_std                   # 俯仰角标准差。
float32 std_heading                 # 航向角标准差。

# 设备和 GPS 状态。
uint32 status                       # 惯导综合状态码。
uint32 gps_flag_pos                 # GPS 定位状态标志。

float64 gps_week_number             # GPS 周编号。

float64 ull_timestamp               # 设备原始时间戳。

float32 temperature                 # 设备温度。

uint32 car_status                   # 车辆或设备工作状态码。

uint32 gps_flag_heading             # GPS 航向状态标志。
uint32 num_sv                       # 可用卫星数量。
