import os
from enum import Enum
from typing import Optional, Dict, List, Any
from pathlib import Path

class AppStatus(Enum):
    NOT_INSTALLED = "not_installed"
    INSTALLED = "installed"
    RUNNING = "running"
    CLOSED = "closed"
    UNKNOWN = "unknown"

class AppInfo:
    def __init__(self, name: str, path: str, status: AppStatus = AppStatus.UNKNOWN, pid: Optional[int] = None):
        self.name = name
        self.path = path
        self.status = status
        self.pid = pid
        self.last_updated = os.path.getmtime(path) if path and os.path.exists(path) else None

class AppStatusChecker:
    def __init__(self):
        self.app_cache: Dict[str, AppInfo] = {}
    
    def update_status(self, name: str, status: AppStatus, pid: Optional[int] = None, path: Optional[str] = None):
        if path and os.path.exists(path):
            self.app_cache[name] = AppInfo(name, path, status, pid)
        elif name in self.app_cache:
            self.app_cache[name].status = status
            if pid is not None:
                self.app_cache[name].pid = pid
        else:
            self.app_cache[name] = AppInfo(name, path, status, pid)
    
    def get_status(self, name: str) -> AppStatus:
        if name in self.app_cache:
            return self.app_cache[name].status
        return AppStatus.NOT_INSTALLED
    
    def get_info(self, name: str) -> Optional[AppInfo]:
        return self.app_cache.get(name)
    
    def is_installed(self, name: str) -> bool:
        status = self.get_status(name)
        return status in [AppStatus.INSTALLED, AppStatus.RUNNING]
    
    def is_running(self, name: str) -> bool:
        return self.get_status(name) == AppStatus.RUNNING
    
    def is_closed(self, name: str) -> bool:
        return self.get_status(name) == AppStatus.CLOSED

if __name__ == "__main__":
    checker = AppStatusChecker()
    
    checker.update_status("tabbit", AppStatus.INSTALLED, path="C:\\Users\\Xjh\\AppData\\Local\\Tabbit\\Application\\Tabbit.exe")
    checker.update_status("wechat", AppStatus.RUNNING, pid=12345, path="D:\\install\\Weixin\\Weixin.exe")
    checker.update_status("feishu", AppStatus.CLOSED, path="D:\\install\\Feishu\\Feishu.exe")
    
    print("状态检查测试:")
    print(f"  Tabbit: {checker.get_status('tabbit').value}")
    print(f"  WeChat: {checker.get_status('wechat').value}")
    print(f"  Feishu: {checker.get_status('feishu').value}")
    
    print(f"\n详细信息:")
    for name in ["tabbit", "wechat", "feishu"]:
        info = checker.get_info(name)
        if info:
            print(f"  {info.name}: {info.status.value}, PID: {info.pid}, Path: {info.path}")