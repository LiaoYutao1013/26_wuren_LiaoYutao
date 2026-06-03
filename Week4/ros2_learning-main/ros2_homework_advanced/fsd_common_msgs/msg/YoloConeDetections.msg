# 一帧 YOLO 锥桶检测结果。
std_msgs/Header header              # 检测结果消息头。
std_msgs/Header image_header        # 原始图像消息头，用于和相机图像时间同步。

fsd_common_msgs/YoloCone[] cone_detections # 当前图像中检测到的锥桶目标列表。
