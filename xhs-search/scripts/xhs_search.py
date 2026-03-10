#!/usr/bin/env python3
"""
XHS Search to Obsidian - Main CLI Entry Point
Search Xiaohongshu and save results to Obsidian vault.
"""

import argparse
import sys
import time
from pathlib import Path
from datetime import datetime
from urllib.parse import quote

from config_manager import ConfigManager
from browser_automation import BrowserAutomation
from content_extractor import XHSExtractor
from ofm_formatter import OFMFormatter


def get_skill_dir() -> Path:
    return Path(__file__).parent.parent


def cmd_search(args, config: ConfigManager):
    keyword = args.keyword
    limit = args.limit or config.get("search.default_limit", 20)
    sort = args.sort or "general"
    subfolder = args.subfolder or config.get("output.subfolder", "xiaohongshu")
    tags = args.tags.split(",") if args.tags else []
    default_tags = config.get("output.default_tags", ["xhs-search"])
    all_tags = list(set(default_tags + tags))
    
    print(f"正在搜索: {keyword}")
    print(f"排序方式: {sort}")
    print(f"结果数量: {limit}")
    
    browser = BrowserAutomation(
        session_name=config.get("browser.session_name", "xhs-search"),
        timeout=config.get("browser.timeout", 30000),
        headed=args.headed or config.get("browser.headed", False)
    )
    
    try:
        if not browser.is_logged_in():
            print("需要登录小红书...")
            browser.open("https://www.xiaohongshu.com")
            if not browser.wait_for_login(timeout=120):
                print("登录失败或超时")
                return 1
        
        print("正在搜索...")
        browser.search(keyword, sort)
        time.sleep(2)
        
        browser.scroll_to_load_more(times=2, delay=config.get("search.request_delay", 2.0))
        
        html = browser.get_page_html()
        
        extractor = XHSExtractor()
        result = extractor.extract_search_results(html, keyword)
        result.notes = result.notes[:limit]
        result.total = len(result.notes)
        
        print(f"找到 {result.total} 条结果")
        
        vault_path = config.get_vault_path()
        if not vault_path:
            print("错误: 未找到 Obsidian vault，请运行 'config set-vault <path>'")
            return 1
        
        asset_folder = config.get_asset_folder()
        formatter = OFMFormatter(
            vault_path=vault_path,
            asset_folder=asset_folder,
            wikilink=config.get("assets.wikilink", True)
        )
        
        content = formatter.format_search_result(result, all_tags)
        
        filename = args.output or f"search-{keyword}-{datetime.now().strftime('%Y-%m-%d')}"
        output_path = formatter.save_to_vault(content, filename, subfolder)
        
        print(f"已保存到: {output_path}")
        return 0
        
    except Exception as e:
        print(f"搜索失败: {e}")
        return 1
    finally:
        if not args.keep_open:
            browser.close()


def cmd_comments(args, config: ConfigManager):
    note_input = args.note_url_or_id
    
    extractor = XHSExtractor()
    note_id = extractor.extract_note_id_from_url(note_input)
    if not note_id:
        note_id = note_input
    
    print(f"正在获取笔记评论: {note_id}")
    
    browser = BrowserAutomation(
        session_name=config.get("browser.session_name", "xhs-search"),
        timeout=config.get("browser.timeout", 30000),
        headed=args.headed or config.get("browser.headed", False)
    )
    
    try:
        if not browser.is_logged_in():
            print("需要登录小红书...")
            browser.open("https://www.xiaohongshu.com")
            if not browser.wait_for_login(timeout=120):
                print("登录失败或超时")
                return 1
        
        browser.open_note(note_id)
        time.sleep(2)
        
        html = browser.get_page_html()
        
        note = extractor.extract_note_detail(html, note_id)
        if not note:
            print("无法获取笔记信息")
            return 1
        
        print("正在加载评论...")
        for _ in range(3):
            browser.scroll("down", 500)
            time.sleep(1)
        
        html = browser.get_page_html()
        comments = extractor.extract_comments(html, limit=args.limit or 50)
        
        print(f"获取到 {len(comments)} 条评论")
        
        vault_path = config.get_vault_path()
        if not vault_path:
            print("错误: 未找到 Obsidian vault")
            return 1
        
        asset_folder = config.get_asset_folder()
        formatter = OFMFormatter(
            vault_path=vault_path,
            asset_folder=asset_folder,
            wikilink=config.get("assets.wikilink", True)
        )
        
        content = formatter.format_comments(note, comments)
        
        filename = args.output or f"comments-{note_id}-{datetime.now().strftime('%Y-%m-%d')}"
        subfolder = args.subfolder or config.get("output.subfolder", "xiaohongshu")
        output_path = formatter.save_to_vault(content, filename, subfolder)
        
        print(f"已保存到: {output_path}")
        return 0
        
    except Exception as e:
        print(f"获取评论失败: {e}")
        return 1
    finally:
        if not args.keep_open:
            browser.close()


def cmd_note(args, config: ConfigManager):
    note_input = args.note_url_or_id
    
    extractor = XHSExtractor()
    note_id = extractor.extract_note_id_from_url(note_input)
    if not note_id:
        note_id = note_input
    
    print(f"正在获取笔记详情: {note_id}")
    
    browser = BrowserAutomation(
        session_name=config.get("browser.session_name", "xhs-search"),
        timeout=config.get("browser.timeout", 30000),
        headed=args.headed or config.get("browser.headed", False)
    )
    
    try:
        if not browser.is_logged_in():
            print("需要登录小红书...")
            browser.open("https://www.xiaohongshu.com")
            if not browser.wait_for_login(timeout=120):
                print("登录失败或超时")
                return 1
        
        browser.open_note(note_id)
        time.sleep(2)
        
        html = browser.get_page_html()
        
        note = extractor.extract_note_detail(html, note_id)
        if not note:
            print("无法获取笔记信息")
            return 1
        
        comments = []
        if args.with_comments:
            print("正在加载评论...")
            for _ in range(3):
                browser.scroll("down", 500)
                time.sleep(1)
            html = browser.get_page_html()
            comments = extractor.extract_comments(html, limit=20)
        
        vault_path = config.get_vault_path()
        if not vault_path:
            print("错误: 未找到 Obsidian vault")
            return 1
        
        asset_folder = config.get_asset_folder()
        formatter = OFMFormatter(
            vault_path=vault_path,
            asset_folder=asset_folder,
            wikilink=config.get("assets.wikilink", True)
        )
        
        tags = args.tags.split(",") if args.tags else []
        content = formatter.format_note_detail(note, tags, args.with_comments, comments)
        
        filename = args.output or f"note-{note_id}-{datetime.now().strftime('%Y-%m-%d')}"
        subfolder = args.subfolder or config.get("output.subfolder", "xiaohongshu")
        output_path = formatter.save_to_vault(content, filename, subfolder)
        
        print(f"已保存到: {output_path}")
        return 0
        
    except Exception as e:
        print(f"获取笔记失败: {e}")
        return 1
    finally:
        if not args.keep_open:
            browser.close()


def cmd_config(args, config: ConfigManager):
    if args.config_command == "list":
        print(config.list_config())
    elif args.config_command == "get":
        value = config.get(args.key)
        print(f"{args.key}: {value}")
    elif args.config_command == "set":
        config.set(args.key, args.value)
        print(f"已设置 {args.key} = {args.value}")
    elif args.config_command == "set-vault":
        config.set_vault_path(args.path)
        print(f"已设置 vault 路径: {args.path}")
    else:
        print("未知配置命令")
        return 1
    return 0


def cmd_login(args, config: ConfigManager):
    browser = BrowserAutomation(
        session_name=config.get("browser.session_name", "xhs-search"),
        timeout=config.get("browser.timeout", 30000),
        headed=True
    )
    
    try:
        if args.reset:
            print("清除旧登录状态...")
            browser.close()
        
        print("请在浏览器中登录小红书...")
        browser.open("https://www.xiaohongshu.com")
        
        if browser.wait_for_login(timeout=180):
            print("登录成功！登录状态已保存。")
            return 0
        else:
            print("登录超时")
            return 1
    finally:
        browser.close()


def main():
    parser = argparse.ArgumentParser(
        description="XHS Search to Obsidian - 搜索小红书并保存到 Obsidian",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 搜索笔记 (中文)
  python xhs_search.py search "英语学习"
  
  # Search notes (English)
  python xhs_search.py search "Learning English"
  
  # 获取笔记评论
  python xhs_search.py comments "https://www.xiaohongshu.com/explore/xxxxx"
  
  # 获取笔记详情
  python xhs_search.py note "65abc123" --with-comments
  
  # 配置 vault 路径
  python xhs_search.py config set-vault "D:/Obsidian/MyVault"
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    search_parser = subparsers.add_parser("search", help="搜索小红书笔记 / Search Xiaohongshu notes")
    search_parser.add_argument("keyword", help="搜索关键词 / Search keyword")
    search_parser.add_argument("-o", "--output", help="输出文件名 / Output filename")
    search_parser.add_argument("--limit", type=int, help="最大结果数 / Max results")
    search_parser.add_argument("--sort", choices=["general", "newest", "hottest"], help="排序方式 / Sort by")
    search_parser.add_argument("--tags", help="附加标签 (逗号分隔) / Additional tags (comma-separated)")
    search_parser.add_argument("--subfolder", help="保存子目录 / Subfolder to save")
    search_parser.add_argument("--headed", action="store_true", help="显示浏览器 / Show browser")
    search_parser.add_argument("--keep-open", action="store_true", help="保持浏览器打开 / Keep browser open")
    
    comments_parser = subparsers.add_parser("comments", help="获取笔记评论 / Get note comments")
    comments_parser.add_argument("note_url_or_id", help="笔记链接或ID / Note URL or ID")
    comments_parser.add_argument("-o", "--output", help="输出文件名 / Output filename")
    comments_parser.add_argument("--limit", type=int, help="最大评论数 / Max comments")
    comments_parser.add_argument("--hot", action="store_true", help="按热度排序 / Sort by hot")
    comments_parser.add_argument("--subfolder", help="保存子目录 / Subfolder to save")
    comments_parser.add_argument("--headed", action="store_true", help="显示浏览器 / Show browser")
    comments_parser.add_argument("--keep-open", action="store_true", help="保持浏览器打开 / Keep browser open")
    
    note_parser = subparsers.add_parser("note", help="获取笔记详情 / Get note details")
    note_parser.add_argument("note_url_or_id", help="笔记链接或ID / Note URL or ID")
    note_parser.add_argument("-o", "--output", help="输出文件名 / Output filename")
    note_parser.add_argument("--with-comments", action="store_true", help="包含评论 / Include comments")
    note_parser.add_argument("--tags", help="附加标签 / Additional tags")
    note_parser.add_argument("--subfolder", help="保存子目录 / Subfolder to save")
    note_parser.add_argument("--headed", action="store_true", help="显示浏览器 / Show browser")
    note_parser.add_argument("--keep-open", action="store_true", help="保持浏览器打开 / Keep browser open")
    
    config_parser = subparsers.add_parser("config", help="配置管理 / Configuration management")
    config_parser.add_argument("config_command", choices=["list", "get", "set", "set-vault"], help="配置命令 / Config command")
    config_parser.add_argument("key", nargs="?", help="配置键 / Config key")
    config_parser.add_argument("value", nargs="?", help="配置值 / Config value")
    config_parser.add_argument("path", nargs="?", help="Vault路径 / Vault path")
    
    login_parser = subparsers.add_parser("login", help="登录小红书 / Login to Xiaohongshu")
    login_parser.add_argument("--reset", action="store_true", help="重新登录 / Re-login")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    config = ConfigManager()
    
    if args.command == "search":
        return cmd_search(args, config)
    elif args.command == "comments":
        return cmd_comments(args, config)
    elif args.command == "note":
        return cmd_note(args, config)
    elif args.command == "config":
        return cmd_config(args, config)
    elif args.command == "login":
        return cmd_login(args, config)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
