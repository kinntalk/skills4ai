"""
XHS Browser Automation
Wrapper for agent-browser to interact with Xiaohongshu.
"""

import io
import json
import subprocess
import time
from pathlib import Path
from typing import Optional, Tuple


class BrowserAutomation:
    """Browser automation using agent-browser CLI."""
    
    XHS_BASE_URL = "https://www.xiaohongshu.com"
    XHS_SEARCH_URL = "https://www.xiaohongshu.com/search_result"
    XHS_EXPLORE_URL = "https://www.xiaohongshu.com/explore"
    
    def __init__(self, session_name: str = "xhs-search", timeout: int = 30000, headed: bool = False):
        self.session_name = session_name
        self.timeout = timeout
        self.headed = headed
        self._is_open = False
    
    def _run_command(self, *args, capture_output: bool = True) -> Tuple[int, str, str]:
        cmd = ["npx", "agent-browser"]
        if self.session_name:
            cmd.extend(["--session", self.session_name])
        if not self.headed:
            cmd.append("--headless")
        cmd.extend(args)
        
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            timeout=self.timeout / 1000 + 30,
            shell=True
        )
        return result.returncode, result.stdout, result.stderr
    
    def open(self, url: str) -> bool:
        code, out, err = self._run_command("open", url)
        if code == 0:
            self._is_open = True
        return code == 0
    
    def close(self) -> bool:
        code, out, err = self._run_command("close")
        self._is_open = False
        return code == 0
    
    def snapshot(self, interactive: bool = True, selector: Optional[str] = None) -> str:
        args = ["snapshot"]
        if interactive:
            args.append("-i")
        if selector:
            args.extend(["-s", selector])
        
        code, out, err = self._run_command(*args)
        return out if code == 0 else ""
    
    def snapshot_json(self, interactive: bool = True) -> dict:
        args = ["snapshot", "-i", "--json"]
        code, out, err = self._run_command(*args)
        if code == 0 and out:
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def wait(self, target: str = "networkidle", timeout_ms: Optional[int] = None) -> bool:
        args = ["wait"]
        if target == "networkidle":
            args.extend(["--load", "networkidle"])
        elif target.startswith("@"):
            args.append(target)
        else:
            args.extend(["--url", target])
        
        if timeout_ms:
            args.append(str(timeout_ms))
        
        code, out, err = self._run_command(*args)
        return code == 0
    
    def click(self, ref: str) -> bool:
        code, out, err = self._run_command("click", ref)
        return code == 0
    
    def fill(self, ref: str, text: str) -> bool:
        code, out, err = self._run_command("fill", ref, text)
        return code == 0
    
    def type_text(self, ref: str, text: str) -> bool:
        code, out, err = self._run_command("type", ref, text)
        return code == 0
    
    def press(self, key: str) -> bool:
        code, out, err = self._run_command("press", key)
        return code == 0
    
    def get_text(self, selector: str = "body") -> str:
        code, out, err = self._run_command("get", "text", selector)
        return out if code == 0 else ""
    
    def get_url(self) -> str:
        code, out, err = self._run_command("get", "url")
        return out.strip() if code == 0 else ""
    
    def get_title(self) -> str:
        code, out, err = self._run_command("get", "title")
        return out.strip() if code == 0 else ""
    
    def scroll(self, direction: str = "down", amount: int = 500) -> bool:
        code, out, err = self._run_command("scroll", direction, str(amount))
        return code == 0
    
    def screenshot(self, output_path: Optional[str] = None) -> str:
        args = ["screenshot"]
        if output_path:
            args.append(output_path)
        code, out, err = self._run_command(*args)
        return out.strip() if code == 0 else ""
    
    def eval_js(self, script: str) -> str:
        code, out, err = self._run_command("eval", script)
        return out if code == 0 else ""
    
    def check_login_status(self) -> str:
        """检查登录状态，返回: 'logged_in', 'need_scan', 'expired', 'need_login'"""
        result = self.eval_js(
            "document.body.innerText.includes('二维码已过期') ? 'expired' : "
            "(document.querySelector('.qrcode-img') ? 'need_scan' : "
            "(document.body.innerText.includes('登录') ? 'need_login' : 'logged_in'))"
        )
        return result.strip().strip('"')
    
    def is_logged_in(self) -> bool:
        self.open(self.XHS_BASE_URL)
        time.sleep(2)
        self.wait("networkidle")
        return self.check_login_status() == 'logged_in'
    
    def get_qr_code_position(self) -> Optional[Tuple[int, int, int, int]]:
        """获取二维码位置 (x, y, width, height)"""
        result = self.eval_js(
            "const qr = document.querySelector('.qrcode-img'); "
            "qr ? qr.getBoundingClientRect().x + ',' + qr.getBoundingClientRect().y + ',' "
            "+ qr.getBoundingClientRect().width + ',' + qr.getBoundingClientRect().height : 'no qr'"
        )
        result = result.strip().strip('"')
        if result == 'no qr':
            return None
        try:
            parts = result.split(',')
            return (int(float(parts[0])), int(float(parts[1])), int(float(parts[2])), int(float(parts[3])))
        except:
            return None
    
    def get_qr_code_image(self, output_path: str, padding: int = 25) -> Optional[str]:
        """获取登录二维码图片并保存，返回保存路径"""
        from PIL import Image
        import base64
        import os
        
        # 方法1: 直接获取二维码原图 base64
        qr_src = self.eval_js("document.querySelector('.qrcode-img')?.src || ''")
        qr_src = qr_src.strip().strip('"')
        
        if qr_src and qr_src.startswith('data:image'):
            try:
                base64_data = qr_src.split(',', 1)[1]
                image_data = base64.b64decode(base64_data)
                
                # 添加白色边距
                img = Image.open(io.BytesIO(image_data))
                from PIL import ImageOps
                img_with_border = ImageOps.expand(img, border=padding, fill='white')
                img_with_border.save(output_path)
                return output_path
            except Exception as e:
                print(f"获取二维码原图失败: {e}")
        
        # 方法2: 截图裁剪
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp_path = tmp.name
        
        self.screenshot(tmp_path)
        
        qr_pos = self.get_qr_code_position()
        if not qr_pos:
            return None
        
        x, y, w, h = qr_pos
        try:
            img = Image.open(tmp_path)
            left = max(0, x - padding)
            top = max(0, y - padding)
            right = min(img.width, x + w + padding)
            bottom = min(img.height, y + h + padding)
            
            qr_img = img.crop((left, top, right, bottom))
            qr_img.save(output_path)
            
            os.unlink(tmp_path)
            return output_path
        except Exception as e:
            print(f"截图裁剪失败: {e}")
            return None
    
    def wait_for_login(self, timeout: int = 180, qr_output_path: str = None) -> bool:
        """等待用户扫码登录，最长等待 timeout 秒（默认3分钟）"""
        import os
        
        if qr_output_path is None:
            qr_output_path = os.path.join(os.getcwd(), 'xhs-login-qr.png')
        
        print("正在检查登录状态...")
        
        # 步骤1: 刷新页面
        self.open(self.XHS_BASE_URL)
        time.sleep(2)
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # 步骤2: 检查登录状态
            status = self.check_login_status()
            
            if status == 'logged_in':
                print("登录成功!")
                return True
            
            if status == 'expired':
                print("二维码已过期，正在刷新...")
                self.open(self.XHS_BASE_URL)
                time.sleep(2)
                continue
            
            if status == 'need_scan':
                # 步骤3: 获取二维码
                qr_path = self.get_qr_code_image(qr_output_path)
                if qr_path:
                    print(f"请扫描二维码登录: {qr_path}")
                time.sleep(5)
                continue
            
            if status == 'need_login':
                print("需要登录，正在获取二维码...")
                time.sleep(2)
                continue
            
            time.sleep(3)
        
        print("登录超时")
        return False
    
    def search(self, keyword: str, sort: str = "general") -> bool:
        search_url = f"{self.XHS_SEARCH_URL}?keyword={keyword}&type={sort}"
        self.open(search_url)
        time.sleep(2)
        self.wait("networkidle")
        return True
    
    def open_note(self, note_id: str) -> bool:
        note_url = f"{self.XHS_EXPLORE_URL}/{note_id}"
        self.open(note_url)
        time.sleep(2)
        self.wait("networkidle")
        return True
    
    def get_page_html(self) -> str:
        return self.eval_js("document.documentElement.outerHTML")
    
    def scroll_to_load_more(self, times: int = 3, delay: float = 2.0) -> None:
        for _ in range(times):
            self.scroll("down", 800)
            time.sleep(delay)
            self.scroll("down", 800)
            time.sleep(delay)
