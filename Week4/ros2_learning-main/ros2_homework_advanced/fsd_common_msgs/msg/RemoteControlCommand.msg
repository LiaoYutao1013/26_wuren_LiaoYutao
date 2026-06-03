# 遥控或上位机输入的控制命令。
std_msgs/Header header              # 控制命令时间戳。

float32 throttle                    # 油门/驱动请求，范围通常为 [-1, 1]。
float32 steering_angle              # 转向请求，范围通常为 [-1, 1]，左转为负、右转为正。

float32 go                          # 启动/放行开关，通常 0=不启动，1=启动。
float32 stop                        # 停车开关，通常 0=不停车，1=停车。
float32 test1                       # 预留测试开关，通常取 0 或 1。
