#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Int32
import requests
import json
from rclpy.qos import QoSProfile, ReliabilityPolicy
from langdetect import detect
import os
from datetime import datetime
import time
import subprocess
import threading

TTS_CLI_PATH = "/home/luolixin/unitree_ros2_ws/install/g1_tts_bridge/lib/g1_tts_bridge/g1_tts_cli"
NETWORK_INTERFACE = "eno2"
TTS_VOLUME = 100

class G1AIController(Node):
    def __init__(self):
        super().__init__('g1_ai_controller')
        self.is_speaking = False
        
        self.log_file_path = os.path.expanduser('~/g1_rag/conversation_log.jsonl')
        self.get_logger().info(f'The conversation log will be saved to: {self.log_file_path}')
        self.get_logger().info(f'The database query results will be saved to: /home/luolixin/g1_rag/neuro_search_history.txt')
        # --- 1. ROS 2 话题设置---

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT, # 关键！匹配机器人的发送模式
            depth=10
        )

        # 订阅用户输入
        self.input_sub = self.create_subscription(
            String,
            '/audio_msg', 
            self.asr_callback, 
            qos_profile) #可换成10
        
        

        self.get_logger().info('Connected to G1 hardware voice channel: /audio_msg')
        
        self.arm_pub = self.create_publisher(Int32, '/g1_arm_action_cmd', 10)
        self.rag_server_url = "http://127.0.0.1:5001/search"
        self.multiplier = 0.3 

        self.start_timer = self.create_timer(1.0, self.say_hello)

        #self.get_logger().info("G1 客户端已就绪，等待连接 RAG 大脑 (Port 5001)...")
        # ---------------------------------------------------------

    def say_hello(self):
        """开机问候语回调函数"""
        begin_text = "Hello! I'm Benben. Feel free to ask me questions."
        begin_text_cn = "大家好！我是笨笨。有什么问题尽管问我吧。"
        self.get_logger().info(f"🔊 Play startup greeting: {begin_text_cn}")       
        self.robot_speak(begin_text)

        self.start_timer.cancel()

    def asr_callback(self, msg):
        # ASR服务回调函数
        if self.is_speaking:
            return
        try:
            #msg.data 是一个 JSON 字符串
            data = json.loads(msg.data)
            

            text = data.get("text", "")
            raw_is_final = data.get("is_final", False)
        
            # 只要它"为真" (1, True, "true" 等)，就认为是结束了
            is_final_flag = False
            if isinstance(raw_is_final, bool):
                is_final_flag = raw_is_final
            elif isinstance(raw_is_final, int):
                is_final_flag = (raw_is_final == 1)
                
            
            if text:
                self.get_logger().info(f"Overheard voice: {text}")                
                ai_reply = self.call_ai_agent(text) # 调用 AI 代理，自动决策调用哪个工具                          
                self.get_logger().info(f"🧠Answer: {ai_reply}")

                self.robot_speak(ai_reply)
                self.log_conversation(text, ai_reply)
                
        except Exception as e:
            self.get_logger().error(f"解析语音消息失败: {e}")

    # ---------------------------------------------------------
    def call_rag_server(self, question):
        """
        通过 HTTP 请求 rag_server.py (运行在 venv 里)
        
        """
        payload = {"question": question}
        
        try:
            
            resp = requests.post(self.rag_server_url, json=payload, timeout=30)
            
            if resp.status_code == 200:
                # 服务端返回格式: {"answer": "..."}
                return resp.json().get("answer", "大脑返回了空内容")
            else:
                return f"大脑连接出错 (状态码 {resp.status_code})"
                
        except requests.exceptions.ConnectionError:
            return "连接失败，请检查 rag_server.py 是否已启动？"
        except Exception as e:
            return f"通信发生错误: {str(e)}"
    # ---------------------------------------------------------

    def call_ai_agent(self, user_prompt):
        """
        AI 代理核心函数：
        根据用户输入，自主选择调用 5000 端口（实验室知识）或 5001 端口（数据库查询）。
        """
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "ask_lab_assistant",
                    "description": "当与用户进行日常对话，或者提问实验室人员信息时，使用该工具进行回复",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string", "description": "转发给对话助手的具体问题"}
                        },
                        "required": ["question"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "normalize_neuro_query",
                    "description": "当用户想要查询神经科学数据库、查找特定脑区（如 MOp）或神经元数据时，使用此工具进行查询。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string", "description": "需要规范化的原始查询语句"}
                        },
                        "required": ["question"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_arm_action",
                    "description": "控制 G1 机器人手臂执行特定的物理预设动作。当用户要求执行手部动作、表达情感（比心等）、提出互动请求或要求机器人展示能力时使用。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action_id": {
                                "type": "integer",
                                "description": "动作 ID 映射表：\n"
                                   "1: 转身挥手, 11: 双手飞吻, 12: 左手飞吻, 13: 右手飞吻, "
                                   "15: 举起双手, 17: 夹取/钳制, 18: 击掌, 19: 拥抱, "
                                   "20: 双手比心, 21: 右手比心, 22: 拒绝/摇头, 23: 举起右手, "
                                   "24: 奥特曼射线, 25: 低手挥手(胸前), 26: 高手挥手(过头), "
                                   "27: 握手(shake hand), 28: 左手拳击获胜, 29: 右手拳击获胜, "
                                   "30: 双手拳击获胜, 33: 右手抚心, 34: 双手向右上方举起, "
                                   "36: 向前推"
                                   "99: 把手放下",
                                "enum": [1, 11, 12, 13, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 33, 34, 36, 99]
                            },
                            "action_name": {
                                "type": "string",
                                "description": "动作的中文描述。例如：'握手'、'飞吻'、'比心'。模型应根据 action_id 选择匹配的名称，用于语音回复。"
                            }
                        },
                        "required": ["action_id", "action_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "move_robot_logic",
                    "description": "控制 G1 机器人的物理状态和底盘运动。涵盖零力矩模式、阻尼模式、预备模式、运动模式及移动转向。当用户提出向前、向后、向左、向右及左转或右转时，需要根据指令计算执行时间",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "direction": {
                            "type": "string",
                            "enum": ["forward", "backward", "left_strafe", "right_strafe", "turn_left", "turn_right", "stand_up", "damp", "start"],
                            "description": "指令模式映射：\n"
                                   "damp: 阻尼模式。\n"
                                   "start: 运动模式。\n"
                                   "stand_up: 预备模式或者站立模式\n"
                                   "zero_torque: 零力矩模式。\n"
                                   "forward: 向前走。\n"
                                   "backward: 向后走。\n"
                                   "left_strafe: 向左走。\n"
                                   "right_strafe: 向右走。\n"
                                   "turn_left: 向左转。\n"
                                   "turn_right: 向右转。\n"
                            },
                        "duration": {
                            "type": "number",
                            "description": "计算出的执行时长。计算公式：距离除以0.2 或 弧度除以0.2。若未给出距离或者弧度，默认为2秒。"
                            },
                        "thought": {
                            "type": "string",
                            "description": "你的计算逻辑\n"
                            "'转身90度约1.57弧度，则duration为1.57除以0.2等于7.85秒。转身180度约3.14弧度，则duration等于3.14除以0.2为15.7秒\n"
                            "向前走10米，则duration=10除以0.2等于50秒"
                            }
                        },
                        "required": ["direction", "duration", "thought"]
                    }
                }
            }
        ]

        ollama_url = "http://127.0.0.1:11434/api/chat"

        payload = {
            "model": "qwen2.5:7b",
            "messages": [{"role": "user", "content": user_prompt}],
            "tools": tools,
            "stream": False,
            "keep_alive": -1 # 保持模型常驻
        }
        self.multiplier = 0.3
        try:
            self.get_logger().info("AI is making decisions...")
            resp = requests.post(ollama_url, json=payload, timeout=30).json()
            message = resp.get("message", {})

            # 2. 判断 AI 的选择
            if "tool_calls" in message:
                final_combined_answer = ""
                for tool_call in message["tool_calls"]:
                    func_name = tool_call["function"]["name"]
                    args = tool_call["function"]["arguments"]
                    # 兼容不同版本的 Ollama 输出格式
                    if isinstance(args, str):
                        args = json.loads(args)
                    
                    target_question = args.get('question', user_prompt)

                    # --- 分支 1: 调用 5000 端口的实验室助理 ---
                    if func_name == "ask_lab_assistant":
                        self.get_logger().info("Calling the 5000 port lab knowledge base...")
                        tool_start = time.time()
                        rag_res = requests.post("http://127.0.0.1:5000/ask", json={"question": target_question}, timeout=60).json()
                        self.get_logger().info(f"Tool response time: {time.time() - tool_start:.2f} 秒")
                        self.multiplier = 0.3
                        final_combined_answer += rag_res.get("answer", "")

                    # --- 分支 2: 调用 5001 端口的数据库查询规范化 ---
                    elif func_name == "normalize_neuro_query":
                        self.get_logger().info("Calling the neuroscience query engine on port 5001...")
                        
                        loading_text = "I'm checking right now. Please wait a moment."
                        self.robot_speak(loading_text)
                        self.get_logger().info("loading_text")
                        
                        search_res = requests.post("http://127.0.0.1:5001/search", 
                                                json={"question": target_question}, timeout=120).json()
                        final_combined_answer += f"The database query results have been generated for you,{search_res.get('answer', '')}"
                        self.multiplier = 0.085
                    # --- 分支 3: 执行机器人动作 ---
                    elif func_name == "execute_arm_action":
                        
                        action_id = args.get('action_id')
                        action_name = args.get('action_name', "执行动作")
    
                        self.get_logger().info(f"🤖 决策动作: {action_name} (ID: {action_id})")
    
                        # 1. 立即发布 ROS2 消息（不等待语音）
                        action_msg = Int32()
                        action_msg.data = int(action_id)
                        self.arm_pub.publish(action_msg)
    
                        # 2. 构造回复内容
                        response_text = f"动作{action_name}。"
                        final_combined_answer += response_text
                        return ""

                        # 3. (可选) 如果你想让机器人边做边说，可以立即调用语音
                        # self.robot_speak(response_text)
                        
                    elif func_name == "move_robot_logic":
                        direction = args.get('direction')
                        duration = args.get('duration', 1.0)
    
                        # 核心映射表：[vx, vy, omega]
                        # 全部固定为 0.2，大模型只决定 duration
                        V = 0.2
                        mapping = {
                            "forward":      [V, 0.0, 0.0],
                            "backward":     [-V, 0.0, 0.0],
                            "left_strafe":  [0.0, V, 0.0],
                            "right_strafe": [0.0, -V, 0.0],
                            "turn_left":    [0.0, 0.0, V],  # 转身是通过 omega 实现的
                            "turn_right":   [0.0, 0.0, -V]
                        }
    
                        if direction in ["stand_up", "damp", "start"]:
                            success, output = self.run_locomotion_cmd(direction, "")
                        elif direction in mapping:
                            vals = mapping[direction]
                            # 拼接成 SDK 最终需要的 4 参数格式: "vx vy omega duration"
                            param_str = f"{vals[0]} {vals[1]} {vals[2]} {duration}"
                            success, output = self.run_locomotion_cmd("set_velocity", param_str)
                        return ""

                return final_combined_answer if final_combined_answer else "The tool call returned an empty result."

            else:
                    return message.get("content", "I understand.")

        except Exception as e:
            self.get_logger().error(f"❌ AI agent execution error: {e}")
            return "Sorry, my brain processing chain has been interrupted."

    def robot_speak(self, text):
        self.is_speaking = True
        
        try:
            lang = detect(text)  # 'zh' / 'en' / 等
        except Exception:
            lang = 'zh-cn'  # 出错默认中文

        speaker_id = 0 if lang == 'zh-cn' else 1

        self.get_logger().info(
            f"Calling TtsMaker: speaker_id={speaker_id}, volume={TTS_VOLUME}, text={text}"
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
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                self.get_logger().info(
                    f"✅ TtsMaker completed: {result.stdout.strip()}"
                )
            else:
                self.get_logger().warn(
                    f"⚠️ TtsMaker failed (code {result.returncode}): {result.stderr.strip()}"
                )
        except subprocess.TimeoutExpired:
            self.get_logger().error("TtsMaker timeout")
        except Exception as e:
            self.get_logger().error(f"TtsMaker exception: {e}")
        finally:
            self.is_speaking = False
            self.get_logger().info("✅ Broadcast complete. Resuming monitoring.")

    def log_conversation(self, input_text, output_text):
        """将对话记录保存到 jsonl 文件"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "input": input_text,
            "output": output_text
        }
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
        except Exception as e:
            self.get_logger().error(f"保存日志失败: {e}")

    def run_locomotion_cmd(self, mode, params=""):
        """
        底层运控指令执行器
        :param mode: 动作模式 (damp, start, stand_up, set_velocity 等)
        :param params: 字符串参数，例如 "0.2 0.0 0.0 5.0"
        :return: (bool 成功与否, str 终端输出或错误信息)
        """
        # 1. 基础配置
        exe_path = "/home/luolixin/unitree_sdk2/build/bin/g1_loco_client"
        interface = "eno1" 
    
        # 2. 构造命令列表
        # 基础命令: [可执行文件路径, 网卡参数]
        cmd = [exe_path, f"--network_interface={interface}"]
    
        # 3. 处理参数逻辑
        if mode == "set_velocity":
            # 如果是速度指令，拼接为 --set_velocity=vx vy omega duration
            if not params:
                return False, "Error: set_velocity 模式必须提供参数"
            cmd.append(f"--set_velocity={params}")
        else:
            # 如果是 flag 指令，拼接为 --damp 或 --stand_up
            cmd.append(f"--{mode}")

        # 4. 执行子进程并捕获反馈
        try:
            self.get_logger().info(f"执行系统命令: {' '.join(cmd)}")
        
            # 使用 run 会阻塞直到动作完成
            # 设置 timeout 防止底层 SDK 挂死导致整个 ROS 节点卡住
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30.0  # 建议比你最大的 duration 稍微长一点
            )
        
            if result.returncode == 0:
                self.get_logger().info("✅ 底层指令执行成功")
                return True, result.stdout
            else:
                self.get_logger().error(f"❌ 底层报错: {result.stderr}")
                return False, result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "Error: 指令执行超时"
        except Exception as e:
            self.get_logger().error(f"系统调用异常: {e}")
            return False, str(e)

def main(args=None):
    print("NeuroXiv search tool started 🚀")
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