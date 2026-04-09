#!/bin/bash
# OpenClaw Monitor 日志查看工具

MONITOR_DIR="$HOME/.local/share/openclaw_monitor"
LOG_FILE="$MONITOR_DIR/monitor.log"

echo "=========================================="
echo "OpenClaw Monitor 日志查看"
echo "=========================================="
echo ""

if [ ! -d "$MONITOR_DIR" ]; then
    echo "监控目录不存在，正在创建..."
    mkdir -p "$MONITOR_DIR"
fi

if [ ! -f "$LOG_FILE" ]; then
    echo "日志文件不存在，监控可能尚未启动"
    echo ""
    echo "启动监控："
    echo "  launchctl load ~/Library/LaunchAgents/com.user.openclaw-monitor.plist"
    exit 0
fi

case "$1" in
    "")
        echo "最近的监控记录："
        echo "----------------------------------------"
        tail -50 "$LOG_FILE"
        ;;
    "-f"|"--follow")
        echo "实时监控日志 (按 Ctrl+C 退出)："
        echo "----------------------------------------"
        tail -f "$LOG_FILE"
        ;;
    "-a"|"--all")
        echo "所有监控记录："
        echo "----------------------------------------"
        cat "$LOG_FILE"
        ;;
    "-g"|"--grep")
        if [ -z "$2" ]; then
            echo "用法: $0 -g <关键词>"
            exit 1
        fi
        echo "搜索关键词: $2"
        echo "----------------------------------------"
        grep -i "$2" "$LOG_FILE"
        ;;
    "-t"|"--today")
        echo "今天的监控记录："
        echo "----------------------------------------"
        TODAY=$(date "+%Y-%m-%d")
        grep "$TODAY" "$LOG_FILE"
        ;;
    "-e"|"--error")
        echo "错误记录："
        echo "----------------------------------------"
        grep "\[ERROR\]" "$LOG_FILE"
        ;;
    "-s"|"--stats")
        echo "监控统计："
        echo "----------------------------------------"
        echo "总记录数: $(wc -l < "$LOG_FILE")"
        echo "进程事件: $(grep -c "\[PROCESS\]" "$LOG_FILE" 2>/dev/null || echo 0)"
        echo "活动事件: $(grep -c "\[ACTIVITY\]" "$LOG_FILE" 2>/dev/null || echo 0)"
        echo "网络事件: $(grep -c "\[NETWORK\]" "$LOG_FILE" 2>/dev/null || echo 0)"
        echo "文件创建: $(grep -c "\[FILE_CREATE\]" "$LOG_FILE" 2>/dev/null || echo 0)"
        echo "文件删除: $(grep -c "\[FILE_DELETE\]" "$LOG_FILE" 2>/dev/null || echo 0)"
        echo "文件修改: $(grep -c "\[FILE_MODIFY\]" "$LOG_FILE" 2>/dev/null || echo 0)"
        echo "错误数: $(grep -c "\[ERROR\]" "$LOG_FILE" 2>/dev/null || echo 0)"
        ;;
    "-h"|"--help")
        echo "用法: $0 [选项]"
        echo ""
        echo "选项:"
        echo "  无参数      显示最近50条记录"
        echo "  -f, --follow  实时监控日志"
        echo "  -a, --all     显示所有记录"
        echo "  -t, --today   显示今天的记录"
        echo "  -g, --grep    搜索关键词"
        echo "  -e, --error   显示错误记录"
        echo "  -s, --stats   显示统计信息"
        echo "  -h, --help    显示帮助"
        ;;
    *)
        echo "未知选项: $1"
        echo "使用 -h 查看帮助"
        ;;
esac
