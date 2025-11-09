#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="$(pwd)"
exec streamlit run src/dashboard/streamlit_app.py \
  --server.port=8501 \
  --server.address=0.0.0.0 \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false