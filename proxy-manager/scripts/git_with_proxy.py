#!/usr/bin/env python3
import json
import os
import sys
import subprocess
from pathlib import Path

# 获取 .trae 目录的路径（从 scripts/ 向上四级）
TRA_DIR = Path(__file__).parent.parent.parent.parent
PROXY_CONFIG_PATH = TRA_DIR / 'proxy_config.json'

def load_proxy_config():
    if not os.path.exists(PROXY_CONFIG_PATH):
        return None
    
    with open(PROXY_CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_git_with_proxy(command, http_proxy=None, https_proxy=None, permanent=False):
    env = os.environ.copy()
    
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
    
    result = subprocess.run(command, env=env, capture_output=True, text=True)
    return result

def main():
    config = load_proxy_config()
    
    if not config or not config.get('proxy', {}).get('enabled', False):
        print("代理未启用或配置不存在，直接执行 git 命令")
        if len(sys.argv) > 1:
            subprocess.run(sys.argv[1:])
        return
    
    git_config = config.get('git', {})
    http_proxy = git_config.get('http_proxy')
    https_proxy = git_config.get('https_proxy')
    
    permanent = '--permanent' in sys.argv
    git_args = [arg for arg in sys.argv[1:] if arg != '--permanent']
    
    if not git_args:
        print("用法: python git_with_proxy.py [--permanent] <git 命令>")
        print("示例: python git_with_proxy.py --permanent clone https://github.com/user/repo.git")
        return
    
    print(f"使用代理执行 git 命令: HTTP={http_proxy}, HTTPS={https_proxy}")
    result = run_git_with_proxy(['git'] + git_args, http_proxy, https_proxy, permanent)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    sys.exit(result.returncode)

if __name__ == '__main__':
    main()
