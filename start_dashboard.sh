#!/bin/bash
# OpenClaw Monitor Dashboard 启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DASHBOARD_SCRIPT="$SCRIPT_DIR/dashboard.py"
PORT=${1:-8765}

echo "=========================================="
echo "OpenClaw Monitor Dashboard"
echo "=========================================="
echo ""
echo "访问地址: http://localhost:$PORT"
echo "按 Ctrl+C 停止"
echo ""

python3 "$DASHBOARD_SCRIPT" $PORT
