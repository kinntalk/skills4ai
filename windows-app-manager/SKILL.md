---
name: windows-app-manager
description: Windows application lifecycle management. Use when user requests to START or STOP desktop applications like WeChat, Feishu, DingTalk, Chrome, etc. Handles application launch and termination only. For login/authentication issues, use `x-login-pw` skill. / Windows 应用程序生命周期管理。当用户请求启动或关闭桌面应用（微信、飞书、钉钉、Chrome 等）时使用。仅处理应用启动和关闭。登录验证问题请使用 `x-login-pw` skill。
allowed-tools: Read, Write, RunCommand, Glob, Grep
---

# Windows App Manager

Application lifecycle management: start and stop Windows desktop applications.

## Commands

| Command | Description |
|---------|-------------|
| `start <app>` | Start an application |
| `stop <app>` | Stop an application |
| `list` | List saved applications |
| `search <keyword>` | Search for applications |

## Usage

```powershell
python ${SKILL_DIR}/scripts/app_manager.py start <app>
python ${SKILL_DIR}/scripts/app_manager.py stop <app>
python ${SKILL_DIR}/scripts/app_manager.py list
```

**Supported Apps**: WeChat, Feishu, DingTalk, Chrome, Notepad, etc.

## Output Format

The output is a JSON object with the following structure:

```json
{
  "success": true,
  "app_id": "dingtalk",
  "need_login": true,
  "message": "dingtalk started",
  "processes": [{"name": "DingTalk", "pid": "1234"}]
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the operation succeeded |
| `app_id` | string | Standardized app identifier for use with `x-login-pw` |
| `need_login` | boolean | Whether this app requires login (triggers `x-login-pw`) |
| `message` | string | Status message |
| `processes` | array | List of running processes (optional) |

## Scope

| In Scope | Out of Scope |
|----------|--------------|
| Start application | Login authentication |
| Stop application | QR code capture |
| Process management | SMS verification |

## Integration with x-login-pw

When `need_login` is `true`, call `x-login-pw` skill with the `app_id`:

```powershell
python ${SKILL_DIR}/../x-login-pw/scripts/qr_capture.py capture <app_id>
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| App not starting | Verify installation path |
| Permission denied | Run as Administrator |
| Process not found | Check if app is already running |
