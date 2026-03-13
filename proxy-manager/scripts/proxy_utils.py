#!/usr/bin/env python3
"""
智能代理工具模块
提供自动代理检测、NO_PROXY 列表生成、代理选择等功能
"""
import os
import socket
import ipaddress
import re
import sys
import subprocess
from urllib.parse import urlparse
from typing import Optional, List, Tuple

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import urllib.request
    import urllib.error
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False


def get_local_network_ranges() -> List[str]:
    """
    自动检测本机网络配置，返回本地网络地址范围列表
    包括：localhost、回环地址、私有网络地址
    """
    local_ranges = [
        'localhost',
        '127.0.0.0/8',
        '::1',
        '0.0.0.0/8',
    ]
    
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        if not local_ip.startswith('127.'):
            local_ranges.append(local_ip)
    except Exception:
        pass
    
    private_ranges = [
        '10.0.0.0/8',
        '172.16.0.0/12',
        '192.168.0.0/16',
        '169.254.0.0/16',
        'fc00::/7',
        'fe80::/10',
    ]
    local_ranges.extend(private_ranges)
    
    return local_ranges


def get_auto_no_proxy() -> str:
    """
    自动生成 NO_PROXY 环境变量值
    包括本地地址和常见本地服务
    """
    no_proxy_list = [
        'localhost',
        '127.0.0.1',
        '::1',
        'localaddress',
        '*.local',
    ]
    
    local_ranges = get_local_network_ranges()
    for r in local_ranges:
        if '/' in r:
            try:
                network = ipaddress.ip_network(r, strict=False)
                no_proxy_list.append(str(network))
            except ValueError:
                pass
        elif r not in no_proxy_list:
            no_proxy_list.append(r)
    
    try:
        hostname = socket.gethostname()
        if hostname:
            no_proxy_list.append(hostname)
            no_proxy_list.append(f'.{hostname}')
    except Exception:
        pass
    
    return ','.join(no_proxy_list)


def is_local_address(host: str) -> bool:
    """
    检查目标主机是否为本地地址
    """
    if not host:
        return True
    
    if host in ('localhost', '127.0.0.1', '::1', '0.0.0.0'):
        return True
    
    if host.endswith('.local') or host.endswith('.localhost'):
        return True
    
    try:
        if ':' in host and not host.startswith('['):
            host_part, port = host.rsplit(':', 1)
            if port.isdigit():
                host = host_part
    except ValueError:
        pass
    
    try:
        ip = socket.gethostbyname(host)
        ip_obj = ipaddress.ip_address(ip)
        
        if ip_obj.is_loopback:
            return True
        if ip_obj.is_private:
            return True
        if ip_obj.is_link_local:
            return True
        if ip_obj.is_reserved:
            return True
        
        return False
    except (socket.gaierror, ValueError):
        pass
    
    local_patterns = [
        r'^localhost$',
        r'^127\.',
        r'^10\.',
        r'^172\.(1[6-9]|2[0-9]|3[01])\.',
        r'^192\.168\.',
        r'^169\.254\.',
        r'^::1$',
        r'^fc',
        r'^fe80:',
    ]
    
    for pattern in local_patterns:
        if re.match(pattern, host, re.IGNORECASE):
            return True
    
    return False


def can_direct_connect(url: str, timeout: float = 2.0) -> Tuple[bool, str]:
    """
    测试是否可以直接连接到目标 URL（不使用代理）
    使用 HTTP HEAD 请求检测，比单纯的 TCP 连接更准确
    
    Args:
        url: 目标 URL
        timeout: 连接超时时间（秒）
    
    Returns:
        (是否可直连, 错误信息)
    """
    parsed = urlparse(url)
    host = parsed.hostname
    port = parsed.port
    
    if not port:
        if parsed.scheme == 'https':
            port = 443
        elif parsed.scheme == 'http':
            port = 80
        else:
            port = 80
    
    try:
        import urllib.request
        test_url = f"{parsed.scheme}://{parsed.netloc}" if parsed.netloc else url
        
        request = urllib.request.Request(test_url, method='HEAD')
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        request.add_header('Accept', '*/*')
        
        old_proxy = {}
        for key in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
            if key in os.environ:
                old_proxy[key] = os.environ[key]
                del os.environ[key]
        
        try:
            response = urllib.request.urlopen(request, timeout=timeout)
            return True, f"HTTP {response.status}"
        finally:
            for key, value in old_proxy.items():
                os.environ[key] = value
                
    except urllib.error.HTTPError as e:
        return True, f"HTTP {e.code} (server responded)"
    except urllib.error.URLError as e:
        return False, f"URL Error: {e.reason}"
    except Exception as e:
        return False, f"Connection error: {e}"


def is_proxy_server_available(host: str = '127.0.0.1', port: int = 10808, timeout: float = 1.0) -> Tuple[bool, str]:
    """
    检测代理服务器是否可用（端口是否有服务监听）
    
    Args:
        host: 代理服务器地址
        port: 代理服务器端口
        timeout: 连接超时时间（秒）
    
    Returns:
        (是否可用, 错误信息)
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            return True, ""
        else:
            return False, f"Proxy server not listening on {host}:{port}"
    except socket.timeout:
        return False, f"Connection timeout to proxy server {host}:{port}"
    except socket.gaierror as e:
        return False, f"DNS resolution failed for proxy server: {e}"
    except OSError as e:
        return False, f"Connection error to proxy server: {e}"


def is_force_proxy_domain(host: str, force_domains: List[str]) -> bool:
    """
    检查域名是否在强制代理列表中
    
    Args:
        host: 目标主机名
        force_domains: 强制代理域名列表（支持通配符，如 *.github.com）
    
    Returns:
        是否需要强制代理
    """
    if not host or not force_domains:
        return False
    
    host_lower = host.lower()
    
    for pattern in force_domains:
        pattern_lower = pattern.lower()
        if pattern_lower.startswith('*.'):
            suffix = pattern_lower[2:]
            if host_lower == suffix or host_lower.endswith('.' + suffix):
                return True
        elif pattern_lower.startswith('.'):
            if host_lower.endswith(pattern_lower) or host_lower == pattern_lower[1:]:
                return True
        elif host_lower == pattern_lower:
            return True
    
    return False


def should_use_proxy(url: str, proxy_config: dict, timeout: float = 2.0) -> Tuple[bool, str]:
    """
    智能判断是否需要使用代理
    
    Args:
        url: 目标 URL
        proxy_config: 代理配置字典
        timeout: 直连测试超时时间
    
    Returns:
        (是否使用代理, 原因说明)
    """
    if not proxy_config or not proxy_config.get('enabled', False):
        return False, "Proxy is disabled"
    
    parsed = urlparse(url)
    host = parsed.hostname
    
    if not host:
        return False, "Invalid URL: no hostname"
    
    force_domains = proxy_config.get('force_proxy_domains', [])
    if is_force_proxy_domain(host, force_domains):
        proxy_host = proxy_config.get('host', '127.0.0.1')
        proxy_port = proxy_config.get('port', 10808)
        proxy_available, proxy_error = is_proxy_server_available(proxy_host, proxy_port)
        if proxy_available:
            return True, f"Forced proxy for domain: {host}"
        else:
            return False, f"Forced proxy domain but proxy unavailable: {proxy_error}"
    
    if is_local_address(host):
        return False, f"Local address: {host}"
    
    no_proxy = proxy_config.get('no_proxy', '') or os.environ.get('NO_PROXY', '')
    if no_proxy:
        no_proxy_list = [p.strip() for p in no_proxy.split(',')]
        for pattern in no_proxy_list:
            if pattern.startswith('*.'):
                if host.endswith(pattern[2:]):
                    return False, f"Matched NO_PROXY pattern: {pattern}"
            elif pattern.startswith('.'):
                if host.endswith(pattern):
                    return False, f"Matched NO_PROXY pattern: {pattern}"
            elif host == pattern:
                return False, f"Matched NO_PROXY: {pattern}"
    
    proxy_host = proxy_config.get('host', '127.0.0.1')
    proxy_port = proxy_config.get('port', 10808)
    proxy_available, proxy_error = is_proxy_server_available(proxy_host, proxy_port)
    
    if not proxy_available:
        can_connect, error = can_direct_connect(url, timeout)
        if can_connect:
            return False, f"Proxy unavailable ({proxy_error}), direct connection available"
        return False, f"Proxy unavailable ({proxy_error}), direct connection also failed: {error}"
    
    can_connect, error = can_direct_connect(url, timeout)
    if can_connect:
        return False, "Direct connection available"
    
    return True, f"Direct connection failed: {error}"


def get_proxy_for_url(url: str, proxy_config: dict) -> Optional[dict]:
    """
    根据目标 URL 获取适当的代理配置
    
    Args:
        url: 目标 URL
        proxy_config: 代理配置字典
    
    Returns:
        代理字典 {'http': proxy_url, 'https': proxy_url} 或 None
    """
    use_proxy, reason = should_use_proxy(url, proxy_config)
    
    if not use_proxy:
        return None
    
    proxy_type = proxy_config.get('type', 'http')
    host = proxy_config.get('host', '127.0.0.1')
    port = proxy_config.get('port', 10808)
    username = proxy_config.get('username')
    password = proxy_config.get('password')
    
    if username and password:
        proxy_url = f"{proxy_type}://{username}:{password}@{host}:{port}"
    else:
        proxy_url = f"{proxy_type}://{host}:{port}"
    
    return {
        'http': proxy_url,
        'https': proxy_url,
        'reason': reason
    }


def get_windows_proxy_status() -> dict:
    """
    获取 Windows 系统代理状态
    
    Returns:
        {'enabled': bool, 'server': str, 'override': str}
    """
    try:
        result = subprocess.run(
            ['powershell', '-Command', 
             "Get-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings' | Select-Object ProxyEnable, ProxyServer, ProxyOverride | ConvertTo-Json"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            return {
                'enabled': bool(data.get('ProxyEnable', 0)),
                'server': data.get('ProxyServer', ''),
                'override': data.get('ProxyOverride', '')
            }
    except Exception as e:
        pass
    return {'enabled': False, 'server': '', 'override': ''}


def get_git_proxy_status() -> dict:
    """
    获取 Git 全局代理配置
    
    Returns:
        {'http_proxy': str, 'https_proxy': str}
    """
    result = {'http_proxy': None, 'https_proxy': None}
    try:
        r = subprocess.run(['git', 'config', '--global', '--get', 'http.proxy'], 
                          capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            result['http_proxy'] = r.stdout.strip()
    except Exception:
        pass
    
    try:
        r = subprocess.run(['git', 'config', '--global', '--get', 'https.proxy'], 
                          capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            result['https_proxy'] = r.stdout.strip()
    except Exception:
        pass
    
    return result


def clear_windows_proxy() -> bool:
    """
    清除 Windows 系统代理设置
    
    Returns:
        是否成功
    """
    try:
        subprocess.run(
            ['powershell', '-Command', 
             "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings' -Name ProxyEnable -Value 0"],
            check=True, timeout=10
        )
        return True
    except Exception as e:
        print(f"清除 Windows 系统代理失败: {e}")
        return False


def clear_git_proxy() -> bool:
    """
    清除 Git 全局代理配置
    
    Returns:
        是否成功
    """
    try:
        subprocess.run(['git', 'config', '--global', '--unset', 'http.proxy'], 
                      capture_output=True, timeout=5)
        subprocess.run(['git', 'config', '--global', '--unset', 'https.proxy'], 
                      capture_output=True, timeout=5)
        return True
    except Exception as e:
        print(f"清除 Git 代理配置失败: {e}")
        return False


if __name__ == '__main__':
    print("智能代理工具模块")
    print("=" * 50)
    
    print("\n本地网络范围:")
    for r in get_local_network_ranges():
        print(f"  - {r}")
    
    print("\n自动生成的 NO_PROXY:")
    print(f"  {get_auto_no_proxy()}")
    
    print("\n代理服务器状态检测:")
    available, error = is_proxy_server_available('127.0.0.1', 10808)
    print(f"  127.0.0.1:10808: {'可用' if available else f'不可用 ({error})'}")
    
    print("\nWindows 系统代理状态:")
    win_proxy = get_windows_proxy_status()
    print(f"  启用: {win_proxy['enabled']}")
    print(f"  服务器: {win_proxy['server']}")
    
    print("\nGit 全局代理状态:")
    git_proxy = get_git_proxy_status()
    print(f"  HTTP: {git_proxy['http_proxy']}")
    print(f"  HTTPS: {git_proxy['https_proxy']}")
    
    print("\n测试地址检测:")
    test_hosts = [
        'localhost',
        '127.0.0.1',
        '192.168.1.1',
        '10.0.0.1',
        'github.com',
        'google.com',
    ]
    
    for host in test_hosts:
        result = "本地地址" if is_local_address(host) else "远程地址"
        print(f"  {host}: {result}")
