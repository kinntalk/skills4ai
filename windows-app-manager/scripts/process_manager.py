import os
import subprocess
import json
import time
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path

sys_path = os.path.dirname(__file__)
if sys_path not in os.sys.path:
    os.sys.path.insert(0, sys_path)

from constants import get_process_keywords


ALLOWED_EXECUTABLES = frozenset(["powershell.exe", "tasklist", "taskkill", "cmd.exe"])


def _validate_executable(exe_path: str) -> bool:
    if not exe_path:
        return False
    exe_name = Path(exe_path).name.lower()
    return exe_name in ALLOWED_EXECUTABLES


def _sanitize_path(path: str) -> str:
    if not path:
        return ""
    try:
        resolved = Path(path).resolve()
        path = str(resolved)
    except (OSError, ValueError):
        return ""
    dangerous_chars = [';', '|', '&', '$', '`', '\n', '\r']
    for char in dangerous_chars:
        path = path.replace(char, '')
    return path


def _sanitize_keyword(keyword: str) -> str:
    if not keyword:
        return ""
    keyword = keyword.strip()
    dangerous_chars = [';', '|', '&', '$', '`', '\n', '\r', '"', "'"]
    for char in dangerous_chars:
        keyword = keyword.replace(char, '')
    return keyword[:100]


def _sanitize_pid(pid: Any) -> int:
    try:
        pid_int = int(pid)
        return pid_int if pid_int > 0 else 0
    except (ValueError, TypeError):
        return 0


class ProcessManager:
    _instance = None
    _process_cache: Optional[List[Dict]] = None
    _process_cache_time: float = 0
    _cache_ttl: int = 2

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

    def _run_powershell(self, command: str, timeout: int = 10) -> Tuple[bool, str]:
        if not _validate_executable("powershell.exe"):
            return False, "PowerShell not allowed"
        try:
            result = subprocess.run(
                ["powershell.exe", "-Command", command],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout
            )
            return result.returncode == 0, result.stdout.strip()
        except (subprocess.TimeoutExpired, OSError) as e:
            return False, str(e)

    def _run_system_tool(self, exe_name: str, args: List[str], timeout: int = 10, encoding: str = "gbk", creationflags: int = 0) -> Tuple[bool, str]:
        if not _validate_executable(exe_name):
            return False, f"{exe_name} not allowed"
        try:
            run_kwargs = {
                "capture_output": True,
                "text": True,
                "encoding": encoding,
                "errors": "replace",
                "timeout": timeout
            }
            if creationflags:
                run_kwargs["creationflags"] = creationflags
            result = subprocess.run([exe_name] + args, **run_kwargs)
            return result.returncode == 0, result.stdout.strip()
        except (subprocess.TimeoutExpired, OSError) as e:
            return False, str(e)

    def _run_tasklist(self, args: List[str], timeout: int = 30) -> Tuple[bool, str]:
        return self._run_system_tool("tasklist", args, timeout, encoding="gbk")

    def _run_taskkill(self, args: List[str], timeout: int = 10) -> Tuple[bool, str]:
        return self._run_system_tool("taskkill", args, timeout, encoding="gbk")

    def _run_cmd(self, command: str, timeout: int = 5) -> Tuple[bool, str]:
        flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
        return self._run_system_tool("cmd.exe", ["/c", command], timeout, encoding="utf-8", creationflags=flags)

    def _invalidate_cache(self):
        self._process_cache = None

    def get_all_processes(self) -> List[Dict[str, str]]:
        now = time.time()
        if self._process_cache and (now - self._process_cache_time) < self._cache_ttl:
            return self._process_cache

        success, output = self._run_powershell(
            "Get-Process | Select-Object Name, Id | ConvertTo-Json -Compress",
            timeout=5
        )

        if success and output:
            try:
                data = json.loads(output)
                if isinstance(data, dict):
                    data = [data]
                processes = [{"name": p.get("Name", ""), "pid": str(p.get("Id", ""))} for p in data]
                self._process_cache = processes
                self._process_cache_time = now
                return processes
            except json.JSONDecodeError:
                pass

        return self._get_all_processes_fallback()

    def _get_all_processes_fallback(self) -> List[Dict[str, str]]:
        success, output = self._run_tasklist(["/fo", "csv"], timeout=30)

        if not success or not output:
            return []

        processes = []
        lines = output.strip().split("\n")
        for line in lines[1:]:
            parts = line.strip('"').split('","')
            if len(parts) >= 2:
                processes.append({"name": parts[0].strip('"'), "pid": parts[1].strip('"')})
        return processes

    def find_process_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        keyword_lower = _sanitize_keyword(keyword).lower()
        if not keyword_lower:
            return []
        return [p for p in self.get_all_processes() if keyword_lower in p["name"].lower()]

    def find_process_exact(self, process_name: str) -> List[Dict[str, Any]]:
        process_name_lower = _sanitize_keyword(process_name).lower()
        if not process_name_lower:
            return []
        if not process_name_lower.endswith(".exe"):
            process_name_lower += ".exe"
        return [p for p in self.get_all_processes() if p["name"].lower() == process_name_lower]

    def is_process_running(self, keyword: str) -> bool:
        return len(self.find_process_by_keyword(keyword)) > 0

    def find_any_matching_processes(self, app_name: str, exe_path: str = None) -> List[Dict[str, Any]]:
        keywords = get_process_keywords(app_name)

        if exe_path:
            keywords.append(Path(exe_path).stem.lower())
            keywords.append(Path(exe_path).parent.name.lower())

        all_results = []
        for kw in set(keywords):
            if len(kw) >= 2:
                for proc in self.find_process_by_keyword(kw):
                    if proc not in all_results:
                        all_results.append(proc)
        return all_results

    def kill_process_by_name(self, process_name: str) -> Tuple[bool, str]:
        process_name = _sanitize_keyword(process_name)
        if not process_name:
            return False, "Invalid process name"
        if not process_name.lower().endswith(".exe"):
            process_name = process_name.split(".")[0] + ".exe"

        success, output = self._run_taskkill(["/F", "/IM", process_name], timeout=10)

        if success:
            time.sleep(0.5)
            self._invalidate_cache()
            return True, f"Terminated {process_name}"
        return False, f"Failed: {output}"

    def kill_process_by_pid(self, pid: int) -> Tuple[bool, str]:
        pid = _sanitize_pid(pid)
        if pid <= 0:
            return False, "Invalid PID"

        success, output = self._run_taskkill(["/F", "/PID", str(pid)], timeout=10)

        if success:
            self._invalidate_cache()
            return True, f"Terminated PID {pid}"
        return False, f"Failed: {output}"

    def start_application(self, exe_path: str, working_dir: Optional[str] = None) -> Tuple[bool, str]:
        exe_path = _sanitize_path(exe_path)
        if not exe_path or not Path(exe_path).exists():
            return False, "Invalid or non-existent path"

        try:
            subprocess.Popen(
                [exe_path],
                cwd=working_dir,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
                close_fds=True
            )
            if self._try_confirm_start(exe_path):
                return True, "Started"
        except (OSError, subprocess.SubprocessError) as e:
            pass

        ps_cmd = f'Start-Process -FilePath "{exe_path}"'
        if working_dir:
            working_dir = _sanitize_path(working_dir)
            ps_cmd += f' -WorkingDirectory "{working_dir}"'
        ps_cmd += ' -ErrorAction SilentlyContinue'

        success, _ = self._run_powershell(ps_cmd, timeout=5)

        if success and self._try_confirm_start(exe_path):
            return True, "Started"

        return False, "Failed to start"

    def _try_confirm_start(self, exe_path: str) -> bool:
        if self._wait_for_process(exe_path, max_wait=2.0, interval=0.2):
            self._invalidate_cache()
            return True
        return False

    def _wait_for_process(self, exe_path: str, max_wait: float = 2.0, interval: float = 0.2) -> bool:
        keywords = self._get_startup_check_keywords(exe_path)
        start_time = time.time()
        while time.time() - start_time < max_wait:
            self._process_cache = None
            for kw in keywords:
                if self._check_process_by_name(kw):
                    return True
            time.sleep(interval)
        return False

    def _get_startup_check_keywords(self, exe_path: str) -> List[str]:
        keywords = []
        exe_name_lower = Path(exe_path).stem.lower()
        keywords.append(exe_name_lower)
        
        if exe_name_lower.endswith("launcher"):
            base_name = exe_name_lower[:-8]
            if len(base_name) >= 2:
                keywords.append(base_name)
        
        parent_dir = Path(exe_path).parent.name.lower()
        if len(parent_dir) >= 2:
            keywords.append(parent_dir)
        
        return list(set(keywords))

    def _check_process_by_name(self, exe_name_lower: str) -> bool:
        return any(exe_name_lower in p["name"].lower() for p in self.get_all_processes())

    def _verify_process_started(self, exe_path: str) -> bool:
        exe_name_lower = Path(exe_path).stem.lower()
        return self._check_process_by_name(exe_name_lower)

    def kill_all_matching(self, keyword: str) -> Tuple[bool, str]:
        processes = self.find_process_by_keyword(keyword)
        if not processes:
            return False, f"No process found matching '{keyword}'"

        killed, failed = [], []
        for proc in processes:
            pid = _sanitize_pid(proc["pid"])
            if pid <= 0:
                continue
            success, _ = self.kill_process_by_pid(pid)
            if success:
                killed.append(proc["pid"])
            else:
                failed.append(f"{proc['name']} ({proc['pid']})")

        if not failed:
            return True, f"Killed {len(killed)} process(es)"
        return False, f"Killed {len(killed)}, failed: {', '.join(failed)}"


def get_process_manager() -> ProcessManager:
    return ProcessManager()
