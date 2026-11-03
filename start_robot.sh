#!/bin/bash
echo "Starting lab RAG server (port 5000)"
cd ~/g1_rag
source venv/bin/activate
python rag_server.py > rag_server.log 2>&1 &
RAG_PID=$!
echo "Starting neuroscience search server (port 5001)"

python search_server.py > search_server.log 2>&1 &
SEARCH_PID=$!

echo "Configuring the ROS 2 environment..."
source /opt/ros/foxy/setup.bash
source ~/unitree_ros2_ws/src/unitree_ros2/setup.sh
source ~/unitree_ros2_ws/install/setup.bash

#unset CYCLONEDDS_URI

ros2 run my_g1_audio brain_update_sequential
#ros2 run my_g1_audio search_service
kill $RAG_PID $SEARCH_PID


#ros2 topic pub --once /audio_msg std_msgs/msg/String "data: '{\"text\": \"复旦大学脑智研究院的地址在哪\", \"is_final\": true}'"
#要执行手臂操作，需要"cd ~/unitree_ros2_ws/build/unitree_ros2_example"和"./g1_arm_action_example",屏幕上出现等待从话题 [/g1_arm_action_cmd] 发送的动作 ID...即为正常，超时报错不用管

# ~/unitree_ros2_ws/install/g1_tts_bridge/lib/g1_tts_bridge/g1_tts_cli eno1 0 "你好，这是测试。"
# 
# ros2 daemon stop

# ros2 topic pub --once /g1/voice_text std_msgs/msg/String "{data: '{\"text\":\"停止\",\"is_final\":true}'}"
# ros2 topic pub --once /g1/voice_text std_msgs/msg/String "{data: '{\"text\":\"跟大家挥挥手打个招呼\",\"is_final\":true}'}"
