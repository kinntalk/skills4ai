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

def save_proxy_config(config):
    with open(PROXY_CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def setup_proxy(proxy_type='http', host='127.0.0.1', port=10808, username=None, password=None):
    config = {
        "version": "1.0",
        "proxy": {
            "enabled": True,
            "type": proxy_type,
            "host": host,
            "port": port,
            "username": username,
            "password": password
        },
        "git": {
            "http_proxy": f"{proxy_type}://{host}:{port}",
            "https_proxy": f"{proxy_type}://{host}:{port}"
        },
        "environment": {
            "HTTP_PROXY": f"{proxy_type}://{host}:{port}",
            "HTTPS_PROXY": f"{proxy_type}://{host}:{port}",
            "NO_PROXY": "localhost,127.0.0.1"
        }
    }
    
    save_proxy_config(config)
    print(f"代理配置已保存到 {PROXY_CONFIG_PATH}")
    print(f"代理类型: {proxy_type}")
    print(f"代理地址: {host}:{port}")

def main():
    if len(sys.argv) < 2:
        print("用法: python setup_proxy.py <proxy_type> <host> <port> [username] [password]")
        print("示例: python setup_proxy.py http 127.0.0.1 10808")
        print("示例: python setup_proxy.py socks5 127.0.0.1 10808")
        return
    
    proxy_type = sys.argv[1]
    host = sys.argv[2] if len(sys.argv) > 2 else '127.0.0.1'
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 10808
    username = sys.argv[4] if len(sys.argv) > 4 else None
    password = sys.argv[5] if len(sys.argv) > 5 else None
    
    setup_proxy(proxy_type, host, port, username, password)

if __name__ == '__main__':
    main()
