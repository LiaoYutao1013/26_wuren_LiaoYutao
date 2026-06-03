# 算法模块耗时统计消息。
std_msgs/Header header              # 耗时统计时间戳。
uint64 frame_id_num                 # 对应数据帧序号。
float32 sum_compute_time            # 总计算耗时。
float32 control_compute_time        # 控制模块计算耗时。
float32 boundary_detector_compute_time # 边界检测模块计算耗时。
float32 line_detector_compute_time  # 线检测模块计算耗时。
float32 skidpad_detector_compute_time # Skidpad 检测模块计算耗时。
float32 lidar_detection_compute_time # 激光雷达检测耗时。
float32 camera_detection_compute_time # 相机检测耗时。
float32 fusion_detection_compute_time # 融合检测耗时。
float32 time2                       # 预留耗时字段 2。
float32 time3                       # 预留耗时字段 3。
float32 time4                       # 预留耗时字段 4。
float32 time5                       # 预留耗时字段 5。
float32 time6                       # 预留耗时字段 6。
float32 time7                       # 预留耗时字段 7。
float32 time8                       # 预留耗时字段 8。
float32 time9                       # 预留耗时字段 9。
