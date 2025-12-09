#!/bin/bash

echo "Installing AiFinOps Agent..."

mkdir -p /opt/aifinops
cd /opt/aifinops

curl -L https://raw.githubusercontent.com/LOLA0786/AiFinops/main/aifinops-agent-latest.tar.gz -o agent.tar.gz

tar -xzf agent.tar.gz
rm agent.tar.gz

echo "Installing Python deps..."
pip install -r requirements.txt

echo "Registering agent..."
aifinops connect

echo "AiFinOps Agent Installed Successfully!"
