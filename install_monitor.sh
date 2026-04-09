#!/bin/bash
# OpenClaw Monitor 安装脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_NAME="com.user.openclaw-monitor.plist"
PLIST_SRC="$SCRIPT_DIR/$PLIST_NAME"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"
MONITOR_DIR="$HOME/.local/share/openclaw_monitor"

echo "=========================================="
echo "OpenClaw Monitor 安装"
echo "=========================================="
echo ""

# 创建监控目录
echo "[1/4] 创建监控目录..."
mkdir -p "$MONITOR_DIR"
echo "      完成: $MONITOR_DIR"

# 复制plist文件
echo "[2/4] 安装后台服务配置..."
cp "$PLIST_SRC" "$PLIST_DEST"
echo "      完成: $PLIST_DEST"

# 加载服务
echo "[3/4] 启动后台服务..."
launchctl unload "$PLIST_DEST" 2>/dev/null
launchctl load "$PLIST_DEST"
echo "      完成"

# 等待启动
echo "[4/4] 验证服务状态..."
sleep 2

# 检查服务状态
SERVICE_PID=$(launchctl list | grep openclaw-monitor | awk '{print $1}')
if [ -n "$SERVICE_PID" ]; then
    echo "      服务已启动 (PID: $SERVICE_PID)"
else
    echo "      警告: 服务可能未正确启动"
fi

echo ""
echo "=========================================="
echo "安装完成！"
echo "=========================================="
echo ""
echo "监控日志位置:"
echo "  $MONITOR_DIR/monitor.log"
echo ""
echo "查看日志:"
echo "  $SCRIPT_DIR/view_monitor.sh         # 最近记录"
echo "  $SCRIPT_DIR/view_monitor.sh -f      # 实时监控"
echo "  $SCRIPT_DIR/view_monitor.sh -t      # 今天记录"
echo "  $SCRIPT_DIR/view_monitor.sh -s      # 统计信息"
echo ""
echo "管理服务:"
echo "  查看状态: launchctl list | grep openclaw-monitor"
echo "  停止服务: launchctl unload $PLIST_DEST"
echo "  启动服务: launchctl load $PLIST_DEST"
echo ""
