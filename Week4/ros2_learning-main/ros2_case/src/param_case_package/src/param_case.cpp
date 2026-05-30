// 1. 包含头文件。
#include <chrono>
#include <memory>
#include <string>
#include <vector>

#include "rclcpp/rclcpp.hpp"

using namespace std::chrono_literals;

// 3. 定义节点类。
class ParamCase : public rclcpp::Node
{
public:
	ParamCase()
	: Node("param_case"),
		turtlesim_node_name_(this->declare_parameter<std::string>("turtlesim_node_name", "turtlesim")),
		background_r_(this->declare_parameter<int>("background_r_start", 0)),
		background_g_(this->declare_parameter<int>("background_g_start", 0)),
		background_b_(this->declare_parameter<int>("background_b_start", 0)),
		background_r_min_(this->declare_parameter<int>("background_r_min", 0)),
		background_g_min_(this->declare_parameter<int>("background_g_min", 0)),
		background_b_min_(this->declare_parameter<int>("background_b_min", 0)),
		background_r_max_(this->declare_parameter<int>("background_r_max", 255)),
		background_g_max_(this->declare_parameter<int>("background_g_max", 255)),
		background_b_max_(this->declare_parameter<int>("background_b_max", 255)),
		background_r_step_(this->declare_parameter<int>("background_r_step", 5)),
		background_g_step_(this->declare_parameter<int>("background_g_step", 3)),
		background_b_step_(this->declare_parameter<int>("background_b_step", 4)),
		loop_rate_hz_(this->declare_parameter<double>("loop_rate_hz", 10.0))
	{
		// 3-1. 创建参数客户端。
		param_client_ = std::make_shared<rclcpp::SyncParametersClient>(this, turtlesim_node_name_);
	}

	void run()
	{
		// 3-2. 连接参数服务端。
		while (rclcpp::ok() && !param_client_->wait_for_service(1s)) {
			RCLCPP_INFO(
				get_logger(),
				"等待 %s 的参数服务启动...",
				turtlesim_node_name_.c_str());
		}

		if (!rclcpp::ok()) {
			return;
		}

		auto initial_results = param_client_->set_parameters(
			{
				rclcpp::Parameter("background_r", background_r_),
				rclcpp::Parameter("background_g", 0),
				rclcpp::Parameter("background_b", 0)
			},
			1s);

		for (const auto & result : initial_results) {
			if (!result.successful) {
				RCLCPP_WARN(get_logger(), "初始化背景颜色失败: %s", result.reason.c_str());
			}
		}

		int red_direction = 1;
		int green_direction = 1;
		int blue_direction = 1;
		rclcpp::Rate rate(loop_rate_hz_);

		while (rclcpp::ok()) {
			// 3-3. 更新参数。
			auto update_channel = [](int & value, int & channel_direction, int channel_min, int channel_max, int channel_step) {
				value += channel_direction * channel_step;
				if (value >= channel_max) {
					value = channel_max;
					channel_direction = -1;
				} else if (value <= channel_min) {
					value = channel_min;
					channel_direction = 1;
				}
			};

			update_channel(background_r_, red_direction, background_r_min_, background_r_max_, background_r_step_);
			update_channel(background_g_, green_direction, background_g_min_, background_g_max_, background_g_step_);
			update_channel(background_b_, blue_direction, background_b_min_, background_b_max_, background_b_step_);

			RCLCPP_INFO(
				get_logger(),
				"background_r = %d, background_g = %d, background_b = %d",
				background_r_,
				background_g_,
				background_b_);

			auto results = param_client_->set_parameters(
				{
					rclcpp::Parameter("background_r", background_r_),
					rclcpp::Parameter("background_g", background_g_),
					rclcpp::Parameter("background_b", background_b_)
				},
				1s);

			for (const auto & result : results) {
				if (!result.successful) {
					RCLCPP_WARN(get_logger(), "更新背景颜色失败: %s", result.reason.c_str());
				}
			}

			rate.sleep();
		}
	}

private:
	std::string turtlesim_node_name_;
	int background_r_;
	int background_g_;
	int background_b_;
	int background_r_min_;
	int background_g_min_;
	int background_b_min_;
	int background_r_max_;
	int background_g_max_;
	int background_b_max_;
	int background_r_step_;
	int background_g_step_;
	int background_b_step_;
	double loop_rate_hz_;
	rclcpp::SyncParametersClient::SharedPtr param_client_;
};

int main(int argc, char * argv[])
{
	// 2. 初始化 ROS2 客户端。
	rclcpp::init(argc, argv);

	// 4. 创建对象指针,并调用其函数。
	auto node = std::make_shared<ParamCase>();
	node->run();

	// 5. 释放资源。
	rclcpp::shutdown();
	return 0;
}

