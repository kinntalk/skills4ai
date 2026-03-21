#!/usr/bin/env python3
"""
DOM Analyzer for WeChat Official Account Editor (Enhanced)

Analyzes the actual DOM structure including Shadow DOM.
"""

import asyncio
import sys
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Error: playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)

from session_manager import SessionManager


async def analyze_dom():
    """Analyze WeChat editor DOM structure including Shadow DOM."""
    session_manager = SessionManager(Path.home() / '.wechat-publisher')
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    context = await session_manager.load_session(browser)
    page = await context.new_page()
    
    new_article_url = "https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=10&lang=zh_CN"
    
    print("Navigating to new article page...")
    await page.goto(new_article_url, timeout=30000)
    await page.wait_for_load_state('networkidle')
    
    print("Waiting for page to fully load (10 seconds)...")
    await page.wait_for_timeout(10000)
    
    print("\n" + "=" * 60)
    print("DOM ANALYSIS RESULTS (Enhanced)")
    print("=" * 60)
    
    print("\n1. PAGE URL:")
    print("-" * 40)
    print(f"  {page.url}")
    
    print("\n2. PAGE TITLE:")
    print("-" * 40)
    title = await page.title()
    print(f"  {title}")
    
    print("\n3. HTML STRUCTURE (first 5000 chars):")
    print("-" * 40)
    html = await page.content()
    print(html[:5000])
    
    print("\n4. USING JAVASCRIPT TO FIND ELEMENTS:")
    print("-" * 40)
    
    js_results = await page.evaluate('''() => {
        const results = {
            inputs: [],
            iframes: [],
            editables: [],
            buttons: [],
            shadowRoots: [],
            titleInputs: [],
            editors: []
        };
        
        document.querySelectorAll('input').forEach(el => {
            results.inputs.push({
                id: el.id,
                className: el.className,
                placeholder: el.placeholder,
                type: el.type,
                name: el.name,
                visible: el.offsetParent !== null
            });
        });
        
        document.querySelectorAll('iframe').forEach(el => {
            results.iframes.push({
                id: el.id,
                className: el.className,
                src: el.src ? el.src.substring(0, 100) : null,
                visible: el.offsetParent !== null
            });
        });
        
        document.querySelectorAll('[contenteditable="true"]').forEach(el => {
            results.editables.push({
                tagName: el.tagName,
                id: el.id,
                className: el.className,
                visible: el.offsetParent !== null
            });
        });
        
        document.querySelectorAll('button, [role="button"], .btn').forEach(el => {
            results.buttons.push({
                tagName: el.tagName,
                id: el.id,
                className: el.className,
                text: el.innerText ? el.innerText.substring(0, 50) : null,
                visible: el.offsetParent !== null
            });
        });
        
        document.querySelectorAll('*').forEach(el => {
            if (el.shadowRoot) {
                results.shadowRoots.push({
                    tagName: el.tagName,
                    id: el.id,
                    className: el.className
                });
            }
        });
        
        document.querySelectorAll('*').forEach(el => {
            const text = el.innerText || '';
            if (text.includes('标题') || text.includes('title') || text.includes('Title')) {
                if (el.tagName === 'INPUT' || el.tagName === 'DIV' || el.tagName === 'SECTION') {
                    results.titleInputs.push({
                        tagName: el.tagName,
                        id: el.id,
                        className: el.className,
                        placeholder: el.placeholder,
                        text: text.substring(0, 100)
                    });
                }
            }
        });
        
        document.querySelectorAll('*').forEach(el => {
            const classLower = (el.className || '').toLowerCase();
            const idLower = (el.id || '').toLowerCase();
            if (classLower.includes('editor') || idLower.includes('editor') ||
                classLower.includes('content') || idLower.includes('content')) {
                results.editors.push({
                    tagName: el.tagName,
                    id: el.id,
                    className: el.className,
                    contentEditable: el.contentEditable
                });
            }
        });
        
        return results;
    }''')
    
    print("\n  INPUTS:")
    for i, inp in enumerate(js_results['inputs'][:10]):
        print(f"    #{i+1}: {inp}")
    
    print("\n  IFRAMES:")
    for i, iframe in enumerate(js_results['iframes'][:10]):
        print(f"    #{i+1}: {iframe}")
    
    print("\n  CONTENTEDITABLE:")
    for i, edit in enumerate(js_results['editables'][:10]):
        print(f"    #{i+1}: {edit}")
    
    print("\n  BUTTONS:")
    for i, btn in enumerate(js_results['buttons'][:10]):
        print(f"    #{i+1}: {btn}")
    
    print("\n  SHADOW ROOTS:")
    for i, shadow in enumerate(js_results['shadowRoots'][:10]):
        print(f"    #{i+1}: {shadow}")
    
    print("\n  TITLE-RELATED ELEMENTS:")
    for i, el in enumerate(js_results['titleInputs'][:10]):
        print(f"    #{i+1}: {el}")
    
    print("\n  EDITOR-RELATED ELEMENTS:")
    for i, el in enumerate(js_results['editors'][:10]):
        print(f"    #{i+1}: {el}")
    
    screenshot_path = Path.home() / '.wechat-publisher' / 'debug' / 'dom_analysis_enhanced.png'
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
    await page.screenshot(path=str(screenshot_path), full_page=True)
    print(f"\nFull page screenshot saved: {screenshot_path}")
    
    print("\n" + "=" * 60)
    print("Analysis complete.")
    print("=" * 60)
    
    await browser.close()


if __name__ == "__main__":
    asyncio.run(analyze_dom())
