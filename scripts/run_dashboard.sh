#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="$(pwd)"
streamlit run src/dashboard/streamlit_app.py --server.port=8501 --server.address=0.0.0.0
EOF
chmod +x /workspace/Shikshasamvad/scripts/run_dashboard.sh