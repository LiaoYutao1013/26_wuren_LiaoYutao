# 带跟踪信息的 YOLO 锥桶检测结果。
std_msgs/Float32 x                  # 目标框中心点 x 像素坐标。
std_msgs/Float32 y                  # 目标框中心点 y 像素坐标。
std_msgs/Float32 width              # 目标框宽度，单位通常为像素。
std_msgs/Float32 height             # 目标框高度，单位通常为像素。

std_msgs/String color               # 锥桶颜色，常用 r=red、b=blue、y=yellow。
std_msgs/Float32 color_confidence   # 颜色/类别检测置信度。

geometry_msgs/Point position        # 估计出的三维位置，包含 x/y/z。
std_msgs/Float32 pose_confidence    # 三维位置估计置信度。

std_msgs/UInt8 tracking_id          # 跟踪目标 ID，用于跨帧关联同一个锥桶。
std_msgs/String tracking_state      # 跟踪状态，例如 OFF、OK、SEARCHING、TERMINATE。
std_msgs/UInt8 missing_frams        # 连续丢失帧数，字段名沿用原定义。
