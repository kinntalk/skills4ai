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
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            return True, ""
        else:
            return False, f"Connection refused (code: {result})"
    except socket.timeout:
        return False, "Connection timeout"
    except socket.gaierror as e:
        return False, f"DNS resolution failed: {e}"
    except OSError as e:
        return False, f"Connection error: {e}"


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


if __name__ == '__main__':
    print("智能代理工具模块")
    print("=" * 50)
    
    print("\n本地网络范围:")
    for r in get_local_network_ranges():
        print(f"  - {r}")
    
    print("\n自动生成的 NO_PROXY:")
    print(f"  {get_auto_no_proxy()}")
    
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
