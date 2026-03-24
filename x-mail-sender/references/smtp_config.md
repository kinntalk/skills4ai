# SMTP Server Configuration Reference

## Preset SMTP Servers

The skill automatically detects and configures the following email providers:

| Provider | SMTP Server | Port | SSL | STARTTLS |
|----------|-------------|------|-----|----------|
| 网易 126 | smtp.126.com | 465 | Yes | No |
| 网易 163 | smtp.163.com | 465 | Yes | No |
| QQ 邮箱 | smtp.qq.com | 465 | Yes | No |
| Gmail | smtp.gmail.com | 465 | Yes | No |
| Outlook | smtp.office365.com | 587 | No | Yes |
| Hotmail | smtp-mail.outlook.com | 587 | No | Yes |

## Getting Authorization Codes

### 网易邮箱 (126/163)

1. Log in to your email web interface
2. Go to Settings (设置) → POP3/SMTP/IMAP
3. Enable SMTP service
4. Follow the prompts to get your authorization code (授权码)
5. **Important**: Use the authorization code, NOT your login password

### QQ 邮箱

1. Log in to QQ Mail web interface
2. Go to Settings (设置) → Account (账户)
3. Find "POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV Service"
4. Enable SMTP service
5. Get your authorization code (授权码)

### Gmail

1. Enable 2-Step Verification on your Google Account
2. Go to Google Account → Security → App passwords
3. Generate a new app password for "Mail"
4. Use the generated 16-character password

### Outlook/Hotmail

1. Enable 2-Step Verification on your Microsoft Account
2. Go to Microsoft Account → Security → App passwords
3. Generate a new app password
4. Use the generated password

## Troubleshooting

### Authentication Failed

- Ensure you're using the authorization code, not your login password
- Check if SMTP service is enabled in your email settings
- For Gmail, ensure 2-Step Verification is enabled and you're using an app password

### Connection Timeout

- Check your network connection
- Verify the SMTP server address and port
- Try alternative ports (465 for SSL, 587 for STARTTLS)
- Check if your firewall blocks SMTP connections

### Chinese Character Issues

The script automatically handles UTF-8 encoding for:
- Email subject
- Email body
- Attachment filenames

### Attachment Issues

- Ensure the file path is correct
- Check if the file is not being used by another program
- Verify the file size is within limits (usually 25MB total)

## Security Notes

1. **Never commit .env file to version control**
2. **Authorization codes are sensitive** - treat them like passwords
3. **Use app passwords** when available for better security
4. **Email content is transmitted over encrypted SMTP connection**
