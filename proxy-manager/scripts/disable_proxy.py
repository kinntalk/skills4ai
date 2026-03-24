#!/usr/bin/env python3
"""
一键关闭代理
- 清除 Git 全局代理
- 更新 proxy_config.json 配置文件
"""
import json
import os
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from proxy_utils import clear_git_proxy, get_git_proxy_status, get_windows_proxy_status, clear_windows_proxy

TRA_DIR = Path(__file__).parent.parent.parent.parent
PROXY_CONFIG_PATH = TRA_DIR / 'proxy_config.json'


def load_proxy_config():
    if not os.path.exists(PROXY_CONFIG_PATH):
        return None
    with open(PROXY_CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_proxy_config(config):
    with open(PROXY_CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def disable_proxy_config() -> bool:
    config = load_proxy_config()
    if not config:
        return False
    
    config['proxy']['enabled'] = False
    config['proxy']['force_proxy_domains'] = []
    save_proxy_config(config)
    return True


def disable_proxy(clear_windows=False):
    print("=" * 50)
    print("关闭代理")
    print("=" * 50)
    
    print(f"\n[1/3] 清除 Git 全局代理...")
    before = get_git_proxy_status()
    if before['http_proxy'] or before['https_proxy']:
        if clear_git_proxy():
            print(f"      ✓ Git 全局代理已清除")
        else:
            print(f"      ✗ 清除 Git 代理失败")
    else:
        print(f"      - Git 全局代理未设置")
    
    if clear_windows:
        print(f"\n[2/3] 清除 Windows 系统代理...")
        win_before = get_windows_proxy_status()
        if win_before['enabled']:
            if clear_windows_proxy():
                print(f"      ✓ Windows 系统代理已禁用")
            else:
                print(f"      ✗ 禁用 Windows 系统代理失败")
        else:
            print(f"      - Windows 系统代理已经是禁用状态")
    else:
        print(f"\n[2/3] 跳过 Windows 系统代理（使用 --clear-windows 可同时清除）")
    
    print(f"\n[3/3] 更新配置文件...")
    if disable_proxy_config():
        print(f"      ✓ 配置文件已更新")
        print(f"      - enabled: False")
        print(f"      - force_proxy_domains: []")
    else:
        print(f"      - 配置文件不存在或无需修改")
    
    print("\n" + "=" * 50)
    print("代理已关闭")
    print("=" * 50)
    
    print("\n当前状态:")
    git_proxy = get_git_proxy_status()
    print(f"  Git HTTP 代理: {git_proxy['http_proxy'] or '未设置'}")
    print(f"  Git HTTPS 代理: {git_proxy['https_proxy'] or '未设置'}")
    
    return 0


def main():
    clear_windows = '--clear-windows' in sys.argv or '-w' in sys.argv
    return disable_proxy(clear_windows)


if __name__ == '__main__':
    sys.exit(main())
