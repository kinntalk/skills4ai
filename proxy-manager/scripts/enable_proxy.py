#!/usr/bin/env python3
"""
一键开启代理
- 设置 Git 全局代理
- 更新 proxy_config.json 配置文件
- 测试代理连接
"""
import json
import os
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from proxy_utils import is_proxy_server_available, get_git_proxy_status, get_windows_proxy_status

TRA_DIR = Path(__file__).parent.parent.parent.parent
PROXY_CONFIG_PATH = TRA_DIR / 'proxy_config.json'

DEFAULT_FORCE_PROXY_DOMAINS = ["*.github.com"]


def load_proxy_config():
    if not os.path.exists(PROXY_CONFIG_PATH):
        return None
    with open(PROXY_CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_proxy_config(config):
    with open(PROXY_CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def set_git_proxy(proxy_type: str, host: str, port: int) -> bool:
    proxy_url = f"{proxy_type}://{host}:{port}"
    try:
        subprocess.run(['git', 'config', '--global', 'http.proxy', proxy_url], 
                      check=True, capture_output=True, timeout=5)
        subprocess.run(['git', 'config', '--global', 'https.proxy', proxy_url], 
                      check=True, capture_output=True, timeout=5)
        return True
    except subprocess.CalledProcessError as e:
        print(f"设置 Git 代理失败: {e}")
        return False
    except Exception as e:
        print(f"设置 Git 代理时发生错误: {e}")
        return False


def test_github_connection() -> bool:
    try:
        result = subprocess.run(
            ['git', 'ls-remote', 'https://github.com/git/git.git', 'HEAD'],
            capture_output=True, text=True, timeout=15
        )
        return result.returncode == 0
    except Exception:
        return False


def enable_proxy(force_domains=None):
    print("=" * 50)
    print("开启代理")
    print("=" * 50)
    
    config = load_proxy_config()
    if not config:
        print("\n错误: 代理配置文件不存在")
        print("请先运行 setup_proxy.py 配置代理")
        return 1
    
    proxy_config = config.get('proxy', {})
    proxy_type = proxy_config.get('type', 'http')
    proxy_host = proxy_config.get('host', '127.0.0.1')
    proxy_port = proxy_config.get('port', 10808)
    
    print(f"\n[1/4] 检测代理服务器...")
    available, error = is_proxy_server_available(proxy_host, proxy_port)
    if not available:
        print(f"      ✗ 代理服务器不可用: {error}")
        print(f"      提示: 请确保 v2rayN 或其他代理软件已启动")
        return 1
    print(f"      ✓ 代理服务器可用: {proxy_host}:{proxy_port}")
    
    print(f"\n[2/4] 设置 Git 全局代理...")
    if set_git_proxy(proxy_type, proxy_host, proxy_port):
        print(f"      ✓ Git 代理已设置: {proxy_type}://{proxy_host}:{proxy_port}")
    else:
        print(f"      ✗ Git 代理设置失败")
        return 1
    
    print(f"\n[3/4] 更新配置文件...")
    config['proxy']['enabled'] = True
    if force_domains is not None:
        config['proxy']['force_proxy_domains'] = force_domains
    elif not config['proxy'].get('force_proxy_domains'):
        config['proxy']['force_proxy_domains'] = DEFAULT_FORCE_PROXY_DOMAINS
    save_proxy_config(config)
    print(f"      ✓ 配置文件已更新")
    print(f"      - enabled: True")
    print(f"      - force_proxy_domains: {config['proxy']['force_proxy_domains']}")
    
    print(f"\n[4/4] 测试 GitHub 连接...")
    if test_github_connection():
        print(f"      ✓ GitHub 连接成功")
    else:
        print(f"      ⚠ GitHub 连接测试失败（代理可能需要时间生效）")
    
    print("\n" + "=" * 50)
    print("代理已开启")
    print("=" * 50)
    
    print("\n当前状态:")
    git_proxy = get_git_proxy_status()
    print(f"  Git HTTP 代理: {git_proxy['http_proxy'] or '未设置'}")
    print(f"  Git HTTPS 代理: {git_proxy['https_proxy'] or '未设置'}")
    
    return 0


def main():
    force_domains = None
    
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    
    if '--no-force-domains' in sys.argv:
        force_domains = []
    elif args:
        force_domains = args
    
    return enable_proxy(force_domains)


if __name__ == '__main__':
    sys.exit(main())
