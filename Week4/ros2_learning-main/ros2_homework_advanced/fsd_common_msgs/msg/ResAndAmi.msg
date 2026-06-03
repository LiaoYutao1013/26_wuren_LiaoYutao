# RES 与 AMI 选择状态。
std_msgs/Header header              # 状态时间戳。
uint8 res_state                     # RES 状态，1 通常代表 go 信号。
string mission                      # AMI 选择的无人驾驶任务：0 inspection，1 ebs_test，2 acceleration，3 skidpad，4 trackdrive。
