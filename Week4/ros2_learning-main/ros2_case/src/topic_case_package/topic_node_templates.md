# ROS2 通用话题发布和订阅节点模板

说明：ROS2 的 C++ 发布/订阅节点在编译期仍然需要确定消息类型，所以这里用 `MsgT` 和占位符把具体类型、话题名、节点名抽象出来。你实际使用时，只需要把占位符替换成自己的消息类型和话题即可。

## 1. 通用发布节点模板

```cpp
// 1. 包含头文件：rclcpp 负责 ROS2 节点，消息头文件替换成你的实际消息类型。
#include <chrono>
#include <functional>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "<YOUR_MSG_HEADER>"

using namespace std::chrono_literals;

template<typename MsgT>
class GenericPublisher : public rclcpp::Node
{
public:
  using FillMessageCallback = std::function<void(MsgT &)>;

  GenericPublisher(
    const std::string & node_name,
    const std::string & topic_name,
    const rclcpp::QoS & qos,
    std::chrono::milliseconds period,
    FillMessageCallback fill_message)
  : Node(node_name), fill_message_(std::move(fill_message))
  {
    // 3-1. 创建发布方：把消息发布到指定话题，qos 用于控制通信队列策略。
    publisher_ = this->create_publisher<MsgT>(topic_name, qos);

    // 3-2. 创建定时器：周期性触发回调，持续发布消息。
    timer_ = this->create_wall_timer(
      period,
      std::bind(&GenericPublisher::publish_message, this));
  }

private:
  void publish_message()
  {
    // 3-3. 组织消息并发布：先构造消息对象，再由外部回调填充字段。
    MsgT msg{};
    if (fill_message_) {
      fill_message_(msg);
    }

    RCLCPP_INFO(this->get_logger(), "publish message on <YOUR_TOPIC_NAME>");
    publisher_->publish(msg);
  }

  typename rclcpp::Publisher<MsgT>::SharedPtr publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
  FillMessageCallback fill_message_;
};

int main(int argc, char ** argv)
{
  // 2. 初始化 ROS2 客户端库。
  rclcpp::init(argc, argv);

  // 3. 定义节点类，并创建发布方节点对象。
  auto node = std::make_shared<GenericPublisher<MsgT>>(
    "<YOUR_NODE_NAME>",
    "<YOUR_TOPIC_NAME>",
    rclcpp::QoS(10),
    std::chrono::milliseconds(100),
    [](MsgT & msg) {
      // 在这里填写消息字段，例如 msg.xxx = ...;
    });

  // 4. 调用 spin 函数，并传入节点对象指针。
  rclcpp::spin(node);

  // 5. 释放资源。
  rclcpp::shutdown();
  return 0;
}
```

## 2. 通用订阅节点模板

```cpp
// 1. 包含头文件：rclcpp 负责 ROS2 节点，消息头文件替换成你的实际消息类型。
#include <functional>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "<YOUR_MSG_HEADER>"

template<typename MsgT>
class GenericSubscriber : public rclcpp::Node
{
public:
  using MessageCallback = std::function<void(typename MsgT::ConstSharedPtr)>;

  GenericSubscriber(
    const std::string & node_name,
    const std::string & topic_name,
    const rclcpp::QoS & qos,
    MessageCallback on_message)
  : Node(node_name), on_message_(std::move(on_message))
  {
    // 3-1. 创建订阅方：监听指定话题上的消息。
    subscription_ = this->create_subscription<MsgT>(
      topic_name,
      qos,
      std::bind(&GenericSubscriber::handle_message, this, std::placeholders::_1));
  }

private:
  void handle_message(typename MsgT::ConstSharedPtr msg)
  {
    // 3-2. 处理订阅到的消息：先做日志输出，再交给外部回调处理。
    RCLCPP_INFO(this->get_logger(), "receive message from <YOUR_TOPIC_NAME>");

    if (on_message_) {
      on_message_(msg);
    }
  }

  typename rclcpp::Subscription<MsgT>::SharedPtr subscription_;
  MessageCallback on_message_;
};

int main(int argc, char ** argv)
{
  // 2. 初始化 ROS2 客户端库。
  rclcpp::init(argc, argv);

  // 3. 定义节点类，并创建订阅方节点对象。
  auto node = std::make_shared<GenericSubscriber<MsgT>>(
    "<YOUR_NODE_NAME>",
    "<YOUR_TOPIC_NAME>",
    rclcpp::QoS(10),
    [](typename MsgT::ConstSharedPtr msg) {
      // 在这里处理收到的消息，例如打印字段、转发到其他话题、写入文件等。
      (void) msg;
    });

  // 4. 调用 spin 函数，并传入节点对象指针。
  rclcpp::spin(node);

  // 5. 释放资源。
  rclcpp::shutdown();
  return 0;
}
```

## 3. 需要替换的占位符

- `MsgT`：你的消息类型，例如 `std_msgs::msg::String`、`geometry_msgs::msg::Twist`。
- `<YOUR_MSG_HEADER>`：对应的头文件，例如 `"std_msgs/msg/string.hpp"`。
- `<YOUR_NODE_NAME>`：节点名，例如 `publisher_node`、`subscriber_node`。
- `<YOUR_TOPIC_NAME>`：话题名，例如 `chat_topic`、`/cmd_vel`。
- `qos`：一般可先用 `rclcpp::QoS(10)`，需要可靠性时再按场景调整。

## 4. 使用方式

如果你要快速套用到具体消息上，只需要三步：

1. 把 `MsgT` 替换成目标消息类型。
2. 把 `<YOUR_MSG_HEADER>` 改成对应消息头文件。
3. 在发布回调或订阅回调里补上你的业务逻辑。