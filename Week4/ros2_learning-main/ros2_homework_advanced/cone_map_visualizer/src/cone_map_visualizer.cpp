#include <functional>
#include <memory>
#include <string>

#include "builtin_interfaces/msg/time.hpp"
#include "fsd_common_msgs/msg/map.hpp"
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/color_rgba.hpp"
#include "visualization_msgs/msg/marker.hpp"
#include "visualization_msgs/msg/marker_array.hpp"

/* ConeMapVisualizer 节点负责
1. 订阅 SLAM/建图节点发布的锥桶地图；
2. 按颜色把锥桶分成 blue/red/unknown/yellow 四组；
3. 生成 SPHERE_LIST 类型的 Marker，发布给 RViz 显示。
*/

class ConeMapVisualizer : public rclcpp::Node
{
public:
  ConeMapVisualizer()
  : Node("cone_map_visualizer")
  {
    input_topic_ = this->declare_parameter<std::string>("input_topic", "/estimation/slam/map");
    marker_topic_ =
      this->declare_parameter<std::string>("marker_topic", "/visualization/cone_markers");
    frame_override_ = this->declare_parameter<std::string>("frame_override", "");

    //Marker的球体直径缩放值，控制RViz中锥桶点的显示大小。
    marker_scale_ = this->declare_parameter<double>("marker_scale", 0.45);

    //z_offset用于抬高marker，这样更好观察。
    z_offset_ = this->declare_parameter<double>("z_offset", 0.18);

    //发布MarkerArray，队列长度10，留一部分作冗余。
    marker_pub_ =
      this->create_publisher<visualization_msgs::msg::MarkerArray>(marker_topic_, 10);

    // 订阅地图消息。收到新地图时，handleMap会重新生成整组可视化 Marker。
    map_sub_ = this->create_subscription<fsd_common_msgs::msg::Map>(
      input_topic_,
      rclcpp::QoS(10),
      std::bind(&ConeMapVisualizer::handleMap, this, std::placeholders::_1));

    RCLCPP_INFO(
      this->get_logger(),
      "Subscribing to %s and publishing MarkerArray to %s",
      input_topic_.c_str(),
      marker_topic_.c_str());
  }

private:
  // 生成RGBA颜色结构体，简化为不同颜色锥桶配置Marker的代码。
  static std_msgs::msg::ColorRGBA makeColor(float r, float g, float b, float a = 1.0F)
  {
    std_msgs::msg::ColorRGBA color;
    color.r = r;
    color.g = g;
    color.b = b;
    color.a = a;
    return color;
  }

  // 决定 Marker 使用的坐标系：
  // 1. frame_override 参数优先级最高；
  // 2. 地图消息 header.frame_id 非空时使用消息自带坐标系；
  // 3. 两者都没有时回退到 world，配合 launch 中的静态 TF 使用。
  std::string resolveFrame(const fsd_common_msgs::msg::Map::SharedPtr & msg) const
  {
    if (!frame_override_.empty()) {
      return frame_override_;
    }
    if (!msg->header.frame_id.empty()) {
      return msg->header.frame_id;
    }
    return "world";
  }

  //用当前ROS时钟生成Marker时间戳。
  //得到 builtin_interfaces::msg::Time 类型。
  builtin_interfaces::msg::Time makeCurrentStamp() const
  {
    const auto now_ns = this->get_clock()->now().nanoseconds();
    builtin_interfaces::msg::Time stamp;
    stamp.sec = static_cast<int32_t>(now_ns / 1000000000LL);
    stamp.nanosec = static_cast<uint32_t>(now_ns % 1000000000LL);
    return stamp;
  }

  //将某一种颜色的锥桶序列转换成一个SPHERE_LIST Marker。
  //ConeSequenceT使用模板，是为了兼容不同容器类型的cone_*字段。
  template<typename ConeSequenceT>
  visualization_msgs::msg::Marker makeConeMarker(
    const std::string & frame_id,
    const builtin_interfaces::msg::Time & stamp,
    const std::string & ns,
    int32_t id,
    const ConeSequenceT & cones,
    const std_msgs::msg::ColorRGBA & color) const
  {
    visualization_msgs::msg::Marker marker;
    marker.header.frame_id = frame_id;
    marker.header.stamp = stamp;

    //namespace + id唯一确定一个Marker，RViz用同名Marker覆盖旧数据。
    marker.ns = ns;
    marker.id = id;

    //SPHERE_LIST可以用一个Marker表示多个同尺寸球体，比逐个发布更轻量。
    marker.type = visualization_msgs::msg::Marker::SPHERE_LIST;
    marker.action = visualization_msgs::msg::Marker::ADD;

    //单位四元数表示无旋转；SPHERE_LIST 的球体本身不依赖姿态。
    marker.pose.orientation.w = 1.0;

    //scale 三个方向相同，使每个锥桶点显示为球体。
    marker.scale.x = marker_scale_;
    marker.scale.y = marker_scale_;
    marker.scale.z = marker_scale_;

    marker.color = color;

    //lifetime为0表示Marker不自动过期，由后续同ns/id的Marker更新。
    marker.lifetime.sec = 0;
    marker.lifetime.nanosec = 0;

    marker.points.reserve(cones.size());
    for (const auto & cone : cones) {
      auto point = cone.position;
      point.z += z_offset_;
      marker.points.push_back(point);
    }

    return marker;
  }

  //地图订阅回调,把四类锥桶分别转换成Marker，再一次性发布MarkerArray。
  void handleMap(const fsd_common_msgs::msg::Map::SharedPtr msg)
  {
    const auto frame_id = resolveFrame(msg);
    const auto marker_stamp = makeCurrentStamp();

    visualization_msgs::msg::MarkerArray marker_array;

    //以下是蓝、红、未知、黄色锥桶的Marker配置，每类锥桶一个Marker，ns区分颜色，id区分同一颜色的不同Marker（这里只有一个）。
    marker_array.markers.push_back(makeConeMarker(
      frame_id,
      marker_stamp,
      "cones_blue",
      0,
      msg->cone_blue,
      makeColor(0.05F, 0.20F, 1.00F)));

    marker_array.markers.push_back(makeConeMarker(
      frame_id,
      marker_stamp,
      "cones_red",
      1,
      msg->cone_red,
      makeColor(1.00F, 0.05F, 0.02F)));

    marker_array.markers.push_back(makeConeMarker(
      frame_id,
      marker_stamp,
      "cones_unknown",
      2,
      msg->cone_unknown,
      makeColor(0.78F, 0.78F, 0.78F)));

    marker_array.markers.push_back(makeConeMarker(
      frame_id,
      marker_stamp,
      "cones_yellow",
      3,
      msg->cone_yellow,
      makeColor(1.00F, 0.82F, 0.05F)));

    marker_pub_->publish(marker_array);

    //打印日志
    RCLCPP_INFO_THROTTLE(
      this->get_logger(),
      *this->get_clock(),
      2000,
      "frame=%s blue=%zu red=%zu unknown=%zu yellow=%zu",
      frame_id.c_str(),
      msg->cone_blue.size(),
      msg->cone_red.size(),
      msg->cone_unknown.size(),
      msg->cone_yellow.size());
  }

  //参数缓存：构造函数中读取，回调中重复使用。
  std::string input_topic_;
  std::string marker_topic_;
  std::string frame_override_;
  double marker_scale_;
  double z_offset_;

  //ROS2 通信对象；SharedPtr由rclcpp管理生命周期。
  rclcpp::Subscription<fsd_common_msgs::msg::Map>::SharedPtr map_sub_;
  rclcpp::Publisher<visualization_msgs::msg::MarkerArray>::SharedPtr marker_pub_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ConeMapVisualizer>());

  rclcpp::shutdown();
  return 0;
}
