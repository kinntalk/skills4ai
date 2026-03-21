# 技术细节

## 目录

- [代理检测优先级](#代理检测优先级)
- [核心函数](#核心函数)
- [脚本说明](#脚本说明)
- [环境变量](#环境变量)
- [Git 代理配置](#git-代理配置)
- [配置文件版本](#配置文件版本)

## 代理检测优先级

系统按以下顺序判断是否使用代理：

### 1. 强制代理域名（v2.1 新增，最高优先级）

**检测函数**: `is_force_proxy_domain(host, force_domains)`

**逻辑**：
- 检查目标域名是否在 `force_proxy_domains` 列表中
- 支持通配符匹配，如 `*.github.com` 匹配 `api.github.com`
- 如果匹配且代理服务器可用，强制使用代理

**适用场景**：
- 需要确保连接稳定性的服务（如 GitHub）
- 即使直连成功也使用代理

### 2. 命令行参数

**选项**：
- `--force-proxy`：强制使用代理
- `--force-direct`：强制直连

**优先级**：
- 命令行参数优先级高于自动检测
- 适用于临时覆盖配置

### 3. 本地地址检测

**检测函数**: `is_local_address(host)`

**本地地址**：
- `localhost`、`127.0.0.1`、`::1`
- 本地网络地址：`192.168.x.x`、`10.x.x.x`、`172.16-31.x.x`
- 本地主机名

**逻辑**：
- 自动识别本地地址
- 本地地址自动直连，无需代理

### 4. NO_PROXY 白名单匹配

**检测逻辑**：
- 检查目标地址是否在 NO_PROXY 列表中
- 支持通配符模式

**NO_PROXY 格式**：
- 逗号分隔的地址列表
- 支持通配符，如 `*.example.com`
- 支持 CIDR 表示法，如 `10.0.0.0/8`

### 5. 直连测试

**测试函数**: `can_direct_connect(url)`

**测试逻辑**：
- 尝试直连目标地址（2秒超时）
- 直连成功则不使用代理
- 直连失败则使用代理

**超时设置**：
- 默认 2 秒超时
- 可在配置文件中调整

### 6. 默认配置

**逻辑**：
- 以上条件都不满足时，根据配置文件决定
- 检查 `proxy.enabled` 字段
- 如果启用，使用代理；否则直连

## 核心函数

### is_local_address(host)

**功能**: 检查是否为本地地址

**参数**:
- `host`: 主机名或 IP 地址

**返回值**: boolean

**实现逻辑**:
```python
def is_local_address(host):
    # 检查 localhost
    if host in ['localhost', '127.0.0.1', '::1']:
        return True

    # 检查本地网络地址
    try:
        ip = ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback:
            return True
    except ValueError:
        pass

    # 检查本地主机名
    try:
        hostname = socket.gethostname()
        if host == hostname:
            return True
    except socket.error:
        pass

    return False
```

### is_force_proxy_domain(host, force_domains)

**功能**: 检查是否为强制代理域名（v2.1 新增）

**参数**:
- `host`: 主机名
- `force_domains`: 强制代理域名列表

**返回值**: boolean

**实现逻辑**:
```python
def is_force_proxy_domain(host, force_domains):
    if not force_domains:
        return False

    for domain in force_domains:
        # 通配符匹配
        if domain.startswith('*.'):
            pattern = domain[2:]
            if host == pattern or host.endswith('.' + pattern):
                return True
        # 精确匹配
        elif host == domain:
            return True

    return False
```

### can_direct_connect(url)

**功能**: 测试直连可达性

**参数**:
- `url`: 目标 URL

**返回值**: boolean

**实现逻辑**:
```python
def can_direct_connect(url, timeout=2):
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code < 400
    except (requests.exceptions.RequestException, requests.exceptions.Timeout):
        return False
```

### should_use_proxy(url, config)

**功能**: 智能判断是否需要代理（v2.1 更新）

**参数**:
- `url`: 目标 URL
- `config`: 代理配置

**返回值**: boolean

**实现逻辑**:
```python
def should_use_proxy(url, config):
    if not config.get('proxy', {}).get('enabled', False):
        return False

    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname

    # 1. 检查强制代理域名
    force_domains = config.get('proxy', {}).get('force_proxy_domains', [])
    if is_force_proxy_domain(host, force_domains):
        return True

    # 2. 检查本地地址
    if is_local_address(host):
        return False

    # 3. 检查 NO_PROXY 白名单
    no_proxy = config.get('proxy', {}).get('no_proxy', '')
    if is_in_no_proxy(host, no_proxy):
        return False

    # 4. 直连测试
    if can_direct_connect(url):
        return False

    # 5. 默认使用代理
    return True
```

### get_auto_no_proxy()

**功能**: 自动生成 NO_PROXY 列表

**返回值**: string

**实现逻辑**:
```python
def get_auto_no_proxy():
    no_proxy = [
        'localhost',
        '127.0.0.1',
        '::1',
        'localaddress',
        '*.local'
    ]

    # 添加本地网络地址
    no_proxy.extend([
        '10.0.0.0/8',
        '172.16.0.0/12',
        '192.168.0.0/16'
    ])

    return ','.join(no_proxy)
```

### get_proxy_for_url(url, config)

**功能**: 获取目标 URL 的代理配置

**参数**:
- `url`: 目标 URL
- `config`: 代理配置

**返回值**: string | None

**实现逻辑**:
```python
def get_proxy_for_url(url, config):
    if not should_use_proxy(url, config):
        return None

    proxy_type = config.get('proxy', {}).get('type', 'http')
    host = config.get('proxy', {}).get('host', '127.0.0.1')
    port = config.get('proxy', {}).get('port', 10808)
    username = config.get('proxy', {}).get('username')
    password = config.get('proxy', {}).get('password')

    if proxy_type == 'socks5':
        proxy_url = f'socks5://{host}:{port}'
    else:
        proxy_url = f'http://{host}:{port}'

    if username and password:
        proxy_url = f'{proxy_url}:{username}:{password}'

    return proxy_url
```

## 脚本说明

### proxy_utils.py

**功能**: 智能代理工具模块，提供核心功能

**导出函数**:
- `is_local_address(host)` - 检查是否为本地地址
- `is_force_proxy_domain(host, force_domains)` - 检查是否为强制代理域名（v2.1 新增）
- `can_direct_connect(url)` - 测试直连可达性
- `should_use_proxy(url, config)` - 智能判断是否需要代理（v2.1 更新）
- `get_auto_no_proxy()` - 自动生成 NO_PROXY 列表
- `get_proxy_for_url(url, config)` - 获取目标 URL 的代理配置

**使用方法**:
```python
from proxy_utils import is_local_address, should_use_proxy

# 检查是否为本地地址
if is_local_address('localhost'):
    print('这是本地地址')

# 判断是否需要代理
if should_use_proxy('https://github.com', config):
    print('需要使用代理')
```

### setup_proxy.py

**功能**: 配置代理设置并保存到配置文件

**用法**:
```bash
python .trae/skills/proxy-manager/scripts/setup_proxy.py <proxy_type> <host> <port> [username] [password] [--no-auto-no-proxy]
```

**参数**:
- `proxy_type`: 代理类型（http、socks5）
- `host`: 代理服务器地址
- `port`: 代理服务器端口
- `username`: 代理用户名（可选）
- `password`: 代理密码（可选）
- `--no-auto-no-proxy`: 禁用自动 NO_PROXY 生成

**输出**: 配置文件保存到 `.trae/proxy_config.json`

### apply_proxy.py

**功能**: 应用代理配置到当前会话

**用法**:
```bash
python .trae/skills/proxy-manager/scripts/apply_proxy.py [--simple] [--no-git] [--test]
```

**参数**:
- `--simple`: 简单模式，不使用智能检测
- `--no-git`: 不配置 Git 代理
- `--test`: 测试代理连接（v2.1 更新，显示强制代理域名信息）

**输出**: 环境变量设置到当前会话

**测试输出示例（v2.1）**:
```
测试代理连接...
  强制代理域名: github.com, *.github.com
  https://github.com: 使用代理 (Forced proxy for domain: github.com)
  https://api.github.com: 使用代理 (Forced proxy for domain: api.github.com)
```

### git_with_proxy.py

**功能**: 使用代理执行 Git 命令（智能模式）

**用法**:
```bash
python .trae/skills/proxy-manager/scripts/git_with_proxy.py [选项] <git 命令>
```

**参数**:
- `--permanent`: 永久配置 Git 代理
- `--force-proxy`: 强制使用代理
- `--force-direct`: 强制直连
- `git 命令`: 要执行的 Git 命令（如 clone、pull 等）

**示例**:
```bash
# 智能模式（自动判断，v2.1 支持强制代理域名）
python .trae/skills/proxy-manager/scripts/git_with_proxy.py clone https://github.com/user/repo.git

# 强制代理
python .trae/skills/proxy-manager/scripts/git_with_proxy.py --force-proxy clone https://github.com/user/repo.git

# 强制直连
python .trae/skills/proxy-manager/scripts/git_with_proxy.py --force-direct clone https://github.com/user/repo.git

# 永久配置代理
python .trae/skills/proxy-manager/scripts/git_with_proxy.py --permanent clone https://github.com/user/repo.git
```

**v2.1 更新**:
- 自动识别强制代理域名并应用代理
- 输出显示是否使用强制代理：`[智能代理] 使用代理: Forced proxy for domain: github.com`

### clear_proxy.py

**功能**: 清除代理配置

**用法**:
```bash
python .trae/skills/proxy-manager/scripts/clear_proxy.py
```

**输出**: 清除环境变量和 Git 代理配置

### proxy_status.py

**功能**: 查看当前代理配置状态

**用法**:
```bash
python .trae/skills/proxy-manager/scripts/proxy_status.py
```

**输出**: 显示当前代理配置信息

### smart_proxy.py

**功能**: 智能代理测试工具

**用法**:
```bash
python .trae/skills/proxy-manager/scripts/smart_proxy.py
```

**输出**: 测试智能代理功能是否正常

## 环境变量

### HTTP_PROXY / http_proxy

**说明**: HTTP 请求代理

**格式**: `http://[username:password@]host:port`

**示例**:
```bash
export HTTP_PROXY=http://127.0.0.1:10808
export HTTP_PROXY=http://user:pass@proxy.example.com:8080
```

### HTTPS_PROXY / https_proxy

**说明**: HTTPS 请求代理

**格式**: `http://[username:password@]host:port`

**示例**:
```bash
export HTTPS_PROXY=http://127.0.0.1:10808
export HTTPS_PROXY=http://user:pass@proxy.example.com:8080
```

### NO_PROXY / no_proxy

**说明**: 代理白名单（自动生成）

**格式**: 逗号分隔的地址列表

**示例**:
```bash
export NO_PROXY=localhost,127.0.0.1,::1,localaddress,*.local,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16
```

**支持通配符**:
- `*.example.com` 匹配所有 `example.com` 的子域名

**支持 CIDR 表示法**:
- `10.0.0.0/8` 匹配 10.0.0.0 - 10.255.255.255
- `172.16.0.0/12` 匹配 172.16.0.0 - 172.31.255.255
- `192.168.0.0/16` 匹配 192.168.0.0 - 192.168.255.255

## Git 代理配置

### HTTP 代理

**配置命令**:
```bash
git config --global http.proxy http://127.0.0.1:10808
```

**查看配置**:
```bash
git config --global --get http.proxy
```

**清除配置**:
```bash
git config --global --unset http.proxy
```

### HTTPS 代理

**配置命令**:
```bash
git config --global https.proxy http://127.0.0.1:10808
```

**查看配置**:
```bash
git config --global --get https.proxy
```

**清除配置**:
```bash
git config --global --unset https.proxy
```

### SOCKS5 代理

**配置命令**:
```bash
git config --global http.proxy socks5://127.0.0.1:10808
git config --global https.proxy socks5://127.0.0.1:10808
```

**查看配置**:
```bash
git config --global --get http.proxy
git config --global --get https.proxy
```

**清除配置**:
```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
```

## 配置文件版本

### v2.1.0（当前版本）

**新增功能**:
- 强制代理域名支持（`force_proxy_domains`）
- 通配符域名匹配（如 `*.github.com`）
- 新增 `is_force_proxy_domain()` 函数
- 更新 `should_use_proxy()` 函数支持强制代理检测
- 更新测试输出显示强制代理域名信息

**改进**:
- 代理判断优先级调整，强制代理域名优先级最高
- 解决特定服务（如 GitHub）的连接稳定性问题
- 不影响其他服务的智能代理判断

**配置文件变更**:
- 版本号从 `2.0` 升级到 `2.1`
- 新增 `proxy.force_proxy_domains` 字段

### v2.0.0

**新增功能**:
- 智能代理检测
- 自动 NO_PROXY 生成
- 本地地址自动排除
- 直连测试功能

**配置文件变更**:
- 新增 `proxy.auto_detect` 字段
- 新增 `proxy.no_proxy` 字段
- 版本号从 `1.0` 升级到 `2.0`

### v1.0.0

**初始版本**:
- 基本代理配置功能
- HTTP 和 SOCKS5 代理支持
- Git 代理配置
- 环境变量管理

**配置文件结构**:
```json
{
  "version": "1.0",
  "proxy": {
    "enabled": true,
    "type": "http",
    "host": "127.0.0.1",
    "port": 10808
  }
}
```
