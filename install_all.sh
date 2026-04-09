#!/bin/bash
# OpenClaw Monitor 完整安装脚本
# 此脚本会自动替换路径占位符

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITOR_DIR="$HOME/.local/share/openclaw_monitor"
INSTALL_PATH="$SCRIPT_DIR"

echo "=========================================="
echo "OpenClaw Monitor 完整安装"
echo "=========================================="
echo ""

# 创建监控目录
echo "[1/7] 创建监控目录..."
mkdir -p "$MONITOR_DIR"
echo "      完成: $MONITOR_DIR"

# 替换 plist 中的占位符
echo "[2/7] 配置服务..."
MONITOR_PLIST="$HOME/Library/LaunchAgents/com.user.openclaw-monitor.plist"
DASHBOARD_PLIST="$HOME/Library/LaunchAgents/com.user.openclaw-dashboard.plist"

# 复制并替换路径
sed "s|{{INSTALL_PATH}}|$INSTALL_PATH|g" "$SCRIPT_DIR/com.user.openclaw-monitor.plist" > "$MONITOR_PLIST"
sed "s|{{INSTALL_PATH}}|$INSTALL_PATH|g" "$SCRIPT_DIR/com.user.openclaw-dashboard.plist" > "$DASHBOARD_PLIST"

# 安装监控服务
echo "[3/7] 安装监控服务..."
launchctl unload "$MONITOR_PLIST" 2>/dev/null
launchctl load "$MONITOR_PLIST"
echo "      完成"

# 安装Dashboard服务
echo "[4/7] 安装Dashboard服务..."
launchctl unload "$DASHBOARD_PLIST" 2>/dev/null
launchctl load "$DASHBOARD_PLIST"
echo "      完成"

# 等待启动
echo "[5/7] 等待服务启动..."
sleep 3

# 检查服务状态
echo "[6/7] 验证服务状态..."
MONITOR_PID=$(launchctl list | grep openclaw-monitor | awk '{print $1}')
DASHBOARD_PID=$(launchctl list | grep openclaw-dashboard | awk '{print $1}')

if [ -n "$MONITOR_PID" ]; then
    echo "      ✅ 监控服务已启动 (PID: $MONITOR_PID)"
else
    echo "      ❌ 监控服务未启动"
fi

if [ -n "$DASHBOARD_PID" ]; then
    echo "      ✅ Dashboard服务已启动 (PID: $DASHBOARD_PID)"
else
    echo "      ❌ Dashboard服务未启动"
fi

echo "[7/7] 安装完成！"
echo ""
echo "=========================================="
echo "使用说明"
echo "=========================================="
echo ""
echo "📊 Dashboard面板:"
echo "   http://localhost:8765"
echo ""
echo "📝 查看日志:"
echo "   $SCRIPT_DIR/view_monitor.sh         # 最近记录"
echo "   $SCRIPT_DIR/view_monitor.sh -f      # 实时监控"
echo "   $SCRIPT_DIR/view_monitor.sh -s      # 统计信息"
echo ""
echo "⚙️ 管理服务:"
echo "   查看状态: launchctl list | grep openclaw"
echo "   停止: launchctl unload ~/Library/LaunchAgents/com.user.openclaw-monitor.plist"
echo "   启动: launchctl load ~/Library/LaunchAgents/com.user.openclaw-monitor.plist"
echo ""
