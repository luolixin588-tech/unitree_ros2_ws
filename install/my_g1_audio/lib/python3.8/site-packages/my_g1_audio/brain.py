#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import requests
import json
import subprocess
import threading
from rclpy.qos import QoSProfile, ReliabilityPolicy
from langdetect import detect

TTS_CLI_PATH = "/home/luolixin/unitree_ros2_ws/install/g1_tts_bridge/lib/g1_tts_bridge/g1_tts_cli"
NETWORK_INTERFACE = "eno2"
TTS_VOLUME = 100

class G1AIController(Node):
    def __init__(self):
        super().__init__('g1_ai_controller')
        self.is_speaking = False
        
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT, 
            depth=10
        )

        self.input_sub = self.create_subscription(
            String,
            '/audio_msg', 
            self.asr_callback, 
            qos_profile)

        self.get_logger().info('已连接到 G1 硬件语音通道: /audio_msg')

        self.say_hello()

        self.rag_server_url = "http://127.0.0.1:5000/ask"
        self.get_logger().info("G1 客户端已就绪，等待连接 RAG 大脑 (Port 5000)...")

    def asr_callback(self, msg):
        if self.is_speaking:
            return
        try:
            data = json.loads(msg.data)
            text = data.get("text", "")
            raw_is_final = data.get("is_final", False)
        
            is_final_flag = False
            if isinstance(raw_is_final, bool):
                is_final_flag = raw_is_final
            elif isinstance(raw_is_final, int):
                is_final_flag = (raw_is_final == 1)
                
            if text:
                ai_reply = self.call_rag_server(text)
                self.get_logger().info(f"AI 的回答: {ai_reply}")
                self.robot_speak(ai_reply)
        except Exception as e:
            self.get_logger().error(f"解析语音消息失败: {e}")

    def call_rag_server(self, question):
        payload = {"question": question}
        try:
            resp = requests.post(self.rag_server_url, json=payload, timeout=30)
            if resp.status_code == 200:
                return resp.json().get("answer", "大脑返回了空内容")
            else:
                return f"大脑连接出错 (状态码 {resp.status_code})"
        except requests.exceptions.ConnectionError:
            return "连接失败，请检查 rag_server.py 是否已启动？"
        except Exception as e:
            return f"通信发生错误: {str(e)}"

    def say_hello(self):
        """开机问候语回调函数"""
        begin_text = "Hello,please ask me questions"
        begin_text_cn = "大家好！我是笨笨。有什么问题尽管问我吧。"
        self.get_logger().info(f"🔊 Play startup greeting: {begin_text_cn}")       
        self.robot_speak(begin_text)

        #self.start_timer.cancel()

    def robot_speak(self, text):
        self.is_speaking = True

        try:
            lang = detect(text)
        except Exception:
            lang = 'zh-cn'

        speaker_id = 0 if lang == 'zh-cn' else 1

        self.get_logger().info(
            f"调用 TtsMaker: speaker_id={speaker_id}, volume={TTS_VOLUME}, text={text}"
        )

        t = threading.Thread(
            target=self._run_tts_cli,
            args=(text, speaker_id),
            daemon=True
        )
        t.start()

    def _run_tts_cli(self, text, speaker_id):
        try:
            result = subprocess.run(
                [TTS_CLI_PATH, NETWORK_INTERFACE, str(speaker_id), str(TTS_VOLUME), text],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                self.get_logger().info(
                    f"✅ TtsMaker 调用成功，播报完成: {result.stdout.strip()}"
                )
            else:
                self.get_logger().warn(
                    f"⚠️ TtsMaker 返回错误 (code {result.returncode}): {result.stderr.strip()}"
                )
        except subprocess.TimeoutExpired:
            self.get_logger().error("TtsMaker 调用超时")
        except Exception as e:
            self.get_logger().error(f"TtsMaker 调用异常: {e}")
        finally:
            self.is_speaking = False
            self.get_logger().info("恢复监听...")

def main(args=None):
    rclpy.init(args=args)
    node = G1AIController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
