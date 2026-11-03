#!/usr/bin/env bash
set -eo pipefail

# 1) 激活 conda 环境（脚本模式下需要先 source conda.sh）
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate g1_ear

# 2) ROS 2 环境
source /opt/ros/foxy/setup.bash

# 3) 编译并加载工作区
cd "$HOME/unitree_ros2_ws"
colcon build --packages-select my_g1_audio
source "$HOME/unitree_ros2_ws/install/setup.bash"

# 4) 让 Python 能直接找到源码包
export PYTHONPATH="$HOME/unitree_ros2_ws/src/my_g1_audio:${PYTHONPATH:-}"

# 5) 组播网卡（可选）
# 连上机器人并确认网卡可用时再设置该变量
export G1_MCAST_IFACE_IP=192.168.123.222

# 6) 启动耳朵节点
python "$HOME/unitree_ros2_ws/src/my_g1_audio/my_g1_audio/audio_bridge_node.py"

#sudo tcpdump -ni eno2 "udp and dst host 239.168.123.161 and dst port 5555"