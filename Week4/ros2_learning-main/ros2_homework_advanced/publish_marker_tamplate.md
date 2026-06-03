# RViz Marker 发布模板

下面是一份可直接套用的 C++ 模板，用于在 ROS2 中向 RViz 发布 `visualization_msgs/msg/Marker`。实际使用时，可以按需求替换坐标系、Marker 类型、颜色、尺寸和位置。

## C++ 模板

```cpp
#include <chrono>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "visualization_msgs/msg/marker.hpp"

using namespace std::chrono_literals;

class MarkerPublisher : public rclcpp::Node
{
public:
	MarkerPublisher() : Node("marker_publisher")
	{
		// 创建 Marker 发布器；topic 名称需要和 RViz 中的 Marker Topic 保持一致。
		marker_pub_ = this->create_publisher<visualization_msgs::msg::Marker>("visualization_marker", 10);

		// 定时重复发布，避免 RViz 启动较晚或临时断开时看不到 Marker。
		timer_ = this->create_wall_timer(500ms, std::bind(&MarkerPublisher::publishMarker, this));
	}

private:
	void publishMarker()
	{
		visualization_msgs::msg::Marker marker;

		// 1. 设置坐标系；必须能被 RViz 的 Fixed Frame 通过 TF 正确关联。
		marker.header.frame_id = "map";
		marker.header.stamp = this->now();

		// 2. 设置命名空间和 ID；同一 ns + id 的 Marker 会被后续消息覆盖更新。
		marker.ns = "basic_shapes";
		marker.id = 0;

		// 3. 设置类型；常用类型包括 CUBE、SPHERE、ARROW、TEXT_VIEW_FACING、LINE_STRIP、POINTS。
		marker.type = visualization_msgs::msg::Marker::SPHERE;

		// 4. 设置动作；ADD 表示新增或更新，DELETE 表示删除。
		marker.action = visualization_msgs::msg::Marker::ADD;

		// 5. 设置位姿；orientation.w = 1.0 表示单位四元数，即无旋转。
		marker.pose.position.x = 0.0;
		marker.pose.position.y = 0.0;
		marker.pose.position.z = 0.5;
		marker.pose.orientation.x = 0.0;
		marker.pose.orientation.y = 0.0;
		marker.pose.orientation.z = 0.0;
		marker.pose.orientation.w = 1.0;

		// 6. 设置尺寸；不同 Marker 类型对 scale 的含义可能不同。
		marker.scale.x = 0.5;
		marker.scale.y = 0.5;
		marker.scale.z = 0.5;

		// 7. 设置颜色；alpha 必须大于 0，否则 Marker 透明不可见。
		marker.color.r = 0.1f;
		marker.color.g = 0.8f;
		marker.color.b = 0.2f;
		marker.color.a = 1.0f;

		// 8. 设置生命周期；0 表示一直显示，直到被同 ns/id 的 Marker 更新或删除。
		marker.lifetime = rclcpp::Duration::from_seconds(0.0);

		// 9. 发布 Marker。
		marker_pub_->publish(marker);
	}

	rclcpp::Publisher<visualization_msgs::msg::Marker>::SharedPtr marker_pub_;
	rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char ** argv)
{
	rclcpp::init(argc, argv);
	rclcpp::spin(std::make_shared<MarkerPublisher>());
	rclcpp::shutdown();
	return 0;
}
```
