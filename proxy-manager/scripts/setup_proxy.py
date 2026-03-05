#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from proxy_utils import get_auto_no_proxy, get_local_network_ranges

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

def setup_proxy(proxy_type='http', host='127.0.0.1', port=10808, username=None, password=None, auto_no_proxy=True):
    no_proxy_value = get_auto_no_proxy() if auto_no_proxy else "localhost,127.0.0.1"
    
    config = {
        "version": "2.0",
        "proxy": {
            "enabled": True,
            "type": proxy_type,
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "auto_detect": True,
            "no_proxy": no_proxy_value
        },
        "git": {
            "http_proxy": f"{proxy_type}://{host}:{port}",
            "https_proxy": f"{proxy_type}://{host}:{port}"
        },
        "environment": {
            "HTTP_PROXY": f"{proxy_type}://{host}:{port}",
            "HTTPS_PROXY": f"{proxy_type}://{host}:{port}",
            "NO_PROXY": no_proxy_value
        }
    }
    
    save_proxy_config(config)
    print(f"代理配置已保存到 {PROXY_CONFIG_PATH}")
    print(f"代理类型: {proxy_type}")
    print(f"代理地址: {host}:{port}")
    print(f"NO_PROXY (自动生成): {no_proxy_value}")
    
    return config

def main():
    if len(sys.argv) < 2:
        print("用法: python setup_proxy.py <proxy_type> <host> <port> [username] [password]")
        print("示例: python setup_proxy.py http 127.0.0.1 10808")
        print("示例: python setup_proxy.py socks5 127.0.0.1 10808")
        print("")
        print("选项:")
        print("  --no-auto-no-proxy  禁用自动 NO_PROXY 生成")
        return
    
    args = sys.argv[1:]
    auto_no_proxy = True
    
    if '--no-auto-no-proxy' in args:
        auto_no_proxy = False
        args = [a for a in args if a != '--no-auto-no-proxy']
    
    if len(args) < 1:
        print("错误: 需要指定代理类型")
        return
    
    proxy_type = args[0]
    host = args[1] if len(args) > 1 else '127.0.0.1'
    port = int(args[2]) if len(args) > 2 else 10808
    username = args[3] if len(args) > 3 else None
    password = args[4] if len(args) > 4 else None
    
    setup_proxy(proxy_type, host, port, username, password, auto_no_proxy)

if __name__ == '__main__':
    main()
