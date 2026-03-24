---
name: x-mail-sender
description: Local email sender via SMTP protocol supporting multiple providers (126, 163, QQ, Gmail, Outlook) with attachment capabilities. Use this skill whenever the user needs to send emails, send reports to email addresses, or mentions "send email", "发邮件", "email", "mail", "邮件". Trigger even when the user doesn't explicitly say "send email" but clearly intends to send content or files to an email address.
allowed-tools: Read, Write, RunCommand, Glob, Grep
---

# x-mail-sender

Local email sender using standard SMTP protocol with multi-provider support and attachment capabilities.

## Directory Structure

```
x-mail-sender/
├── SKILL.md              # This file
├── .gitignore            # Excludes sensitive files (.env, history/)
├── config/
│   └── .env.example      # Configuration template
├── evals/
│   └── evals.json        # Test cases
├── references/
│   └── smtp_config.md    # SMTP configuration reference
└── scripts/
    ├── config_loader.py  # Configuration loader
    ├── email_history.py  # History manager
    ├── send_email.py     # Main email sender
    ├── validate_config.py# Configuration validator
    └── requirements.txt  # Python dependencies
```

## Supported Email Providers

| Provider | SMTP Server | Port | Notes |
|----------|-------------|------|-------|
| NetEase 126 | smtp.126.com | 465/25 | Requires SMTP service + authorization code |
| NetEase 163 | smtp.163.com | 465/25 | Requires SMTP service + authorization code |
| QQ Mail | smtp.qq.com | 465 | Requires SMTP service + authorization code |
| Gmail | smtp.gmail.com | 465/587 | Requires 2FA + app password |
| Outlook | smtp.office365.com | 587 | Requires app password |
| Custom | User-defined | User-defined | Any SMTP server supported |

## Quick Start

### 1. Initial Setup

Copy the configuration template and edit:

```powershell
cp "${SKILL_DIR}/config/.env.example" "${SKILL_DIR}/.env"
```

Edit `.env` with your email settings:

```env
SMTP_SERVER=smtp.126.com
SMTP_PORT=465
SENDER_EMAIL=your_email@126.com
SENDER_PASSWORD=your_authorization_code
SENDER_NAME=AI Assistant
```

### 2. Validate Configuration

```powershell
python ${SKILL_DIR}/scripts/validate_config.py
```

### 3. Send Email

```powershell
python ${SKILL_DIR}/scripts/send_email.py --to "recipient@example.com" --subject "Subject" --body "Message body"
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--to` | Yes* | Recipient email(s), comma-separated |
| `--subject` | Yes* | Email subject |
| `--body` | Yes* | Email body content |
| `--attachments` | No | File path(s), comma-separated |
| `--html` | No | Flag for HTML body format |
| `--cc` | No | CC address(es), comma-separated |
| `--bcc` | No | BCC address(es), comma-separated |
| `--validate-config` | No | Validate email configuration |
| `--history` | No | Show recent email history |

*Not required when using `--validate-config` or `--history`

## Configuration

Configuration file location: `${SKILL_DIR}/.env` (gitignored for security)

### Configuration Template

See `config/.env.example` for the full template:

```env
# SMTP server address (required)
SMTP_SERVER=smtp.126.com

# SMTP port (default: 465 for SSL)
SMTP_PORT=465

# Your email address (required)
SENDER_EMAIL=your_email@126.com

# SMTP authorization code (required)
# NOTE: This is NOT your email login password!
SENDER_PASSWORD=your_authorization_code_here

# Sender display name (optional)
SENDER_NAME=AI Assistant

# Use SSL connection (default: true for port 465)
SMTP_USE_SSL=true

# Use STARTTLS (default: false, set true for port 587)
SMTP_USE_STARTTLS=false
```

### Getting Authorization Codes

**NetEase (126/163):**
1. Login to webmail
2. Settings → POP3/SMTP/IMAP
3. Enable SMTP service
4. Get authorization code (NOT login password)

**Gmail:**
1. Enable 2-Step Verification
2. Google Account → Security → App passwords
3. Generate app password for Mail

**QQ Mail:**
1. Login to QQ Mail web
2. Settings → Account
3. Enable SMTP service
4. Get authorization code

## Output Format

### Success Response

```json
{
  "success": true,
  "message": "Email sent successfully",
  "recipient": "recipient@example.com",
  "subject": "Subject",
  "attachments": ["file1.pdf"],
  "timestamp": "2026-03-24T10:30:00",
  "smtp_server": "smtp.126.com",
  "from": "sender@126.com"
}
```

### Error Response

```json
{
  "success": false,
  "error": "SMTP Authentication Error: ...",
  "error_code": "AUTH_FAILED",
  "hint": "Please check your email authorization code",
  "smtp_server": "smtp.126.com",
  "troubleshooting": [
    "Verify using authorization code, not login password",
    "Check if SMTP service is enabled"
  ]
}
```

### Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `CONFIG_MISSING` | Missing configuration | Check SENDER_EMAIL and SENDER_PASSWORD in .env |
| `SMTP_SERVER_MISSING` | No SMTP server | Configure SMTP_SERVER or use supported provider |
| `INVALID_EMAIL` | Invalid email address | Verify recipient email format |
| `ATTACHMENT_NOT_FOUND` | File not found | Check attachment file path |
| `AUTH_FAILED` | Authentication failed | Use authorization code, not password |
| `RECIPIENT_REFUSED` | Recipient rejected | Check if email is valid/allowed |
| `TIMEOUT` | Connection timeout | Check network and SMTP server |
| `DNS_ERROR` | DNS resolution failed | Verify SMTP server address |

## Advanced Features

### Configuration Validation

```powershell
# Validate config
python ${SKILL_DIR}/scripts/validate_config.py

# Test SMTP connection
python ${SKILL_DIR}/scripts/validate_config.py --test-connection

# JSON output
python ${SKILL_DIR}/scripts/validate_config.py --json
```

### Email History

```powershell
# View recent emails
python ${SKILL_DIR}/scripts/email_history.py list

# View statistics
python ${SKILL_DIR}/scripts/email_history.py stats

# Export history
python ${SKILL_DIR}/scripts/email_history.py export

# Clear history
python ${SKILL_DIR}/scripts/email_history.py clear --confirm
```

## Usage Examples

**Example 1: Simple email**
> User: "Send an email to boss@company.com saying I'll be late"

```powershell
python ${SKILL_DIR}/scripts/send_email.py --to "boss@company.com" --subject "Attendance Notice" --body "I will arrive around 10am today."
```

**Example 2: With attachment**
> User: "Send the Excel report to finance@company.com"

```powershell
python ${SKILL_DIR}/scripts/send_email.py --to "finance@company.com" --subject "Monthly Report" --body "Please find the attached report." --attachments "D:/reports/monthly.xlsx"
```

**Example 3: Multiple recipients**
> User: "Email team1@company.com and team2@company.com about the project update"

```powershell
python ${SKILL_DIR}/scripts/send_email.py --to "team1@company.com,team2@company.com" --subject "Project Update" --body "Please review the latest changes."
```

## Security

1. **Local storage**: Credentials stored locally in `.env`, never uploaded
2. **Gitignored**: `.env` file is excluded from version control via `.gitignore`
3. **Encryption**: All SMTP connections use SSL/TLS
4. **Size limit**: Keep attachments under 25MB total
5. **History**: Last 100 emails stored locally for debugging
6. **No third-party**: Direct SMTP, no external services

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Login failed | Use authorization code, not password |
| Connection timeout | Check network and SMTP server |
| Attachment failed | Verify file path and access |
| Chinese garbled | UTF-8 handled automatically |
| Marked as spam | Avoid bulk similar content |

## Technical Details

- Python standard library: `smtplib`, `email`
- SSL/TLS encrypted transmission
- Automatic MIME type detection
- UTF-8 encoding for internationalization
- No external API dependencies
- Built-in history tracking
- Fallback configuration loader for robustness

## Reference

- [SMTP Configuration Guide](references/smtp_config.md) - Detailed provider settings
- [Configuration Template](config/.env.example) - Template file for setup
