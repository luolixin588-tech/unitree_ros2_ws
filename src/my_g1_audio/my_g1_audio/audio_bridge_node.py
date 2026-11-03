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
import os
import time
from collections import deque
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from faster_whisper import WhisperModel
try:
    from opencc import OpenCC
except Exception:
    OpenCC = None
# export G1_MCAST_IFACE_IP=192.168.123.222
class G1AudioBridge(Node):
    def __init__(self):
        super().__init__('g1_audio_bridge')
        
        # 1. ROS2 发布者：识别后的文字发往 /g1/voice_text
        self.text_pub = self.create_publisher(String, '/g1/voice_text', 10)

        # Audio format: mono / 16kHz / 16-bit
        self.sample_rate = 16000
        self.sample_width_bytes = 2
        self.channels = 1
        self.vad_frame_samples = 512   # 32ms @ 16kHz
        self.vad_frame_bytes = self.vad_frame_samples * self.sample_width_bytes

        # VAD segment rules (slightly earlier speech onset + longer pre-roll reduce clipped sentence starts)
        self.vad_prob_limit = 0.45
        self.vad_keep_prob_limit = 0.36
        self.silence_threshold_frames = 20  # 1280ms, tolerate in-sentence pauses
        self.min_speech_frames = 8          # 256ms
        self.pre_speech_frames = 22         # ~704ms pre-roll before first speech frame

        self.stop_event = threading.Event()

        # 2. 初始化 VAD 模型 (Silero VAD ONNX)
        vad_model_candidates = self._resolve_vad_model_paths()
        if not vad_model_candidates:
            raise FileNotFoundError(
                "silero_vad.onnx not found. Place it in package share directory "
                "or beside audio_bridge_node.py in source package."
            )
        self.vad_session = None
        last_vad_error = None
        for vad_model_path in vad_model_candidates:
            try:
                self.vad_session = ort.InferenceSession(vad_model_path)
                self._init_vad_io_schema()
                self.reset_vad_state()
                self.get_logger().info(f"Silero VAD model loaded: {vad_model_path}")
                break
            except Exception as e:
                last_vad_error = e
                self.get_logger().warning(
                    f"Skip invalid VAD model at {vad_model_path}: {e}"
                )
        if self.vad_session is None:
            self.get_logger().error(f"Failed to load VAD model: {last_vad_error}")
            raise RuntimeError(f"Failed to load VAD model: {last_vad_error}")

        # 3. 初始化 STT 模型 (Faster-Whisper)
        # Prefer GPU for speed, fallback to CPU for robustness.
        try:
            self.stt_model = WhisperModel("base", device="cuda", compute_type="float16")
            self.get_logger().info("Faster-Whisper model loaded on CUDA (float16)")
        except Exception as e:
            self.get_logger().warning(
                f"CUDA STT init failed, fallback to CPU int8: {e}"
            )
            try:
                self.stt_model = WhisperModel("large", device="cpu", compute_type="int8")
                self.get_logger().info("Faster-Whisper model loaded on CPU (int8)")
            except Exception as e2:
                self.get_logger().error(f"Failed to load STT model on both CUDA and CPU: {e2}")
                raise
        self.zh_converter = None
        if OpenCC is not None:
            try:
                self.zh_converter = OpenCC("t2s")
                self.get_logger().info("OpenCC loaded (traditional->simplified)")
            except Exception as e:
                self.get_logger().warning(f"OpenCC init failed, skip zh conversion: {e}")
        else:
            self.get_logger().warning("OpenCC not installed, skip zh conversion")

        # STT: 仅接受 Whisper 自动检测为中文或英文的结果，避免噪声被强制 zh/en
        # 解码成乱码，或被模型判成日语等其它语言后仍输出。
        self.stt_min_language_probability = 0.35

        # 4. 配置 UDP 组播接收机器人音频
        self.MCAST_GRP = '239.168.123.161'
        self.MCAST_PORT = 5555
        self.MCAST_IFACE_IP = os.environ.get("G1_MCAST_IFACE_IP", "0.0.0.0")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.MCAST_PORT))
        # Linux x64 下 "4sl" 可能是 16 字节，IP_ADD_MEMBERSHIP 期望 8 字节，使用 "4s4s" 更稳妥
        mreq = struct.pack(
            "4s4s",
            socket.inet_aton(self.MCAST_GRP),
            socket.inet_aton(self.MCAST_IFACE_IP)
        )
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.sock.settimeout(1.0)

        # 5. 启动后台音频处理线程
        self.worker_thread = threading.Thread(target=self.audio_worker, daemon=True)
        self.worker_thread.start()
        self.get_logger().info(
            f"Ear node started, listening on {self.MCAST_GRP}:{self.MCAST_PORT} "
            f"(mono/{self.sample_rate}Hz/16bit, iface={self.MCAST_IFACE_IP})"
        )

    def _resolve_vad_model_paths(self):
        """Resolve VAD model candidates from install/share and source tree."""
        candidates = []
        try:
            share_dir = Path(get_package_share_directory("my_g1_audio"))
            candidates.append(share_dir / "silero_vad.onnx")
        except Exception:
            pass
        candidates.append(Path(__file__).with_name("silero_vad.onnx"))
        return [str(p) for p in candidates if p.exists()]

    @staticmethod
    def _last_positive_int(shape, default_value):
        """Get the last known positive int dim from ONNX shape."""
        if not isinstance(shape, (list, tuple)):
            return default_value
        for dim in reversed(shape):
            if isinstance(dim, int) and dim > 0:
                return dim
        return default_value

    def _init_vad_io_schema(self):
        """Detect VAD model input schema to support old and new Silero ONNX."""
        input_map = {inp.name: inp for inp in self.vad_session.get_inputs()}
        if "state" in input_map:
            self._vad_mode = "state"
            state_shape = input_map["state"].shape
            layers = state_shape[0] if isinstance(state_shape[0], int) and state_shape[0] > 0 else 2
            hidden = self._last_positive_int(state_shape, 128)
            self._vad_state_shape = (layers, 1, hidden)
        elif "h" in input_map and "c" in input_map:
            self._vad_mode = "hc"
            h_shape = input_map["h"].shape
            c_shape = input_map["c"].shape
            h_layers = h_shape[0] if isinstance(h_shape[0], int) and h_shape[0] > 0 else 2
            c_layers = c_shape[0] if isinstance(c_shape[0], int) and c_shape[0] > 0 else 2
            h_hidden = self._last_positive_int(h_shape, 64)
            c_hidden = self._last_positive_int(c_shape, 64)
            self._vad_h_shape = (h_layers, 1, h_hidden)
            self._vad_c_shape = (c_layers, 1, c_hidden)
        else:
            input_names = list(input_map.keys())
            raise RuntimeError(
                "Unsupported Silero VAD ONNX inputs: "
                f"{input_names}. Expected ['input', 'state', 'sr'] or ['input', 'sr', 'h', 'c']."
            )

    def reset_vad_state(self):
        """重置 RNN 模型内部状态"""
        if self._vad_mode == "state":
            self._state = np.zeros(self._vad_state_shape, dtype=np.float32)
        else:
            self._h = np.zeros(self._vad_h_shape, dtype=np.float32)
            self._c = np.zeros(self._vad_c_shape, dtype=np.float32)

    def process_vad(self, data_bytes):
        """
        将固定帧 PCM16LE 原始字节转为 VAD 概率
        """
        if len(data_bytes) != self.vad_frame_bytes:
            raise ValueError(f"Unexpected frame size: {len(data_bytes)} bytes")

        # 将 int16 转换为 float32 归一化数组
        audio_int16 = np.frombuffer(data_bytes, dtype=np.int16)
        audio_float32 = audio_int16.astype(np.float32) / 32768.0

        # 准备模型输入
        ort_inputs = {
            'input': audio_float32.reshape(1, -1),
            'sr': np.array(self.sample_rate, dtype=np.int64),
        }
        if self._vad_mode == "state":
            ort_inputs['state'] = self._state
        else:
            ort_inputs['h'] = self._h
            ort_inputs['c'] = self._c
        
        # 推理并更新状态
        outputs = self.vad_session.run(None, ort_inputs)
        if self._vad_mode == "state":
            if len(outputs) < 2:
                raise RuntimeError(f"Unexpected VAD output count for state mode: {len(outputs)}")
            out, next_state = outputs[0], outputs[1]
            self._state = next_state
        else:
            if len(outputs) < 3:
                raise RuntimeError(f"Unexpected VAD output count for h/c mode: {len(outputs)}")
            out, h, c = outputs[0], outputs[1], outputs[2]
            self._h, self._c = h, c
        return float(out[0][0])

    @staticmethod
    def _whisper_lang_is_zh_or_en(lang_code):
        if not lang_code:
            return False
        if lang_code == "en":
            return True
        # Whisper 中文一般为 "zh"
        return lang_code.startswith("zh")

    def stt_recognize(self, audio_bytes):
        """语音转文字"""
        try:
            audio_int16 = np.frombuffer(audio_bytes, dtype=np.int16)
            if audio_int16.size == 0:
                return "", 0.0, "unknown"
            audio_float32 = audio_int16.astype(np.float32) / 32768.0

            # 自动检测语言后只保留 zh/en；避免噪声在强制 zh/en 二选一下变成乱码，
            # 或被判成日语等语言后仍被当作有效指令输出。
            stt_begin_t = time.monotonic()
            segments, info = self.stt_model.transcribe(
                audio_float32,
                language=None,
                vad_filter=False,
            )
            segment_list = list(segments)
            text = "".join(s.text for s in segment_list).strip()

            detected_lang = getattr(info, "language", None) or "unknown"
            lang_prob = getattr(info, "language_probability", None)

            stt_ms = (time.monotonic() - stt_begin_t) * 1000.0

            if not text:
                return "", stt_ms, detected_lang

            if not self._whisper_lang_is_zh_or_en(detected_lang):
                self.get_logger().info(
                    f"STT dropped non zh/en (lang={detected_lang}, "
                    f"lang_prob={lang_prob}): {text[:120]!r}"
                )
                return "", stt_ms, detected_lang

            if (
                lang_prob is not None
                and lang_prob < self.stt_min_language_probability
            ):
                self.get_logger().info(
                    f"STT dropped low language confidence "
                    f"(lang={detected_lang}, lang_prob={lang_prob})"
                )
                return "", stt_ms, detected_lang

            if detected_lang.startswith("zh") and self.zh_converter is not None:
                text = self.zh_converter.convert(text)

            return text, stt_ms, detected_lang
        except Exception as e:
            self.get_logger().error(f"STT Error: {e}")
            return "", 0.0, "unknown"

    def audio_worker(self):
        """独立线程中的死循环"""
        pending_bytes = bytearray()
        speech_frames = []
        pre_roll_buffer = deque(maxlen=self.pre_speech_frames)
        is_speaking = False
        silence_count = 0
        speech_start_t = None
        last_speech_frame_t = None

        while rclpy.ok() and not self.stop_event.is_set():
            try:
                # 接收 G1 的降噪后 PCM16LE 数据 (mono / 16kHz / 16bit)
                data, _ = self.sock.recvfrom(8192)
                if not data:
                    continue

                pending_bytes.extend(data)
                while len(pending_bytes) >= self.vad_frame_bytes:
                    frame = bytes(pending_bytes[:self.vad_frame_bytes])
                    del pending_bytes[:self.vad_frame_bytes]

                    prob = self.process_vad(frame)

                    speech_prob_limit = self.vad_keep_prob_limit if is_speaking else self.vad_prob_limit
                    if prob > speech_prob_limit:
                        if not is_speaking:
                            is_speaking = True
                            # Prepend a short pre-roll so early syllables are not clipped.
                            speech_frames = list(pre_roll_buffer)
                            speech_start_t = time.monotonic()
                            self.get_logger().info("Voice detected")
                        speech_frames.append(frame)
                        last_speech_frame_t = time.monotonic()
                        silence_count = 0
                    else:
                        if is_speaking:
                            speech_frames.append(frame)
                            silence_count += 1

                            if silence_count > self.silence_threshold_frames:
                                is_speaking = False
                                if len(speech_frames) >= self.min_speech_frames:
                                    full_voice = b"".join(speech_frames)
                                    stt_request_t = time.monotonic()
                                    endpoint_ms = 0.0
                                    if last_speech_frame_t is not None:
                                        endpoint_ms = (stt_request_t - last_speech_frame_t) * 1000.0
                                    self.get_logger().info(
                                        f"Running STT... endpoint_ms={endpoint_ms:.1f}"
                                    )
                                    text, stt_ms, detected_lang = self.stt_recognize(full_voice)
                                    # Keep metric name e2e_ms, but define it as post-speech latency:
                                    # from the last speech frame to text publication readiness.
                                    e2e_ms = 0.0
                                    if last_speech_frame_t is not None:
                                        e2e_ms = (time.monotonic() - last_speech_frame_t) * 1000.0
                                    if text.strip():
                                        self.get_logger().info(
                                            f"Recognized(lang={detected_lang}): {text}"
                                        )
                                        msg = String()
                                        msg.data = text
                                        self.text_pub.publish(msg)
                                    self.get_logger().info(
                                        f"Latency: stt_ms={stt_ms:.1f}, "
                                        f"endpoint_ms={endpoint_ms:.1f}, e2e_ms={e2e_ms:.1f}"
                                    )
                                speech_frames = []
                                speech_start_t = None
                                last_speech_frame_t = None
                                self.reset_vad_state()
                        else:
                            pre_roll_buffer.append(frame)
            except socket.timeout:
                continue
            except OSError as e:
                if self.stop_event.is_set():
                    break
                self.get_logger().error(f"Socket error: {e}")
            except Exception as e:
                self.get_logger().error(f"Worker Loop Error: {e}")

    def destroy_node(self):
        self.stop_event.set()
        try:
            self.sock.close()
        except Exception:
            pass
        if hasattr(self, "worker_thread") and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    try:
        node = G1AudioBridge()
    except Exception:
        rclpy.shutdown()
        raise
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()