#include <functional>
#include <memory>
#include <string>

#include "builtin_interfaces/msg/time.hpp"
#include "fsd_common_msgs/msg/map.hpp"
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/color_rgba.hpp"
#include "visualization_msgs/msg/marker.hpp"
#include "visualization_msgs/msg/marker_array.hpp"

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
    marker_scale_ = this->declare_parameter<double>("marker_scale", 0.45);
    z_offset_ = this->declare_parameter<double>("z_offset", 0.18);

    marker_pub_ =
      this->create_publisher<visualization_msgs::msg::MarkerArray>(marker_topic_, 10);

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
  static std_msgs::msg::ColorRGBA makeColor(float r, float g, float b, float a = 1.0F)
  {
    std_msgs::msg::ColorRGBA color;
    color.r = r;
    color.g = g;
    color.b = b;
    color.a = a;
    return color;
  }

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

  builtin_interfaces::msg::Time makeCurrentStamp() const
  {
    const auto now_ns = this->get_clock()->now().nanoseconds();
    builtin_interfaces::msg::Time stamp;
    stamp.sec = static_cast<int32_t>(now_ns / 1000000000LL);
    stamp.nanosec = static_cast<uint32_t>(now_ns % 1000000000LL);
    return stamp;
  }

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
    marker.ns = ns;
    marker.id = id;
    marker.type = visualization_msgs::msg::Marker::SPHERE_LIST;
    marker.action = visualization_msgs::msg::Marker::ADD;
    marker.pose.orientation.w = 1.0;
    marker.scale.x = marker_scale_;
    marker.scale.y = marker_scale_;
    marker.scale.z = marker_scale_;
    marker.color = color;
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

  void handleMap(const fsd_common_msgs::msg::Map::SharedPtr msg)
  {
    const auto frame_id = resolveFrame(msg);
    const auto marker_stamp = makeCurrentStamp();

    visualization_msgs::msg::MarkerArray marker_array;
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

  std::string input_topic_;
  std::string marker_topic_;
  std::string frame_override_;
  double marker_scale_;
  double z_offset_;

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
