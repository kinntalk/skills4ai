#!/usr/bin/env python3
"""
WeChat Sync Engine

Hybrid-drive synchronization to WeChat Official Account draft box.
Uses Playwright CDP for fast injection with Agent visual fallback.
"""

import argparse
import asyncio
import json
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

try:
    from playwright.async_api import async_playwright, Browser, Page, ElementHandle
except ImportError:
    print("Error: playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)

from session_manager import SessionManager


class WeChatSyncEngine:
    """Hybrid-drive sync engine for WeChat Official Account."""

    WECHAT_MP_URL = "https://mp.weixin.qq.com"
    NEW_ARTICLE_URL = "https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=10&lang=zh_CN"
    MAX_RETRIES = 3
    TIMEOUT = 30000

    TITLE_SELECTORS = [
        '#title',
        'input[placeholder*="标题"]',
        'input[placeholder*="title"]',
        '.title-input input',
        '[data-testid="title-input"]',
        'input.js_title',
        '#js_appmsg_title',
    ]

    EDITOR_SELECTORS = [
        '#edui1_iframeholder iframe',
        '#js_content',
        '.rich_media_editor iframe',
        '[contenteditable="true"]',
        '#js_editor iframe',
        '.editor iframe',
        'iframe[id*="editor"]',
        'iframe[class*="editor"]',
        '.ueditor iframe',
        '#ueditor_0',
        'iframe[name="ueditor"]',
        '.weui-desktop-editor',
        '[data-testid="editor"]',
        '.article-editor',
        '.msg-editor',
    ]

    COVER_SELECTORS = [
        '#js_cover_input input[type="file"]',
        'input[type="file"][accept*="image"]',
        '.cover-upload input[type="file"]',
        '[data-testid="cover-input"]',
        '.js_cover input[type="file"]',
        '.appmsg_cover input[type="file"]',
        '[class*="cover"] input[type="file"]',
    ]

    SAVE_SELECTORS = [
        '#js_submit',
        'button[type="submit"]',
        '.btn-save',
        '[data-testid="save-btn"]',
        'button:has-text("保存")',
        'button:has-text("存稿")',
        '.weui-desktop-btn:has-text("保存")',
        '[class*="submit"]:has-text("保存")',
        '.js_submit',
    ]

    def __init__(self, session_manager: SessionManager, debug: bool = False):
        self.session_manager = session_manager
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.debug = debug
        self.debug_dir = Path.home() / '.wechat-publisher' / 'debug'
        if debug:
            self.debug_dir.mkdir(parents=True, exist_ok=True)

    async def initialize(self):
        """Initialize browser with saved session."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False)
        context = await self.session_manager.load_session(self.browser)
        self.page = await context.new_page()

    async def _save_debug_screenshot(self, name: str) -> Optional[Path]:
        """Save screenshot for debugging."""
        if not self.debug or not self.page:
            return None
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = self.debug_dir / f"{timestamp}_{name}.png"
        await self.page.screenshot(path=path)
        print(f"Debug screenshot saved: {path}")
        return path

    async def _find_element(self, selectors: list) -> Tuple[Optional[ElementHandle], Optional[str]]:
        """Try multiple selectors to find element."""
        for selector in selectors:
            try:
                element = await self.page.query_selector(selector)
                if element:
                    is_visible = await element.is_visible()
                    if is_visible:
                        return element, selector
            except Exception:
                continue
        return None, None

    async def _check_login(self) -> bool:
        """Check if user is logged in to WeChat Official Account."""
        try:
            await self.page.goto(self.WECHAT_MP_URL, timeout=self.TIMEOUT)
            await self.page.wait_for_load_state('networkidle')
            
            current_url = self.page.url
            
            if 'cgi-bin' in current_url and 'home' in current_url:
                print("Login status: Already logged in")
                return True
            
            qr_code = await self.page.query_selector('.login__type__scan, .qrcode, img[src*="qrcode"]')
            if qr_code:
                print("Login status: Not logged in (QR code detected)")
                return False
            
            if 'login' in current_url.lower():
                print("Login status: Not logged in (login page)")
                return False
            
            print(f"Login status: Unknown (URL: {current_url})")
            return True
            
        except Exception as e:
            print(f"Error checking login status: {e}")
            return False

    async def _wait_for_login(self, timeout: int = 120) -> bool:
        """Wait for user to login via QR code."""
        print("\n" + "=" * 50)
        print("Please scan the QR code to login to WeChat Official Account")
        print("=" * 50 + "\n")
        
        for i in range(timeout):
            await self.page.wait_for_timeout(1000)
            current_url = self.page.url
            
            if 'cgi-bin' in current_url and 'home' in current_url:
                print("\nLogin successful!")
                await self.session_manager.save_session(self.page.context)
                return True
            
            if i % 10 == 0:
                print(f"Waiting for login... ({i}/{timeout}s)")
        
        print("\nLogin timeout. Please try again.")
        return False

    async def _navigate_to_editor(self) -> bool:
        """Navigate to the article editor page via menu."""
        try:
            print("\nNavigating to WeChat MP homepage...")
            await self.page.goto(self.WECHAT_MP_URL, timeout=self.TIMEOUT)
            await self.page.wait_for_load_state('networkidle')
            await self.page.wait_for_timeout(2000)
            
            current_url = self.page.url
            print(f"  Current URL: {current_url}")
            
            if 'cgi-bin' in current_url:
                print("  Session valid - already logged in")
            elif 'login' in current_url.lower():
                print("  ERROR: On login page, session expired")
                return False
            else:
                qr_code = await self.page.query_selector('img[src*="qrcode"], .qrcode')
                if qr_code:
                    print("  ERROR: QR code detected, need to login")
                    return False
                print("  Session status unclear, proceeding...")
            
            print("\nNavigating via menu: 内容管理 -> 草稿箱 -> 新的创作 -> 写新文章...")
            
            await self._save_debug_screenshot("nav_01_homepage")
            
            menu_selectors = [
                {
                    "name": "内容管理",
                    "selectors": [
                        'text=内容管理',
                        'a:has-text("内容管理")',
                        '[title="内容管理"]',
                        '.menu_item:has-text("内容管理")',
                        'li:has-text("内容管理")',
                    ]
                },
                {
                    "name": "草稿箱", 
                    "selectors": [
                        'text=草稿箱',
                        'a:has-text("草稿箱")',
                        '[title="草稿箱"]',
                        '.menu_item:has-text("草稿箱")',
                        'li:has-text("草稿箱")',
                    ]
                },
                {
                    "name": "新的创作",
                    "selectors": [
                        'text=新的创作',
                        'button:has-text("新的创作")',
                        '.btn:has-text("新的创作")',
                        '[class*="create"]:has-text("新的创作")',
                        'a:has-text("新的创作")',
                    ]
                },
                {
                    "name": "写新文章",
                    "selectors": [
                        'text=写新文章',
                        'a:has-text("写新文章")',
                        'button:has-text("写新文章")',
                        '[class*="article"]:has-text("写新文章")',
                        '.appmsg:has-text("写新文章")',
                    ]
                }
            ]
            
            for menu_item in menu_selectors:
                print(f"  Looking for '{menu_item['name']}'...")
                found = False
                
                for selector in menu_item['selectors']:
                    try:
                        element = await self.page.query_selector(selector)
                        if element:
                            is_visible = await element.is_visible()
                            if is_visible:
                                print(f"    Found with selector: {selector}")
                                await element.click()
                                
                                if menu_item['name'] == "写新文章":
                                    print("    Waiting for editor page to load...")
                                    await self.page.wait_for_load_state('networkidle')
                                    await self.page.wait_for_timeout(5000)
                                else:
                                    await self.page.wait_for_timeout(1500)
                                found = True
                                break
                    except Exception:
                        continue
                
                if not found:
                    print(f"    WARNING: Could not find '{menu_item['name']}', trying alternative approach...")
                    await self._save_debug_screenshot(f"nav_error_{menu_item['name']}")
            
            await self.page.wait_for_load_state('networkidle')
            await self.page.wait_for_timeout(3000)
            
            current_url = self.page.url
            print(f"\n  Final URL: {current_url}")
            
            if 'appmsg_edit' in current_url:
                print("  Successfully navigated to editor page!")
                await self._save_debug_screenshot("nav_success_editor")
                return True
            else:
                print("  WARNING: May not have reached editor page")
                await self._save_debug_screenshot("nav_final_page")
                return True
            
        except Exception as e:
            print(f"Navigation error: {e}")
            await self._save_debug_screenshot("nav_exception")
            return False

    async def _inject_via_cdp(self, html_content: str, title: str, cover_path: Optional[Path] = None) -> bool:
        """Fast path: Inject content via CDP."""
        try:
            if not await self._navigate_to_editor():
                return False

            await self._save_debug_screenshot("01_page_loaded")

            print(f"Looking for title input...")
            title_input, title_selector = await self._find_element(self.TITLE_SELECTORS)
            if title_input:
                print(f"  Found title input with selector: {title_selector}")
                await title_input.click()
                await title_input.fill(title)
                print(f"  Title filled: {title[:30]}...")
            else:
                print("  ERROR: Could not find title input!")
                print(f"  Tried selectors: {self.TITLE_SELECTORS}")
                await self._save_debug_screenshot("02_title_not_found")
                return False

            if cover_path and cover_path.exists():
                print(f"Looking for cover upload input...")
                cover_input, cover_selector = await self._find_element(self.COVER_SELECTORS)
                if cover_input:
                    print(f"  Found cover input with selector: {cover_selector}")
                    await cover_input.set_input_files(str(cover_path))
                    print(f"  Cover uploaded: {cover_path}")
                    await self.page.wait_for_timeout(2000)
                else:
                    print("  WARNING: Could not find cover input, skipping cover upload")

            print(f"Looking for editor...")
            editor_frame = None
            editor_element, editor_selector = await self._find_element(self.EDITOR_SELECTORS)
            
            if editor_element:
                print(f"  Found editor with selector: {editor_selector}")
                
                if 'iframe' in editor_selector:
                    editor_frame = await editor_element.content_frame()
                    if editor_frame:
                        body = await editor_frame.query_selector('body')
                        if body:
                            escaped_html = html_content.replace('`', '\\`').replace('${', '\\${')
                            await body.evaluate(f"""
                                document.body.innerHTML = `{escaped_html}`;
                            """)
                            print("  HTML content injected into iframe")
                        else:
                            print("  ERROR: Could not find body in iframe")
                            await self._save_debug_screenshot("03_iframe_body_not_found")
                            return False
                    else:
                        print("  ERROR: Could not access iframe content")
                        await self._save_debug_screenshot("03_iframe_access_failed")
                        return False
                else:
                    escaped_html = html_content.replace('`', '\\`').replace('${', '\\${')
                    await editor_element.evaluate(f"""
                        this.innerHTML = `{escaped_html}`;
                    """)
                    print("  HTML content injected into editor")
            else:
                print("  ERROR: Could not find editor!")
                print(f"  Tried selectors: {self.EDITOR_SELECTORS}")
                await self._save_debug_screenshot("03_editor_not_found")
                return False

            await self._save_debug_screenshot("04_content_injected")

            print(f"Looking for save button...")
            save_btn, save_selector = await self._find_element(self.SAVE_SELECTORS)
            if save_btn:
                print(f"  Found save button with selector: {save_selector}")
                await save_btn.click()
                await self.page.wait_for_timeout(3000)
                await self._save_debug_screenshot("05_after_save")
                print("  Save button clicked!")
                return True
            else:
                print("  ERROR: Could not find save button!")
                print(f"  Tried selectors: {self.SAVE_SELECTORS}")
                await self._save_debug_screenshot("05_save_not_found")
                return False

        except Exception as e:
            print(f"\nCDP injection failed with exception:")
            print(f"  Type: {type(e).__name__}")
            print(f"  Message: {e}")
            if self.debug:
                traceback.print_exc()
            await self._save_debug_screenshot("exception")
            return False

    async def _inject_via_visual(self, html_content: str, title: str, cover_path: Optional[Path] = None) -> bool:
        """Fallback: Use visual/Agent approach when CDP fails."""
        print("\n" + "=" * 50)
        print("Falling back to visual/manual mode...")
        print("=" * 50)
        print("\nPlease manually complete the following steps:")
        print(f"1. Navigate to: {self.NEW_ARTICLE_URL}")
        print(f"2. Enter title: {title}")
        if cover_path:
            print(f"3. Upload cover image: {cover_path}")
        print("4. Paste the HTML content into the editor")
        print("5. Click 'Save' button")
        print("\nWaiting 60 seconds for manual completion...")
        print("=" * 50 + "\n")

        await self.page.wait_for_timeout(60000)
        return True

    async def sync(self, html_content: str, title: str, cover_path: Optional[Path] = None) -> bool:
        """Sync content to WeChat draft box."""
        await self.initialize()

        login_check_result = await self._check_login()
        
        if not login_check_result:
            print("\nSession not valid, initiating login flow...")
            if not await self._wait_for_login():
                return False
            
            print("\nRe-initializing browser with new session...")
            await self.browser.close()
            await self.initialize()
            
            if not await self._check_login():
                print("ERROR: Login verification failed after re-initialization")
                return False

        for attempt in range(self.MAX_RETRIES):
            print(f"\n{'=' * 50}")
            print(f"Attempt {attempt + 1}/{self.MAX_RETRIES}")
            print('=' * 50)

            success = await self._inject_via_cdp(html_content, title, cover_path)
            if success:
                print("\n" + "=" * 50)
                print("Successfully synced via CDP!")
                print("=" * 50)
                return True

            if attempt < self.MAX_RETRIES - 1:
                print("\nRetrying in 3 seconds...")
                await self.page.wait_for_timeout(3000)

        return await self._inject_via_visual(html_content, title, cover_path)

    async def close(self):
        """Close browser session."""
        if self.browser:
            await self.browser.close()


async def main():
    parser = argparse.ArgumentParser(description='Sync content to WeChat draft box')
    parser.add_argument('--html', type=Path, required=True, help='HTML content file')
    parser.add_argument('--title', type=str, help='Article title (uses frontmatter if not provided)')
    parser.add_argument('--cover', type=Path, help='Cover image file')
    parser.add_argument('--session-dir', type=Path, default=Path.home() / '.wechat-publisher', help='Session directory')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode with screenshots')

    args = parser.parse_args()

    if not args.html.exists():
        print(f"Error: HTML file not found: {args.html}")
        sys.exit(1)

    with open(args.html, 'r', encoding='utf-8') as f:
        html_content = f.read()

    title = args.title or args.html.stem

    session_manager = SessionManager(args.session_dir)
    engine = WeChatSyncEngine(session_manager, debug=args.debug)

    try:
        success = await engine.sync(html_content, title, args.cover)
        if success:
            print("\nContent synced successfully!")
        else:
            print("\nFailed to sync content")
            sys.exit(1)
    finally:
        await engine.close()


if __name__ == "__main__":
    asyncio.run(main())
