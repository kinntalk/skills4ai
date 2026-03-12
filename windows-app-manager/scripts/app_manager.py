import sys
import os
import re
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from constants import _t, get_process_keywords, get_app_id, is_login_required
from process_manager import get_process_manager
from path_finder import get_path_finder
from config_manager import get_config_manager


class AppManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.process_manager = get_process_manager()
        self.path_finder = get_path_finder()
        self.config_manager = get_config_manager()

    def parse_command(self, command: str) -> tuple:
        command = command.strip().lower()

        start_patterns = [
            r"启动(.+)",
            r"打开(.+)",
            r"运行(.+)",
            r"start\s+(.+)",
            r"launch\s+(.+)",
            r"open\s+(.+)",
        ]

        stop_patterns = [
            r"关闭(.+)",
            r"停止(.+)",
            r"退出(.+)",
            r"stop\s+(.+)",
            r"close\s+(.+)",
            r"quit\s+(.+)",
            r"exit\s+(.+)",
        ]

        for pattern in start_patterns:
            match = re.search(pattern, command)
            if match:
                return "start", match.group(1).strip()

        for pattern in stop_patterns:
            match = re.search(pattern, command)
            if match:
                return "stop", match.group(1).strip()

        if "启动" in command or "打开" in command or "运行" in command or "start" in command or "launch" in command:
            parts = command.split()
            if len(parts) >= 2:
                return "start", parts[-1]

        if "关闭" in command or "停止" in command or "stop" in command or "close" in command:
            parts = command.split()
            if len(parts) >= 2:
                return "stop", parts[-1]

        return "unknown", command

    def find_path(self, app_name: str) -> tuple:
        path, method = self.path_finder.find_application(app_name)
        if not path:
            saved_app = self.config_manager.find_app_by_keyword(app_name)
            if saved_app:
                path = saved_app.get("path")
        return path, method

    def check_running(self, app_name: str, exe_path: str = None) -> list:
        keywords = get_process_keywords(app_name)

        if exe_path:
            try:
                exe_dir = Path(exe_path).parent
                if exe_dir and exe_dir != Path(exe_path):
                    dir_name = exe_dir.name.lower()
                    if dir_name and len(dir_name) >= 2:
                        keywords.append(dir_name)
            except (ValueError, OSError):
                pass

            try:
                exe_base = Path(exe_path).stem.lower()
                if exe_base and len(exe_base) >= 2:
                    keywords.append(exe_base)
            except (ValueError, OSError):
                pass

        keywords = list(set([k for k in keywords if len(k) >= 2]))

        all_processes = self.process_manager.get_all_processes()

        matching_processes = []
        for proc in all_processes:
            proc_name_lower = proc["name"].lower()
            for kw in keywords:
                if kw in proc_name_lower:
                    matching_processes.append(proc)
                    break

        return matching_processes

    def start_app(self, app_name: str, path: str = None) -> dict:
        app_id = get_app_id(app_name)
        need_login = is_login_required(app_name)

        if not path:
            path, _ = self.find_path(app_name)

        if not path:
            return {
                "success": False,
                "app_id": app_id,
                "need_login": need_login,
                "message": _t("cannot_find", app_name=app_name)
            }

        if not os.path.exists(path):
            return {
                "success": False,
                "app_id": app_id,
                "need_login": need_login,
                "message": f"Path not found: {path}"
            }

        exe_path = path

        running = self.check_running(app_name, exe_path)
        if running:
            return {
                "success": True,
                "app_id": app_id,
                "need_login": need_login,
                "message": _t("already_running", app_name=app_name),
                "processes": [{"name": p["name"], "pid": p["pid"]} for p in running]
            }

        working_dir = os.path.dirname(exe_path) if os.path.isfile(exe_path) else None
        success, msg = self.process_manager.start_application(exe_path, working_dir)

        if success:
            running = self.check_running(app_name, exe_path)
            self.config_manager.save_app_info(app_name, exe_path)
            result = {
                "success": True,
                "app_id": app_id,
                "need_login": need_login,
                "message": _t("started_success", app_name=app_name)
            }
            if running:
                result["processes"] = [{"name": p["name"], "pid": p["pid"]} for p in running]
            return result

        return {
            "success": False,
            "app_id": app_id,
            "need_login": need_login,
            "message": _t("failed_to_start", message=msg)
        }

    def stop_app(self, app_name: str) -> dict:
        app_id = get_app_id(app_name)

        app_info = self.config_manager.find_app_by_keyword(app_name)
        exe_path = app_info.get("path") if app_info else None

        running = self.check_running(app_name, exe_path)

        if not running:
            return {
                "success": True,
                "app_id": app_id,
                "message": _t("not_running", app_name=app_name)
            }

        killed_pids = []
        failed_pids = []

        for proc in running:
            pid = int(proc["pid"])
            success, msg = self.process_manager.kill_process_by_pid(pid)
            if success:
                killed_pids.append(proc["pid"])
            else:
                failed_pids.append(f"{proc['name']} ({proc['pid']})")

        if failed_pids:
            proc_names = list(set([p["name"].replace(".exe", "") for p in running]))
            for proc_name in proc_names:
                success, msg = self.process_manager.kill_all_matching(proc_name)
                if success:
                    killed_pids.extend([p["pid"] for p in running if p["name"].replace(".exe", "") == proc_name])

        still_running = self.check_running(app_name, exe_path)

        if still_running:
            return {
                "success": False,
                "app_id": app_id,
                "message": "Some processes still running",
                "processes": [{"name": p["name"], "pid": p["pid"]} for p in still_running]
            }
        else:
            return {
                "success": True,
                "app_id": app_id,
                "message": _t("stopped_success", app_name=app_name)
            }

    def list_apps(self) -> dict:
        apps = self.config_manager.list_apps()
        return {"success": True, "apps": apps, "message": _t("found_apps", count=len(apps))}

    def search_app(self, keyword: str) -> dict:
        results = self.path_finder.search_applications(keyword)
        return {"success": True, "results": results, "message": _t("found_results", count=len(results))}

    def execute(self, command: str) -> dict:
        action, target = self.parse_command(command)

        if action == "start":
            return self.start_app(target)
        elif action == "stop":
            return self.stop_app(target)
        elif command == "list" or command == "ls":
            return self.list_apps()
        elif command.startswith("search "):
            keyword = command[7:].strip()
            return self.search_app(keyword)
        else:
            return {"success": False, "message": f"Unknown command: {command}"}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "message": "Usage: python app_manager.py <command>",
            "commands": ["start <app>", "stop <app>", "list", "search <keyword>"]
        }, indent=2))
        return

    manager = AppManager()
    command = " ".join(sys.argv[1:])
    result = manager.execute(command)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result.get("success", False) else 1)


if __name__ == "__main__":
    main()
