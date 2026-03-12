import win32gui
import win32con
import win32process
import psutil
import time
import pyautogui
from PIL import ImageGrab, Image
import cv2
import numpy as np
import sys
from typing import Optional, Tuple, Dict, Any, List
from pathlib import Path

from app_profile_manager import AppProfileManager

MSG = {
    "en": {
        "qr_found": "[INFO] QR found: {x}, {y}, {w}, {h}",
        "qr_valid": "[INFO] QR code is valid (decodable)",
        "qr_invalid": "[WARN] QR code is invalid/expired, refreshing...",
        "clicking_refresh": "[INFO] Clicking refresh at: ({x}, {y})",
        "refresh_found": "[INFO] Refresh button found at ({x}, {y})",
        "found_window": "[INFO] Found window: {title} ({process_name})",
        "window_position": "[INFO] Window position: {rect}",
        "waiting_refresh": "[INFO] Waiting {time}s for QR code to refresh...",
        "window_not_found": "[FAIL] Window not found for '{identifier}'",
        "qr_not_detected": "[FAIL] QR code not detected",
        "refresh_failed": "[FAIL] Failed to get valid QR after {attempts} attempts"
    }
}


class UniversalAppCapture:
    
    def __init__(self, profile_manager: AppProfileManager = None, lang: str = "en"):
        self.profile_manager = profile_manager or AppProfileManager()
        self.lang = lang
    
    def _msg(self, key: str, **kwargs) -> str:
        template = MSG.get(self.lang, MSG["en"]).get(key, key)
        return template.format(**kwargs)
    
    def _get_process_info(self, hwnd: int) -> Tuple[str, str]:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            process = psutil.Process(pid)
            return process.name().lower()
        except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
            return ""
    
    def _match_window(self, hwnd: int, title: str, exe_name: str, 
                       identifier: str = None, process_names: list = None, 
                       window_patterns: list = None) -> Optional[Tuple[int, str, str]]:
        if identifier:
            identifier_lower = identifier.lower()
            if identifier_lower in title.lower() or identifier_lower in exe_name:
                return (hwnd, title, exe_name)
        
        if process_names:
            for proc_name in process_names:
                if proc_name.lower() in exe_name:
                    return (hwnd, title, exe_name)
        
        if window_patterns:
            for pattern in window_patterns:
                if pattern.lower() in title.lower():
                    return (hwnd, title, exe_name)
        
        return None
    
    def _enum_windows(self, match_func) -> Optional[Tuple[int, str, str]]:
        def callback(hwnd, windows):
            if not win32gui.IsWindowVisible(hwnd):
                return True
            title = win32gui.GetWindowText(hwnd)
            exe_name = self._get_process_info(hwnd)
            result = match_func(hwnd, title, exe_name)
            if result:
                windows.append(result)
            return True
        
        windows = []
        win32gui.EnumWindows(callback, windows)
        return windows[0] if windows else None
    
    def find_window(self, identifier: str) -> Optional[Tuple[int, str, str]]:
        def match_func(hwnd, title, exe_name):
            return self._match_window(hwnd, title, exe_name, identifier=identifier)
        return self._enum_windows(match_func)
    
    def find_window_by_profile(self, app_id: str) -> Optional[Tuple[int, str, str]]:
        profile = self.profile_manager.find_app_profile(app_id)
        if not profile:
            return None
        
        process_names = profile.get("process_names", [])
        window_patterns = profile.get("window_patterns", [])
        
        def match_func(hwnd, title, exe_name):
            return self._match_window(hwnd, title, exe_name, 
                                       process_names=process_names, 
                                       window_patterns=window_patterns)
        return self._enum_windows(match_func)
    
    def activate_window(self, hwnd: int, app_id: str = None) -> bool:
        try:
            if not win32gui.IsWindow(hwnd):
                return False
            win32gui.SetForegroundWindow(hwnd)
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            wait_time = self.profile_manager.get_app_config(app_id, "wait_after_activate", default=2)
            time.sleep(wait_time)
            return True
        except Exception:
            return False
    
    def _detect_qr_opencv(self, gray) -> Optional[Tuple[int, int, int, int]]:
        detector = cv2.QRCodeDetector()
        value, points, _ = detector.detectAndDecode(gray)
        
        if points is not None and len(points) > 0:
            points = points[0].astype(int)
            x = int(points[:, 0].min())
            y = int(points[:, 1].min())
            w = int(points[:, 0].max()) - x
            h = int(points[:, 1].max()) - y
            return (x, y, w, h)
        return None
    
    def _decode_qr(self, image: Image.Image) -> Optional[str]:
        try:
            img_array = np.array(image)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            detector = cv2.QRCodeDetector()
            value, _, _ = detector.detectAndDecode(gray)
            return value if value else None
        except Exception:
            return None
    
    def _is_qr_valid(self, image: Image.Image, qr_pos: tuple) -> bool:
        """
        Check if QR code is valid by detecting expired/invalid text.
        
        Strategy:
        - If we can decode the QR, it's definitely valid
        - If we can't decode, check for "expired/invalid" text indicators
        - If no expired text found, assume it's valid (most apps start with valid QR)
        """
        x, y, w, h = qr_pos
        padding = 10
        left, top = max(0, x - padding), max(0, y - padding)
        right, bottom = min(image.width, x + w + padding), min(image.height, y + h + padding)
        qr_region = image.crop((left, top, right, bottom))
        
        decoded = self._decode_qr(qr_region)
        if decoded is not None and len(decoded) > 0:
            return True
        
        if self._has_expired_indicator(qr_region):
            return False
        
        return True
    
    def _has_expired_indicator(self, image: Image.Image) -> bool:
        """
        Detect if QR code area has expired/invalid indicators.
        Look for:
        1. Blue text (common for refresh buttons)
        2. High contrast text area in center (common for "expired" text)
        """
        img_array = np.array(image)
        
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        blue_lower = np.array([90, 50, 50])
        blue_upper = np.array([130, 255, 255])
        blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
        blue_pixels = cv2.countNonZero(blue_mask)
        
        h, w = img_array.shape[:2]
        total_pixels = h * w
        blue_ratio = blue_pixels / total_pixels if total_pixels > 0 else 0
        
        if blue_ratio > 0.02:
            return True
        
        return False
    
    def _detect_qr_color(self, img_array, min_size: int, max_size: int) -> Optional[Tuple[int, int, int, int]]:
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv, (0, 0, 220), (180, 30, 255))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if min_size <= w <= max_size and min_size <= h <= max_size:
                if 0.9 <= float(w) / h <= 1.1:
                    return (x, y, w, h)
        return None
    
    def _estimate_qr_position(self, image: Image.Image, position_hint: dict) -> Optional[Tuple[int, int, int, int]]:
        if not position_hint:
            return None
        width, height = image.size
        x = int(width * position_hint.get("x_ratio", 0.5) - position_hint.get("size", 250) / 2)
        y = int(height * position_hint.get("y_ratio", 0.5) - position_hint.get("size", 250) / 2)
        return (x, y, position_hint.get("size", 250), position_hint.get("size", 250))
    
    def find_qr_code(self, image: Image.Image, app_id: str = None) -> Optional[Tuple[int, int, int, int]]:
        img_array = np.array(image)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        qr_config = self.profile_manager.get_app_config(app_id, "qr_detection", default={})
        min_size, max_size = qr_config.get("min_size", 100), qr_config.get("max_size", 500)
        
        qr_pos = self._detect_qr_opencv(gray)
        if qr_pos and min_size <= qr_pos[2] <= max_size and min_size <= qr_pos[3] <= max_size:
            print(self._msg("qr_found", x=qr_pos[0], y=qr_pos[1], w=qr_pos[2], h=qr_pos[3]), file=sys.stderr, flush=True)
            return qr_pos
        
        qr_pos = self._detect_qr_color(img_array, min_size, max_size)
        if qr_pos:
            print(self._msg("qr_found", x=qr_pos[0], y=qr_pos[1], w=qr_pos[2], h=qr_pos[3]), file=sys.stderr, flush=True)
            return qr_pos
        
        qr_pos = self._estimate_qr_position(image, qr_config.get("position_hint"))
        if qr_pos:
            print(self._msg("qr_found", x=qr_pos[0], y=qr_pos[1], w=qr_pos[2], h=qr_pos[3]), file=sys.stderr, flush=True)
        return qr_pos
    
    def _find_refresh_button(self, image: Image.Image, qr_pos: tuple) -> Optional[Tuple[int, int]]:
        """
        Find refresh button inside QR code area.
        
        Strategy:
        1. Search for blue text in the bottom 40% of QR area (most apps put refresh text there)
        2. If no blue text found, use relative position (bottom center of QR area)
        """
        x, y, w, h = qr_pos
        
        search_left = max(0, x)
        search_top = max(0, y + int(h * 0.6))
        search_right = min(image.width, x + w)
        search_bottom = min(image.height, y + h)
        
        if search_right <= search_left or search_bottom <= search_top:
            return self._get_fallback_refresh_pos(qr_pos)
        
        roi = image.crop((search_left, search_top, search_right, search_bottom))
        roi_array = np.array(roi)
        
        hsv = cv2.cvtColor(roi_array, cv2.COLOR_RGB2HSV)
        
        blue_lower = np.array([90, 50, 50])
        blue_upper = np.array([130, 255, 255])
        blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
        
        blue_pixels = cv2.countNonZero(blue_mask)
        
        if blue_pixels > 50:
            moments = cv2.moments(blue_mask)
            if moments["m00"] > 0:
                cx = int(moments["m10"] / moments["m00"])
                cy = int(moments["m01"] / moments["m00"])
                btn_x = search_left + cx
                btn_y = search_top + cy
                print(self._msg("refresh_found", x=btn_x, y=btn_y), file=sys.stderr, flush=True)
                return (btn_x, btn_y)
        
        gray = cv2.cvtColor(roi_array, cv2.COLOR_RGB2GRAY)
        _, binary = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
        
        white_pixels = cv2.countNonZero(binary)
        qr_area = w * int(h * 0.4)
        white_ratio = white_pixels / qr_area if qr_area > 0 else 0
        
        if 0.1 < white_ratio < 0.5:
            moments = cv2.moments(binary)
            if moments["m00"] > 0:
                cx = int(moments["m10"] / moments["m00"])
                cy = int(moments["m01"] / moments["m00"])
                btn_x = search_left + cx
                btn_y = search_top + cy
                print(self._msg("refresh_found", x=btn_x, y=btn_y), file=sys.stderr, flush=True)
                return (btn_x, btn_y)
        
        return self._get_fallback_refresh_pos(qr_pos)
    
    def _get_fallback_refresh_pos(self, qr_pos: tuple) -> Tuple[int, int]:
        """
        Fallback: Return bottom center position of QR area.
        This is a relative position that works for most apps.
        """
        x, y, w, h = qr_pos
        btn_x = x + w // 2
        btn_y = y + int(h * 0.85)
        print(f"[INFO] Using fallback position: ({btn_x}, {btn_y})", file=sys.stderr, flush=True)
        return (btn_x, btn_y)
    
    def click_refresh_button(self, hwnd: int, rect: Tuple[int, int, int, int], 
                               app_id: str, qr_pos: tuple = None, 
                               screenshot: Image.Image = None) -> bool:
        if not qr_pos:
            return False
        
        btn_pos = self._find_refresh_button(screenshot, qr_pos)
        
        if not btn_pos:
            return False
        
        screen_x = rect[0] + btn_pos[0]
        screen_y = rect[1] + btn_pos[1]
        
        print(self._msg("clicking_refresh", x=screen_x, y=screen_y), file=sys.stderr, flush=True)
        try:
            pyautogui.click(screen_x, screen_y)
            return True
        except pyautogui.FailSafeException:
            return False
    
    def _resolve_app_id(self, identifier: str) -> Optional[str]:
        profile = self.profile_manager.find_app_profile(identifier)
        if profile:
            for aid, prof in self.profile_manager.profiles.get("apps", {}).items():
                if prof is profile:
                    return aid
        return None
    
    def _build_success_result(self, qr_pos: tuple, rect: tuple, output_path: str, 
                               app_id: str, title: str, process_name: str, refreshed: bool = False) -> Dict[str, Any]:
        return {
            "success": True,
            "qr_position": list(qr_pos),
            "window_position": list(rect),
            "output_path": output_path,
            "app_id": app_id,
            "window_title": title,
            "process_name": process_name,
            "refreshed": refreshed
        }
    
    def _build_error_result(self, error: str, details: str = None, **kwargs) -> Dict[str, Any]:
        result = {"success": False, "error": error}
        if details:
            result["details"] = details
        result.update(kwargs)
        return result
    
    def _save_qr_image(self, screenshot: Image.Image, qr_pos: tuple, 
                        app_id: str, output_path: str) -> Tuple[Optional[str], Optional[str]]:
        x, y, w, h = qr_pos
        padding = self.profile_manager.get_app_config(app_id, "padding", default=30)
        
        left, top = max(0, x - padding), max(0, y - padding)
        right = min(screenshot.width, x + w + padding)
        bottom = min(screenshot.height, y + h + padding)
        
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            screenshot.crop((left, top, right, bottom)).save(output_path)
            return output_path, None
        except (FileNotFoundError, PermissionError, OSError) as e:
            return None, str(e)
    
    def _capture_and_validate_qr(self, rect: tuple, app_id: str, output_path: str, 
                                  title: str, process_name: str, max_attempts: int = 3, force_refresh: bool = False) -> Dict[str, Any]:
        last_qr_pos = None
        last_screenshot = None
        
        if force_refresh:
            screenshot = ImageGrab.grab(rect)
            last_screenshot = screenshot
            qr_pos = self.find_qr_code(screenshot, app_id)
            if qr_pos:
                print("[INFO] Force refreshing QR code...", file=sys.stderr, flush=True)
                self.click_refresh_button(0, rect, app_id, qr_pos, screenshot)
                wait_time = self.profile_manager.get_app_config(app_id, "wait_after_refresh", default=3)
                print(self._msg("waiting_refresh", time=wait_time), file=sys.stderr, flush=True)
                time.sleep(wait_time)
        
        for attempt in range(max_attempts):
            screenshot = ImageGrab.grab(rect)
            last_screenshot = screenshot
            qr_pos = self.find_qr_code(screenshot, app_id)
            
            if not qr_pos:
                if attempt < max_attempts - 1:
                    print(self._msg("qr_invalid"), file=sys.stderr, flush=True)
                    if last_qr_pos:
                        self.click_refresh_button(0, rect, app_id, last_qr_pos, last_screenshot)
                    wait_time = self.profile_manager.get_app_config(app_id, "wait_after_refresh", default=3)
                    print(self._msg("waiting_refresh", time=wait_time), file=sys.stderr, flush=True)
                    time.sleep(wait_time)
                    continue
                return self._build_error_result("QR code not detected", 
                                                window_position=list(rect), app_id=app_id)
            
            last_qr_pos = qr_pos
            
            if self._is_qr_valid(screenshot, qr_pos):
                print(self._msg("qr_valid"), file=sys.stderr, flush=True)
                output_path, error = self._save_qr_image(screenshot, qr_pos, app_id, output_path)
                if error:
                    return self._build_error_result("Failed to save QR code image", error)
                return self._build_success_result(qr_pos, rect, output_path, app_id, title, process_name, 
                                                   refreshed=(attempt > 0 or force_refresh))
            
            print(self._msg("qr_invalid"), file=sys.stderr, flush=True)
            
            if attempt < max_attempts - 1:
                self.click_refresh_button(0, rect, app_id, qr_pos, screenshot)
                wait_time = self.profile_manager.get_app_config(app_id, "wait_after_refresh", default=3)
                print(self._msg("waiting_refresh", time=wait_time), file=sys.stderr, flush=True)
                time.sleep(wait_time)
        
        return self._build_error_result("Failed to get valid QR code", 
                                        self._msg("refresh_failed", attempts=max_attempts),
                                        window_position=list(rect), app_id=app_id)
    
    def capture_qr_code(self, identifier: str, app_id: str = None, output_path: str = None, force_refresh: bool = False) -> Dict[str, Any]:
        if app_id is None:
            app_id = self._resolve_app_id(identifier)
        
        window_info = self.find_window_by_profile(app_id) if app_id else self.find_window(identifier)
        if not window_info:
            return self._build_error_result("Window not found", 
                                            self._msg("window_not_found", identifier=identifier))
        
        hwnd, title, process_name = window_info
        print(self._msg("found_window", title=title, process_name=process_name), file=sys.stderr, flush=True)
        
        self.activate_window(hwnd, app_id)
        rect = win32gui.GetWindowRect(hwnd)
        print(self._msg("window_position", rect=rect), file=sys.stderr, flush=True)
        
        return self._capture_and_validate_qr(rect, app_id, output_path, title, process_name, force_refresh=force_refresh)
