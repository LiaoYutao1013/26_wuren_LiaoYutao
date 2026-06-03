# 决策切换标志消息，用于异常情况下切换控制策略。
std_msgs/Header header              # 决策标志时间戳。

uint8 lap1_state                    # 第一圈状态：0=正常，1=规划异常并触发 EBS。
uint8 lap2_state                    # 第二圈策略状态：0=正常。
# lap2_state=1：规划异常但 SLAM 正常，跟踪首圈轨迹或 Ribbon。
# lap2_state=2：规划异常且 SLAM 异常，触发 EBS。
# lap2_state=3：规划和 SLAM 正常，但仍选用 Ribbon。

uint8 map_state                     # 地图策略：0=根据 lap2_state 选择，1=一直使用局部地图；优先级高于 lap2_state。
