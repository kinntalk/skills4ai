"""
Chrome DevTools Protocol (CDP) client for url-to-obsidian skill.

This module provides Python implementation of CDP for browser automation,
including login detection and content extraction.
"""

import asyncio
import json
import platform
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Optional, Tuple
from urllib.parse import urlparse

try:
    import websockets
except ImportError:
    print("websockets not installed. Run: pip install websockets")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("requests not installed. Run: pip install requests")
    sys.exit(1)


DEFAULT_TIMEOUT_MS = 30000
CDP_CONNECT_TIMEOUT_MS = 15000
NETWORK_IDLE_TIMEOUT_MS = 1500
POST_LOAD_DELAY_MS = 800
SCROLL_STEP_WAIT_MS = 600
SCROLL_MAX_STEPS = 8
LOGIN_CHECK_INTERVAL_MS = 1000
MAX_LOGIN_WAIT_MS = 120000


def find_chrome_executable(chrome_path: Optional[str] = None) -> Optional[str]:
    """Find Chrome or Edge executable on the system.
    
    Args:
        chrome_path: Optional explicit path to Chrome executable
        
    Returns:
        Path to Chrome executable or None if not found
    """
    import os
    
    if chrome_path and Path(chrome_path).exists():
        return chrome_path
    
    override = os.environ.get("URL_CHROME_PATH", "").strip()
    if override and Path(override).exists():
        return override
    
    candidates = []
    system = platform.system()
    
    if system == "Windows":
        candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        ]
    elif system == "Darwin":
        candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
            "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        ]
    else:
        candidates = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
            "/usr/bin/microsoft-edge",
        ]
    
    for path in candidates:
        if Path(path).exists():
            return path
    
    return None


def get_chrome_profile_dir() -> Path:
    """Get Chrome profile directory for CDP sessions.
    
    Returns:
        Path to Chrome profile directory
    """
    system = platform.system()
    
    if system == "Windows":
        base = Path.home() / "AppData" / "Roaming"
    elif system == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".local" / "share"
    
    return base / "url-to-obsidian" / "chrome-profile"


class CdpConnection:
    """WebSocket connection to Chrome DevTools Protocol."""
    
    def __init__(self, ws_url: str):
        self.ws_url = ws_url
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.next_id = 0
        self.pending: dict[int, asyncio.Future] = {}
        self.event_handlers: dict[str, set[Callable]] = {}
        self._receive_task: Optional[asyncio.Task] = None
    
    async def connect(self, timeout_ms: int = CDP_CONNECT_TIMEOUT_MS) -> None:
        """Connect to Chrome via WebSocket.
        
        Args:
            timeout_ms: Connection timeout in milliseconds
        """
        try:
            self.ws = await asyncio.wait_for(
                websockets.connect(self.ws_url),
                timeout=timeout_ms / 1000
            )
            self._receive_task = asyncio.create_task(self._receive_loop())
        except asyncio.TimeoutError:
            raise TimeoutError("CDP connection timeout")
    
    async def _receive_loop(self) -> None:
        """Background task to receive messages from WebSocket."""
        if not self.ws:
            return
        
        try:
            async for message in self.ws:
                try:
                    data = json.loads(message)
                    
                    if "id" in data:
                        msg_id = data["id"]
                        if msg_id in self.pending:
                            future = self.pending.pop(msg_id)
                            if "error" in data:
                                future.set_exception(Exception(data["error"].get("message", "Unknown error")))
                            else:
                                future.set_result(data.get("result"))
                    elif "method" in data:
                        method = data["method"]
                        if method in self.event_handlers:
                            for handler in self.event_handlers[method]:
                                try:
                                    await handler(data.get("params", {})) if asyncio.iscoroutinefunction(handler) else handler(data.get("params", {}))
                                except Exception:
                                    pass
                except json.JSONDecodeError:
                    pass
        except websockets.ConnectionClosed:
            pass
        finally:
            for future in self.pending.values():
                if not future.done():
                    future.set_exception(Exception("CDP connection closed"))
            self.pending.clear()
    
    def on(self, event: str, handler: Callable) -> None:
        """Register an event handler.
        
        Args:
            event: Event name
            handler: Event handler function
        """
        if event not in self.event_handlers:
            self.event_handlers[event] = set()
        self.event_handlers[event].add(handler)
    
    def off(self, event: str, handler: Callable) -> None:
        """Unregister an event handler.
        
        Args:
            event: Event name
            handler: Event handler function
        """
        if event in self.event_handlers:
            self.event_handlers[event].discard(handler)
    
    async def send(self, method: str, params: Optional[dict] = None, session_id: Optional[str] = None, timeout_ms: int = 15000) -> Any:
        """Send a CDP command and wait for response.
        
        Args:
            method: CDP method name
            params: Method parameters
            session_id: Target session ID
            timeout_ms: Response timeout in milliseconds
            
        Returns:
            Command result
        """
        if not self.ws:
            raise Exception("Not connected")
        
        msg_id = self.next_id
        self.next_id += 1
        
        message: dict = {"id": msg_id, "method": method}
        if params:
            message["params"] = params
        if session_id:
            message["sessionId"] = session_id
        
        future: asyncio.Future = asyncio.get_event_loop().create_future()
        self.pending[msg_id] = future
        
        await self.ws.send(json.dumps(message))
        
        try:
            return await asyncio.wait_for(future, timeout=timeout_ms / 1000)
        except asyncio.TimeoutError:
            self.pending.pop(msg_id, None)
            raise TimeoutError(f"CDP timeout: {method}")
    
    async def close(self) -> None:
        """Close the WebSocket connection."""
        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
        
        if self.ws:
            await self.ws.close()
            self.ws = None


class ChromeBrowser:
    """Chrome browser instance with CDP support."""
    
    def __init__(self, port: int = 0):
        self.port = port or self._get_free_port()
        self.process: Optional[subprocess.Popen] = None
        self.cdp: Optional[CdpConnection] = None
        self.profile_dir = get_chrome_profile_dir()
    
    def _get_free_port(self) -> int:
        """Get a free TCP port."""
        import socket
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    
    def launch(self, url: str, headless: bool = False, chrome_path: Optional[str] = None) -> None:
        """Launch Chrome browser.
        
        Args:
            url: Initial URL to open
            headless: Whether to run in headless mode
            chrome_path: Optional path to Chrome executable
        """
        chrome = find_chrome_executable(chrome_path)
        if not chrome:
            raise Exception("Chrome executable not found. Install Chrome, set URL_CHROME_PATH env, or configure 'browser.chrome_path'.")
        
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        
        args = [
            chrome,
            f"--remote-debugging-port={self.port}",
            f"--user-data-dir={self.profile_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-popup-blocking",
        ]
        
        if headless:
            args.append("--headless=new")
        
        args.append(url)
        
        self.process = subprocess.Popen(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True if platform.system() == "Windows" else False
        )
    
    async def connect(self, timeout_ms: int = CDP_CONNECT_TIMEOUT_MS) -> None:
        """Connect to Chrome via CDP.
        
        Args:
            timeout_ms: Connection timeout in milliseconds
        """
        ws_url = await self._wait_for_debug_port(timeout_ms)
        self.cdp = CdpConnection(ws_url)
        await self.cdp.connect(timeout_ms)
    
    async def _wait_for_debug_port(self, timeout_ms: int) -> str:
        """Wait for Chrome debug port to be ready.
        
        Args:
            timeout_ms: Timeout in milliseconds
            
        Returns:
            WebSocket URL for CDP
        """
        start = time.time()
        timeout = timeout_ms / 1000
        
        while time.time() - start < timeout:
            try:
                response = requests.get(f"http://127.0.0.1:{self.port}/json/version", timeout=5)
                if response.ok:
                    data = response.json()
                    ws_url = data.get("webSocketDebuggerUrl")
                    if ws_url:
                        return ws_url
            except Exception:
                pass
            
            await asyncio.sleep(0.2)
        
        raise TimeoutError("Chrome debug port not ready")
    
    async def get_page_session(self) -> Tuple[str, str]:
        """Get the target ID and session ID for the main page.
        
        Returns:
            Tuple of (target_id, session_id)
        """
        if not self.cdp:
            raise Exception("Not connected")
        
        targets = await self.cdp.send("Target.getTargets")
        page_target = None
        
        for target in targets.get("targetInfos", []):
            if target.get("type") == "page" and target.get("url", "").startswith("http"):
                page_target = target
                break
        
        if not page_target:
            raise Exception("No page target found")
        
        target_id = page_target["targetId"]
        result = await self.cdp.send("Target.attachToTarget", {"targetId": target_id, "flatten": True})
        session_id = result["sessionId"]
        
        await self.cdp.send("Network.enable", {}, session_id=session_id)
        await self.cdp.send("Page.enable", {}, session_id=session_id)
        
        return target_id, session_id
    
    async def wait_for_network_idle(self, session_id: str, timeout_ms: int = NETWORK_IDLE_TIMEOUT_MS) -> None:
        """Wait for network to be idle.
        
        Args:
            session_id: Target session ID
            timeout_ms: Idle timeout in milliseconds
        """
        if not self.cdp:
            return
        
        pending = 0
        idle_future: asyncio.Future = asyncio.get_event_loop().create_future()
        
        def on_request(_: Any) -> None:
            nonlocal pending
            pending += 1
        
        def on_finish(_: Any) -> None:
            nonlocal pending
            pending = max(0, pending - 1)
        
        self.cdp.on("Network.requestWillBeSent", on_request)
        self.cdp.on("Network.loadingFinished", on_finish)
        self.cdp.on("Network.loadingFailed", on_finish)
        
        try:
            await asyncio.wait_for(asyncio.sleep(timeout_ms / 1000), timeout=timeout_ms / 1000 + 1)
        except asyncio.TimeoutError:
            pass
        finally:
            self.cdp.off("Network.requestWillBeSent", on_request)
            self.cdp.off("Network.loadingFinished", on_finish)
            self.cdp.off("Network.loadingFailed", on_finish)
    
    async def wait_for_page_load(self, session_id: str, timeout_ms: int = 30000) -> None:
        """Wait for page load event.
        
        Args:
            session_id: Target session ID
            timeout_ms: Timeout in milliseconds
        """
        if not self.cdp:
            return
        
        load_future: asyncio.Future = asyncio.get_event_loop().create_future()
        
        def on_load(_: Any) -> None:
            if not load_future.done():
                load_future.set_result(None)
        
        self.cdp.on("Page.loadEventFired", on_load)
        
        try:
            await asyncio.wait_for(load_future, timeout=timeout_ms / 1000)
        except asyncio.TimeoutError:
            pass
        finally:
            self.cdp.off("Page.loadEventFired", on_load)
    
    async def auto_scroll(self, session_id: str, steps: int = SCROLL_MAX_STEPS, wait_ms: int = SCROLL_STEP_WAIT_MS) -> None:
        """Auto-scroll the page to trigger lazy-loaded content.
        
        Args:
            session_id: Target session ID
            steps: Number of scroll steps
            wait_ms: Wait time between steps in milliseconds
        """
        if not self.cdp:
            return
        
        last_height = await self.evaluate_script(session_id, "document.body.scrollHeight")
        
        for _ in range(steps):
            await self.evaluate_script(session_id, "window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(wait_ms / 1000)
            
            new_height = await self.evaluate_script(session_id, "document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        await self.evaluate_script(session_id, "window.scrollTo(0, 0)")
    
    async def evaluate_script(self, session_id: str, script: str, timeout_ms: int = 30000) -> Any:
        """Evaluate JavaScript in the page.
        
        Args:
            session_id: Target session ID
            script: JavaScript code to evaluate
            timeout_ms: Timeout in milliseconds
            
        Returns:
            Script result
        """
        if not self.cdp:
            raise Exception("Not connected")
        
        result = await self.cdp.send(
            "Runtime.evaluate",
            {"expression": script, "returnByValue": True, "awaitPromise": True},
            session_id=session_id,
            timeout_ms=timeout_ms
        )
        
        return result.get("result", {}).get("value")
    
    async def get_current_url(self, session_id: str) -> str:
        """Get the current page URL.
        
        Args:
            session_id: Target session ID
            
        Returns:
            Current URL
        """
        return await self.evaluate_script(session_id, "window.location.href") or ""
    
    async def get_page_title(self, session_id: str) -> str:
        """Get the current page title.
        
        Args:
            session_id: Target session ID
            
        Returns:
            Page title
        """
        return await self.evaluate_script(session_id, "document.title") or ""
    
    async def close(self) -> None:
        """Close the browser and cleanup."""
        if self.cdp:
            try:
                await self.cdp.send("Browser.close", {}, timeout_ms=5000)
            except Exception:
                pass
            await self.cdp.close()
            self.cdp = None
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
            self.process = None


LOGIN_INDICATORS = [
    "login", "signin", "sign-in", "auth", "authenticate",
    "password", "username", "email", "credential",
    "log in", "sign in", "log on"
]

LOGIN_FORM_SELECTORS = [
    "input[type='password']",
    "input[name*='login']",
    "input[name*='user']",
    "input[name*='email']",
    "form[action*='login']",
    "form[action*='signin']",
    "form[action*='auth']",
    "#login-form",
    "#signin-form",
    ".login-form",
    ".signin-form",
]

CONTENT_INDICATORS = [
    "article", "content", "main", "post", "entry",
    "documentation", "docs", "tutorial", "guide"
]


async def detect_login_page(session_id: str, browser: ChromeBrowser) -> bool:
    """Detect if the current page is a login page.
    
    Args:
        session_id: Target session ID
        browser: Chrome browser instance
        
    Returns:
        True if login page is detected
    """
    script = """
    (function() {
        const url = window.location.href.toLowerCase();
        const title = document.title.toLowerCase();
        const body = document.body ? document.body.innerText.toLowerCase() : '';
        
        const loginKeywords = ['login', 'signin', 'sign-in', 'auth', 'password', 'log in', 'sign in', '账号', '登录', '密码'];
        for (const kw of loginKeywords) {
            if (url.includes(kw) || title.includes(kw)) return true;
        }
        
        const loginForms = document.querySelectorAll("input[type='password'], form[action*='login'], form[action*='signin'], #login-form, .login-form");
        if (loginForms.length > 0) return true;
        
        const hasPasswordField = document.querySelector("input[type='password']") !== null;
        if (hasPasswordField) return true;
        
        const hasLoginButton = document.querySelector("button[type='submit'], input[type='submit'], .login-btn, .signin-btn, .btn-login") !== null;
        const hasPasswordField2 = document.querySelector("input[type='password']") !== null;
        if (hasLoginButton && hasPasswordField2) return true;
        
        const bodyText = body.toLowerCase();
        const loginTextIndicators = ['账号登录', '短信登录', '账号密码', '下次自动登录', '忘记密码', '登录账号', '用户名', 'username', 'password'];
        for (const indicator of loginTextIndicators) {
            if (bodyText.includes(indicator.toLowerCase())) return true;
        }
        
        return false;
    })()
    """
    
    try:
        result = await browser.evaluate_script(session_id, script)
        return bool(result)
    except Exception:
        return False


async def detect_login_success(session_id: str, browser: ChromeBrowser, original_url: str) -> bool:
    """Detect if login was successful.
    
    Args:
        session_id: Target session ID
        browser: Chrome browser instance
        original_url: Original URL before login
        
    Returns:
        True if login appears successful
    """
    current_url = await browser.get_current_url(session_id)
    
    if current_url != original_url:
        lower_url = current_url.lower()
        if not any(x in lower_url for x in ["login", "signin", "auth", "password"]):
            return True
    
    is_login_page = await detect_login_page(session_id, browser)
    if not is_login_page:
        return True
    
    script = """
    (function() {
        const hasPasswordField = document.querySelector("input[type='password']") !== null;
        const hasLoginForm = document.querySelector("form[action*='login'], form[action*='signin'], #login-form, .login-form") !== null;
        
        if (!hasPasswordField && !hasLoginForm) {
            return true;
        }
        
        const bodyText = document.body ? document.body.innerText.toLowerCase() : '';
        const loginTextIndicators = ['账号登录', '短信登录', '账号密码', '请登录', '登录账号'];
        for (const indicator of loginTextIndicators) {
            if (bodyText.includes(indicator.toLowerCase())) {
                return false;
            }
        }
        
        return false;
    })()
    """
    
    try:
        result = await browser.evaluate_script(session_id, script)
        return bool(result)
    except Exception:
        return False


async def wait_for_login_completion(
    session_id: str,
    browser: ChromeBrowser,
    original_url: str,
    max_wait_ms: int = MAX_LOGIN_WAIT_MS,
    check_interval_ms: int = LOGIN_CHECK_INTERVAL_MS,
    on_status: Optional[Callable[[str], None]] = None
) -> bool:
    """Wait for login to complete with automatic detection.
    
    Args:
        session_id: Target session ID
        browser: Chrome browser instance
        original_url: Original URL before login
        max_wait_ms: Maximum wait time in milliseconds
        check_interval_ms: Check interval in milliseconds
        on_status: Optional callback for status updates
        
    Returns:
        True if login completed successfully
    """
    start_time = time.time()
    max_wait = max_wait_ms / 1000
    interval = check_interval_ms / 1000
    
    while time.time() - start_time < max_wait:
        try:
            success = await detect_login_success(session_id, browser, original_url)
            if success:
                if on_status:
                    on_status("Login detected as successful")
                return True
        except Exception:
            pass
        
        await asyncio.sleep(interval)
    
    if on_status:
        on_status("Login wait timeout - proceeding anyway")
    
    return False


CONTENT_EXTRACTION_SCRIPT = """
(function() {
    const baseUrl = document.baseURI || location.href;
    
    function toAbsolute(url) {
        if (!url) return url;
        try {
            return new URL(url, baseUrl).href;
        } catch {
            return url;
        }
    }
    
    function absolutizeAttr(selector, attr) {
        document.querySelectorAll(selector).forEach((el) => {
            const value = el.getAttribute(attr);
            if (!value) return;
            const abs = toAbsolute(value);
            if (abs) el.setAttribute(attr, abs);
        });
    }
    
    function absolutizeSrcset(selector) {
        document.querySelectorAll(selector).forEach((el) => {
            const srcset = el.getAttribute("srcset");
            if (!srcset) return;
            
            const normalized = srcset
                .split(",")
                .map((part) => {
                    const trimmed = part.trim();
                    if (!trimmed) return "";
                    const pieces = trimmed.split(/\\s+/);
                    const url = pieces[0];
                    const descriptor = pieces.slice(1).join(" ");
                    const absoluteUrl = toAbsolute(url);
                    return descriptor ? absoluteUrl + " " + descriptor : absoluteUrl;
                })
                .filter(Boolean)
                .join(", ");
            
            if (normalized) {
                el.setAttribute("srcset", normalized);
            }
        });
    }
    
    absolutizeAttr("a[href]", "href");
    absolutizeAttr("img[src], video[src], audio[src], source[src]", "src");
    absolutizeSrcset("img[srcset], source[srcset]");
    
    const removeSelectors = [
        "noscript", "template", ".cookie-banner", ".cookie-consent",
        ".consent-banner", "[aria-label*='cookie' i]",
        ".advertisement", ".ads"
    ];
    
    for (const sel of removeSelectors) {
        try {
            document.querySelectorAll(sel).forEach((el) => el.remove());
        } catch {}
    }
    
    function getMeta(names) {
        for (const name of names) {
            const el = document.querySelector('meta[name="' + name + '"]') || 
                       document.querySelector('meta[property="' + name + '"]');
            const content = el && el.getAttribute("content");
            if (content && content.trim()) return content.trim();
        }
        return undefined;
    }
    
    function extractJsonLdMeta() {
        const scripts = document.querySelectorAll('script[type="application/ld+json"]');
        for (const script of scripts) {
            try {
                const parsed = JSON.parse(script.textContent || "");
                const items = Array.isArray(parsed) ? parsed : 
                             (Array.isArray(parsed["@graph"]) ? parsed["@graph"] : [parsed]);
                
                for (const item of items) {
                    const rawType = Array.isArray(item["@type"]) ? item["@type"][0] : item["@type"];
                    if (typeof rawType !== "string") continue;
                    if (!["Article", "NewsArticle", "BlogPosting", "WebPage"].includes(rawType)) continue;
                    
                    const author = (() => {
                        if (typeof item.author === "string") return item.author;
                        if (Array.isArray(item.author) && item.author.length > 0) {
                            const first = item.author[0];
                            return first && typeof first === "object" ? first.name : undefined;
                        }
                        if (item.author && typeof item.author === "object") {
                            return item.author.name;
                        }
                        return undefined;
                    })();
                    
                    return {
                        title: item.headline || item.name,
                        description: item.description,
                        author: typeof author === "string" ? author : undefined,
                        published: item.datePublished || item.dateCreated,
                    };
                }
            } catch {}
        }
        return {};
    }
    
    const jsonLd = extractJsonLdMeta();
    
    const title =
        getMeta(["og:title", "twitter:title"]) ||
        (typeof jsonLd.title === "string" ? jsonLd.title : undefined) ||
        document.querySelector("h1")?.textContent?.trim() ||
        document.title?.trim() ||
        "";
    
    const description =
        getMeta(["description", "og:description", "twitter:description"]) ||
        (typeof jsonLd.description === "string" ? jsonLd.description : undefined);
    
    const author =
        getMeta(["author", "article:author", "twitter:creator"]) ||
        (typeof jsonLd.author === "string" ? jsonLd.author : undefined);
    
    const published =
        document.querySelector("time[datetime]")?.getAttribute("datetime") ||
        getMeta(["article:published_time", "datePublished", "publishdate", "date"]) ||
        (typeof jsonLd.published === "string" ? jsonLd.published : undefined);
    
    return {
        title,
        description,
        author,
        published,
        html: document.documentElement.outerHTML,
        url: window.location.href
    };
})()
"""


async def extract_page_content(session_id: str, browser: ChromeBrowser, timeout_ms: int = DEFAULT_TIMEOUT_MS) -> dict:
    """Extract page content and metadata.
    
    Args:
        session_id: Target session ID
        browser: Chrome browser instance
        timeout_ms: Extraction timeout in milliseconds
        
    Returns:
        Dictionary with title, description, author, published, html, url
    """
    return await browser.evaluate_script(session_id, CONTENT_EXTRACTION_SCRIPT, timeout_ms)


async def capture_page(
    url: str,
    wait_for_login: bool = True,
    headless: bool = False,
    chrome_path: Optional[str] = None,
    on_status: Optional[Callable[[str], None]] = None
) -> dict:
    """Capture a web page with optional login detection.
    
    Args:
        url: URL to capture
        wait_for_login: Whether to wait for login if detected
        headless: Whether to run browser in headless mode
        chrome_path: Optional path to Chrome executable
        on_status: Optional callback for status updates
        
    Returns:
        Dictionary with extracted content and metadata
    """
    browser = ChromeBrowser()
    
    try:
        if on_status:
            on_status(f"Launching browser for: {url}")
        
        browser.launch(url, headless, chrome_path)
        await browser.connect()
        
        _, session_id = await browser.get_page_session()
        
        if on_status:
            on_status("Waiting for page to load...")
        
        await browser.wait_for_page_load(session_id, 15000)
        await browser.wait_for_network_idle(session_id)
        await asyncio.sleep(POST_LOAD_DELAY_MS / 1000)
        
        is_login_page = await detect_login_page(session_id, browser)
        
        if on_status:
            on_status(f"Login page detected: {is_login_page}")
        
        if is_login_page and wait_for_login and not headless:
            if on_status:
                on_status("Login page detected! Please log in the browser window...")
            
            login_success = await wait_for_login_completion(
                session_id, browser, url,
                on_status=on_status
            )
            
            if login_success:
                await browser.wait_for_network_idle(session_id)
                await asyncio.sleep(POST_LOAD_DELAY_MS / 1000)
        
        if on_status:
            on_status("Scrolling to trigger lazy-loaded content...")
        
        await browser.auto_scroll(session_id)
        await asyncio.sleep(POST_LOAD_DELAY_MS / 1000)
        
        if on_status:
            on_status("Extracting page content...")
        
        content = await extract_page_content(session_id, browser)
        
        return content
    
    finally:
        await browser.close()


def run_capture_sync(
    url: str,
    wait_for_login: bool = True,
    headless: bool = False,
    chrome_path: Optional[str] = None,
    on_status: Optional[Callable[[str], None]] = None
) -> dict:
    """Synchronous wrapper for capture_page.
    
    Args:
        url: URL to capture
        wait_for_login: Whether to wait for login if detected
        headless: Whether to run browser in headless mode
        chrome_path: Optional path to Chrome executable
        on_status: Optional callback for status updates
        
    Returns:
        Dictionary with extracted content and metadata
    """
    return asyncio.run(capture_page(url, wait_for_login, headless, chrome_path, on_status))


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CDP Client for URL capture")
    parser.add_argument("url", help="URL to capture")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--no-wait-login", action="store_true", help="Don't wait for login")
    
    args = parser.parse_args()
    
    def print_status(msg: str) -> None:
        print(f"[STATUS] {msg}")
    
    result = run_capture_sync(
        args.url,
        wait_for_login=not args.no_wait_login,
        headless=args.headless,
        on_status=print_status
    )
    
    print(f"\nTitle: {result.get('title', 'N/A')}")
    print(f"URL: {result.get('url', 'N/A')}")
    print(f"HTML length: {len(result.get('html', ''))}")
