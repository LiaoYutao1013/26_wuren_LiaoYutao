# 惯导里程计增量信息。
std_msgs/Header header              # 增量数据时间戳。

float32 total_omega                 # 累计角度变化或角速度积分。
float32 total_distance_x            # x 方向累计位移。
float32 total_distance_y            # y 方向累计位移。
