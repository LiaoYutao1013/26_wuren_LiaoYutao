# 一帧带 DBSCAN 聚类信息的锥桶检测结果。
std_msgs/Header header                     # 检测结果时间戳和坐标系。

fsd_common_msgs/ConeDbscan[] cone_detections # 当前帧检测到的聚类锥桶列表。
