/*  
  需求：在turtlesim节点中发布话题使乌龟做圆周运动
  步骤：
    1.包含头文件；
    2.初始化 ROS2 客户端；
    3.定义节点类；
      3-1.创建发布方；
      3-2.创建定时器；
      3-3.组织消息并发布。
    4.调用spin函数，并传入节点对象指针；
    5.释放资源。
*/


// 1. 包含头文件：rclcpp 负责创建 ROS2 节点，geometry_msgs::msg::Twist 负责描述乌龟的速度指令。
#include <chrono>
#include <functional>
#include <memory>

#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"

using namespace std::chrono_literals;

class TopicPublisher : public rclcpp::Node
{
public:
  TopicPublisher()
  : Node("topic_publisher")
  {
    // 3-1. 创建发布方：向 /circle_cmd 发布 Twist 消息，队列深度设置为 10，避免短时阻塞。
    publisher_ = this->create_publisher<geometry_msgs::msg::Twist>("/circle_cmd", 10);

    // 3-2. 创建定时器：每 100ms 触发一次回调，持续发送圆周运动控制指令。
    timer_ = this->create_wall_timer(
      100ms, std::bind(&TopicPublisher::publish_circle_command, this));
  }

private:
  void publish_circle_command()
  {
    // 3-3. 组织消息并发布：线速度和角速度同时赋值，乌龟就会沿圆周运动。
    geometry_msgs::msg::Twist msg;
    msg.linear.x = 2.0;
    msg.linear.y = 0.0;
    msg.linear.z = 0.0;
    msg.angular.x = 0.0;
    msg.angular.y = 0.0;
    msg.angular.z = 1.0;

    RCLCPP_INFO(
      this->get_logger(),
      "发布圆周运动指令: linear.x=%.2f, angular.z=%.2f",
      msg.linear.x,
      msg.angular.z);

    publisher_->publish(msg);
  }

  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char ** argv)
{
  // 2. 初始化 ROS2 客户端库，让当前进程能够参与 rclcpp 通信。
  rclcpp::init(argc, argv);

  // 3. 定义节点类，并创建发布方节点对象。
  auto node = std::make_shared<TopicPublisher>();

  // 4. 调用 spin 函数，并传入节点对象指针，保持节点持续运行并响应定时器。
  rclcpp::spin(node);

  // 5. 释放资源：关闭 ROS2 客户端库，结束节点生命周期。
  rclcpp::shutdown();
  return 0;
}
