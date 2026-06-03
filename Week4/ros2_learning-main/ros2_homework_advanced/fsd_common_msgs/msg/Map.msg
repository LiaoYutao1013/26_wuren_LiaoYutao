# 按颜色分类的锥桶地图消息。
std_msgs/Header header            # 地图时间戳和坐标系信息。

fsd_common_msgs/Cone[] cone_yellow # 黄色锥桶列表。
fsd_common_msgs/Cone[] cone_blue   # 蓝色锥桶列表。
fsd_common_msgs/Cone[] cone_red    # 红色锥桶列表。
fsd_common_msgs/Cone[] cone_unknown # 未知颜色或未分类锥桶列表。
