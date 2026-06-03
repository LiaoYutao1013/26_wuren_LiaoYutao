# YOLO 图像检测到的单个锥桶目标框。
std_msgs/Float32 x                  # 目标框中心点 x 像素坐标。
std_msgs/Float32 y                  # 目标框中心点 y 像素坐标。
std_msgs/Float32 width              # 目标框宽度，单位通常为像素。
std_msgs/Float32 height             # 目标框高度，单位通常为像素。

std_msgs/String color               # 锥桶颜色，常用 r=red、b=blue、y=yellow。
std_msgs/Float32 color_confidence   # YOLO 对颜色/类别判断的置信度。
