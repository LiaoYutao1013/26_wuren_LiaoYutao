# 单个锥桶的通用消息定义。
geometry_msgs/Point position      # 锥桶三维坐标，通常 x/y 表示平面位置，z 表示高度。
string color                      # 锥桶颜色标签，如 blue、yellow、red、unknown。
float64 pose_confidence           # 位置估计置信度。
float64 color_confidence          # 颜色分类置信度。
