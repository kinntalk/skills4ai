#!/usr/bin/env python3
import json
import os
import sys
import subprocess
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent))
from proxy_utils import is_local_address, should_use_proxy, get_auto_no_proxy

TRA_DIR = Path(__file__).parent.parent.parent.parent
PROXY_CONFIG_PATH = TRA_DIR / 'proxy_config.json'

def load_proxy_config():
    if not os.path.exists(PROXY_CONFIG_PATH):
        return None
    
    with open(PROXY_CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_url_from_git_args(args):
    """从 git 参数中提取 URL"""
    for i, arg in enumerate(args):
        if arg.startswith('http://') or arg.startswith('https://') or arg.startswith('git://'):
            return arg
        if arg in ['clone', 'fetch', 'pull', 'push'] and i + 1 < len(args):
            next_arg = args[i + 1]
            if next_arg.startswith('http') or next_arg.startswith('git://'):
                return next_arg
    return None

def run_git_smart(args, config, permanent=False):
    """智能执行 git 命令，自动判断是否需要代理"""
    env = os.environ.copy()
    
    no_proxy = config.get('proxy', {}).get('no_proxy', '')
    if not no_proxy:
        no_proxy = get_auto_no_proxy()
    env['NO_PROXY'] = no_proxy
    env['no_proxy'] = no_proxy.lower()
    
    target_url = extract_url_from_git_args(args)
    
    if target_url:
        parsed = urlparse(target_url)
        host = parsed.hostname if parsed else None
        
        if host and is_local_address(host):
            print(f"[智能代理] 检测到本地地址 {host}，直连模式")
            result = subprocess.run(['git'] + args, env=env, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            return result.returncode
        
        use_proxy, reason = should_use_proxy(target_url, config.get('proxy', {}))
        
        if use_proxy:
            git_config = config.get('git', {})
            http_proxy = git_config.get('http_proxy')
            https_proxy = git_config.get('https_proxy')
            
            print(f"[智能代理] 使用代理: {reason}")
            
            if http_proxy:
                env['HTTP_PROXY'] = http_proxy
                env['http_proxy'] = http_proxy
                if permanent:
                    subprocess.run(['git', 'config', '--global', 'http.proxy', http_proxy], check=True)
            
            if https_proxy:
                env['HTTPS_PROXY'] = https_proxy
                env['https_proxy'] = https_proxy
                if permanent:
                    subprocess.run(['git', 'config', '--global', 'https.proxy', https_proxy], check=True)
        else:
            print(f"[智能代理] 直连模式: {reason}")
    else:
        git_config = config.get('git', {})
        http_proxy = git_config.get('http_proxy')
        https_proxy = git_config.get('https_proxy')
        
        if http_proxy:
            env['HTTP_PROXY'] = http_proxy
            env['http_proxy'] = http_proxy
        if https_proxy:
            env['HTTPS_PROXY'] = https_proxy
            env['https_proxy'] = https_proxy
    
    result = subprocess.run(['git'] + args, env=env, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    return result.returncode

def main():
    config = load_proxy_config()
    
    permanent = '--permanent' in sys.argv
    force_proxy = '--force-proxy' in sys.argv
    force_direct = '--force-direct' in sys.argv
    git_args = [arg for arg in sys.argv[1:] if arg not in ['--permanent', '--force-proxy', '--force-direct']]
    
    if not git_args:
        print("用法: python git_with_proxy.py [选项] <git 命令>")
        print("")
        print("选项:")
        print("  --permanent    永久配置 Git 代理")
        print("  --force-proxy  强制使用代理")
        print("  --force-direct 强制直连")
        print("")
        print("示例:")
        print("  python git_with_proxy.py clone https://github.com/user/repo.git")
        print("  python git_with_proxy.py --permanent clone https://github.com/user/repo.git")
        print("  python git_with_proxy.py --force-direct clone https://github.com/user/repo.git")
        return
    
    if not config or not config.get('proxy', {}).get('enabled', False):
        print("[智能代理] 代理未启用或配置不存在，使用直连模式")
        subprocess.run(['git'] + git_args)
        return
    
    if force_proxy:
        print("[智能代理] 强制代理模式")
        git_config = config.get('git', {})
        env = os.environ.copy()
        env['HTTP_PROXY'] = git_config.get('http_proxy', '')
        env['HTTPS_PROXY'] = git_config.get('https_proxy', '')
        result = subprocess.run(['git'] + git_args, env=env, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
        return
    
    if force_direct:
        print("[智能代理] 强制直连模式")
        env = os.environ.copy()
        env['NO_PROXY'] = '*'
        result = subprocess.run(['git'] + git_args, env=env, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
        return
    
    returncode = run_git_smart(git_args, config, permanent)
    sys.exit(returncode)

if __name__ == '__main__':
    main()
