# 自动驾驶系统状态消息。
std_msgs/Header header              # 状态消息时间戳。
string mission                      # 当前任务名称，例如 inspection、acceleration、skidpad、trackdrive。
uint8 which_lap                     # 当前圈数，用于 trackdrive 等需要记圈的任务。
uint8 end                           # 是否到达指定停车位置：0=未到达，1=已到达。
# stop 字段曾用于表示停车请求，此处保留说明但不作为实际消息字段。
uint8 finished                      # 任务是否完成：0=未完成，1=完成。
uint8 camera_state                  # 相机状态：0=正常，1=断线或异常。
uint8 lidar_state                   # 激光雷达状态：0=正常，1=断线或异常。
uint8 ins_state                     # 组合惯导状态：0=正常，1=断线或异常。
uint8 sensor_state                  # 综合传感器状态：0=全部正常，1=至少一个传感器异常。
uint8 ready                         # 无人系统是否准备好接收传感器并输出控制：0=正常。
float32 count_time                  # 接收到 go 信号后的累计运行时间。
