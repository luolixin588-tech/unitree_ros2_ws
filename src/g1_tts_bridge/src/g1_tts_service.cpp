#include <memory>
#include <string>
#include <thread>
#include <chrono>
#include <algorithm>

#include "rclcpp/rclcpp.hpp"
#include "g1_tts_bridge/srv/tts.hpp"
#include <unitree/robot/channel/channel_subscriber.hpp>

// 【修改 1】直接引用标准 SDK 头文件 (系统路径)
#include <unitree/robot/g1/audio/g1_audio_client.hpp>

using std::placeholders::_1;
using std::placeholders::_2;

class G1TtsService : public rclcpp::Node
{
public:
  G1TtsService() : Node("g1_tts_service_node")
  {
    this->declare_parameter<std::string>("network_interface", "eno1");
    const auto interface = this->get_parameter("network_interface").as_string();
    unitree::robot::ChannelFactory::Instance()->Init(0, interface);
    RCLCPP_INFO(this->get_logger(), "ChannelFactory initialized on %s", interface.c_str());

    audio_client_ = std::make_shared<unitree::robot::g1::AudioClient>();
    
    // 【修改这里】Init() 返回 void，直接调用即可
    // 如果想要更安全，可以包在 try-catch 里，但直接调用也能编译通过
    audio_client_->Init();
    RCLCPP_INFO(this->get_logger(), "G1 Audio Client initialized.");

    // 创建服务端
    service_ = this->create_service<g1_tts_bridge::srv::TTS>(
        "g1_tts", 
        std::bind(&G1TtsService::handle_tts_request, this, _1, _2));

    RCLCPP_INFO(this->get_logger(), "G1 TTS Bridge Service is ready.");
  }

private:
  // 【修改 3】使用标准 SDK 的类型定义
  std::shared_ptr<unitree::robot::g1::AudioClient> audio_client_;
  rclcpp::Service<g1_tts_bridge::srv::TTS>::SharedPtr service_;

  double estimate_speak_seconds(const std::string &text, int32_t speaker_id) const
  {
    // speaker_id=0(中文)通常更慢，speaker_id=1(英文)通常更快
    const double per_char = (speaker_id == 1) ? 0.085 : 0.30;
    return std::max(0.8, static_cast<double>(text.size()) * per_char + 0.5);
  }

  void handle_tts_request(
      const std::shared_ptr<g1_tts_bridge::srv::TTS::Request> request,
      std::shared_ptr<g1_tts_bridge::srv::TTS::Response> response)
  {
    std::string text_to_speak = request->text;
    RCLCPP_INFO(this->get_logger(), "Received TTS request: '%s'", text_to_speak.c_str());

    if (!audio_client_) {
      response->success = false;
      response->message = "Audio client not initialized";
      return;
    }

    try {
      // 调用 SDK 的 TTS 接口
      // 参数：内容, 语言ID (0=默认)
      int32_t ret = audio_client_->TtsMaker(text_to_speak, request->speaker_id);

      if (ret == 0) {
        const double wait_sec = estimate_speak_seconds(text_to_speak, request->speaker_id);
        std::this_thread::sleep_for(std::chrono::duration<double>(wait_sec));
        response->success = true;
        response->message = "done";
      } else {
        RCLCPP_WARN(this->get_logger(), "TTS Error Code: %d", ret);
        response->success = false;
        response->message = "SDK Error: " + std::to_string(ret);
      }
    } catch (const std::exception &e) {
      RCLCPP_ERROR(this->get_logger(), "Exception: %s", e.what());
      response->success = false;
      response->message = e.what();
    }
  }
};

int main(int argc, char **argv)
{
  rclcpp::init(argc, argv);

  // 【修改 4】单节点模式
  // 因为 AudioClient 只是一个普通 C++ 类，不是 ROS 节点，
  // 所以我们不需要 MultiThreadedExecutor，直接 spin 我们的服务节点即可。
  auto node = std::make_shared<G1TtsService>();
  
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}