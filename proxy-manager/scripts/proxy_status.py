#!/usr/bin/env python3
"""
检测当前代理状态
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from proxy_utils import (
    get_windows_proxy_status, 
    get_git_proxy_status, 
    is_proxy_server_available,
    is_local_address,
    should_use_proxy,
    can_direct_connect
)

TRA_DIR = Path(__file__).parent.parent.parent.parent
PROXY_CONFIG_PATH = TRA_DIR / 'proxy_config.json'

def load_proxy_config():
    import json
    if os.path.exists(PROXY_CONFIG_PATH):
        with open(PROXY_CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def check_proxy_server(config):
    """检查代理服务器状态"""
    if not config:
        return None, "配置文件不存在"
    
    proxy_config = config.get('proxy', {})
    if not proxy_config.get('enabled', False):
        return None, "代理未启用"
    
    host = proxy_config.get('host', '127.0.0.1')
    port = proxy_config.get('port', 10808)
    
    available, error = is_proxy_server_available(host, port)
    return available, error

def test_connection(config):
    """测试网络连接"""
    test_urls = [
        ('https://github.com', 'GitHub'),
        ('https://gitlab.com', 'GitLab'),
        ('https://www.baidu.com', '百度'),
    ]
    
    results = []
    proxy_config = config.get('proxy', {}) if config else {}
    
    for url, name in test_urls:
        use_proxy, reason = should_use_proxy(url, proxy_config)
        can_direct, _ = can_direct_connect(url, timeout=3.0)
        
        results.append({
            'name': name,
            'url': url,
            'use_proxy': use_proxy,
            'can_direct': can_direct,
            'reason': reason
        })
    
    return results

def main():
    print("=" * 60)
    print("代理状态检测报告")
    print("=" * 60)
    
    config = load_proxy_config()
    
    print("\n┌─ 1. Windows 系统代理 ─────────────────────────────────────")
    win_proxy = get_windows_proxy_status()
    status_icon = "🟢" if win_proxy['enabled'] else "🔴"
    print(f"│ 状态: {status_icon} {'已启用' if win_proxy['enabled'] else '已禁用'}")
    if win_proxy['server']:
        print(f"│ 服务器: {win_proxy['server']}")
    if win_proxy['override']:
        override_short = win_proxy['override'][:40] + "..." if len(win_proxy['override']) > 40 else win_proxy['override']
        print(f"│ 白名单: {override_short}")
    print("└────────────────────────────────────────────────────────────")
    
    print("\n┌─ 2. Git 全局代理 ─────────────────────────────────────────")
    git_proxy = get_git_proxy_status()
    http_icon = "🟢" if git_proxy['http_proxy'] else "🔴"
    https_icon = "🟢" if git_proxy['https_proxy'] else "🔴"
    print(f"│ HTTP 代理:  {http_icon} {git_proxy['http_proxy'] or '未设置'}")
    print(f"│ HTTPS 代理: {https_icon} {git_proxy['https_proxy'] or '未设置'}")
    print("└────────────────────────────────────────────────────────────")
    
    print("\n┌─ 3. 代理配置文件 ─────────────────────────────────────────")
    if config:
        proxy_config = config.get('proxy', {})
        enabled = proxy_config.get('enabled', False)
        enabled_icon = "🟢" if enabled else "🔴"
        print(f"│ 文件: {PROXY_CONFIG_PATH}")
        print(f"│ 启用: {enabled_icon} {enabled}")
        print(f"│ 类型: {proxy_config.get('type', 'http')}")
        print(f"│ 地址: {proxy_config.get('host', '')}:{proxy_config.get('port', '')}")
    else:
        print(f"│ 文件不存在: {PROXY_CONFIG_PATH}")
    print("└────────────────────────────────────────────────────────────")
    
    print("\n┌─ 4. 代理服务器状态 ───────────────────────────────────────")
    available, error = check_proxy_server(config)
    if available is None:
        print(f"│ 状态: ⚪ {error}")
    elif available:
        print(f"│ 状态: 🟢 可用")
    else:
        print(f"│ 状态: 🔴 不可用 ({error})")
        print(f"│ 提示: 请确保 v2rayN 或其他代理软件已启动")
    print("└────────────────────────────────────────────────────────────")
    
    print("\n┌─ 5. 网络连接测试 ─────────────────────────────────────────")
    conn_results = test_connection(config)
    for r in conn_results:
        mode = "代理" if r['use_proxy'] else "直连"
        direct = "✓" if r['can_direct'] else "✗"
        print(f"│ {r['name']}: [{mode}] 直连:{direct}")
    print("└────────────────────────────────────────────────────────────")
    
    print("\n┌─ 6. 当前会话环境变量 ─────────────────────────────────────")
    for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY']:
        value = os.environ.get(key)
        icon = "🟢" if value else "🔴"
        print(f"│ {key}: {icon} {value or '未设置'}")
    print("└────────────────────────────────────────────────────────────")
    
    print("\n" + "=" * 60)
    
    if win_proxy['enabled'] or git_proxy['http_proxy'] or git_proxy['https_proxy']:
        print("⚠️  警告: 检测到静态代理配置")
        print("   建议运行: python clear_proxy.py 清除静态代理")
        print("   然后使用按需代理模式")
    
    print("=" * 60)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
