#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import socket
import struct
import numpy as np
import onnxruntime as ort
import threading
from faster_whisper import WhisperModel

class G1AudioBridge(Node):
    def __init__(self):
        super().__init__('g1_audio_bridge')
        
        # 1. ROS2 发布者：识别后的文字发往 /g1/voice_text
        self.text_pub = self.create_publisher(String, '/g1/voice_text', 10)

        # 2. 初始化 VAD 模型 (Silero VAD ONNX)
        # 请确保 silero_vad.onnx 在脚本同目录下
        try:
            self.vad_session = ort.InferenceSession("silero_vad.onnx")
            self.reset_vad_state()
            self.get_logger().info("✅ Silero VAD 模型加载成功")
        except Exception as e:
            self.get_logger().error(f"❌ 无法加载 VAD 模型: {e}")

        # 3. 初始化 STT 模型 (Faster-Whisper)
        # device 可选 "cuda" 或 "cpu"
        self.stt_model = WhisperModel("base", device="cpu", compute_type="int8")
        self.get_logger().info("✅ Faster-Whisper 模型加载成功")

        # 4. 配置 UDP 组播接收机器人音频
        self.MCAST_GRP = '239.168.123.161'
        self.MCAST_PORT = 5555
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.MCAST_PORT))
        mreq = struct.pack("4sl", socket.inet_aton(self.MCAST_GRP), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        # 5. 启动后台音频处理线程
        self.worker_thread = threading.Thread(target=self.audio_worker, daemon=True)
        self.worker_thread.start()
        self.get_logger().info("🚀 耳朵节点 (earNode) 已启动，开始监听...")

    def reset_vad_state(self):
        """重置 RNN 模型内部状态"""
        self._h = np.zeros((2, 1, 64)).astype('float32')
        self._c = np.zeros((2, 1, 64)).astype('float32')

    def process_vad(self, data_bytes):
        """
        核心函数：将原始字节转为概率
        """
        # 将 int16 转换为 float32 归一化数组
        audio_int16 = np.frombuffer(data_bytes, dtype=np.int16)
        audio_float32 = audio_int16.astype(np.float32) / 32768.0

        # 准备模型输入
        ort_inputs = {
            'input': audio_float32.reshape(1, -1),
            'sr': np.array([16000], dtype=np.int64),
            'h': self._h,
            'c': self._c
        }
        
        # 推理并更新状态
        out, h, c = self.vad_session.run(None, ort_inputs)
        self._h, self._c = h, c
        return out[0][0]

    def stt_recognize(self, audio_bytes):
        """语音转文字"""
        try:
            audio_int16 = np.frombuffer(audio_bytes, dtype=np.int16)
            audio_float32 = audio_int16.astype(np.float32) / 32768.0
            
            # 使用 Faster-Whisper 识别
            segments, _ = self.stt_model.transcribe(audio_float32, language="zh")
            text = "".join([s.text for s in segments])
            return text
        except Exception as e:
            self.get_logger().error(f"STT Error: {e}")
            return ""

    def audio_worker(self):
        """独立线程中的死循环"""
        audio_buffer = []
        is_speaking = False
        silence_threshold = 20  # 约 600ms 静默
        silence_count = 0
        VAD_PROB_LIMIT = 0.5

        while rclpy.ok():
            try:
                # 接收 G1 的音频包 (512 samples * 2 bytes)
                data, _ = self.sock.recvfrom(1024)
                if not data: continue

                prob = self.process_vad(data)

                if prob > VAD_PROB_LIMIT:
                    if not is_speaking:
                        is_speaking = True
                        audio_buffer = []
                        self.get_logger().info("🎤 检测到人声...")
                    
                    audio_buffer.append(data)
                    silence_count = 0
                else:
                    if is_speaking:
                        audio_buffer.append(data)
                        silence_count += 1
                        
                        if silence_count > silence_threshold:
                            is_speaking = False
                            full_voice = b"".join(audio_buffer)
                            self.get_logger().info("⌛ 正在转换语音...")
                            
                            text = self.stt_recognize(full_voice)
                            if text.strip():
                                self.get_logger().info(f"📝 识别到: {text}")
                                msg = String()
                                msg.data = text
                                self.text_pub.publish(msg)
                            
                            audio_buffer = []
                            self.reset_vad_state()
            except Exception as e:
                self.get_logger().error(f"Worker Loop Error: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = G1AudioBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()