# OpenClaw Monitor

🛡️ **一个用于监控 OpenClaw AI Agent 活动的安全工具**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: macOS](https://img.shields.io/badge/Platform-macOS-lightgrey.svg)](https://www.apple.com/macos)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)

---

## 📖 目录

- [背景与痛点](#背景与痛点)
- [解决方案](#解决方案)
- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [安装部署](#安装部署)
- [使用指南](#使用指南)
- [安全评分系统](#安全评分系统)
- [技术架构](#技术架构)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## 背景与痛点

### 什么是 OpenClaw？

[OpenClaw](https://github.com/openclaw/openclaw)，可以执行各种系统操作，包括：
- 执行 Shell 命令
- 读写文件
- 打开应用程序
- 控制摄像头
- 网络请求

### 为什么需要监控？

随着 AI Agent 的普及，越来越多的用户开始使用 OpenClaw 等工具来自动化任务。然而，这也带来了安全风险：

| 风险类型 | 描述 |
|---------|------|
| 🔴 **未授权操作** | AI Agent 可能在用户不知情的情况下执行敏感操作 |
| 🔴 **远程控制** | 如果 AI Agent 被入侵，攻击者可以远程控制您的电脑 |
| 🔴 **隐私泄露** | AI Agent 可能访问摄像头、麦克风等敏感设备 |
| 🔴 **数据丢失** | AI Agent 可能删除或修改重要文件 |

### 真实案例

> **用户故事**：某用户回家后发现桌面多了几个"未命名文件夹"，Photo Booth 被打开，摄像头指示灯亮过。用户怀疑电脑被入侵，但无法确定是谁执行了这些操作。

这正是 OpenClaw Monitor 诞生的原因 —— **让用户清楚地知道 AI Agent 在做什么**。

---

## 解决方案

OpenClaw Monitor 是一个**轻量级、非侵入式**的监控工具，专门用于监控 OpenClaw 的所有活动。

### 核心设计理念

1. **非侵入式监控** - 不修改 OpenClaw 本身，独立运行
2. **全面记录** - 记录所有进程、网络、文件操作
3. **智能分析** - 自动检测可疑活动并给出安全评分
4. **易于使用** - 提供网页面板，小白也能看懂

### 与其他方案的对比

| 方案 | 优点 | 缺点 |
|-----|------|------|
| 系统日志 | 官方支持 | 信息分散，难以理解 |
| 进程监控工具 | 功能强大 | 需要专业知识 |
| **OpenClaw Monitor** | **专门针对 OpenClaw，易用** | 仅支持 macOS |

---

## 功能特性

### 📊 实时监控

- **进程监控** - 监控 OpenClaw 进程的启动和退出
- **日志监控** - 实时监控 OpenClaw 日志的变化
- **会话监控** - 监控 AI 会话的变化
- **网络监控** - 监控网络连接的变化
- **文件监控** - 监控 Desktop、Documents、Downloads 目录

### 🎯 智能分析

- **安全评分** - 0-100 分，分数越高越安全
- **可疑活动检测** - 自动检测并高亮可疑操作
- **异常告警** - 发现异常时自动提醒

### 🖥️ 网页面板

- **实时刷新** - 每 5 秒自动更新
- **可视化展示** - 清晰的图表和状态指示
- **一键清理** - 轻松管理日志文件

### 🔒 安全设计

- **独立存储** - 日志存储在独立目录，不易被发现
- **只读监控** - 不修改 OpenClaw 的任何文件
- **低资源占用** - 内存占用 < 30MB，CPU < 1%

---

## 快速开始

### 前置要求

- macOS 10.15+
- Python 3.8+
- OpenClaw 已安装

### 一键安装

```bash
# 克隆仓库
git clone https://github.com/chinahui/openclaw-monitor.git
cd openclaw-monitor

# 安装并启动
./install_all.sh
```

### 访问面板

安装完成后，打开浏览器访问：

```
http://localhost:8765
```

---

## 安装部署

### 方式一：完整安装（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/chinahui/openclaw-monitor.git
cd openclaw-monitor

# 2. 运行安装脚本
./install_all.sh
```

这会安装：
- 监控服务（后台运行）
- Dashboard 网页面板

### 方式二：手动安装

```bash
# 1. 克隆仓库
git clone https://github.com/chinahui/openclaw-monitor.git
cd openclaw-monitor

# 2. 安装监控服务
cp com.user.openclaw-monitor.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.user.openclaw-monitor.plist

# 3. 安装 Dashboard 服务
cp com.user.openclaw-dashboard.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.user.openclaw-dashboard.plist
```

### 方式三：仅运行监控（无网页面板）

```bash
# 前台运行
python3 openclaw_monitor.py

# 或后台运行
nohup python3 openclaw_monitor.py &
```

### 验证安装

```bash
# 检查服务状态
launchctl list | grep openclaw

# 应该看到两个服务
# 12345  0  com.user.openclaw-monitor
# 12346  0  com.user.openclaw-dashboard
```

---

## 使用指南

### 网页面板

打开浏览器访问 `http://localhost:8765`，您会看到：
<img width="1100" height="876" alt="image" src="https://github.com/user-attachments/assets/804010a7-1da5-4746-a8bd-08cc708ce111" />


#### 安全评分

| 分数 | 状态 | 说明 |
|-----|------|------|
| 90-100 | 🟢 安全 | 系统运行正常，无异常 |
| 70-89 | 🔵 正常 | 有少量活动，但正常 |
| 50-69 | 🟠 注意 | 有一些可疑活动，需要关注 |
| 0-49 | 🔴 警告 | 发现异常活动，需要立即检查 |

#### 状态监控

- OpenClaw 运行状态
- 进程数量
- 最近事件数
- 错误和可疑活动数

#### 日志管理

- 查看日志文件大小
- 一键清理日志

### 命令行工具

```bash
# 查看最近 50 条记录
./view_monitor.sh

# 实时监控（按 Ctrl+C 退出）
./view_monitor.sh -f

# 显示今天的记录
./view_monitor.sh -t

# 显示统计信息
./view_monitor.sh -s

# 搜索关键词
./view_monitor.sh -g "mkdir"

# 显示错误记录
./view_monitor.sh -e

# 显示帮助
./view_monitor.sh -h
```

### 服务管理

```bash
# 查看服务状态
launchctl list | grep openclaw

# 停止监控
launchctl unload ~/Library/LaunchAgents/com.user.openclaw-monitor.plist

# 停止 Dashboard
launchctl unload ~/Library/LaunchAgents/com.user.openclaw-dashboard.plist

# 启动监控
launchctl load ~/Library/LaunchAgents/com.user.openclaw-monitor.plist

# 启动 Dashboard
launchctl load ~/Library/LaunchAgents/com.user.openclaw-dashboard.plist
```

---

## 安全评分系统

### 评分算法

初始分数为 100，根据以下规则扣分：

| 事件类型 | 扣分规则 |
|---------|---------|
| 错误 | 每个错误扣 5 分，最多扣 30 分 |
| 可疑活动 | 每个可疑活动扣 10 分，最多扣 50 分 |
| 文件操作频繁 | 超过 10 次后，每次扣 2 分，最多扣 20 分 |
| 网络连接较多 | 超过 20 次后，每次扣 1 分，最多扣 10 分 |

### 可疑活动检测

以下活动会被标记为可疑：

| 活动 | 正则表达式 |
|-----|-----------|
| 在桌面创建文件夹 | `mkdir.*Desktop` |
| 打开 Photo Booth | `open.*Photo` |
| 摄像头操作 | `camera` |
| 删除文件 | `exec.*rm` |
| 启动新进程 | `spawn` |
| 执行 Shell 命令 | `shell.*command` |
| 创建"未命名"文件夹 | `未命名` |

---

## 技术架构

### 文件结构

```
openclaw-monitor/
├── openclaw_monitor.py      # 主监控程序
├── dashboard.py              # 网页面板
├── view_monitor.sh           # 日志查看工具
├── install_all.sh            # 一键安装脚本
├── start_dashboard.sh        # 启动 Dashboard
├── com.user.openclaw-monitor.plist    # 监控服务配置
├── com.user.openclaw-dashboard.plist  # Dashboard 服务配置
├── MONITOR_README.md         # 详细使用说明
└── README.md                 # 本文件
```

### 数据流

```
OpenClaw 活动
      ↓
监控程序捕获 (openclaw_monitor.py)
      ↓
写入日志文件 (~/.local/share/openclaw_monitor/)
      ↓
Dashboard 读取 (dashboard.py)
      ↓
网页展示 (http://localhost:8765)
```

### 日志存储

日志文件存储在独立目录，避免被 OpenClaw 发现：

```
~/.local/share/openclaw_monitor/
├── monitor.log              # 主监控日志
├── monitor_stdout.log       # 标准输出
├── monitor_stderr.log       # 错误输出
├── dashboard_stdout.log     # Dashboard 输出
└── dashboard_stderr.log     # Dashboard 错误
```

---

## 常见问题

### Q: Dashboard 打不开？

检查服务是否运行：

```bash
launchctl list | grep openclaw
```

如果没有运行，重新安装：

```bash
./install_all.sh
```

### Q: 监控会占用多少资源？

- 内存：约 10-30 MB
- CPU：< 1%
- 磁盘：日志会持续增长，建议定期清理

### Q: 监控会影响 OpenClaw 吗？

不会。监控程序是独立的，只读取 OpenClaw 的日志文件，不修改任何内容。

### Q: 如何查看历史记录？

```bash
./view_monitor.sh -a    # 所有记录
./view_monitor.sh -t    # 今天记录
```

### Q: 如何清理日志？

方式一：在 Dashboard 点击"清理日志"按钮

方式二：命令行清理

```bash
> ~/.local/share/openclaw_monitor/monitor.log
```

### Q: 支持 Linux/Windows 吗？

目前仅支持 macOS。Linux/Windows 支持正在开发中。

---

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 开发环境

```bash
# 克隆仓库
git clone https://github.com/chinahui/openclaw-monitor.git
cd openclaw-monitor

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖（目前无外部依赖）
# pip install -r requirements.txt
```

### 提交代码

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 报告问题

请使用 [GitHub Issues](https://github.com/chinahui/openclaw-monitor/issues) 报告问题。

---

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

## 致谢

- 感谢 [OpenClaw](https://github.com/openclaw/openclaw) 团队
- 感谢所有贡献者

---

## 联系方式

- GitHub Issues: [https://github.com/chinahui/openclaw-monitor/issues](https://github.com/chinahui/openclaw-monitor/issues)

---

**⭐ 如果这个项目对您有帮助，请给一个 Star！**
