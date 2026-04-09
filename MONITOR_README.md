# OpenClaw Monitor 使用说明

## 功能

监控OpenClaw的所有活动，包括：

1. **进程监控** - 监控OpenClaw进程的启动和退出
2. **日志监控** - 实时监控日志文件的变化
3. **会话监控** - 监控AI会话的变化
4. **网络监控** - 监控网络连接的变化
5. **文件监控** - 监控Desktop、Documents、Downloads目录的文件变化
6. **安全评分** - 自动分析活动并给出安全评分

---

## 快速开始

### 访问Dashboard面板

打开浏览器访问：**http://localhost:8765**

Dashboard会自动刷新，显示：
- 🔢 安全评分（0-100分）
- 📊 系统状态
- 📋 最近事件
- ⚠️ 可疑活动

---

## 安装

### 完整安装（推荐）

```bash
cd /Users/apple/编程/trae/openclaw
./install_all.sh
```

这会安装：
- 监控服务（后台运行）
- Dashboard面板（网页界面）

---

## 使用方法

### 1. Dashboard面板（推荐）

打开浏览器访问：**http://localhost:8765**

Dashboard会显示：
- **安全评分**：0-100分，分数越高越安全
- **状态**：安全/正常/注意/警告
- **原因**：如果有问题，会显示具体原因

#### 评分说明

| 分数 | 状态 | 说明 |
|-----|------|------|
| 90-100 | 🟢 安全 | 系统运行正常，无异常 |
| 70-89 | 🔵 正常 | 有少量活动，但正常 |
| 50-69 | 🟠 注意 | 有一些可疑活动，需要关注 |
| 0-49 | 🔴 警告 | 发现异常活动，需要立即检查 |

### 2. 命令行查看

```bash
# 显示最近50条记录
./view_monitor.sh

# 实时监控（按Ctrl+C退出）
./view_monitor.sh -f

# 显示今天的记录
./view_monitor.sh -t

# 显示统计信息
./view_monitor.sh -s

# 搜索关键词
./view_monitor.sh -g "mkdir"

# 显示错误记录
./view_monitor.sh -e
```

---

## 日志文件

监控日志保存在隐藏目录中，不容易被发现：
- `~/.local/share/openclaw_monitor/monitor.log` - 主监控日志
- `~/.local/share/openclaw_monitor/dashboard_stdout.log` - Dashboard输出

**注意**：日志不放在 `~/.openclaw/` 目录下，避免被OpenClaw发现。

---

## 管理服务

### 查看服务状态

```bash
launchctl list | grep openclaw
```

### 停止服务

```bash
# 停止监控
launchctl unload ~/Library/LaunchAgents/com.user.openclaw-monitor.plist

# 停止Dashboard
launchctl unload ~/Library/LaunchAgents/com.user.openclaw-dashboard.plist
```

### 启动服务

```bash
# 启动监控
launchctl load ~/Library/LaunchAgents/com.user.openclaw-monitor.plist

# 启动Dashboard
launchctl load ~/Library/LaunchAgents/com.user.openclaw-dashboard.plist
```

---

## 可疑活动检测

监控会自动检测以下可疑活动：

| 活动 | 说明 |
|-----|------|
| `mkdir.*Desktop` | 在桌面创建文件夹 |
| `open.*Photo` | 打开Photo Booth |
| `camera` | 摄像头相关操作 |
| `exec.*rm` | 删除文件命令 |
| `spawn` | 启动新进程 |
| `shell.*command` | 执行Shell命令 |
| `未命名` | 创建"未命名"文件夹 |

---

## 文件列表

| 文件 | 说明 |
|-----|------|
| `openclaw_monitor.py` | 主监控程序 |
| `dashboard.py` | Dashboard网页面板 |
| `view_monitor.sh` | 日志查看工具 |
| `install_all.sh` | 完整安装脚本 |
| `start_dashboard.sh` | 启动Dashboard |
| `com.user.openclaw-monitor.plist` | 监控服务配置 |
| `com.user.openclaw-dashboard.plist` | Dashboard服务配置 |

---

## 常见问题

### Q: Dashboard打不开？

检查服务是否运行：
```bash
launchctl list | grep openclaw
```

如果没有运行，重新安装：
```bash
./install_all.sh
```

### Q: 如何查看历史记录？

```bash
./view_monitor.sh -a    # 所有记录
./view_monitor.sh -t    # 今天记录
```

### Q: 如何清理日志？

```bash
# 清理监控日志
> ~/.local/share/openclaw_monitor/monitor.log
```

### Q: 监控会占用多少资源？

- 内存：约 10-30 MB
- CPU：< 1%
- 磁盘：日志会持续增长，建议定期清理
