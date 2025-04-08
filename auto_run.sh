#!/bin/bash

# export agentmake venv bin path
# assuming `ai` is the virtual environment directory for installing agentmake
export PATH=$PATH:$HOME/ai/bin

# Function to start AgentMake Studio
start_agentmakestudio() {
  echo "Starting AgentMake Studio ..."
  nohup agentmakestudio &
  echo "AgentMake Studio started."
}

# Check if AgentMake Studio is already running
if ! pgrep -f "agentmakestudio/main.py" > /dev/null; then
  start_agentmakestudio
else
  echo "AgentMake Studio is already running."
fi