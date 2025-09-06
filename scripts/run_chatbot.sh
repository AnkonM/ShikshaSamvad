#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="$(pwd)"
python src/chatbot/server.py
EOF
chmod +x /workspace/Shikshasamvaad/scripts/run_chatbot.sh