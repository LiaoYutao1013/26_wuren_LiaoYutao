# 赛道边界和计时设备位置。
std_msgs/Header header              # 赛道消息时间戳和坐标系。
geometry_msgs/Point[] cones_left    # 左侧边界锥桶点列。
geometry_msgs/Point[] cones_right   # 右侧边界锥桶点列。
geometry_msgs/Point[] cones_orange  # 橙色锥桶点列。
geometry_msgs/Point[] cones_orange_big # 大橙桶点列。
geometry_msgs/Point[] tk_device_start # 计时设备起点位置。
geometry_msgs/Point[] tk_device_end # 计时设备终点位置。
