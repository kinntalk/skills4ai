#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from proxy_utils import get_auto_no_proxy, is_local_address, should_use_proxy

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

def apply_git_proxy(http_proxy, https_proxy):
    if http_proxy:
        os.system(f'git config --global http.proxy "{http_proxy}"')
        print(f"设置 Git HTTP 代理: {http_proxy}")
    
    if https_proxy:
        os.system(f'git config --global https.proxy "{https_proxy}"')
        print(f"设置 Git HTTPS 代理: {https_proxy}")

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

def main():
    config = load_proxy_config()
    
    if not config:
        print("代理配置文件不存在，请先运行 setup_proxy.py 配置代理")
        return 1
    
    print("应用代理配置 (智能模式)...")
    
    smart_mode = '--simple' not in sys.argv
    
    if apply_proxy_to_environment(config, smart_mode):
        http_proxy, https_proxy = get_git_proxy_config(config)
        
        if '--no-git' not in sys.argv:
            apply_git_proxy(http_proxy, https_proxy)
        
        print("\n代理配置已应用")
        
        if '--test' in sys.argv:
            test_proxy_connection(config)
        
        return 0
    
    return 1

if __name__ == '__main__':
    sys.exit(main())
