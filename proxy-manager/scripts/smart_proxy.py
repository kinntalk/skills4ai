#!/usr/bin/env python3
"""
智能代理包装器
自动检测代理服务器状态和目标地址可达性，智能选择代理或直连
"""
import os
import sys
import subprocess
import json
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent))
from proxy_utils import (
    is_local_address, 
    should_use_proxy, 
    is_proxy_server_available,
    get_auto_no_proxy,
    get_windows_proxy_status,
    get_git_proxy_status
)

TRA_DIR = Path(__file__).parent.parent.parent.parent
PROXY_CONFIG_PATH = TRA_DIR / 'proxy_config.json'

def load_proxy_config():
    if os.path.exists(PROXY_CONFIG_PATH):
        with open(PROXY_CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def extract_url_from_args(args):
    """从命令参数中提取 URL"""
    for arg in args:
        if arg.startswith('http://') or arg.startswith('https://') or arg.startswith('git://'):
            return arg
    return None

def run_with_smart_proxy(command_args, config=None):
    """
    智能执行命令，自动选择代理或直连
    
    Args:
        command_args: 命令参数列表
        config: 代理配置
    
    Returns:
        命令返回码
    """
    env = os.environ.copy()
    
    no_proxy = get_auto_no_proxy()
    env['NO_PROXY'] = no_proxy
    env['no_proxy'] = no_proxy.lower()
    
    target_url = extract_url_from_args(command_args)
    
    if target_url:
        parsed = urlparse(target_url)
        host = parsed.hostname if parsed else None
        
        if host and is_local_address(host):
            print(f"[智能代理] 本地地址 {host}，直连模式")
            result = subprocess.run(command_args, env=env)
            return result.returncode
        
        if config and config.get('proxy', {}).get('enabled', False):
            proxy_config = config.get('proxy', {})
            proxy_host = proxy_config.get('host', '127.0.0.1')
            proxy_port = proxy_config.get('port', 10808)
            
            available, error = is_proxy_server_available(proxy_host, proxy_port)
            
            if available:
                use_proxy, reason = should_use_proxy(target_url, proxy_config)
                
                if use_proxy:
                    print(f"[智能代理] 使用代理: {reason}")
                    git_config = config.get('git', {})
                    http_proxy = git_config.get('http_proxy')
                    https_proxy = git_config.get('https_proxy')
                    
                    if http_proxy:
                        env['HTTP_PROXY'] = http_proxy
                        env['http_proxy'] = http_proxy
                    if https_proxy:
                        env['HTTPS_PROXY'] = https_proxy
                        env['https_proxy'] = https_proxy
                else:
                    print(f"[智能代理] 直连模式: {reason}")
            else:
                print(f"[智能代理] 代理服务器不可用，直连模式")
    
    result = subprocess.run(command_args, env=env)
    return result.returncode

def main():
    if len(sys.argv) < 2:
        print("智能代理包装器")
        print("")
        print("用法: python smart_proxy.py <命令> [参数...]")
        print("")
        print("示例:")
        print("  python smart_proxy.py git clone https://github.com/user/repo.git")
        print("  python smart_proxy.py curl https://api.github.com")
        print("  python smart_proxy.py npm install")
        print("")
        print("功能:")
        print("  - 自动检测代理服务器是否可用")
        print("  - 自动检测目标地址是否可直连")
        print("  - 智能选择代理或直连模式")
        print("  - 本地地址始终直连")
        return 1
    
    command_args = sys.argv[1:]
    config = load_proxy_config()
    
    return run_with_smart_proxy(command_args, config)

if __name__ == '__main__':
    sys.exit(main())
