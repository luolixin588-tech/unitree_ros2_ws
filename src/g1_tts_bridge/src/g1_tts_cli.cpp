#include <iostream>
#include <string>
#include <cstdlib>
#include <cctype>
#include <unitree/robot/channel/channel_factory.hpp>
#include <unitree/robot/g1/audio/g1_audio_client.hpp>

static bool is_integer(const char *s) {
  if (s == nullptr || *s == '\0') return false;
  for (const char *p = s; *p != '\0'; ++p) {
    if (!std::isdigit(static_cast<unsigned char>(*p))) return false;
  }
  return true;
}

int main(int argc, char *argv[]) {
  if (argc < 4) {
    std::cerr << "Usage: g1_tts_cli <network_interface> <speaker_id> [volume_0_100] <text>"
              << std::endl;
    return 1;
  }

  const std::string interface = argv[1];
  const int32_t speaker_id = std::atoi(argv[2]);
  int32_t target_volume = 100;
  int text_start_idx = 3;
  if (argc >= 5 && is_integer(argv[3])) {
    target_volume = std::atoi(argv[3]);
    if (target_volume < 0) target_volume = 0;
    if (target_volume > 100) target_volume = 100;
    text_start_idx = 4;
  }

  std::string text;
  for (int i = text_start_idx; i < argc; ++i) {
    if (i > text_start_idx) text += " ";
    text += argv[i];
  }
  if (text.empty()) {
    std::cerr << "Error: empty text." << std::endl;
    return 1;
  }

  try {
    unitree::robot::ChannelFactory::Instance()->Init(0, interface);
    unitree::robot::g1::AudioClient client;
    client.Init();
    client.SetTimeout(10.0f);

    uint8_t current_volume = 0;
    int32_t ret = client.GetVolume(current_volume);
    if (ret == 0) {
      std::cout << "Current volume: " << static_cast<int>(current_volume) << std::endl;
    } else {
      std::cerr << "GetVolume error code: " << ret << std::endl;
    }

    ret = client.SetVolume(static_cast<uint8_t>(target_volume));
    if (ret != 0) {
      std::cerr << "SetVolume error code: " << ret << std::endl;
    } else {
      std::cout << "SetVolume success: " << target_volume << std::endl;
    }

    ret = client.TtsMaker(text, speaker_id);
    if (ret != 0) {
      std::cerr << "TtsMaker error code: " << ret << std::endl;
      return 2;
    }
    std::cout << "TtsMaker ret: 0" << std::endl;
  } catch (const std::exception &e) {
    std::cerr << "Exception: " << e.what() << std::endl;
    return 3;
  }

  return 0;
}
