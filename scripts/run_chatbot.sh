#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="$(pwd)"
python src/chatbot/server.py
EOF
chmod +x /workspace/Shikshasamvad/scripts/run_chatbot.sh