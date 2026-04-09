#!/usr/bin/env python3
"""
OpenClaw Monitor - 监控OpenClaw的所有活动
"""

import os
import sys
import json
import time
import subprocess
import hashlib
from datetime import datetime
from pathlib import Path
from threading import Thread
import queue

class OpenClawMonitor:
    def __init__(self):
        self.openclaw_dir = Path.home() / ".openclaw"
        self.log_dir = self.openclaw_dir / "logs"
        self.sessions_dir = self.openclaw_dir / "agents" / "main" / "sessions"
        
        # 监控日志放在隐藏的系统目录，不容易被发现
        self.monitor_dir = Path.home() / ".local" / "share" / "openclaw_monitor"
        self.monitor_dir.mkdir(parents=True, exist_ok=True)
        
        self.monitor_log = self.monitor_dir / "monitor.log"
        self.running = True
        self.file_hashes = {}
        self.command_queue = queue.Queue()
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}\n"
        print(log_line.strip())
        with open(self.monitor_log, "a") as f:
            f.write(log_line)
    
    def get_file_hash(self, filepath):
        try:
            with open(filepath, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None
    
    def monitor_process(self):
        """监控OpenClaw进程"""
        self.log("开始监控OpenClaw进程...")
        last_pids = set()
        
        while self.running:
            try:
                result = subprocess.run(
                    ["pgrep", "-f", "openclaw"],
                    capture_output=True, text=True
                )
                current_pids = set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()
                
                new_pids = current_pids - last_pids
                gone_pids = last_pids - current_pids
                
                for pid in new_pids:
                    if pid:
                        self.log(f"新OpenClaw进程启动: PID={pid}", "PROCESS")
                        self.get_process_info(pid)
                
                for pid in gone_pids:
                    if pid:
                        self.log(f"OpenClaw进程退出: PID={pid}", "PROCESS")
                
                last_pids = current_pids
                
            except Exception as e:
                self.log(f"监控进程错误: {e}", "ERROR")
            
            time.sleep(5)
    
    def get_process_info(self, pid):
        """获取进程详细信息"""
        try:
            result = subprocess.run(
                ["ps", "-p", pid, "-o", "pid,ppid,user,%cpu,%mem,command"],
                capture_output=True, text=True
            )
            self.log(f"进程信息:\n{result.stdout}", "PROCESS_INFO")
        except:
            pass
    
    def monitor_logs(self):
        """监控日志文件变化"""
        self.log("开始监控OpenClaw日志文件...")
        
        log_files = [
            self.log_dir / "gateway.log",
            self.log_dir / "gateway.err.log",
        ]
        
        file_positions = {}
        
        for log_file in log_files:
            if log_file.exists():
                file_positions[log_file] = log_file.stat().st_size
        
        while self.running:
            for log_file in log_files:
                if not log_file.exists():
                    continue
                
                try:
                    current_size = log_file.stat().st_size
                    last_position = file_positions.get(log_file, 0)
                    
                    if current_size > last_position:
                        with open(log_file, "r") as f:
                            f.seek(last_position)
                            new_content = f.read()
                            
                            for line in new_content.split("\n"):
                                if line.strip():
                                    self.parse_log_line(log_file.name, line)
                        
                        file_positions[log_file] = current_size
                    
                except Exception as e:
                    self.log(f"监控日志错误 {log_file}: {e}", "ERROR")
            
            time.sleep(1)
    
    def parse_log_line(self, filename, line):
        """解析日志行"""
        keywords = ["exec", "mkdir", "open", "camera", "spawn", "run", "command", "shell"]
        
        for keyword in keywords:
            if keyword.lower() in line.lower():
                self.log(f"[{filename}] {line}", "ACTIVITY")
                break
    
    def monitor_sessions(self):
        """监控会话文件变化"""
        self.log("开始监控OpenClaw会话文件...")
        
        while self.running:
            try:
                if self.sessions_dir.exists():
                    for session_file in self.sessions_dir.glob("*.jsonl"):
                        current_hash = self.get_file_hash(session_file)
                        
                        if session_file not in self.file_hashes:
                            self.file_hashes[session_file] = current_hash
                        elif self.file_hashes[session_file] != current_hash:
                            self.log(f"会话文件变化: {session_file.name}", "SESSION")
                            self.file_hashes[session_file] = current_hash
                            self.parse_session_changes(session_file)
            
            except Exception as e:
                self.log(f"监控会话错误: {e}", "ERROR")
            
            time.sleep(2)
    
    def parse_session_changes(self, session_file):
        """解析会话变化"""
        try:
            with open(session_file, "r") as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1]
                    try:
                        data = json.loads(last_line)
                        role = data.get("role", "unknown")
                        content = data.get("content", "")[:200]
                        timestamp = data.get("timestamp", "")
                        
                        self.log(f"会话更新 [{timestamp}] [{role}]: {content}...", "SESSION_DETAIL")
                    except:
                        pass
        except:
            pass
    
    def monitor_network(self):
        """监控网络连接"""
        self.log("开始监控OpenClaw网络连接...")
        last_connections = set()
        
        while self.running:
            try:
                result = subprocess.run(
                    ["lsof", "-i", "-P"],
                    capture_output=True, text=True
                )
                
                openclaw_connections = set()
                for line in result.stdout.split("\n"):
                    if "node" in line.lower() or "openclaw" in line.lower():
                        parts = line.split()
                        if len(parts) >= 9:
                            conn = (parts[0], parts[8])
                            openclaw_connections.add(conn)
                
                new_connections = openclaw_connections - last_connections
                closed_connections = last_connections - openclaw_connections
                
                for conn in new_connections:
                    self.log(f"新网络连接: {conn[0]} -> {conn[1]}", "NETWORK")
                
                for conn in closed_connections:
                    self.log(f"网络连接关闭: {conn[0]} -> {conn[1]}", "NETWORK")
                
                last_connections = openclaw_connections
                
            except Exception as e:
                self.log(f"监控网络错误: {e}", "ERROR")
            
            time.sleep(10)
    
    def monitor_file_operations(self):
        """监控文件系统操作"""
        self.log("开始监控文件系统操作...")
        
        watch_dirs = [
            Path.home() / "Desktop",
            Path.home() / "Documents",
            Path.home() / "Downloads",
        ]
        
        dir_states = {}
        
        for watch_dir in watch_dirs:
            if watch_dir.exists():
                dir_states[watch_dir] = self.get_dir_state(watch_dir)
        
        while self.running:
            for watch_dir in watch_dirs:
                if not watch_dir.exists():
                    continue
                
                try:
                    current_state = self.get_dir_state(watch_dir)
                    last_state = dir_states.get(watch_dir, {})
                    
                    new_files = set(current_state.keys()) - set(last_state.keys())
                    deleted_files = set(last_state.keys()) - set(current_state.keys())
                    modified_files = []
                    
                    for filepath in set(current_state.keys()) & set(last_state.keys()):
                        if current_state[filepath] != last_state[filepath]:
                            modified_files.append(filepath)
                    
                    for filepath in new_files:
                        self.log(f"新文件创建: {filepath}", "FILE_CREATE")
                    
                    for filepath in deleted_files:
                        self.log(f"文件删除: {filepath}", "FILE_DELETE")
                    
                    for filepath in modified_files:
                        self.log(f"文件修改: {filepath}", "FILE_MODIFY")
                    
                    dir_states[watch_dir] = current_state
                
                except Exception as e:
                    self.log(f"监控目录错误 {watch_dir}: {e}", "ERROR")
            
            time.sleep(5)
    
    def get_dir_state(self, directory):
        """获取目录状态"""
        state = {}
        try:
            for item in directory.rglob("*"):
                if item.is_file():
                    try:
                        state[str(item)] = (item.stat().st_size, item.stat().st_mtime)
                    except:
                        pass
        except:
            pass
        return state
    
    def start(self):
        """启动监控"""
        self.log("=" * 60)
        self.log("OpenClaw Monitor 启动")
        self.log(f"监控目录: {self.openclaw_dir}")
        self.log(f"日志文件: {self.monitor_log}")
        self.log("=" * 60)
        
        threads = [
            Thread(target=self.monitor_process, daemon=True),
            Thread(target=self.monitor_logs, daemon=True),
            Thread(target=self.monitor_sessions, daemon=True),
            Thread(target=self.monitor_network, daemon=True),
            Thread(target=self.monitor_file_operations, daemon=True),
        ]
        
        for t in threads:
            t.start()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.log("收到停止信号，正在关闭...")
            self.running = False

def main():
    monitor = OpenClawMonitor()
    monitor.start()

if __name__ == "__main__":
    main()
