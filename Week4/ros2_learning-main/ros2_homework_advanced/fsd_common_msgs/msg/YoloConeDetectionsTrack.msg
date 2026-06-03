# 一帧带跨帧跟踪状态的 YOLO 锥桶检测结果。
std_msgs/Header header                    # 检测结果时间戳和坐标系/图像来源信息。

fsd_common_msgs/YoloConeTrack[] cone_detections # 当前帧所有带 tracking_id 的锥桶目标。
