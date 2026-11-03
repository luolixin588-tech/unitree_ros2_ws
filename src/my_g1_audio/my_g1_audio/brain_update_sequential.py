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
from dataclasses import dataclass
from typing import Any, Callable, Dict, List
from enum import Enum
import re

_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))


def _resolve_relative(*candidates):
    """Pick the first existing path relative to this file.

    ros2 run loads the installed copy under install/.../site-packages.
    Running the source file directly is rooted at src/my_g1_audio.
    """
    resolved = [
        os.path.normpath(os.path.join(_MODULE_DIR, *parts)) for parts in candidates
    ]
    for path in resolved:
        if os.path.exists(path):
            return path
    return resolved[0]


TTS_CLI_PATH = _resolve_relative(
    ("..", "..", "..", "..", "..", "..", "third_party", "prebuilt", "bin", "g1_tts_cli"),
    ("..", "..", "..", "third_party", "prebuilt", "bin", "g1_tts_cli"),
    ("..", "..", "..", "..", "..", "g1_tts_bridge", "lib", "g1_tts_bridge", "g1_tts_cli"),
    ("..", "..", "..", "install", "g1_tts_bridge", "lib", "g1_tts_bridge", "g1_tts_cli"),
)
NETWORK_INTERFACE = "eno1"
TTS_VOLUME = 100
STOP_KEYWORDS = ("停止", "停一下", "别说了", "闭嘴", "stop", "停下来","停")


class AgentState(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    CALLING_TOOL = "calling_tool"
    WAITING_TOOL_RESULT = "waiting_tool_result"
    EXECUTING_ROBOT = "executing_robot"
    RESPONDING = "responding"
    ERROR = "error"


@dataclass
class MCPToolSpec:
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable[[Dict[str, Any]], Any]


class MCPToolRegistry:
    """A lightweight MCP-style tool registry."""

    def __init__(self, logger):
        """
        功能:
            初始化工具注册中心。
        输入:
            logger: ROS2 logger 对象，用于输出工具注册/执行日志。
        输出:
            无（初始化内部工具字典）。
        """
        self._logger = logger
        self._tools: Dict[str, MCPToolSpec] = {}

    def register_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable[[Dict[str, Any]], Any],
    ) -> None:
        """
        功能:
            注册一个 MCP 风格工具定义及其执行函数。
        输入:
            name: 工具名称（唯一键）。
            description: 工具描述，供 LLM 决策使用。
            parameters: 工具参数 JSON Schema。
            handler: 工具执行函数，签名为 handler(args: dict)。
        输出:
            无（将工具写入注册表）。
        """
        self._tools[name] = MCPToolSpec(
            name=name,
            description=description,
            parameters=parameters,
            handler=handler,
        )
        self._logger.info(f"[Tool Registry] registered: {name}")

    def to_ollama_tools(self) -> List[Dict[str, Any]]:
        """
        功能:
            将已注册工具转换为 Ollama /api/chat 所需的 tools 格式。
        输入:
            无。
        输出:
            List[Dict[str, Any]]: 可直接放入请求 payload 的 tools 列表。
        """
        tools_payload = []
        for tool in self._tools.values():
            tools_payload.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters,
                    },
                }
            )
        return tools_payload

    def call_tool(self, name: str, args: Dict[str, Any]) -> Any:
        """
        功能:
            按名称执行已注册工具，并记录执行耗时日志。
        输入:
            name: 工具名称。
            args: 工具参数字典。
        输出:
            Any: 工具 handler 的原始返回值。
        """
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' is not registered")

        start_t = time.time()
        self._logger.info(f"[Tool Call] {name} args={args}")
        result = self._tools[name].handler(args)
        cost_s = time.time() - start_t
        
        self._logger.info(f"[Tool Done] {name} took {cost_s:.3f}s")
        return result

    def get_tool_specs(self) -> List[MCPToolSpec]:
        """
        功能:
            返回当前注册表中的全部工具规格，用于构建规划器可见工具目录。
        输入:
            无。
        输出:
            List[MCPToolSpec]: 工具规格列表。
        """
        return list(self._tools.values())


class PlannerEngine:
    """Independent LLM planner layer (above tools)."""

    def __init__(self, logger, ollama_url: str, model: str, planner_prompt: str, max_attempts: int = 3):
        self._logger = logger
        self._ollama_url = ollama_url
        self._model = model
        self._planner_prompt = planner_prompt
        self._max_attempts = max_attempts

    @staticmethod
    def _extract_first_json_object(text: str):
        if not text:
            return None
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        return text[start : end + 1]

    def plan(
        self,
        user_prompt: str,
        tool_catalog: List[Dict[str, Any]],
        planner_json_schema: Dict[str, Any],
        plan_validator: Callable[[Any], Any] = None,
    ):
        """
        功能:
            使用独立规划 LLM 生成结构化步骤计划。
        输入:
            user_prompt: str,用户请求。
            tool_catalog: List[Dict[str, Any]],工具目录（name/description/parameters）。
            planner_json_schema: Dict[str, Any],规划输出 schema 约束。
        输出:
            Dict[str, Any]: 标准返回 {"status","data","error"}，成功时 data 包含 steps。
        """
        planner_feedback = ""
        last_raw_output = ""
        last_error = "unknown planner error"
        tool_catalog_json = json.dumps(tool_catalog, ensure_ascii=False)

        for attempt in range(1, self._max_attempts + 1):
            try:
                messages = [
                    {"role": "system", "content": self._planner_prompt},
                    {
                        "role": "system",
                        "content": (
                            "下面是当前可用工具目录（name/description/parameters）。"
                            "你只能从这里选择工具名，并严格按参数 schema 填参：\n"
                            f"{tool_catalog_json}"
                        ),
                    },
                ]
                if planner_feedback:
                    messages.append(
                        {
                            "role": "system",
                            "content": (
                                "上一次规划不合法，请严格修正后重试。"
                                f"错误原因: {planner_feedback}"
                            ),
                        }
                    )
                messages.append({"role": "user", "content": user_prompt})

                payload = {
                    "model": self._model,
                    "messages": messages,
                    "format": planner_json_schema,
                    "stream": False,
                    "keep_alive": -1,
                    "options": {"temperature": 0},
                }
                resp = requests.post(self._ollama_url, json=payload, timeout=30)
                resp.raise_for_status()
                content = (resp.json().get("message", {}).get("content") or "").strip()
                last_raw_output = content

                parsed = None
                try:
                    parsed = json.loads(content)
                except Exception:
                    maybe_json = self._extract_first_json_object(content)
                    if maybe_json:
                        parsed = json.loads(maybe_json)

                if not isinstance(parsed, dict):
                    last_error = "planner output is not valid JSON object"
                    planner_feedback = last_error
                    continue

                steps = parsed.get("steps")
                if plan_validator is not None:
                    valid, err = plan_validator(steps)
                    if not valid:
                        last_error = f"invalid plan steps: {err}"
                        planner_feedback = last_error
                        self._logger.warn(
                            f"[PlannerEngine] attempt {attempt}/{self._max_attempts} invalid: {err}"
                        )
                        continue

                return {
                    "status": "ok",
                    "data": {"steps": steps},
                    "error": None,
                }
            except Exception as e:
                last_error = f"planner request failed: {e}"
                planner_feedback = last_error
                self._logger.warn(
                    f"[PlannerEngine] attempt {attempt}/{self._max_attempts} exception: {e}"
                )

        return {
            "status": "error",
            "data": {"raw_planner_output": last_raw_output},
            "error": last_error,
        }


class G1AIController(Node):
    def __init__(self):
        """
        功能:
            初始化 G1 AI 控制节点，包括语音输入订阅、动作发布、Agent 配置和工具注册。
        输入:
            无（ROS2 Node 初始化参数由 rclpy 处理）。
        输出:
            无（完成节点资源初始化）。
        """
        super().__init__('g1_ai_controller')
        self.is_speaking = False
        self.active_tts_process = None
        self.tts_lock = threading.Lock()
        self.arm_action_wait_s = 10.0
        self.locomotion_wait_s = 5.0
        
        self.log_file_path = os.path.expanduser('~/g1_rag/conversation_log.jsonl')
        self.plan_log_file_path = os.path.expanduser('~/g1_rag/agent_plan_log.jsonl')
        self.get_logger().info(f'The conversation log will be saved to: {self.log_file_path}')
        self.get_logger().info(f'The plan trace log will be saved to: {self.plan_log_file_path}')
        self.get_logger().info(
            "The database query results will be saved to: "
            + os.path.expanduser("~/g1_rag/neuro_search_history.txt")
        )
        # --- 1. ROS 2 话题设置---

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT, # 关键！匹配机器人的发送模式
            depth=10
        )

        # 订阅用户输入（来自 audio_bridge_node 的纯文本识别结果）
        self.input_sub = self.create_subscription(
            String,
            '/g1/voice_text',
            self.asr_callback, 
            qos_profile) #可换成10
        
        

        self.get_logger().info('Connected voice channel: /g1/voice_text')
        
        self.arm_pub = self.create_publisher(Int32, '/g1_arm_action_cmd', 10)
        self.rag_server_url = "http://127.0.0.1:5001/search"
        self.multiplier = 0.3 
        self.max_tool_iterations = 5
        self.ollama_url = "http://127.0.0.1:11434/api/chat"
        self.ollama_model = "qwen2.5:14b"
        self.agent_system_prompt = (
            "你是机器人“笨笨”的机载语音助手，运行在真实机器人上。"
            "回答必须是可直接播报的纯文本，不要输出 Markdown、链接、图片、代码块。"
            "禁止使用“模拟动作”“示意图”“如图所示”等措辞。"
            "当用户既要求对话内容又要求动作（例如‘先介绍自己再握手’）时："
            "先给简短自然语言回复，再调用对应动作工具，最后给一句简短确认。"
            "身份介绍时请说你是机器人笨笨"
            "回复风格：简洁、口语化、中文优先。"
        )
        self.planner_tool_enum = [
            "ask_lab_assistant",
            "normalize_neuro_query",
            "execute_arm_action",
            "move_robot_logic",
        ]
        self.planner_direction_enum = [
            "forward",
            "backward",
            "left_strafe",
            "right_strafe",
            "turn_left",
            "turn_right",
            "stand_up",
            "damp",
            "start",
        ]
        self.planner_action_id_enum = [
            11, 12, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 99
        ]
        self.agent_planner_prompt = (
            "你是机器人任务规划器。你的唯一任务是输出严格 JSON 计划。"
            "JSON 顶层只有一个字段: steps。"
            "steps 是数组，每个元素只能是以下二选一结构："
            "1) speak 步骤: {\"type\":\"speak\",\"content\":\"<要播报的中文文本>\"}。"
            "2) tool 步骤: {\"type\":\"tool\",\"name\":\"<工具名>\",\"args\":{...}}。"
            "name 只能取: ask_lab_assistant / normalize_neuro_query / execute_arm_action / move_robot_logic。"
            "args 约束："
            "ask_lab_assistant.args={\"question\":string};"
            "normalize_neuro_query.args={\"question\":string};"
            "execute_arm_action.args 必须包含 action_id(int, 枚举) 与 action_name(string);"
            "move_robot_logic.args 必须包含 direction(枚举)；duration 可选且为 number。"
            "如果用户有“先/再/然后/最后”顺序语义，steps 必须按该顺序排列。"
            "用户要求问候或自我介绍时，优先先输出 speak 步骤；自称必须为“机器人笨笨”。"
            "当用户意图是挥手/招手/打招呼时，必须调用 execute_arm_action，"
            "并优先使用 action_id=25(胸前挥手) 或 26(高举挥手)。"
            "除非用户明确要求移动（前进/后退/左移/右移/转向），否则禁止使用 move_robot_logic。"
            "禁止输出 markdown、注释、解释文字、代码块。除 JSON 外不能有任何额外文本。"
            "当用户要求做危险动作时，输出 speak 步骤，告知用户危险，并拒绝执行。"
            "当用户要求做系统不具备的能力时，输出 speak 步骤，告知用户系统不具备该能力，并拒绝执行。"
            "当用户要求做不道德或触及隐私的行为时，输出 speak 步骤，告知用户不道德，并拒绝执行。"
        )
        self.planner_json_schema = {
            "type": "object",
            "additionalProperties": False,
            "required": ["steps"],
            "properties": {
                "steps": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 6,
                    "items": {
                        "oneOf": [
                            {
                                "type": "object",
                                "additionalProperties": False,
                                "required": ["type", "content"],
                                "properties": {
                                    "type": {"type": "string", "enum": ["speak"]},
                                    "content": {"type": "string", "minLength": 1},
                                },
                            },
                            {
                                "type": "object",
                                "additionalProperties": False,
                                "required": ["type", "name", "args"],
                                "properties": {
                                    "type": {"type": "string", "enum": ["tool"]},
                                    "name": {"type": "string", "enum": self.planner_tool_enum},
                                    "args": {
                                        "type": "object",
                                        "additionalProperties": True,
                                        "properties": {
                                            "question": {"type": "string"},
                                            "action_id": {"type": "integer", "enum": self.planner_action_id_enum},
                                            "action_name": {"type": "string"},
                                            "direction": {"type": "string", "enum": self.planner_direction_enum},
                                            "duration": {"type": "number"},
                                        },
                                    },
                                },
                            },
                        ]
                    },
                }
            },
        }
        self.tool_registry = self._build_tool_registry()
        self.planner = PlannerEngine(
            logger=self.get_logger(),
            ollama_url=self.ollama_url,
            model=self.ollama_model,
            planner_prompt=self.agent_planner_prompt,
            max_attempts=3,
        )
        self.agent_state = AgentState.IDLE

        self.start_timer = self.create_timer(1.0, self.say_hello)

        #self.get_logger().info("G1 客户端已就绪，等待连接 RAG 大脑 (Port 5001)...")
        # ---------------------------------------------------------

    def say_hello(self):
        """
        功能:
            在节点启动后播放一次开机问候语。
        输入:
            无（由定时器触发）。
        输出:
            无（触发 TTS 播放并取消定时器）。
        """
        #begin_text = "Hello! I'm Benben. Feel free to ask me questions."
        begin_text = "Hello"
        begin_text_cn = "大家好！我是笨笨。有什么问题尽管问我吧。"
        self.get_logger().info(f"🔊 Play startup greeting: {begin_text_cn}")       
        self.robot_speak(begin_text)

        self.start_timer.cancel()

    def asr_callback(self, msg):
        """
        功能:
            处理 ASR 文本输入，执行打断逻辑、调用 AI Agent、播报回答并写入对话日志。
        输入:
            msg: std_msgs.msg.String，来自 /g1/voice_text 的识别文本。
        输出:
            无（可能触发 stop_speaking、call_ai_agent、robot_speak 和日志记录）。
        """
        # ASR服务回调函数
        try:
            # /g1/voice_text 的消息是纯文本，默认视为 final。
            text = msg.data.strip()
            is_final_flag = True
                
            
            if text:
                normalized_text = text.strip().lower()
                # 停止词最高优先级：不经过 AI，直接尝试打断当前播报。
                if is_final_flag and any(k in normalized_text for k in STOP_KEYWORDS):
                    self.get_logger().warn("🛑 Stop keyword detected, interrupting TTS directly.")
                    self.stop_speaking()
                    # 对“本地进程已退出但机器人仍在播报”的场景，先强制静音一拍。
                    self._force_mute_tts_output()
                    return

                # 说话期间默认屏蔽输入，仅在 final 且命中停止关键词时中断播报。
                with self.tts_lock:
                    speaking_now = self.is_speaking

                if speaking_now:
                    # 非停止指令在播报期间直接忽略，避免自激和抢话。
                    return

                self.get_logger().info(f"Overheard voice: {text}")                
                ai_reply = self.call_ai_agent(text) # 调用 AI 代理，自动决策调用哪个工具                          
                self.get_logger().info(f"🧠Answer: {ai_reply}")
                if ai_reply and ai_reply.strip():
                    self.robot_speak(ai_reply)
                self.log_conversation(text, ai_reply)
                
        except Exception as e:
            self.get_logger().error(f"解析语音消息失败: {e}")

    # ---------------------------------------------------------
    def call_rag_server(self, question):
        """
        功能:
            通过 HTTP 调用 RAG 服务（5001）获取问答结果（保留兼容方法）。
        输入:
            question: str，用户问题。
        输出:
            str: RAG 返回答案或错误描述文本。
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

    def _set_agent_state(self, new_state: AgentState, reason: str = ""):
        """
        功能:
            更新 Agent 当前状态，并记录状态迁移日志。
        输入:
            new_state: AgentState，新状态。
            reason: str，可选状态切换原因说明。
        输出:
            无（更新 self.agent_state）。
        """
        if self.agent_state == new_state:
            return
        old_state = self.agent_state
        self.agent_state = new_state
        if reason:
            self.get_logger().info(
                f"[Agent State] {old_state.value} -> {new_state.value} ({reason})"
            )
        else:
            self.get_logger().info(
                f"[Agent State] {old_state.value} -> {new_state.value}"
            )

    @staticmethod
    def _tool_result(status: str, data: Any = None, error: Any = None):
        """
        功能:
            构造统一的工具返回结构。
        输入:
            status: str，通常为 "ok" 或 "error"。
            data: Any，工具业务结果数据。
            error: Any，错误信息（无错误时为 None）。
        输出:
            Dict[str, Any]: {"status", "data", "error"}。
        """
        return {
            "status": status,
            "data": data,
            "error": error,
        }

    def _normalize_tool_result(self, tool_name: str, raw_result: Any):
        """
        功能:
            将工具原始返回值标准化为 {"status","data","error"} 结构。
        输入:
            tool_name: str，工具名称（用于日志）。
            raw_result: Any，工具原始返回值（dict/str/其他）。
        输出:
            Dict[str, Any]: 标准化后的工具结果。
        """
        if isinstance(raw_result, dict):
            if {"status", "data", "error"}.issubset(raw_result.keys()):
                normalized = {
                    "status": str(raw_result.get("status", "error")),
                    "data": raw_result.get("data"),
                    "error": raw_result.get("error"),
                }
            else:
                normalized = self._tool_result(
                    "error" if raw_result.get("error") else "ok",
                    data=raw_result,
                    error=raw_result.get("error"),
                )
        elif isinstance(raw_result, str):
            normalized = self._tool_result("ok", data={"message": raw_result}, error=None)
        else:
            normalized = self._tool_result("ok", data=raw_result, error=None)

        self.get_logger().info(
            f"[Tool Result] {tool_name} status={normalized['status']} error={normalized['error']}"
        )
        return normalized

    @staticmethod
    def _sanitize_ai_reply(text: str) -> str:
        """
        功能:
            清理模型输出中的 markdown/链接等不适合 TTS 的内容。
        输入:
            text: str，模型原始回复。
        输出:
            str: 适合直接播报的纯文本。
        """
        if not text:
            return ""
        cleaned = text
        # 移除 markdown 图片/链接
        cleaned = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", cleaned)
        cleaned = re.sub(r"\[[^\]]+\]\([^)]+\)", "", cleaned)
        # 移除裸 URL
        cleaned = re.sub(r"https?://\S+", "", cleaned)
        # 移除代码块与反引号
        cleaned = cleaned.replace("```", " ").replace("`", "")
        # 折叠多余空白
        cleaned = re.sub(r"\n{2,}", "\n", cleaned)
        cleaned = re.sub(r"[ \t]{2,}", " ", cleaned).strip()
        return cleaned

    @staticmethod
    def _extract_first_json_object(text: str):
        """
        功能:
            从文本中提取第一个 JSON 对象字符串（用于容错解析）。
        输入:
            text: str，原始文本。
        输出:
            Optional[str]: 提取到的 JSON 字符串；失败返回 None。
        """
        if not text:
            return None
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        return text[start : end + 1]

    def _build_tool_registry(self):
        """
        功能:
            创建并注册系统所有可供 LLM 调用的工具定义与处理函数。
        输入:
            无。
        输出:
            MCPToolRegistry: 完成注册的工具中心实例。
        """
        registry = MCPToolRegistry(self.get_logger())

        registry.register_tool(
            name="ask_lab_assistant",
            description="当与用户进行日常对话，或者提问实验室人员信息时，使用该工具进行回复",
            parameters={
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "转发给对话助手的具体问题"}
                },
                "required": ["question"],
            },
            handler=self._tool_ask_lab_assistant,
        )

        registry.register_tool(
            name="normalize_neuro_query",
            description="当用户想要查询神经科学数据库、查找特定脑区（如 MOp）或神经元数据时，使用此工具进行查询。",
            parameters={
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "需要规范化的原始查询语句"}
                },
                "required": ["question"],
            },
            handler=self._tool_normalize_neuro_query,
        )

        registry.register_tool(
            name="execute_arm_action",
            description="控制 G1 机器人手臂执行特定的物理预设动作。当用户要求执行手部动作、表达情感（比心等）、提出互动请求或要求机器人展示能力时使用。",
            parameters={
                "type": "object",
                "properties": {
                    "action_id": {
                        "type": "integer",
                        "description": "动作 ID 映射表：\n"
                        "99: 恢复初始手臂位姿, 11: 双手飞吻, 12: 单手飞吻, "
                        "15: 平举, 17: 鼓掌, 18: 击掌, 19: 拥抱, "
                        "20: 双手比心, 21: 右手比心, 22: 双手打X, 23: 右手平举, "
                        "24: 动感光波, 25: 胸前挥手, 26: 高举挥手, 27: 握手",
                        "enum": [11, 12, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 99],
                    },
                    "action_name": {
                        "type": "string",
                        "description": "动作的中文描述。例如：'握手'、'飞吻'、'比心'。模型应根据 action_id 选择匹配的名称，用于语音回复。",
                    },
                },
                "required": ["action_id", "action_name"],
            },
            handler=self._tool_execute_arm_action,
        )

        registry.register_tool(
            name="move_robot_logic",
            description="控制 G1 机器人的物理状态和底盘运动。涵盖零力矩模式、阻尼模式、预备模式、运动模式及移动转向。当用户提出向前、向后、向左、向右及左转或右转时，需要根据指令计算执行时间",
            parameters={
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
                        "turn_right: 向右转。\n",
                    },
                    "duration": {
                        "type": "number",
                        "description": "计算出的执行时长。计算公式：距离除以0.2 或 弧度除以0.2。若未给出距离或者弧度，默认为2秒。",
                    },
                    "thought": {
                        "type": "string",
                        "description": "你的计算逻辑\n"
                        "'转身90度约1.57弧度，则duration为1.57除以0.2等于7.85秒。转身180度约3.14弧度，则duration等于3.14除以0.2为15.7秒\n"
                        "向前走10米，则duration=10除以0.2等于50秒",
                    },
                },
                "required": ["direction", "duration", "thought"],
            },
            handler=self._tool_move_robot_logic,
        )
        return registry

    def _build_planner_tool_catalog(self):
        """
        功能:
            从工具注册表导出规划器可见工具目录（name/description/parameters）。
        输入:
            无。
        输出:
            List[Dict[str, Any]]: 规划器工具目录。
        """
        catalog = []
        for spec in self.tool_registry.get_tool_specs():
            catalog.append(
                {
                    "name": spec.name,
                    "description": spec.description,
                    "parameters": spec.parameters,
                }
            )
        return catalog

    def _parse_tool_arguments(self, raw_args):
        """
        功能:
            兼容解析 Ollama 工具参数（dict 或 JSON 字符串）。
        输入:
            raw_args: Any，模型输出的 function.arguments。
        输出:
            Dict[str, Any]: 解析后的参数字典；异常时返回兜底字典。
        """
        if isinstance(raw_args, dict):
            return raw_args
        if isinstance(raw_args, str):
            text = raw_args.strip()
            if not text:
                return {}
            try:
                return json.loads(text)
            except json.JSONDecodeError as e:
                self.get_logger().warn(f"[Tool Args] JSON parse failed, fallback to raw string: {e}")
                return {"raw_input": raw_args}
        self.get_logger().warn(f"[Tool Args] Unsupported argument type: {type(raw_args)}")
        return {}

    def _ask_lab_assistant_api(self, question):
        """
        功能:
            调用 5000 端口实验室问答服务。
        输入:
            question: str，问题文本。
        输出:
            Dict[str, Any]: 服务返回 JSON；失败时包含 error 字段。
        """
        try:
            resp = requests.post(
                "http://127.0.0.1:5000/ask",
                json={"question": question},
                timeout=60,
            )
            if resp.status_code != 200:
                return {"error": f"5000 service error status={resp.status_code}"}
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def _validate_plan_steps(self, steps):
        """
        功能:
            校验规划步骤结构合法性与安全边界。
        输入:
            steps: Any，规划器输出的 steps。
        输出:
            Tuple[bool, str]: (是否合法, 错误信息)。
        """
        if not isinstance(steps, list):
            return False, "steps must be a list"
        if len(steps) == 0:
            return False, "steps is empty"
        if len(steps) > 6:
            return False, "steps exceeds max length 6"
        allowed_tools = {
            "ask_lab_assistant",
            "normalize_neuro_query",
            "execute_arm_action",
            "move_robot_logic",
        }
        for idx, step in enumerate(steps):
            if not isinstance(step, dict):
                return False, f"step[{idx}] is not object"
            step_type = step.get("type")
            if step_type == "speak":
                content = str(step.get("content", "")).strip()
                if not content:
                    return False, f"step[{idx}] speak.content is empty"
            elif step_type == "tool":
                name = step.get("name")
                if name not in allowed_tools:
                    return False, f"step[{idx}] unsupported tool: {name}"
                tool_args = step.get("args", {})
                if not isinstance(tool_args, dict):
                    return False, f"step[{idx}] tool.args must be object"
                ok, msg = self._validate_tool_args(name, tool_args)
                if not ok:
                    return False, f"step[{idx}] {msg}"
            else:
                return False, f"step[{idx}] invalid type: {step_type}"
        return True, ""

    def _validate_tool_args(self, tool_name, tool_args):
        """
        功能:
            校验单个工具参数是否满足执行器的强约束。
        输入:
            tool_name: str，工具名。
            tool_args: Dict[str, Any]，工具参数。
        输出:
            Tuple[bool, str]: (是否合法, 错误信息)。
        """
        if tool_name in {"ask_lab_assistant", "normalize_neuro_query"}:
            question = tool_args.get("question")
            if not isinstance(question, str) or not question.strip():
                return False, f"{tool_name}.args.question must be non-empty string"
            return True, ""

        if tool_name == "execute_arm_action":
            if "action_id" not in tool_args:
                return False, "execute_arm_action.args.action_id is required"
            if "action_name" not in tool_args:
                return False, "execute_arm_action.args.action_name is required"
            try:
                action_id = int(tool_args.get("action_id"))
            except Exception:
                return False, "execute_arm_action.args.action_id must be integer"
            valid_ids = {11, 12, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 99}
            if action_id not in valid_ids:
                return False, f"execute_arm_action.args.action_id not in allowed ids: {action_id}"
            action_name = tool_args.get("action_name")
            if not isinstance(action_name, str) or not action_name.strip():
                return False, "execute_arm_action.args.action_name must be non-empty string"
            return True, ""

        if tool_name == "move_robot_logic":
            direction = tool_args.get("direction")
            allowed_dirs = {
                "forward", "backward", "left_strafe", "right_strafe",
                "turn_left", "turn_right", "stand_up", "damp", "start"
            }
            if direction not in allowed_dirs:
                return False, f"move_robot_logic.args.direction invalid: {direction}"
            if "duration" in tool_args:
                try:
                    float(tool_args.get("duration"))
                except Exception:
                    return False, "move_robot_logic.args.duration must be number when provided"
            return True, ""

        return False, f"unknown tool: {tool_name}"

    def _wait_until_tts_idle(self, timeout_s=12.0, poll_s=0.05):
        """
        功能:
            等待当前 TTS 播报完成（用于按步骤串行执行 speak -> tool）。
        输入:
            timeout_s: float，最长等待时间。
            poll_s: float，轮询间隔。
        输出:
            bool: True 表示检测到空闲；False 表示超时。
        """
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            with self.tts_lock:
                speaking_now = self.is_speaking
            if not speaking_now:
                return True
            time.sleep(poll_s)
        return False

    def _wait_for_physical_completion(self, tool_name, tool_args):
        try:
            if tool_name == "execute_arm_action":
                wait_s = self.arm_action_wait_s
            elif tool_name == "move_robot_logic":
                wait_s = self.locomotion_wait_s
            else:
                return True, ""

            self.get_logger().info(
                f"[Execution Barrier] waiting {wait_s:.1f}s for {tool_name}"
            )

            time.sleep(wait_s)

            self.get_logger().info(
                f"[Execution Barrier] completed wait for {tool_name}"
            )

            return True, ""

        except Exception as e:
            return False, f"physical execution wait failed: {e}"

    def _execute_plan_steps(self, steps):
        """
        功能:
            按顺序执行规划步骤；支持 speak 与 tool 两种步骤。
        输入:
            steps: List[Dict[str, Any]]，已校验的步骤列表。
        输出:
            Dict[str, Any]: 标准工具结果，data 含执行明细和 final_text。
        """
        valid, err = self._validate_plan_steps(steps)
        if not valid:
            return self._tool_result("error", data={"steps": steps}, error=err)

        step_results = []
        had_speak = False
        tool_answers = []
        last_qa_tool_idx = -1
        speak_after_qa_tool = False
        qa_tools = {"ask_lab_assistant", "normalize_neuro_query"}

        for idx, step in enumerate(steps):
            step_type = step.get("type")
            if step_type == "speak":
                content = self._sanitize_ai_reply(str(step.get("content", "")).strip())
                if not content:
                    continue
                if last_qa_tool_idx >= 0 and idx > last_qa_tool_idx:
                    speak_after_qa_tool = True
                had_speak = True
                self._set_agent_state(AgentState.RESPONDING, f"executing speak step {idx + 1}")
                self.robot_speak(content)
                self._wait_until_tts_idle(timeout_s=12.0)
                step_results.append({"step": idx + 1, "type": "speak", "content": content, "status": "ok"})
                continue

            tool_name = step.get("name")
            tool_args = step.get("args", {})
            if tool_name in {"execute_arm_action", "move_robot_logic"}:
                self._set_agent_state(AgentState.EXECUTING_ROBOT, f"executing robot tool {tool_name}")
            else:
                self._set_agent_state(AgentState.WAITING_TOOL_RESULT, f"waiting for {tool_name}")

            try:
                raw_tool_result = self.tool_registry.call_tool(tool_name, tool_args)
            except Exception as tool_err:
                raw_tool_result = self._tool_result(
                    "error",
                    data={"tool_name": tool_name, "args": tool_args},
                    error=str(tool_err),
                )
                self.get_logger().error(f"[Plan Exec] {tool_name} failed: {tool_err}")

            tool_result = self._normalize_tool_result(tool_name, raw_tool_result)
            step_results.append(
                {
                    "step": idx + 1,
                    "type": "tool",
                    "name": tool_name,
                    "status": tool_result.get("status"),
                    "error": tool_result.get("error"),
                }
            )
            if tool_result.get("status") != "ok":
                return self._tool_result("error", data={"step_results": step_results}, error=tool_result.get("error"))

            if tool_name in {"execute_arm_action", "move_robot_logic"}:
                completed, completion_error = self._wait_for_physical_completion(
                    tool_name,
                    tool_args,
                )

                if not completed:
                    return self._tool_result(
                        "error",
                        data={"step_results": step_results},
                        error=completion_error,
                    )

            if tool_name in qa_tools:
                last_qa_tool_idx = idx
                answer = str((tool_result.get("data") or {}).get("answer", "")).strip()
                if answer:
                    tool_answers.append(answer)

            self._set_agent_state(AgentState.THINKING, f"plan tool {tool_name} executed")

        # 问答/检索工具已有 answer，且其后没有 speak 来播报结果时，补播工具答案。
        # - 无 speak：写入 final_text，由 asr_callback 播报。
        # - 仅有前置 speak（如“请稍候”）：执行器内直接 robot_speak，避免 had_speak 挡住 final_text。
        final_text = ""
        if tool_answers and not speak_after_qa_tool:
            answer_text = self._sanitize_ai_reply(tool_answers[-1])
            if answer_text:
                if had_speak:
                    self._set_agent_state(AgentState.RESPONDING, "broadcasting tool answer")
                    self.robot_speak(answer_text)
                    self._wait_until_tts_idle(timeout_s=12.0)
                else:
                    final_text = answer_text

        return self._tool_result(
            "ok",
            data={
                "step_results": step_results,
                "final_text": final_text,
            },
            error=None,
        )

    def _normalize_neuro_query_api(self, question):
        """
        功能:
            调用 5001 端口神经科学检索服务。
        输入:
            question: str，检索问题文本。
        输出:
            Dict[str, Any]: 服务返回 JSON；失败时包含 error 字段。
        """
        try:
            resp = requests.post(
                "http://127.0.0.1:5001/search",
                json={"question": question},
                timeout=120,
            )
            if resp.status_code != 200:
                return {"error": f"5001 service error status={resp.status_code}"}
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def _tool_ask_lab_assistant(self, args):
        """
        功能:
            MCP 工具：调用实验室知识问答服务并标准化结果。
        输入:
            args: Dict[str, Any]，需包含 question。
        输出:
            Dict[str, Any]: 标准工具结果 {"status","data","error"}。
        """
        question = str(args.get("question", "")).strip()
        if not question:
            return self._tool_result("error", data=None, error="missing required argument: question")
        result = self._ask_lab_assistant_api(question)
        self.multiplier = 0.3
        if result.get("error"):
            return self._tool_result("error", data=result, error=result.get("error"))
        answer = str(result.get("answer", "")).strip()
        self.get_logger().info(f"[RAG] question={question}")
        self.get_logger().info(f"[RAG] answer={answer}")
        return self._tool_result("ok", data={"answer": answer}, error=None)

    def _tool_normalize_neuro_query(self, args):
        """
        功能:
            MCP 工具：调用神经科学数据库检索，并在检索前播报等待提示。
        输入:
            args: Dict[str, Any]，需包含 question。
        输出:
            Dict[str, Any]: 标准工具结果 {"status","data","error"}。
        """
        question = str(args.get("question", "")).strip()
        if not question:
            return self._tool_result("error", data=None, error="missing required argument: question")

        loading_text = "I'm checking right now. Please wait a moment."
        self.robot_speak(loading_text)
        self.get_logger().info("[Tool] normalize_neuro_query loading text sent")

        result = self._normalize_neuro_query_api(question)
        self.multiplier = 0.085
        if result.get("error"):
            return self._tool_result("error", data=result, error=result.get("error"))
        return self._tool_result("ok", data={"answer": result.get("answer", "")}, error=None)

    def _tool_execute_arm_action(self, args):
        """
        功能:
            MCP 工具：发布手臂动作 ID 到 ROS2 话题，触发机器人预设动作。
        输入:
            args: Dict[str, Any]，需包含 action_id，可选 action_name。
        输出:
            Dict[str, Any]: 标准工具结果 {"status","data","error"}。
        """
        action_id = args.get("action_id")
        action_name = args.get("action_name", "执行动作")
        if action_id is None:
            return self._tool_result("error", data=None, error="missing required argument: action_id")
        try:
            action_id = int(action_id)
        except Exception:
            return self._tool_result("error", data={"action_id": action_id}, error=f"invalid action_id: {action_id}")

        self.get_logger().info(f"🤖 决策动作: {action_name} (ID: {action_id})")
        action_msg = Int32()
        action_msg.data = action_id
        self.arm_pub.publish(action_msg)
        return self._tool_result(
            "ok",
            data={
                "action_id": action_id,
                "action_name": action_name,
                "message": f"动作{action_name}。",
            },
            error=None,
        )

    def _tool_move_robot_logic(self, args):
        """
        功能:
            MCP 工具：根据方向与时长计算/组装底盘控制参数并执行底层运控命令。
        输入:
            args: Dict[str, Any]，需包含 direction，可选 duration/thought。
        输出:
            Dict[str, Any]: 标准工具结果 {"status","data","error"}。
        """
        direction = args.get("direction")
        if direction is None:
            return self._tool_result("error", data=None, error="missing required argument: direction")

        try:
            duration = float(args.get("duration", 1.0))
        except Exception:
            return self._tool_result(
                "error",
                data={"duration": args.get("duration")},
                error=f"invalid duration: {args.get('duration')}",
            )

        v = 0.2
        mapping = {
            "forward": [v, 0.0, 0.0],
            "backward": [-v, 0.0, 0.0],
            "left_strafe": [0.0, v, 0.0],
            "right_strafe": [0.0, -v, 0.0],
            "turn_left": [0.0, 0.0, v],
            "turn_right": [0.0, 0.0, -v],
        }

        if direction in ["stand_up", "damp", "start"]:
            success, output = self.run_locomotion_cmd(direction, "")
        elif direction in mapping:
            vals = mapping[direction]
            param_str = f"{vals[0]} {vals[1]} {vals[2]} {duration}"
            success, output = self.run_locomotion_cmd("set_velocity", param_str)
        else:
            return self._tool_result(
                "error",
                data={"direction": direction},
                error=f"unsupported direction: {direction}",
            )

        return self._tool_result(
            "ok" if success else "error",
            data={
                "direction": direction,
                "duration": duration,
                "execution_output": output,
            },
            error=None if success else output,
        )

    def call_ai_agent(self, user_prompt):
        """
        功能:
            Agent 核心循环：向 LLM 发送消息、执行 tool_calls、回填工具结果，
            直至获得最终自然语言回答或达到最大工具迭代次数。
        输入:
            user_prompt: str，用户输入文本。
        输出:
            str: 最终面向用户的自然语言回答（异常时返回兜底提示）。
        """
        self.multiplier = 0.3
        final_answer = "Sorry, my brain processing chain has been interrupted."
        plan_result = None
        exec_result = None

        try:
            self._set_agent_state(AgentState.THINKING, "planning task sequence")
            raw_plan_result = self.planner.plan(
                user_prompt=user_prompt,
                tool_catalog=self._build_planner_tool_catalog(),
                planner_json_schema=self.planner_json_schema,
                plan_validator=self._validate_plan_steps,
            )
            plan_result = self._normalize_tool_result("planner_engine", raw_plan_result)
            if plan_result.get("status") != "ok":
                self._set_agent_state(AgentState.ERROR, "planning failed")
                final_answer = "抱歉，我暂时无法稳定规划这条指令，请换一种说法再试一次。"
                return final_answer

            steps = (plan_result.get("data") or {}).get("steps", [])
            self.get_logger().info(f"[Plan] steps={steps}")

            self._set_agent_state(AgentState.CALLING_TOOL, "executing plan steps")
            exec_result = self._execute_plan_steps(steps)
            if exec_result.get("status") != "ok":
                self._set_agent_state(AgentState.ERROR, "plan execution failed")
                final_answer = "抱歉，执行过程中出现问题，请再试一次。"
                return final_answer

            final_answer = ((exec_result.get("data") or {}).get("final_text") or "").strip()
            final_answer = self._sanitize_ai_reply(final_answer)
            self._set_agent_state(AgentState.RESPONDING, "plan execution finished")
            # 仅 tool 时 final_text 由 asr_callback 播报；speak+tool 时答案已在执行器内播报。
            return final_answer

        except Exception as e:
            self._set_agent_state(AgentState.ERROR, "agent execution exception")
            self.get_logger().error(f"❌ AI agent execution error: {e}")
            final_answer = "Sorry, my brain processing chain has been interrupted."
            return final_answer
        finally:
            self.log_plan_trace(
                user_prompt=user_prompt,
                plan_result=plan_result,
                exec_result=exec_result,
                final_answer=final_answer,
                final_state=self.agent_state.value,
            )
            self._set_agent_state(AgentState.IDLE, "agent cycle finished")

    def robot_speak(self, text):
        """
        功能:
            启动机器人 TTS 播放流程（可自动中断上一个播放任务）。
        输入:
            text: str，要播报的文本。
        输出:
            无（异步启动 TTS 子线程）。
        """
        with self.tts_lock:
            speaking_now = self.is_speaking

        if speaking_now:
            self.stop_speaking()

        with self.tts_lock:
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
        """
        功能:
            在后台线程中调用 g1_tts_cli 执行语音播报，并维护播放状态。
        输入:
            text: str，播报文本。
            speaker_id: int，音色 ID（中文/英文）。
        输出:
            无（通过日志反馈执行结果）。
        """
        current_proc = None
        try:
            current_proc = subprocess.Popen(
                [TTS_CLI_PATH, NETWORK_INTERFACE, str(speaker_id), str(TTS_VOLUME), text],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            with self.tts_lock:
                self.active_tts_process = current_proc

            stdout, stderr = current_proc.communicate()

            if current_proc.returncode == 0:
                self.get_logger().info(
                    f"✅ TtsMaker completed: {stdout.strip()}"
                )
            else:
                self.get_logger().warn(
                    f"⚠️ TtsMaker stopped/failed (code {current_proc.returncode}): {stderr.strip()}"
                )
        except Exception as e:
            self.get_logger().error(f"TtsMaker exception: {e}")
        finally:
            with self.tts_lock:
                if self.active_tts_process is current_proc:
                    self.active_tts_process = None
                self.is_speaking = False
            self.get_logger().info("✅ Broadcast status reset.")

    def stop_speaking(self):
        """
        功能:
            强行停止当前 TTS 子进程并重置播报状态。
        输入:
            无。
        输出:
            无。
        """
        with self.tts_lock:
            proc = self.active_tts_process
            speaking_now = self.is_speaking

        if not proc:
            if speaking_now:
                with self.tts_lock:
                    self.is_speaking = False
            return

        self.get_logger().warn("🤫 Interrupting TTS playback...")
        try:
            proc.terminate()
            proc.wait(timeout=1.0)
        except subprocess.TimeoutExpired:
            self.get_logger().warn("TTS process did not exit in time, force killing.")
            proc.kill()
            proc.wait(timeout=1.0)
        except Exception as e:
            self.get_logger().error(f"Failed to stop TTS: {e}")
        finally:
            with self.tts_lock:
                if self.active_tts_process is proc:
                    self.active_tts_process = None
                self.is_speaking = False

    def _force_mute_tts_output(self):
        """
        功能:
            强制向 g1_tts_cli 下发一次音量=0 的指令，用于尽快压低外放音量。
        输入:
            无。
        输出:
            无（失败时仅记录日志，不抛异常）。
        """
        try:
            # 发送一条“音量为0”的 TTS 指令。即使文本被播放，也应为静音。
            result = subprocess.run(
                [TTS_CLI_PATH, NETWORK_INTERFACE, "0", "0", "mute"],
                capture_output=True,
                text=True,
                timeout=2.0,
            )
            if result.returncode == 0:
                self.get_logger().info("🔇 Forced mute command sent (volume=0).")
            else:
                self.get_logger().warn(
                    f"⚠️ Forced mute command failed (code {result.returncode}): {result.stderr.strip()}"
                )
        except Exception as e:
            self.get_logger().warn(f"⚠️ Forced mute command exception: {e}")

    def log_conversation(self, input_text, output_text):
        """
        功能:
            将一轮输入输出对话记录追加写入 jsonl 文件。
        输入:
            input_text: str，用户输入。
            output_text: str，系统回复。
        输出:
            无（文件写入失败时记录错误日志）。
        """
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

    def log_plan_trace(self, user_prompt, plan_result, exec_result, final_answer, final_state):
        """
        功能:
            将 Agent 规划与执行轨迹保存到 jsonl，便于回放“为什么这么决策”。
        输入:
            user_prompt: str，用户输入。
            plan_result: Dict/None，规划工具返回。
            exec_result: Dict/None，步骤执行返回。
            final_answer: str，最终回复文本。
            final_state: str，记录时的 agent 状态。
        输出:
            无（文件写入失败时记录错误日志）。
        """
        data = {
            "timestamp": datetime.now().isoformat(),
            "input": user_prompt,
            "plan_result": plan_result,
            "exec_result": exec_result,
            "final_answer": final_answer,
            "final_state": final_state,
        }
        try:
            with open(self.plan_log_file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
        except Exception as e:
            self.get_logger().error(f"保存规划轨迹失败: {e}")

    def run_locomotion_cmd(self, mode, params=""):
        """
        功能:
            执行底层运动控制命令（旗标模式或 set_velocity 模式）。
        输入:
            mode: str，动作模式（damp/start/stand_up/set_velocity 等）。
            params: str，可选速度参数字符串（仅 set_velocity 需要）。
        输出:
            Tuple[bool, str]: (执行是否成功, stdout 或错误信息)。
        """
        # 1. 基础配置
        exe_path = _resolve_relative(
            ("..", "..", "..", "..", "..", "..", "third_party", "unitree_sdk2", "bin", "g1_loco_client"),
            ("..", "..", "..", "third_party", "unitree_sdk2", "bin", "g1_loco_client"),
            ("..", "..", "..", "..", "..", "..", "..", "unitree_sdk2", "build", "bin", "g1_loco_client"),
            ("..", "..", "..", "..", "unitree_sdk2", "build", "bin", "g1_loco_client"),
        )
        interface = "eno1"
        lib_dir = os.path.normpath(os.path.join(os.path.dirname(exe_path), "..", "lib"))
        run_env = os.environ.copy()
        if os.path.isdir(lib_dir):
            run_env["LD_LIBRARY_PATH"] = lib_dir + os.pathsep + run_env.get("LD_LIBRARY_PATH", "") 
    
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
                timeout=30.0,  # 建议比你最大的 duration 稍微长一点
                env=run_env,
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
    """
    功能:
        程序入口，初始化 ROS2、启动 G1AIController 并进入 spin 循环。
    输入:
        args: 可选 ROS2 启动参数。
    输出:
        无（阻塞运行直到中断）。
    """
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