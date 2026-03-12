---
name: x-login-pw
description: "Desktop application login authentication handler. Use AFTER application is started (by `windows-app-manager`) and user needs login assistance. Handles QR code capture, SMS verification, and other authentication tasks. **Prerequisite: Target application MUST be running.** / 桌面应用登录验证处理器。在应用程序启动后（由 `windows-app-manager` 启动）且用户需要登录协助时使用。处理二维码捕获、短信验证等认证任务。**前置条件：目标应用必须已运行。**"
allowed-tools: Bash(python *)
---

# X-Login-PW

Desktop application login authentication handler. Use after `windows-app-manager` starts the application.

## Prerequisites

**Target application MUST be running.** Start it with `windows-app-manager` first:

```powershell
python ${SKILL_DIR}/../windows-app-manager/scripts/app_manager.py start <app>
```

## Commands

| Command | Description |
|---------|-------------|
| `capture <app>` | Capture login QR code |
| `list` | List supported applications |

## Usage

```powershell
python ${SKILL_DIR}/scripts/qr_capture.py capture <app_id> [-o OUTPUT]
python ${SKILL_DIR}/scripts/qr_capture.py list
```

**Supported Apps**: `feishu`, `wechat`, `dingtalk`

## Scope

| In Scope | Out of Scope |
|----------|--------------|
| QR code capture | Application startup |
| SMS verification | Application termination |
| Login authentication | Process management |

For application lifecycle (start/stop), use `windows-app-manager` skill.

## Output

```json
{
  "success": true,
  "output_path": "login_qr.png",
  "app_id": "dingtalk"
}
```

## Output Standards

**IMPORTANT: Follow these rules for every output:**

1. **File Location**: All output files MUST be saved to `${SKILL_DIR}/output/` directory, NEVER in `scripts/` or other directories.

2. **User Presentation**: When presenting output files to users, ALWAYS provide a clickable file link in markdown format:
   ```
   [filename.png](file:///absolute/path/to/output/filename.png)
   ```
   DO NOT just output the raw file path like `d:\path\to\file.png`.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Window not found | Start app with `windows-app-manager` first |
| QR not detected | Check if login page is displayed |
