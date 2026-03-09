#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from proxy_utils import get_auto_no_proxy, is_local_address, should_use_proxy, is_proxy_server_available, get_windows_proxy_status, get_git_proxy_status, clear_windows_proxy, clear_git_proxy

TRA_DIR = Path(__file__).parent.parent.parent.parent
PROXY_CONFIG_PATH = TRA_DIR / 'proxy_config.json'

def load_proxy_config():
    if not os.path.exists(PROXY_CONFIG_PATH):
        return None
    
    with open(PROXY_CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def apply_proxy_to_environment(config, smart_mode=True):
    if not config or not config.get('proxy', {}).get('enabled', False):
        print("代理未启用或配置不存在")
        return False
    
    proxy_config = config.get('proxy', {})
    proxy_host = proxy_config.get('host', '127.0.0.1')
    proxy_port = proxy_config.get('port', 10808)
    
    available, error = is_proxy_server_available(proxy_host, proxy_port)
    if not available:
        print(f"警告: 代理服务器 {proxy_host}:{proxy_port} 不可用 ({error})")
        print("提示: 请确保 v2rayN 或其他代理软件已启动")
        return False
    
    env = config.get('environment', {})
    
    if smart_mode:
        no_proxy = config.get('proxy', {}).get('no_proxy', '')
        if not no_proxy:
            no_proxy = get_auto_no_proxy()
        env['NO_PROXY'] = no_proxy
        env['no_proxy'] = no_proxy.lower()
    
    for key, value in env.items():
        os.environ[key] = value
        print(f"设置环境变量: {key}={value}")
    
    return True

def get_git_proxy_config(config):
    if not config or not config.get('proxy', {}).get('enabled', False):
        return None, None
    
    git_config = config.get('git', {})
    return git_config.get('http_proxy'), git_config.get('https_proxy')

def apply_git_proxy_temporarily(http_proxy, https_proxy):
    """仅返回环境变量，不设置 Git 全局配置"""
    env_additions = {}
    if http_proxy:
        env_additions['HTTP_PROXY'] = http_proxy
        env_additions['http_proxy'] = http_proxy
        print(f"Git 临时代理: HTTP_PROXY={http_proxy}")
    
    if https_proxy:
        env_additions['HTTPS_PROXY'] = https_proxy
        env_additions['https_proxy'] = https_proxy
        print(f"Git 临时代理: HTTPS_PROXY={https_proxy}")
    
    return env_additions

def test_proxy_connection(config):
    """测试代理连接是否正常工作"""
    test_urls = [
        'https://github.com',
        'https://api.github.com',
    ]
    
    print("\n测试代理连接...")
    proxy_config = config.get('proxy', {})
    
    for url in test_urls:
        use_proxy, reason = should_use_proxy(url, proxy_config)
        status = "使用代理" if use_proxy else "直连"
        print(f"  {url}: {status} ({reason})")
    
    return True

def clear_all_proxy():
    """清除所有代理设置"""
    print("清除所有代理设置...")
    
    print("\n1. 清除 Windows 系统代理...")
    if clear_windows_proxy():
        print("   Windows 系统代理已禁用")
    else:
        print("   清除 Windows 系统代理失败")
    
    print("\n2. 清除 Git 全局代理...")
    if clear_git_proxy():
        print("   Git 全局代理已清除")
    else:
        print("   清除 Git 全局代理失败")
    
    print("\n3. 清除当前会话环境变量...")
    for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
        if key in os.environ:
            del os.environ[key]
            print(f"   已清除 {key}")
    
    print("\n所有代理设置已清除")
    return True

def show_status():
    """显示当前代理状态"""
    print("=" * 50)
    print("代理状态检查")
    print("=" * 50)
    
    print("\n1. Windows 系统代理:")
    win_proxy = get_windows_proxy_status()
    print(f"   启用状态: {'已启用' if win_proxy['enabled'] else '已禁用'}")
    if win_proxy['server']:
        print(f"   代理服务器: {win_proxy['server']}")
    if win_proxy['override']:
        print(f"   代理白名单: {win_proxy['override'][:50]}...")
    
    print("\n2. Git 全局代理:")
    git_proxy = get_git_proxy_status()
    print(f"   HTTP 代理: {git_proxy['http_proxy'] or '未设置'}")
    print(f"   HTTPS 代理: {git_proxy['https_proxy'] or '未设置'}")
    
    print("\n3. 代理配置文件:")
    config = load_proxy_config()
    if config:
        proxy_config = config.get('proxy', {})
        print(f"   配置文件: {PROXY_CONFIG_PATH}")
        print(f"   启用状态: {proxy_config.get('enabled', False)}")
        print(f"   代理类型: {proxy_config.get('type', 'http')}")
        print(f"   代理地址: {proxy_config.get('host', '')}:{proxy_config.get('port', '')}")
        
        proxy_host = proxy_config.get('host', '127.0.0.1')
        proxy_port = proxy_config.get('port', 10808)
        available, error = is_proxy_server_available(proxy_host, proxy_port)
        print(f"   服务器状态: {'可用' if available else f'不可用 ({error})'}")
    else:
        print(f"   配置文件不存在: {PROXY_CONFIG_PATH}")
    
    print("\n4. 当前会话环境变量:")
    for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY']:
        value = os.environ.get(key, '未设置')
        print(f"   {key}: {value}")
    
    return True

def main():
    if '--clear' in sys.argv:
        clear_all_proxy()
        return 0
    
    if '--status' in sys.argv:
        show_status()
        return 0
    
    config = load_proxy_config()
    
    if not config:
        print("代理配置文件不存在，请先运行 setup_proxy.py 配置代理")
        return 1
    
    print("应用代理配置 (智能模式)...")
    print("注意: 不再设置 Git 全局代理，使用按需代理模式")
    
    smart_mode = '--simple' not in sys.argv
    
    if apply_proxy_to_environment(config, smart_mode):
        print("\n代理配置已应用到当前会话环境变量")
        
        if '--test' in sys.argv:
            test_proxy_connection(config)
        
        return 0
    
    return 1

if __name__ == '__main__':
    sys.exit(main())
