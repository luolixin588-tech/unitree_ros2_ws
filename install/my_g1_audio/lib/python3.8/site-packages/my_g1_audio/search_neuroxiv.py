#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import requests
import json
from unitree_api.msg import Request, Response
import random
from rclpy.qos import QoSProfile, ReliabilityPolicy
from langdetect import detect
import os
from datetime import datetime
import time

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
        
        # 发布 TTS 话题
        self.tts_pub = self.create_publisher(Request, '/api/voice/request', 10)

        # ---------------------------------------------------------
        # 配置 RAG 服务器地址，不再直接连 Ollama
        # ---------------------------------------------------------
        # self.ollama_url = "http://127.0.0.1:11434/api/generate"  
        # self.model = "qwen:7b"                                   
    
        self.rag_server_url = "http://127.0.0.1:5001/search"
        self.multiplier = 0.3 

        self.start_timer = self.create_timer(1.0, self.say_hello)

        #self.get_logger().info("G1 客户端已就绪，等待连接 RAG 大脑 (Port 5001)...")
        # ---------------------------------------------------------

    def say_hello(self):
        """开机问候语回调函数"""
        begin_text = "Hello! I'm Benben. Feel free to ask me questions."
        self.get_logger().info(f"🔊 Play startup greeting: {begin_text}")       
        self.robot_speak(begin_text)

        self.start_timer.cancel()

    def asr_callback(self, msg):
        # ASR服务回调函数
        if self.is_speaking:
            return
        try:
            #msg.data 是一个 JSON 字符串
            data = json.loads(msg.data)
            #self.get_logger().info(f"收到原始数据: {data}")

            text = data.get("text", "")
            raw_is_final = data.get("is_final", False)
        
            # 只要它"为真" (1, True, "true" 等)，就认为是结束了
            is_final_flag = False
            if isinstance(raw_is_final, bool):
                is_final_flag = raw_is_final
            elif isinstance(raw_is_final, int):
                is_final_flag = (raw_is_final == 1)
                
            # 只有当识别完成 (is_final) 且文字不为空时才处理
            if text:
                self.get_logger().info(f"Overheard voice: {text}")                
                ai_reply = self.call_ai_agent(text) # 调用 AI 代理，自动决策调用哪个工具                          
                self.get_logger().info(f"🧠Answer: {ai_reply}")
                #——————————————————————————————————————————————————

                #——————————————————————————————————————————————————

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
            }
        ]

        ollama_url = "http://127.0.0.1:11434/api/chat"
        # 使用 qwen2.5:7b，它的工具调用能力在本地模型中非常出色
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
                return final_combined_answer if final_combined_answer else "The tool call returned an empty result."

            else:
                # 如果 AI 觉得不需要调工具（比如只是闲聊），直接返回它的对话内容
                return message.get("content", "I understand.")

        except Exception as e:
            self.get_logger().error(f"❌ AI agent execution error: {e}")
            return "Sorry, my brain processing chain has been interrupted."

    def robot_speak(self, text):
        msg = Request()
        self.is_speaking = True
        
        try:
            lang = detect(text)  # 'zh' / 'en' / 等
        except:
            lang = 'zh-cn'  # 出错默认中文

        speaker_id = 0 if lang == 'zh-cn' else 1

        if lang == 'zh-cn':           
            self.multiplier = 0.3
            
        else:                  
            self.multiplier = 0.085
            

        # 设置身份信息：ID 0，API_ID 1001 是 G1 的语音服务代码
        msg.header.identity.id = random.getrandbits(32)
        msg.header.identity.api_id = 1001 
        
        #构造参数：必须是一个 JSON 格式的字符串
        voice_params = {
        "index": 0,
        "speaker_id": speaker_id,
        "text": text
        }

        msg.parameter = json.dumps(voice_params,ensure_ascii=False)
        
        self.tts_pub.publish(msg)
        self.get_logger().info(f"🎤Voice command sent to the robot: {msg.parameter}")

       # wait_time = len(text) * 0.3 + 0.5
        #self.timer = self.create_timer(wait_time, self.reset_speech_status)
        if hasattr(self, 'timer') and self.timer is not None:
            self.timer.cancel()
            self.timer = None

        wait_time = len(text) * self.multiplier + 1.0
        self.timer = self.create_timer(wait_time, self.reset_speech_status)

    def reset_speech_status(self):
        self.is_speaking = False
        self.get_logger().info("✅ Broadcast complete. Resuming monitoring.")

    # 只 cancel，不 destroy node
        if self.timer:
            self.timer.cancel()
            self.timer = None

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