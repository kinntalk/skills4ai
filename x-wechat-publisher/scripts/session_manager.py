#!/usr/bin/env python3
"""
Session Manager

Manages browser sessions for WeChat Official Account login.
Handles session persistence, encryption, and restoration.
"""

import argparse
import asyncio
import base64
import json
import sys
from pathlib import Path
from typing import Optional

try:
    from playwright.async_api import BrowserContext, async_playwright
except ImportError:
    print("Error: playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)

try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class SessionManager:
    """Manages WeChat browser sessions with encryption."""

    SESSION_FILE = "session.json"
    COOKIES_FILE = "cookies.json"
    LOCAL_STORAGE_FILE = "local_storage.json"

    def __init__(self, session_dir: Path):
        self.session_dir = session_dir
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self._cipher = self._init_cipher()

    def _init_cipher(self) -> Optional[Fernet]:
        """Initialize encryption cipher."""
        if not CRYPTO_AVAILABLE:
            return None

        key_file = self.session_dir / ".key"
        if key_file.exists():
            key = key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            key_file.write_bytes(key)
            key_file.chmod(0o600)

        return Fernet(key)

    def _encrypt(self, data: str) -> str:
        """Encrypt data if encryption is available."""
        if self._cipher:
            return self._cipher.encrypt(data.encode()).decode()
        return base64.b64encode(data.encode()).decode()

    def _decrypt(self, data: str) -> str:
        """Decrypt data if encryption is available."""
        if self._cipher:
            return self._cipher.decrypt(data.encode()).decode()
        return base64.b64decode(data.encode()).decode()

    async def save_session(self, context: BrowserContext):
        """Save browser session data."""
        cookies = await context.cookies()
        storage = await context.storage_state()

        session_data = {
            "cookies": cookies,
            "storage": storage
        }

        session_file = self.session_dir / self.SESSION_FILE
        encrypted = self._encrypt(json.dumps(session_data))
        session_file.write_text(encrypted)
        print(f"Session saved to: {session_file}")

    async def load_session(self, browser) -> BrowserContext:
        """Load browser session data."""
        session_file = self.session_dir / self.SESSION_FILE

        if session_file.exists():
            try:
                encrypted = session_file.read_text()
                decrypted = self._decrypt(encrypted)
                session_data = json.loads(decrypted)

                context = await browser.new_context(
                    storage_state=session_data.get("storage")
                )
                await context.add_cookies(session_data.get("cookies", []))
                print("Session restored successfully!")
                return context
            except Exception as e:
                print(f"Failed to load session: {e}")
                print("Creating new session...")

        return await browser.new_context()

    def clear_session(self):
        """Clear saved session data."""
        for file in [self.SESSION_FILE, self.COOKIES_FILE, self.LOCAL_STORAGE_FILE]:
            path = self.session_dir / file
            if path.exists():
                path.unlink()
        print("Session cleared.")

    async def setup(self):
        """Interactive session setup with QR code login."""
        print("Starting browser for WeChat login...")
        print("Please scan the QR code to log in.")

        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://mp.weixin.qq.com")
        print("Waiting for login...")

        max_wait = 120
        for i in range(max_wait):
            await page.wait_for_timeout(1000)
            current_url = page.url
            if "cgi-bin" in current_url and "home" in current_url:
                print("Login successful!")
                await self.save_session(context)
                await browser.close()
                return True

            if i % 10 == 0:
                print(f"Waiting for login... ({i}/{max_wait}s)")

        print("Login timeout. Please try again.")
        await browser.close()
        return False


async def main():
    parser = argparse.ArgumentParser(description='Manage WeChat browser sessions')
    parser.add_argument('--setup', action='store_true', help='Setup new session with QR login')
    parser.add_argument('--clear', action='store_true', help='Clear saved session')
    parser.add_argument('--session-dir', type=Path, default=Path.home() / '.wechat-publisher', help='Session directory')

    args = parser.parse_args()

    manager = SessionManager(args.session_dir)

    if args.setup:
        success = await manager.setup()
        sys.exit(0 if success else 1)
    elif args.clear:
        manager.clear_session()
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
