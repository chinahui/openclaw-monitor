#!/bin/bash
# OpenClaw Monitor 启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITOR_SCRIPT="$SCRIPT_DIR/openclaw_monitor.py"
LOG_FILE="$HOME/.openclaw/monitor.log"

echo "=========================================="
echo "OpenClaw Monitor"
echo "=========================================="
echo ""
echo "监控日志: $LOG_FILE"
echo ""
echo "按 Ctrl+C 停止监控"
echo ""

python3 "$MONITOR_SCRIPT"
