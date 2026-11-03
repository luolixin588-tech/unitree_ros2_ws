# G1 语言驱动控制：同一台电脑上的复现与启动

这套程序让 Unitree G1 听一句中文或英文，由本地大模型规划技能，再驱动语音、手臂和底盘。它分两个进程：

- **耳朵**：`start_ear.sh` 接收机器人麦克风的组播音频，做语音活动检测和语音识别，把文本发到 `/audio_msg`。
- **规划**：`start_robot.sh` 先启动两个本机检索服务，再启动 `brain_update_sequential`。该节点订阅 `/audio_msg`，向本机 Ollama 的 `qwen2.5:14b` 要一份有顺序的计划，然后逐步执行。手臂动作之后固定等待 10 秒，底盘移动之后固定等待 5 秒，再执行下一步。

仓库是私有的。另一个 Linux 账户要先能用有权限的 GitHub 账号克隆。

| 仓库 | 地址 | 克隆到 |
|---|---|---|
| 本仓库 | `https://github.com/luolixin588-tech/unitree_ros2_ws` | `~/unitree_ros2_ws` |
| 检索服务 | `https://github.com/luolixin588-tech/g1_rag` | `~/g1_rag` |

运动客户端来自 Unitree 官方 SDK，不放在这两个仓库里。请单独克隆到 `~/unitree_sdk2`：

`https://github.com/unitreerobotics/unitree_sdk2`

家目录下必须保持这个相对位置，代码按它查找语音程序和运动程序：

```text
~/unitree_ros2_ws
~/unitree_sdk2
~/g1_rag
~/miniconda3
```

## 1. 系统环境

在这台机器上，系统级软件可以共用，不必为新账户重装：

- Ubuntu 20.04
- ROS 2 Foxy：`/opt/ros/foxy`
- 编译 Unitree SDK 所需的 CMake、g++、Eigen、Boost、yaml-cpp、spdlog、fmt
- Ollama 服务，并且已经拉取模型 `qwen2.5:14b`

新账户自己需要：

- Miniconda，安装在 `~/miniconda3`。`start_ear.sh` 会读取这个路径。
- 一个名为 `g1_ear` 的 conda 环境。
- `~/g1_rag/venv`。不要把原来的虚拟环境直接拷过来，里面的解释器路径属于旧账户。

机器人通信使用网卡 `eno1`。耳朵节点还会把组播绑定到 `192.168.123.222`。这是本机连接机器人时的地址；换网卡或地址时，要同时改 `src/unitree_ros2/setup.sh` 和 `start_ear.sh`。

## 2. 克隆

在新账户中执行：

```bash
cd ~
git clone https://github.com/luolixin588-tech/unitree_ros2_ws.git
git clone https://github.com/luolixin588-tech/g1_rag.git
git clone https://github.com/unitreerobotics/unitree_sdk2.git
```

## 3. 准备耳朵环境

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda create -n g1_ear python=3.8 -y
conda activate g1_ear
pip install numpy onnxruntime faster-whisper opencc-python-reimplemented
```

第一次识别时，Faster-Whisper 会把模型下载到这个账户自己的缓存。耳朵节点优先使用 CUDA；GPU 不可用时会改用 CPU。

## 4. 准备检索环境

```bash
python3 -m venv ~/g1_rag/venv
~/g1_rag/venv/bin/pip install -r ~/g1_rag/requirements.txt
```

两个服务的资料和日志都相对 `g1_rag` 目录本身，不依赖原来的用户名：

| 服务 | 脚本 | 端口 | 资料 |
|---|---|---|---|
| 实验室问答 | `rag_server.py` | 5000 | `data/lab_info.txt` |
| 神经科学检索 | `search_server.py` | 5001 | `data/search_info.txt` |

神经科学检索还会访问实验室内网 `http://10.133.59.101:5454/answer`。不在该网络时，这一项检索会失败，实验室问答和机器人动作规划仍然可以启动。两个服务都使用本机 Ollama 做向量和回答。

## 5. 编译

运动客户端：

```bash
cd ~/unitree_sdk2
mkdir -p build && cd build
cmake ..
make -j
```

完成后应存在 `~/unitree_sdk2/build/bin/g1_loco_client`。

语音桥和规划节点：

```bash
source /opt/ros/foxy/setup.bash
cd ~/unitree_ros2_ws
colcon build --packages-select g1_tts_bridge my_g1_audio
```

`g1_tts_bridge` 提供播报程序。`my_g1_audio` 提供命令 `brain_update_sequential`。CycloneDDS 使用仓库里已经生成的 `src/unitree_ros2/cyclonedds_ws/install`，它的 bash 脚本按自身位置定位，克隆到新的家目录后可以继续用。

## 6. 启动

先确认 Ollama 在运行，并且能看到 `qwen2.5:14b`：

```bash
ollama list
```

开两个终端，都使用新账户。

终端 A，耳朵：

```bash
bash ~/unitree_ros2_ws/start_ear.sh
```

这个脚本会激活 `g1_ear`，编译 `my_g1_audio`，然后运行 `audio_bridge_node.py`。它订阅机器人麦克风组播 `239.168.123.161:5555`，识别完成后向 `/audio_msg` 发布 JSON 文本。

终端 B，规划：

```bash
bash ~/unitree_ros2_ws/start_robot.sh
```

这个脚本会：

1. 在 `~/g1_rag` 的虚拟环境里后台启动 5000 端口的实验室问答。
2. 后台启动 5001 端口的神经科学检索。
3. 加载 ROS 2、Unitree CycloneDDS 和本工作区。
4. 前台运行 `ros2 run my_g1_audio brain_update_sequential`。

规划节点的名字是 `g1_ai_controller`。日志里应出现正在监听 `/audio_msg`。对机器人说话后，规划请求发往 `http://127.0.0.1:11434/api/chat`。

停止终端 B 的规划节点后，脚本会关掉刚才启动的两个检索服务。检索日志写在 `~/g1_rag/rag_server.log` 和 `~/g1_rag/search_server.log`。

## 7. 不使用脚本时的等价命令

耳朵：

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate g1_ear
source /opt/ros/foxy/setup.bash
cd ~/unitree_ros2_ws
colcon build --packages-select my_g1_audio
source install/setup.bash
export PYTHONPATH="$HOME/unitree_ros2_ws/src/my_g1_audio:${PYTHONPATH:-}"
export G1_MCAST_IFACE_IP=192.168.123.222
python src/my_g1_audio/my_g1_audio/audio_bridge_node.py
```

规划：

```bash
cd ~/g1_rag
source venv/bin/activate
python rag_server.py > rag_server.log 2>&1 &
python search_server.py > search_server.log 2>&1 &
source /opt/ros/foxy/setup.bash
source ~/unitree_ros2_ws/src/unitree_ros2/setup.sh
source ~/unitree_ros2_ws/install/setup.bash
ros2 run my_g1_audio brain_update_sequential
```

不要启动 `brain_update_service`。那个入口对应没有逐步等待的旧规划节点。

## 8. 手臂动作

只启动上面两个脚本时，手臂命令会发到 `/g1_arm_action_cmd`。机器人真正执行预设动作，还需要动作示例程序处于等待状态。在已编译的 Unitree ROS 2 示例目录中运行 `g1_arm_action_example`，看到它正在等待该话题上的动作编号即可。
