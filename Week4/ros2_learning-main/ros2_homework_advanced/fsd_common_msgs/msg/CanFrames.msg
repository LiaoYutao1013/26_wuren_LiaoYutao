# 一组 CAN 帧消息。
std_msgs/Header header              # CAN 帧集合的时间戳。

can_msgs/Frame[] frames             # 同一周期内接收或待发送的 CAN 帧数组。
