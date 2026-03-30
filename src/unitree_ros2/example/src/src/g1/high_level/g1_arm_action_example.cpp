/**
 * @file g1_arm_action_example.cpp
 * @brief This example demonstrates how to use the G1 Arm Action Client to
 * execute predefined arm actions in ROS2.
 */
#include <iostream>
#include <memory>
#include <string>
#include <thread>

#include "common/ut_errror.hpp"
#include "g1/g1_arm_action_client.hpp"
#include "rclcpp/rclcpp.hpp"

#include "std_msgs/msg/int32.hpp"

class G1ArmActionNode : public rclcpp::Node {
 public:
  explicit G1ArmActionNode() : Node("g1_arm_action_node") {
    client_ = std::make_shared<unitree::robot::g1::G1ArmActionClient>(this);

    subscription_ = this->create_subscription<std_msgs::msg::Int32>(
      "/g1_arm_action_cmd", 10,
      std::bind(&G1ArmActionNode::action_callback, this, std::placeholders::_1));
    RCLCPP_INFO(this->get_logger(), "等待从话题 [/g1_arm_action_cmd] 发送的动作 ID...");

    // thread_ = std::thread([this] {
    //   using namespace std::chrono_literals;
    //   while (true) {
    //     std::this_thread::sleep_for(100ms);
    //     checkForInput();
    //   }
    // });
  }

 private:
  void checkForInput() {
    static std::string line;
    static bool getting_input = false;
    RCLCPP_INFO(this->get_logger(),
                "G1 Arm Action Node initialized\n"
                "Usage:\n"
                "  - 0: print supported actions.\n"
                "  - an id: execute an action.\n"
                "Attention:\n"
                "  Some actions will not be displayed on the APP,\n"
                "  but can be executed by the program.\n"
                "  These actions may cause the robot to fall,\n"
                "  so please execute them with caution.");
    if (!getting_input) {
      std::cout << "\nEnter action ID (or 'q' to quit): ";
      getting_input = true;
    }

    if (std::cin.peek() != EOF) {
      std::getline(std::cin, line);
      getting_input = false;

      if (line == "q") {
        rclcpp::shutdown();
        return;
      }

      try {
        int32_t action_id = std::stoi(line);
        ProcessAction(action_id);
      } catch (const std::exception& e) {
        RCLCPP_ERROR(this->get_logger(),
                     "Invalid input: %s. Please enter an integer.", e.what());
      }
    }
  }

  void action_callback(const std_msgs::msg::Int32::SharedPtr msg) {
    int32_t action_id = msg->data; // 从消息包里取出数字
    RCLCPP_INFO(this->get_logger(), "指令 ID: %d", action_id);
    
    // 直接复用原来的执行逻辑
    ProcessAction(action_id);
  }

  void ProcessAction(int32_t action_id) {
    if (action_id == 0) {
      std::string action_list_data;
      int32_t ret = client_->GetActionList(action_list_data);
      if (ret != 0) {       
        handleActionError(ret);
        return;
      }
      RCLCPP_INFO(this->get_logger(), "Available actions:\n%s",
                  action_list_data.c_str());
    } 
    else {
      int32_t ret = client_->ExecuteAction(action_id);
      if (ret != 0) {
        if (ret == -1) {
        RCLCPP_WARN(this->get_logger(), "动作已发出，但反馈超时");}
        else{
        handleActionError(ret);}} 
      else {
        RCLCPP_INFO(this->get_logger(), "Action %d executed successfully",
                    action_id);
      }
    }
  }

  void handleActionError(int32_t error_code) {
    RCLCPP_ERROR(this->get_logger(), "Execute action failed, error code: %d",
                 error_code);
    UT_PRINT_ERR(error_code,
                 unitree::robot::g1::UT_ROBOT_ARM_ACTION_ERR_ARMSDK);
    UT_PRINT_ERR(error_code,
                 unitree::robot::g1::UT_ROBOT_ARM_ACTION_ERR_HOLDING);
    UT_PRINT_ERR(error_code,
                 unitree::robot::g1::UT_ROBOT_ARM_ACTION_ERR_INVALID_ACTION_ID);
    UT_PRINT_ERR(error_code,
                 unitree::robot::g1::UT_ROBOT_ARM_ACTION_ERR_INVALID_FSM_ID);
    UT_PRINT_ERR(error_code, UT_ROBOT_TASK_TIMEOUT);
  }

  //std::thread thread_;
  std::shared_ptr<unitree::robot::g1::G1ArmActionClient> client_;

  rclcpp::Subscription<std_msgs::msg::Int32>::SharedPtr subscription_;
};

int main(int argc, const char** argv) {
  rclcpp::init(argc, argv);

  auto node = std::make_shared<G1ArmActionNode>();
  rclcpp::spin(node);
  rclcpp::shutdown();

  return 0;
}