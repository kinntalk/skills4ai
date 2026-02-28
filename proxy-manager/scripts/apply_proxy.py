#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

# 获取 .trae 目录的路径（从 scripts/ 向上四级）
TRA_DIR = Path(__file__).parent.parent.parent.parent
PROXY_CONFIG_PATH = TRA_DIR / 'proxy_config.json'

def load_proxy_config():
    if not os.path.exists(PROXY_CONFIG_PATH):
        return None
    
    with open(PROXY_CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def apply_proxy_to_environment(config):
    if not config or not config.get('proxy', {}).get('enabled', False):
        print("代理未启用或配置不存在")
        return False
    
    env = config.get('environment', {})
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

def main():
    config = load_proxy_config()
    
    if not config:
        print("代理配置文件不存在，请先运行 setup_proxy.py 配置代理")
        return 1
    
    print("应用代理配置...")
    
    if apply_proxy_to_environment(config):
        http_proxy, https_proxy = get_git_proxy_config(config)
        apply_git_proxy(http_proxy, https_proxy)
        print("代理配置已应用")
        return 0
    
    return 1

if __name__ == '__main__':
    sys.exit(main())
