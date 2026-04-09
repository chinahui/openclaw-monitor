#!/usr/bin/env python3
"""
OpenClaw Monitor Dashboard - 网页监控面板
"""

import os
import json
import time
import re
from datetime import datetime, timedelta
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread
import urllib.parse

class MonitorDashboard:
    def __init__(self):
        self.monitor_dir = Path.home() / ".local" / "share" / "openclaw_monitor"
        self.log_file = self.monitor_dir / "monitor.log"
        self.openclaw_dir = Path.home() / ".openclaw"
        
    def parse_log(self):
        """解析日志文件"""
        events = []
        if not self.log_file.exists():
            return events
            
        with open(self.log_file, "r") as f:
            for line in f:
                try:
                    # 解析日志行
                    # [2026-04-08 22:39:21] [INFO] 消息
                    match = re.match(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[(\w+)\] (.+)', line)
                    if match:
                        timestamp, level, message = match.groups()
                        events.append({
                            "timestamp": timestamp,
                            "level": level,
                            "message": message.strip()
                        })
                except:
                    pass
        return events
    
    def analyze_events(self, events):
        """分析事件"""
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        one_day_ago = now - timedelta(days=1)
        
        stats = {
            "total": len(events),
            "last_hour": 0,
            "last_day": 0,
            "by_level": {},
            "by_type": {},
            "errors": [],
            "warnings": [],
            "suspicious": [],
            "file_operations": [],
            "network_connections": [],
            "process_events": [],
        }
        
        for event in events:
            try:
                event_time = datetime.strptime(event["timestamp"], "%Y-%m-%d %H:%M:%S")
                
                # 时间统计
                if event_time > one_hour_ago:
                    stats["last_hour"] += 1
                if event_time > one_day_ago:
                    stats["last_day"] += 1
                
                # 级别统计
                level = event["level"]
                stats["by_level"][level] = stats["by_level"].get(level, 0) + 1
                
                # 类型统计
                message = event["message"]
                if "[PROCESS]" in message or "进程" in message:
                    stats["by_type"]["process"] = stats["by_type"].get("process", 0) + 1
                    stats["process_events"].append(event)
                elif "[NETWORK]" in message or "网络" in message:
                    stats["by_type"]["network"] = stats["by_type"].get("network", 0) + 1
                    stats["network_connections"].append(event)
                elif "[FILE_" in message or "文件" in message:
                    stats["by_type"]["file"] = stats["by_type"].get("file", 0) + 1
                    stats["file_operations"].append(event)
                elif "[ACTIVITY]" in message:
                    stats["by_type"]["activity"] = stats["by_type"].get("activity", 0) + 1
                elif "[SESSION]" in message:
                    stats["by_type"]["session"] = stats["by_type"].get("session", 0) + 1
                
                # 错误和警告
                if level == "ERROR":
                    stats["errors"].append(event)
                elif level == "WARNING":
                    stats["warnings"].append(event)
                
                # 可疑活动检测
                suspicious_keywords = [
                    "mkdir.*Desktop", "open.*Photo", "camera", "exec.*rm",
                    "spawn", "shell.*command", "未命名"
                ]
                for keyword in suspicious_keywords:
                    if re.search(keyword, message, re.IGNORECASE):
                        stats["suspicious"].append(event)
                        break
                        
            except:
                pass
        
        return stats
    
    def calculate_score(self, stats):
        """计算安全评分"""
        score = 100
        reasons = []
        
        # 错误扣分
        error_count = len(stats["errors"])
        if error_count > 0:
            score -= min(error_count * 5, 30)
            reasons.append(f"发现 {error_count} 个错误")
        
        # 可疑活动扣分
        suspicious_count = len(stats["suspicious"])
        if suspicious_count > 0:
            score -= min(suspicious_count * 10, 50)
            reasons.append(f"发现 {suspicious_count} 个可疑活动")
        
        # 文件操作扣分
        file_ops = len(stats["file_operations"])
        if file_ops > 10:
            score -= min((file_ops - 10) * 2, 20)
            reasons.append(f"文件操作频繁 ({file_ops} 次)")
        
        # 网络连接扣分
        network_ops = len(stats["network_connections"])
        if network_ops > 20:
            score -= min((network_ops - 20) * 1, 10)
            reasons.append(f"网络连接较多 ({network_ops} 次)")
        
        # 确保分数在0-100之间
        score = max(0, min(100, score))
        
        # 状态判断
        if score >= 90:
            status = "安全"
            status_color = "green"
        elif score >= 70:
            status = "正常"
            status_color = "blue"
        elif score >= 50:
            status = "注意"
            status_color = "orange"
        else:
            status = "警告"
            status_color = "red"
        
        return {
            "score": score,
            "status": status,
            "status_color": status_color,
            "reasons": reasons
        }
    
    def get_openclaw_status(self):
        """获取OpenClaw状态"""
        import subprocess
        try:
            result = subprocess.run(
                ["pgrep", "-f", "openclaw"],
                capture_output=True, text=True
            )
            pids = result.stdout.strip().split("\n") if result.stdout.strip() else []
            return {
                "running": len(pids) > 0,
                "process_count": len(pids),
                "pids": pids
            }
        except:
            return {"running": False, "process_count": 0, "pids": []}
    
    def get_log_size(self):
        """获取日志文件大小"""
        sizes = {}
        
        # 监控日志
        if self.log_file.exists():
            sizes["monitor_log"] = self.log_file.stat().st_size
        
        # Dashboard日志
        dashboard_stdout = self.monitor_dir / "dashboard_stdout.log"
        dashboard_stderr = self.monitor_dir / "dashboard_stderr.log"
        
        if dashboard_stdout.exists():
            sizes["dashboard_stdout"] = dashboard_stdout.stat().st_size
        if dashboard_stderr.exists():
            sizes["dashboard_stderr"] = dashboard_stderr.stat().st_size
        
        # 总大小
        sizes["total"] = sum(sizes.values())
        
        # 格式化大小
        def format_size(size):
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            elif size < 1024 * 1024 * 1024:
                return f"{size / (1024 * 1024):.1f} MB"
            else:
                return f"{size / (1024 * 1024 * 1024):.1f} GB"
        
        sizes["formatted"] = {
            "monitor_log": format_size(sizes.get("monitor_log", 0)),
            "dashboard_stdout": format_size(sizes.get("dashboard_stdout", 0)),
            "dashboard_stderr": format_size(sizes.get("dashboard_stderr", 0)),
            "total": format_size(sizes["total"])
        }
        
        # 是否需要清理（超过10MB）
        sizes["need_cleanup"] = sizes["total"] > 10 * 1024 * 1024
        
        return sizes
    
    def get_dashboard_data(self):
        """获取面板数据"""
        events = self.parse_log()
        stats = self.analyze_events(events)
        score = self.calculate_score(stats)
        openclaw_status = self.get_openclaw_status()
        log_size = self.get_log_size()
        
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "openclaw_status": openclaw_status,
            "score": score,
            "stats": stats,
            "log_size": log_size,
            "recent_events": events[-50:] if events else []
        }

# 全局实例
dashboard = MonitorDashboard()

class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(self.generate_html().encode("utf-8"))
        elif self.path == "/api/data":
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            data = dashboard.get_dashboard_data()
            self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == "/api/clear-logs":
            try:
                # 读取日志文件，保留最近100行
                log_file = dashboard.log_file
                if log_file.exists():
                    with open(log_file, "r") as f:
                        lines = f.readlines()
                    
                    # 保留最近100行
                    with open(log_file, "w") as f:
                        f.writelines(lines[-100:])
                
                # 清理Dashboard日志
                dashboard_stdout = dashboard.monitor_dir / "dashboard_stdout.log"
                dashboard_stderr = dashboard.monitor_dir / "dashboard_stderr.log"
                
                for log in [dashboard_stdout, dashboard_stderr]:
                    if log.exists():
                        log.unlink()
                
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
        else:
            self.send_error(404)
    
    def generate_html(self):
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenClaw Monitor Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { margin-bottom: 20px; color: #333; }
        
        /* 评分卡片 */
        .score-card {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        .score-value {
            font-size: 72px;
            font-weight: bold;
            margin: 20px 0;
        }
        .score-status {
            font-size: 24px;
            padding: 10px 20px;
            border-radius: 20px;
            display: inline-block;
        }
        .green { color: #22c55e; background: #dcfce7; }
        .blue { color: #3b82f6; background: #dbeafe; }
        .orange { color: #f59e0b; background: #fef3c7; }
        .red { color: #ef4444; background: #fee2e2; }
        
        /* 状态卡片 */
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .status-item {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .status-label { color: #666; font-size: 14px; margin-bottom: 5px; }
        .status-value { font-size: 24px; font-weight: bold; }
        
        /* 事件列表 */
        .events-section {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .events-title { font-size: 18px; margin-bottom: 15px; }
        .event-item {
            padding: 10px;
            border-bottom: 1px solid #eee;
            font-size: 13px;
        }
        .event-time { color: #666; margin-right: 10px; }
        .event-level { 
            display: inline-block;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
            margin-right: 10px;
        }
        .event-level.INFO { background: #e0e7ff; color: #3730a3; }
        .event-level.ERROR { background: #fee2e2; color: #dc2626; }
        .event-level.WARNING { background: #fef3c7; color: #d97706; }
        .event-level.PROCESS { background: #dbeafe; color: #2563eb; }
        .event-level.NETWORK { background: #d1fae5; color: #059669; }
        
        /* 原因列表 */
        .reasons-list {
            margin-top: 20px;
            text-align: left;
        }
        .reason-item {
            padding: 8px 12px;
            background: #fef2f2;
            border-left: 3px solid #ef4444;
            margin-bottom: 8px;
            border-radius: 0 4px 4px 0;
        }
        
        /* 刷新按钮 */
        .refresh-btn {
            background: #3b82f6;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .refresh-btn:hover { background: #2563eb; }
        
        /* 自动刷新提示 */
        .auto-refresh {
            color: #666;
            font-size: 12px;
            margin-left: 10px;
        }
        
        /* 日志大小 */
        .log-size-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }
        .log-size-item {
            padding: 10px;
            background: #f8fafc;
            border-radius: 6px;
        }
        .log-size-label {
            color: #666;
            font-size: 13px;
        }
        .log-size-value {
            font-weight: bold;
            color: #333;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ OpenClaw Monitor Dashboard</h1>
        <button class="refresh-btn" onclick="loadData()">🔄 刷新</button>
        <span class="auto-refresh">自动刷新: 每5秒</span>
        
        <!-- 评分卡片 -->
        <div class="score-card">
            <div class="status-label">安全评分</div>
            <div class="score-value" id="score">--</div>
            <div class="score-status" id="status">加载中...</div>
            <div class="reasons-list" id="reasons"></div>
        </div>
        
        <!-- 状态网格 -->
        <div class="status-grid">
            <div class="status-item">
                <div class="status-label">OpenClaw状态</div>
                <div class="status-value" id="openclaw-status">--</div>
            </div>
            <div class="status-item">
                <div class="status-label">进程数</div>
                <div class="status-value" id="process-count">--</div>
            </div>
            <div class="status-item">
                <div class="status-label">最近1小时事件</div>
                <div class="status-value" id="events-hour">--</div>
            </div>
            <div class="status-item">
                <div class="status-label">总事件数</div>
                <div class="status-value" id="events-total">--</div>
            </div>
            <div class="status-item">
                <div class="status-label">错误数</div>
                <div class="status-value" id="error-count">--</div>
            </div>
            <div class="status-item">
                <div class="status-label">可疑活动</div>
                <div class="status-value" id="suspicious-count">--</div>
            </div>
        </div>
        
        <!-- 日志大小 -->
        <div class="events-section" id="log-size-section">
            <div class="events-title">📁 日志文件大小</div>
            <div class="log-size-grid">
                <div class="log-size-item">
                    <span class="log-size-label">监控日志:</span>
                    <span class="log-size-value" id="log-monitor">--</span>
                </div>
                <div class="log-size-item">
                    <span class="log-size-label">Dashboard日志:</span>
                    <span class="log-size-value" id="log-dashboard">--</span>
                </div>
                <div class="log-size-item">
                    <span class="log-size-label">总大小:</span>
                    <span class="log-size-value" id="log-total">--</span>
                </div>
            </div>
            <div id="log-warning" style="display:none; margin-top:15px; padding:10px; background:#fef3c7; border-radius:6px; color:#92400e;">
                ⚠️ 日志文件较大，建议清理
            </div>
            <div style="margin-top:15px;">
                <button class="refresh-btn" style="background:#ef4444;" onclick="clearLogs()">🗑️ 清理日志</button>
                <span style="color:#666; font-size:12px; margin-left:10px;">清理后保留最近100条记录</span>
            </div>
        </div>
        
        <!-- 最近事件 -->
        <div class="events-section">
            <div class="events-title">📋 最近事件</div>
            <div id="events-list">加载中...</div>
        </div>
        
        <!-- 可疑活动 -->
        <div class="events-section" id="suspicious-section" style="display:none;">
            <div class="events-title">⚠️ 可疑活动</div>
            <div id="suspicious-list"></div>
        </div>
    </div>
    
    <script>
        function loadData() {
            fetch('/api/data')
                .then(r => r.json())
                .then(data => {
                    // 更新评分
                    document.getElementById('score').textContent = data.score.score;
                    document.getElementById('score').className = 'score-value ' + data.score.status_color;
                    document.getElementById('status').textContent = data.score.status;
                    document.getElementById('status').className = 'score-status ' + data.score.status_color;
                    
                    // 更新原因
                    const reasonsDiv = document.getElementById('reasons');
                    if (data.score.reasons.length > 0) {
                        reasonsDiv.innerHTML = data.score.reasons.map(r => 
                            '<div class="reason-item">' + r + '</div>'
                        ).join('');
                    } else {
                        reasonsDiv.innerHTML = '<div style="color:#22c55e;">✅ 系统运行正常，未发现异常</div>';
                    }
                    
                    // 更新状态
                    const ocStatus = data.openclaw_status.running ? '运行中' : '已停止';
                    document.getElementById('openclaw-status').textContent = ocStatus;
                    document.getElementById('process-count').textContent = data.openclaw_status.process_count;
                    document.getElementById('events-hour').textContent = data.stats.last_hour;
                    document.getElementById('events-total').textContent = data.stats.total;
                    document.getElementById('error-count').textContent = data.stats.errors.length;
                    document.getElementById('suspicious-count').textContent = data.stats.suspicious.length;
                    
                    // 更新日志大小
                    document.getElementById('log-monitor').textContent = data.log_size.formatted.monitor_log;
                    document.getElementById('log-dashboard').textContent = 
                        data.log_size.formatted.dashboard_stdout + ' + ' + data.log_size.formatted.dashboard_stderr;
                    document.getElementById('log-total').textContent = data.log_size.formatted.total;
                    
                    // 显示警告
                    const logWarning = document.getElementById('log-warning');
                    if (data.log_size.need_cleanup) {
                        logWarning.style.display = 'block';
                    } else {
                        logWarning.style.display = 'none';
                    }
                    
                    // 更新事件列表
                    const eventsDiv = document.getElementById('events-list');
                    if (data.recent_events.length > 0) {
                        eventsDiv.innerHTML = data.recent_events.reverse().map(e => 
                            '<div class="event-item">' +
                            '<span class="event-time">' + e.timestamp + '</span>' +
                            '<span class="event-level ' + e.level + '">' + e.level + '</span>' +
                            e.message.substring(0, 100) + 
                            '</div>'
                        ).join('');
                    } else {
                        eventsDiv.innerHTML = '<div class="event-item">暂无事件</div>';
                    }
                    
                    // 更新可疑活动
                    const suspiciousSection = document.getElementById('suspicious-section');
                    const suspiciousDiv = document.getElementById('suspicious-list');
                    if (data.stats.suspicious.length > 0) {
                        suspiciousSection.style.display = 'block';
                        suspiciousDiv.innerHTML = data.stats.suspicious.map(e => 
                            '<div class="event-item" style="background:#fef2f2;">' +
                            '<span class="event-time">' + e.timestamp + '</span>' +
                            e.message.substring(0, 150) + 
                            '</div>'
                        ).join('');
                    } else {
                        suspiciousSection.style.display = 'none';
                    }
                })
                .catch(err => {
                    console.error('加载数据失败:', err);
                });
        }
        
        // 初始加载
        loadData();
        
        // 自动刷新
        setInterval(loadData, 5000);
        
        // 清理日志
        function clearLogs() {
            if (confirm('确定要清理日志吗？将保留最近100条记录。')) {
                fetch('/api/clear-logs', { method: 'POST' })
                    .then(r => r.json())
                    .then(data => {
                        if (data.success) {
                            alert('日志已清理！');
                            loadData();
                        } else {
                            alert('清理失败: ' + data.error);
                        }
                    })
                    .catch(err => {
                        alert('清理失败: ' + err);
                    });
            }
        }
    </script>
</body>
</html>'''

def run_server(port=8765):
    server = HTTPServer(('0.0.0.0', port), DashboardHandler)
    print(f"Dashboard 运行在: http://localhost:{port}")
    print(f"按 Ctrl+C 停止")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
