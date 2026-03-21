import os
import subprocess
import json
import time
import string
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path

sys_path = os.path.dirname(__file__)
if sys_path not in os.sys.path:
    os.sys.path.insert(0, sys_path)

from constants import get_translated_names, COMMON_INSTALL_DIRS


class PathFinder:
    _instance = None
    _cache: Dict[str, Tuple[Optional[str], float]] = {}
    _cache_ttl: int = 300

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.standard_paths = self._get_standard_paths()
        self.common_locations = self._get_common_locations()
        self._config_cache: Optional[Dict] = None
        self._config_cache_time: float = 0

    def _run_powershell_and_get_path(self, cmd: str, timeout: int = 5) -> Optional[str]:
        try:
            result = subprocess.run(
                ["powershell.exe", "-Command", cmd],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout
            )
            if result.stdout.strip():
                path = result.stdout.strip().split('\n')[0].strip()
                if Path(path).exists():
                    return path
        except (subprocess.TimeoutExpired, OSError):
            pass
        return None
    
    def _search_deep(self, executables: List[str]) -> Optional[str]:
        exe_names_lower = [e.lower() for e in executables]
        
        if os.name == 'nt':
            drives = [f'{d}:' for d in string.ascii_uppercase if os.path.exists(f'{d}:')]
        else:
            drives = ['/']
        
        for drive in drives:
            found_paths = self._search_drive_root(drive, executables, max_depth=2)
            if found_paths:
                return found_paths[0]
        
        return None

    def _get_standard_paths(self) -> List[str]:
        paths = []
        
        if os.name == 'nt':
            drives = [f'{d}:' for d in string.ascii_uppercase if os.path.exists(f'{d}:')]
        else:
            drives = ['/']
        
        for drive in drives:
            if Path(drive).exists():
                program_dirs = self._get_program_dirs(drive)
                
                for pf in program_dirs:
                    if isinstance(pf, str):
                        p = Path(pf)
                    else:
                        p = pf
                    
                    if p.exists():
                        paths.append(str(p))
        
        return paths
    
    def _get_program_dirs(self, drive: str) -> List[str]:
        program_dirs = []
        
        if os.name == 'nt':
            program_dirs.extend([
                "Program Files",
                "Program Files (x86)",
                "ProgramW6432Node",
                "Program Files (ARM)",
                "Program Files (ARM64)",
            ])
            
            drives = [f'{d}:' for d in string.ascii_uppercase if os.path.exists(f'{d}:')]
            custom_dirs = ["install", "software", "apps", "application", "applications"]
            for drive in drives:
                for custom_dir in custom_dirs:
                    p = Path(drive) / custom_dir
                    if p.exists() and p.is_dir():
                        program_dirs.append(str(p))
            
            user_profile = os.environ.get('USERPROFILE', '')
            if user_profile and Path(user_profile).exists():
                user_dirs = [
                    Path(user_profile) / "AppData" / "Local",
                    Path(user_profile) / "AppData" / "Roaming",
                    Path(user_profile) / "AppData" / "LocalLow",
                ]
                for user_dir in user_dirs:
                    if user_dir.exists():
                        program_dirs.append(str(user_dir))
        else:
            program_dirs.extend([
                "usr",
                "usr/local",
                "opt",
                "Applications",
                "bin",
                "local/bin",
            ])
            
            home = os.environ.get('HOME', '')
            if home and Path(home).exists():
                home_dirs = [
                    Path(home) / ".local" / "bin",
                    Path(home) / ".local" / "share" / "applications",
                    Path(home) / "bin",
                    Path(home) / "Applications",
                ]
                for home_dir in home_dirs:
                    if home_dir.exists():
                        program_dirs.append(str(home_dir))
        
        return program_dirs
    
    def _search_drive_root(self, drive: str, executables: List[str], max_depth: int = 2) -> List[str]:
        found_paths = []
        drive_path = Path(drive)
        
        if not drive_path.exists():
            return found_paths
        
        try:
            for root, dirs, files in os.walk(drive_path):
                current_depth = root.count(os.sep) - str(drive_path).count(os.sep)
                if current_depth > max_depth:
                    dirs[:] = []
                    continue
                
                for file in files:
                    if file.lower().endswith('.exe'):
                        file_path = Path(root) / file
                        file_lower = file.lower()
                        for exe in executables:
                            if exe.lower() == file_lower:
                                found_paths.append(str(file_path))
                                break
        except (PermissionError, OSError):
            pass
        
        return found_paths
    
    def _get_program_dirs(self, drive: str) -> List[str]:
        program_dirs = []
        
        if os.name == 'nt':
            program_dirs.extend([
                "Program Files",
                "Program Files (x86)",
                "ProgramW6432Node",
                "Program Files (ARM)",
                "Program Files (ARM64)",
            ])
            
            custom_dirs = ["install", "software", "apps", "application", "applications"]
            for custom_dir in custom_dirs:
                p = Path(drive) / custom_dir
                if p.exists() and p.is_dir():
                    program_dirs.append(custom_dir)
            
            user_profile = os.environ.get('USERPROFILE', '')
            if user_profile and Path(user_profile).exists():
                user_dirs = [
                    Path(user_profile) / "AppData" / "Local",
                    Path(user_profile) / "AppData" / "Roaming",
                    Path(user_profile) / "AppData" / "LocalLow",
                ]
                for user_dir in user_dirs:
                    if user_dir.exists():
                        program_dirs.append(str(user_dir))
        else:
            program_dirs.extend([
                "usr",
                "usr/local",
                "opt",
                "Applications",
                "bin",
                "local/bin",
            ])
            
            home = os.environ.get('HOME', '')
            if home and Path(home).exists():
                home_dirs = [
                    Path(home) / ".local" / "bin",
                    Path(home) / ".local" / "share" / "applications",
                    Path(home) / "bin",
                    Path(home) / "Applications",
                ]
                for home_dir in home_dirs:
                    if home_dir.exists():
                        program_dirs.append(str(home_dir))
        
        return program_dirs

    def _get_common_locations(self) -> List[str]:
        locations = []
        env_vars = [
            ("LOCALAPPDATA", "Programs"),
            ("LOCALAPPDATA", None),
            ("APPDATA", None),
            ("USERPROFILE", "Desktop"),
            ("PROGRAMDATA", r"Microsoft\Windows\Start Menu\Programs"),
        ]
        for env, subdir in env_vars:
            path = os.environ.get(env, "")
            if path:
                full_path = Path(path) / subdir if subdir else Path(path)
                if full_path.exists():
                    locations.append(str(full_path))
        return locations

    def _load_config(self) -> Dict:
        now = time.time()
        if self._config_cache and (now - self._config_cache_time) < 30:
            return self._config_cache
        
        config_file = Path(__file__).parent.parent / "templates" / "app_config.json"
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8", errors="replace") as f:
                    self._config_cache = json.load(f)
                    self._config_cache_time = now
                    return self._config_cache
            except (json.JSONDecodeError, PermissionError):
                pass
        return {"apps": {}, "settings": {}}

    def find_application(self, app_name: str, search_executables: Optional[List[str]] = None) -> Tuple[Optional[str], str]:
        cache_key = app_name.lower().strip()
        if cache_key in self._cache:
            cached_path, cached_time = self._cache[cache_key]
            if time.time() - cached_time < self._cache_ttl:
                return cached_path, "Cache"

        if search_executables is None:
            search_executables = get_translated_names(app_name)

        methods = [
            ("Config", self._search_config),
            ("Registry", self._search_registry),
            ("InstallDirs", self._search_common_install_dirs),
        ]

        for method_name, method_func in methods:
            result = method_func(search_executables)
            if result:
                self._cache[cache_key] = (result, time.time())
                return result, method_name

        return None, "NotFound"

    def _search_config(self, executables: List[str]) -> Optional[str]:
        config = self._load_config()
        apps = config.get("apps", {})
        
        for exe_name in executables:
            exe_key = exe_name.lower().replace(".exe", "")
            for app_key, app_info in apps.items():
                if app_key == exe_key or app_key == exe_name.lower():
                    path = app_info.get("path", "")
                    if path and Path(path).exists():
                        return path
        return None

    def _search_registry(self, executables: List[str]) -> Optional[str]:
        registry_paths = [
            r"HKLM:\Software\Microsoft\Windows\CurrentVersion\App Paths",
            r"HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths",
            r"HKCU:\Software\Microsoft\Windows\CurrentVersion\App Paths",
        ]
        
        exe_list = ",".join([f'"{e}"' for e in executables])
        reg_list = ",".join([f'"{p}"' for p in registry_paths])
        
        cmd = f'''
$exeNames = @({exe_list})
$regPaths = @({reg_list})
foreach ($regPath in $regPaths) {{
    foreach ($exeName in $exeNames) {{
        $fullPath = Join-Path $regPath $exeName
        $path = (Get-ItemProperty -Path $fullPath -ErrorAction SilentlyContinue)."(Default)"
        if ($path -and (Test-Path $path)) {{
            Write-Output $path
            exit 0
        }}
    }}
}}
'''
        return self._run_powershell_and_get_path(cmd, timeout=3)

    def _search_start_menu(self, executables: List[str]) -> Optional[str]:
        start_menu_paths = [
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
            os.path.expandvars(r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs"),
        ]
        return self._search_shortcuts(start_menu_paths, executables)

    def _search_desktop(self, executables: List[str]) -> Optional[str]:
        desktop_paths = [
            os.path.expandvars(r"%USERPROFILE%\Desktop"),
            os.path.expandvars(r"%PUBLIC%\Desktop"),
        ]
        return self._search_shortcuts(desktop_paths, executables)

    def _search_shortcuts(self, search_paths: List[str], executables: List[str]) -> Optional[str]:
        exe_names_lower = [e.lower() for e in executables]
        shortcut_files = []
        
        for search_path_str in search_paths:
            search_path = Path(search_path_str)
            if not search_path.exists():
                continue
            try:
                for root, dirs, files in os.walk(search_path):
                    for file in files:
                        if file.endswith(".lnk"):
                            shortcut_files.append(os.path.join(root, file))
                            if len(shortcut_files) >= 50:
                                break
                    if len(shortcut_files) >= 50:
                        break
            except (PermissionError, OSError):
                continue
        
        if not shortcut_files:
            return None
        
        shortcut_list = ",".join([f'"{s}"' for s in shortcut_files])
        exe_list = ",".join([f'"{e}"' for e in exe_names_lower])
        
        cmd = f'''
$shell = New-Object -ComObject WScript.Shell
$shortcuts = @({shortcut_list})
$exeNames = @({exe_list})
foreach ($shortcutPath in $shortcuts) {{
    try {{
        $shortcut = $shell.CreateShortcut($shortcutPath)
        $target = $shortcut.TargetPath
        if ($target -and (Test-Path $target)) {{
            $targetName = Split-Path $target -Leaf
            if ($exeNames -contains $targetName.ToLower()) {{
                Write-Output $target
                exit 0
            }}
        }}
    }} catch {{}}
}}
'''
        return self._run_powershell_and_get_path(cmd, timeout=5)

    def _search_common_install_dirs(self, executables: List[str]) -> Optional[str]:
        exe_names_lower = [e.lower() for e in executables]
        
        for drive in ["D:", "C:"]:
            if not Path(drive).exists():
                continue
            
            for install_dir in COMMON_INSTALL_DIRS:
                search_path = Path(drive) / install_dir
                if not search_path.exists():
                    continue
                
                try:
                    for root, dirs, files in os.walk(search_path):
                        for f in files:
                            if f.lower() in exe_names_lower:
                                full_path = os.path.join(root, f)
                                return full_path
                except (PermissionError, OSError):
                    continue
        return None

    def search_applications(self, keyword: str, max_results: int = 10) -> List[Dict[str, Any]]:
        results = []
        keyword_lower = keyword.lower()

        search_paths = self.standard_paths + self.common_locations

        for search_path_str in search_paths:
            search_path = Path(search_path_str)
            if not search_path.exists():
                continue

            try:
                for root, dirs, files in os.walk(search_path):
                    for f in files:
                        if f.lower().endswith(".exe"):
                            if keyword_lower in f.lower():
                                results.append({
                                    "name": f,
                                    "path": os.path.join(root, f),
                                    "directory": root
                                })
                                if len(results) >= max_results:
                                    return results
            except (PermissionError, OSError):
                continue

        return results


def get_path_finder() -> PathFinder:
    return PathFinder()
