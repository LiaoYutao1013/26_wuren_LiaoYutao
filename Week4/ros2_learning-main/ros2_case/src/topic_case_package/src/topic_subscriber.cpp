/*  
    需求：订阅发布方发布的消息，并输出到终端。
    步骤：
        1.包含头文件；
        2.初始化 ROS2 客户端；
        3.定义节点类；
            3-1.创建订阅方；
            3-2.处理订阅到的消息。
        4.调用spin函数，并传入节点对象指针；
        5.释放资源。
*/

// 1. 包含头文件：rclcpp 用于创建订阅节点，geometry_msgs::msg::Twist 用于接收和转发乌龟控制指令。
#include <functional>
#include <memory>

#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"

class TopicSubscriber : public rclcpp::Node
{
public:
  TopicSubscriber()
  : Node("topic_subscriber")
  {
    // 3-1. 创建订阅方：监听发布方发送到 /circle_cmd 的 Twist 消息，队列深度为 10。
    subscription_ = this->create_subscription<geometry_msgs::msg::Twist>(
      "/circle_cmd",
      10,
      std::bind(&TopicSubscriber::handle_circle_command, this, std::placeholders::_1));

    // 为了把订阅到的消息反馈给乌龟节点，这里再创建一个发布方，把消息转发到 /turtle1/cmd_vel。
    publisher_ = this->create_publisher<geometry_msgs::msg::Twist>("/turtle1/cmd_vel", 10);
  }

private:
  void handle_circle_command(const geometry_msgs::msg::Twist::SharedPtr msg)
  {
    // 3-2. 处理订阅到的消息：先打印收到的速度值，再原样转发给 turtlesim。
    RCLCPP_INFO(
      this->get_logger(),
      "收到圆周运动指令并转发: linear.x=%.2f, angular.z=%.2f",
      msg->linear.x,
      msg->angular.z);

    publisher_->publish(*msg);
  }

  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr subscription_;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
};

int main(int argc, char ** argv)
{
  // 2. 初始化 ROS2 客户端库，让当前进程可以参与发布/订阅通信。
  rclcpp::init(argc, argv);

  // 3. 定义节点类，并创建订阅方节点对象。
  auto node = std::make_shared<TopicSubscriber>();

  // 4. 调用 spin 函数，并传入节点对象指针，持续监听发布方消息并完成转发。
  rclcpp::spin(node);

  // 5. 释放资源：关闭 ROS2 客户端库，结束节点生命周期。
  rclcpp::shutdown();
  return 0;
}