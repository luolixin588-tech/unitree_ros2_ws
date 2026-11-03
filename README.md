# G1 语言驱动控制：同一台电脑上的复现与启动

这套程序让 Unitree G1 听一句中文或英文，由本地大模型规划技能，再驱动语音、手臂和底盘。它分三个必须同时开着的进程：

- **耳朵**：`start_ear.sh` 接收机器人麦克风的组播音频，做语音活动检测和语音识别，把文本发到 `/g1/voice_text`。
- **运动服务**：`g1_arm_action_example` 订阅 `/g1_arm_action_cmd`。`brain_update_sequential.py` 只往这个话题发布动作编号，真正让机器人做挥手、握手等预设动作的是这个程序。它不在两个启动脚本里，要单独开一个终端，并一直保持运行。
- **规划**：`start_robot.sh` 启动 `brain_update_sequential`。该节点订阅 `/g1/voice_text`，向本机 Ollama 的 `qwen2.5:14b` 要一份有顺序的计划，然后逐步执行。手臂动作之后固定等待 10 秒，底盘移动之后固定等待 5 秒，再执行下一步。底盘移动不经过上面的运动服务，每次由规划节点直接调用本仓库里的 `third_party/unitree_sdk2/bin/g1_loco_client`。实验室问答和神经科学检索不参与启动；这两个服务没开时，说话、手臂和底盘仍可执行。

仓库是私有的。另一个 Linux 账户要先能用有权限的 GitHub 账号克隆。

| 仓库 | 地址 | 克隆到 |
|---|---|---|
| 本仓库 | `https://github.com/luolixin588-tech/unitree_ros2_ws` | `~/unitree_ros2_ws` |

底盘程序已经放在本仓库的 `third_party/unitree_sdk2/`。它是 Unitree SDK 编好的 `g1_loco_client`，以及它要加载的 `libddscxx.so`。许可是 BSD 3-Clause，原文在 `third_party/unitree_sdk2/LICENSE`。不需要再克隆或编译 `unitree_sdk2`。

家目录下保持这个相对位置：

```text
~/unitree_ros2_ws
~/miniconda3
```

## 1. 系统环境

在这台机器上，系统级软件可以共用，不必为新账户重装：

- Ubuntu 20.04
- ROS 2 Foxy：`/opt/ros/foxy`
- Ollama，程序在 `/opt/ollama/bin/ollama`，模型目录在 `/opt/ollama/models`。规划使用的模型是 `qwen2.5:14b`。

新账户自己需要：

- Miniconda，安装在 `~/miniconda3`。`start_ear.sh` 会读取这个路径。
- 一个名为 `g1_ear` 的 conda 环境。

机器人通信使用网卡 `eno1`。耳朵节点还会把组播绑定到 `192.168.123.222`。这是本机连接机器人时的地址；换网卡或地址时，要同时改 `src/unitree_ros2/setup.sh` 和 `start_ear.sh`。

## 2. 克隆

在新账户中执行：

```bash
cd ~
git clone https://github.com/luolixin588-tech/unitree_ros2_ws.git
```

## 3. 准备耳朵环境

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda create -n g1_ear python=3.8 -y
conda activate g1_ear
pip install numpy onnxruntime faster-whisper opencc-python-reimplemented
```

第一次识别时，Faster-Whisper 会把模型下载到这个账户自己的缓存。耳朵节点优先使用 CUDA；GPU 不可用时会改用 CPU。

## 4. 已编译的程序

底盘、语音和手臂运动服务都使用仓库里已经编译好的程序，不要再编译：

| 程序 | 路径 |
|---|---|
| 底盘 | `third_party/unitree_sdk2/bin/g1_loco_client` |
| 语音 | `third_party/prebuilt/bin/g1_tts_cli` |
| 手臂运动服务 | `third_party/prebuilt/bin/g1_arm_action_example` |

这些程序依赖本机的 `/opt/ros/foxy`。同一台电脑上的另一个账户可以直接运行。

规划节点是 Python。要让 `ros2 run my_g1_audio brain_update_sequential` 找到入口，做一次安装即可，这一步不编译 C++：

```bash
source /opt/ros/foxy/setup.bash
source ~/unitree_ros2_ws/src/unitree_ros2/setup.sh
cd ~/unitree_ros2_ws
colcon build --packages-select my_g1_audio
```

CycloneDDS 使用仓库里已经生成的 `src/unitree_ros2/cyclonedds_ws/install`，它的 bash 脚本按自身位置定位，克隆到新的家目录后可以继续用。

## 5. 启动和关闭 Ollama

Ollama 是系统服务，由 root 运行，监听 11434 端口。规划节点把请求发到 `http://127.0.0.1:11434/api/chat`。启动三个终端之前先打开它。

启动：

```bash
sudo systemctl start ollama
/opt/ollama/bin/ollama list
```

`ollama list` 的结果里要有 `qwen2.5:14b`。没有这个模型时，先执行：

```bash
/opt/ollama/bin/ollama pull qwen2.5:14b
```

关闭：

```bash
sudo systemctl stop ollama
```

看当前状态：

```bash
systemctl is-active ollama
```

`active` 表示正在运行，`inactive` 表示已关闭。这个服务当前没有设成开机自启，机器重启后需要再执行一次 `sudo systemctl start ollama`。

## 6. 启动机器人

开三个终端，都使用新账户。顺序是耳朵、运动服务、规划。运动服务要先于规划进入等待状态，否则手臂指令发出后没有程序接收。

终端 A，耳朵：

```bash
bash ~/unitree_ros2_ws/start_ear.sh
```

这个脚本会激活 `g1_ear`，安装 `my_g1_audio`，然后运行 `audio_bridge_node.py`。它订阅机器人麦克风组播 `239.168.123.161:5555`，识别完成后向 `/g1/voice_text` 发布文本。

终端 B，运动服务：

```bash
source /opt/ros/foxy/setup.bash
source ~/unitree_ros2_ws/src/unitree_ros2/setup.sh
source ~/unitree_ros2_ws/install/setup.bash
~/unitree_ros2_ws/third_party/prebuilt/bin/g1_arm_action_example
```

先加载这三份环境再运行。不加载时，程序会因为找不到 `librosidl_typesupport_cpp.so` 而退出。正常时应看到：

```text
等待从话题 [/g1_arm_action_cmd] 发送的动作 ID...
```

屏幕上如果随后出现动作反馈超时，可以继续保持这个进程，规划节点仍然会往这个话题发动作编号。这个终端要一直开着。`brain_update_sequential.py` 里的 `execute_arm_action` 只发布一个 `Int32` 动作编号，执行发生在这里。

终端 C，规划：

```bash
bash ~/unitree_ros2_ws/start_robot.sh
```

这个脚本会加载 ROS 2、Unitree CycloneDDS 和本工作区，然后前台运行 `ros2 run my_g1_audio brain_update_sequential`。家里如果已经有 `~/g1_rag`，它会顺带启动检索；没有这个目录就跳过，规划节点照常启动。

规划节点的名字是 `g1_ai_controller`。日志里应出现已连接 `/g1/voice_text`。对机器人说话后，规划请求发往 `http://127.0.0.1:11434/api/chat`。

终端 B 的运动服务不会被这个脚本关掉。

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
source /opt/ros/foxy/setup.bash
source ~/unitree_ros2_ws/src/unitree_ros2/setup.sh
source ~/unitree_ros2_ws/install/setup.bash
ros2 run my_g1_audio brain_update_sequential
```

不要启动 `brain_update_service`。那个入口对应没有逐步等待的旧规划节点。

运动服务的等价命令就是上一节终端 B 的那四行。规划节点发出底盘命令时，会自己调用仓库里的 `g1_loco_client`，不需要再开一个底盘服务。
