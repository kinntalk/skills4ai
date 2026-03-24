#!/usr/bin/env python3
"""
清除所有代理设置
包括：Windows 系统代理、Git 全局代理、环境变量
"""
import os
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from proxy_utils import clear_windows_proxy, clear_git_proxy, get_windows_proxy_status, get_git_proxy_status

TRA_DIR = Path(__file__).parent.parent.parent.parent
PROXY_CONFIG_PATH = TRA_DIR / 'proxy_config.json'

def clear_environment_proxy():
    """清除当前会话的环境变量代理设置"""
    cleared = []
    for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
        if key in os.environ:
            del os.environ[key]
            cleared.append(key)
    return cleared

def disable_proxy_config():
    """禁用 proxy_config.json 中的代理配置"""
    import json
    config_path = PROXY_CONFIG_PATH
    if not config_path.exists():
        return False
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    config['proxy']['enabled'] = False
    config['proxy']['force_proxy_domains'] = []
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    return True

def main():
    print("=" * 50)
    print("清除所有代理设置")
    print("=" * 50)
    
    print("\n[1/4] 清除 Windows 系统代理...")
    before = get_windows_proxy_status()
    if before['enabled']:
        if clear_windows_proxy():
            after = get_windows_proxy_status()
            if not after['enabled']:
                print("      ✓ Windows 系统代理已禁用")
            else:
                print("      ✗ 禁用失败")
        else:
            print("      ✗ 清除失败")
    else:
        print("      - Windows 系统代理已经是禁用状态")
    
    print("\n[2/4] 清除 Git 全局代理...")
    before = get_git_proxy_status()
    if before['http_proxy'] or before['https_proxy']:
        if clear_git_proxy():
            after = get_git_proxy_status()
            if not after['http_proxy'] and not after['https_proxy']:
                print("      ✓ Git 全局代理已清除")
            else:
                print("      ✗ 清除失败")
        else:
            print("      ✗ 清除失败")
    else:
        print("      - Git 全局代理未设置")
    
    print("\n[3/4] 清除环境变量代理设置...")
    cleared = clear_environment_proxy()
    if cleared:
        print(f"      ✓ 已清除环境变量: {', '.join(cleared)}")
    else:
        print("      - 环境变量中无代理设置")
    
    print("\n[4/4] 禁用代理配置文件...")
    if disable_proxy_config():
        print("      ✓ proxy_config.json 中的代理已禁用")
    else:
        print("      - proxy_config.json 不存在或无需修改")
    
    print("\n" + "=" * 50)
    print("所有代理设置已清除")
    print("=" * 50)
    
    print("\n当前状态:")
    win_proxy = get_windows_proxy_status()
    git_proxy = get_git_proxy_status()
    print(f"  Windows 系统代理: {'已启用' if win_proxy['enabled'] else '已禁用'}")
    print(f"  Git HTTP 代理: {git_proxy['http_proxy'] or '未设置'}")
    print(f"  Git HTTPS 代理: {git_proxy['https_proxy'] or '未设置'}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
