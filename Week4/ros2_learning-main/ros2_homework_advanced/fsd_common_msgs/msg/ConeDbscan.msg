# 带 DBSCAN 聚类状态的锥桶检测结果。
geometry_msgs/Point position          # 锥桶坐标，通常使用 x/y 表示平面位置。
std_msgs/String color                 # 锥桶颜色，常用 b=blue、y=yellow、o=orange。
std_msgs/Float32 pose_confidence      # 位置检测置信度。
std_msgs/Float32 color_confidence     # 颜色检测置信度。

uint8 cluster                         # DBSCAN 聚类编号。
uint8 point_type                      # 点类型，例如核心点、边界点或噪声点的编码。
uint8 pts                             # 聚类相关点数或邻域点数统计。
uint8 visited                         # 聚类算法是否已访问该点的标志。
uint8[] corepts                       # 与该点相关的核心点索引列表。
