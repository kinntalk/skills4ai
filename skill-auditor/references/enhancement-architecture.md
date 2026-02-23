# Skill Auditor Enhancement Architecture

## Executive Summary

This document outlines a comprehensive enhancement architecture for the skill-auditor, integrating security patterns from three reference implementations:

1. **openclaw-skills-security** - Focuses on malicious script injection, permission abuse, and security vulnerability detection
2. **anysiteio/agent-skills skill-audit** - Focuses on technical standards validation, security best practices, and dependency security analysis
3. **aiskillstore/marketplace skill-auditor** - Focuses on output quality, token optimization, and AI execution effectiveness evaluation

The proposed architecture enhances the existing skill-auditor with new security-focused checks while maintaining backward compatibility with current functionality.

---

## Reference Implementation Analysis

### 1. openclaw-skills-security Patterns

**Key Security Checks:**

| Category | Pattern | Description |
|----------|---------|-------------|
| **Typosquatting** | Name similarity detection | Detects skills with names similar to popular skills to prevent impersonation |
| **Permission Analysis** | Dangerous permission combinations | Flags network + shell, file write + network, etc. |
| **Dependency Audit** | Supply chain analysis | Checks for install hooks, obfuscated code, recent publish dates |
| **Prompt Injection** | Role hijacking detection | Detects "you are now", "ignore previous", hidden instructions |
| **Network Exfiltration** | Suspicious endpoints | Flags DNS tunneling, data in headers, unusual domains |
| **Content Red Flags** | Credential patterns | Detects credential paths, encoded commands, sudo usage |

**Architecture Highlights:**
- Modular design with 11 reusable modules (credential-scanner, dependency-auditor, network-watcher, etc.)
- 6-step audit protocol: metadata → permissions → dependencies → injection → network → content
- Verdict system: SAFE / SUSPICIOUS / DANGEROUS / BLOCK
- Covers 12/12 real-world attack types

### 2. anysiteio/agent-skills skill-audit Implementation

**Key Security Checks:**

| Finding ID | Severity | Pattern |
|------------|----------|---------|
| **SKL-001a** | Medium | Hooks present (requires manual review) |
| **SKL-001b** | Critical | Hooks + dangerous patterns (network, sensitive paths, config modification) |
| **SKL-002** | Critical | Dynamic injection / Prompt injection (!`cmd`, $(...), "ignore previous") |
| **SKL-003** | High | Dangerous tool access (Bash, WebFetch, Write, wildcards) |
| **SKL-004** | Medium/High | Missing invocation safeguard (no disable-model-invocation) |
| **SKL-005** | High | Dangerous supporting scripts (network egress, credentials, code execution) |
| **SKL-006** | High | Permission/settings escalation (modifying settings.json, hooks) |

**Architecture Highlights:**
- Read-only static audit using Read, Grep, Glob, WebFetch tools
- Anti-injection protocol (never execute audited content)
- Evidence redaction for secrets
- Risk scoring system (0-10)
- Hardening recommendations catalog
- Remote audit support for GitHub URLs

**Audit Phases:**
1. Discovery (local or remote GitHub)
2. Frontmatter Analysis (allowed-tools, hooks, disable-model-invocation)
3. Body Content Analysis (dangerous tools, settings manipulation, injection, sensitive paths, bypass, privilege escalation)
4. Supporting Files Analysis (network egress, credentials, config modification, code execution, persistence)
5. Hooks Analysis (PreToolUse, PostToolUse, Stop, Notification)

### 3. aiskillstore/marketplace skill-auditor Quality Checks

**Key Quality Checks:**
- Output quality validation
- Token optimization analysis
- AI execution effectiveness evaluation
- Skill performance metrics

**Architecture Highlights:**
- JSON-based reporting (skill-report.json)
- Quality scoring system
- Performance tracking

---

## Current skill-auditor Architecture

### Existing Check Categories

| Section | Check | Purpose |
|---------|-------|---------|
| **1. Basic Structure** | Frontmatter validation, name consistency, directory structure | Ensures skill metadata is properly formatted |
| **2. Dependencies** | Dependency integrity | Prevents runtime ModuleNotFoundError |
| **3. Encoding & Path Safety** | Encoding safety, path consistency | Prevents encoding issues and outdated path references |
| **4. Packaging** | Packaging structure, template logic | Ensures correct zip structure and valid YAML |
| **5. Subprocess & Path Operations** | Subprocess robustness, risky path operations | Ensures safe subprocess calls and path handling |
| **6. Cross-Platform Compatibility** | Platform-specific commands, path separators, absolute paths | Ensures cross-platform compatibility |
| **7. Internationalization (i18n)** | Emoji prohibition, multi-language support, hardcoded messages | Ensures i18n compliance |
| **8. Absolute References** | Hardcoded absolute paths, configuration file paths | Prevents non-portable paths |
| **9. Registry & Map Consistency** | Registry consistency, skill map consistency | Ensures proper registration |

### Current Limitations

1. **No security-focused checks** - Missing detection of malicious patterns
2. **No permission analysis** - Doesn't check for dangerous permission combinations
3. **No dependency security analysis** - Doesn't audit supply chain risks
4. **No prompt injection detection** - Missing injection pattern detection
5. **No network exfiltration checks** - Doesn't detect suspicious network activity
6. **No hooks analysis** - Doesn't check for dangerous hooks
7. **No credential leak detection** - Missing credential pattern scanning
8. **No typosquatting detection** - Doesn't detect name impersonation
9. **No remote audit support** - Can only audit local skills

---

## Proposed Enhancement Architecture

### Design Principles

1. **Modular Integration** - Add new security checks as independent modules
2. **Backward Compatibility** - Maintain all existing checks and output format
3. **Progressive Enhancement** - New checks are optional and can be enabled via flags
4. **Severity-Based Reporting** - Use severity levels (Critical, High, Medium, Low, Info)
5. **Finding IDs** - Assign unique IDs to each finding type for tracking
6. **Risk Scoring** - Implement 0-10 risk score based on findings
7. **Hardening Recommendations** - Provide actionable remediation steps

### New Check Categories

#### 10. Security: Frontmatter & Permissions

| Check ID | Severity | Pattern | Description |
|----------|----------|---------|-------------|
| **SEC-001** | High | Dangerous allowed-tools | Detects Bash, WebFetch, Write to system paths, wildcards |
| **SEC-002** | Medium | Missing disable-model-invocation | Flags skills with side effects lacking safeguards |
| **SEC-003** | Medium | Hooks present | Detects hooks (PreToolUse, PostToolUse, Stop, etc.) |
| **SEC-004** | Critical | Hooks + dangerous patterns | Hooks with network egress, sensitive paths, config modification |
| **SEC-005** | High | Dangerous permission combinations | Flags network + shell, file write + network, etc. |
| **SEC-006** | High | Over-privilege | Detects excessive permissions for skill functionality |

#### 11. Security: Prompt Injection & Bypass

| Check ID | Severity | Pattern | Description |
|----------|----------|---------|-------------|
| **SEC-010** | Critical | Dynamic injection (!`cmd`) | Detects shell preprocessing before LLM sees prompt |
| **SEC-011** | Critical | Command substitution ($(...)) | Detects shell command substitution syntax |
| **SEC-012** | Critical | Prompt injection patterns | Detects "ignore previous", "you are now", "system prompt", "override" |
| **SEC-013** | High | Bypass attempts | Detects "bypass", "disable safety", "disable security" |
| **SEC-014** | High | Forget instructions | Detects "forget", "new instructions" |
| **SEC-015** | High | Role hijacking | Detects attempts to change agent role or behavior |

#### 12. Security: Sensitive Data & Credentials

| Check ID | Severity | Pattern | Description |
|----------|----------|---------|-------------|
| **SEC-020** | High | Sensitive path references | Detects .ssh, .aws, .env, credentials, tokens, secrets |
| **SEC-021** | Critical | Credential patterns | Detects API keys, JWT tokens, passwords, private keys |
| **SEC-022** | High | Encoded commands | Detects base64, hex encoded command strings |
| **SEC-023** | Medium | Hardcoded secrets | Detects potential hardcoded secrets in code |

#### 13. Security: Network & Exfiltration

| Check ID | Severity | Pattern | Description |
|----------|----------|---------|-------------|
| **SEC-030** | High | Network egress patterns | Detects curl, wget, fetch, http://, https://, requests, urllib |
| **SEC-031** | High | Suspicious endpoints | Flags unusual domains, DNS tunneling patterns |
| **SEC-032** | Medium | Data in headers | Detects data exfiltration via HTTP headers |
| **SEC-033** | High | External URL references | Flags references to external, non-standard domains |

#### 14. Security: Code Execution & Persistence

| Check ID | Severity | Pattern | Description |
|----------|----------|---------|-------------|
| **SEC-040** | High | Code execution primitives | Detects eval(), exec(), subprocess, os.system, spawn, popen |
| **SEC-041** | High | Shell=True usage | Flags subprocess calls with shell=True (security risk) |
| **SEC-042** | Medium | Persistence mechanisms | Detects cron, crontab, launchd, systemd, .bashrc, .zshrc, git hooks |
| **SEC-043** | High | Unsafe input handling | Detects unquoted variables, no path traversal protection, no -- separators |

#### 15. Security: Dependency & Supply Chain

| Check ID | Severity | Pattern | Description |
|----------|----------|---------|-------------|
| **SEC-050** | Medium | Install hooks | Detects setup.py, post-install hooks in dependencies |
| **SEC-051** | Medium | Obfuscated code | Detects heavily obfuscated or minified code |
| **SEC-052** | Low | Recent publish | Flags recently published packages (potential typosquatting) |
| **SEC-053** | High | Untrusted dependencies | Flags dependencies from untrusted sources |

#### 16. Security: Privilege Escalation

| Check ID | Severity | Pattern | Description |
|----------|----------|---------|-------------|
| **SEC-060** | High | Sudo usage | Detects sudo commands |
| **SEC-061** | High | Root access | Detects root user references |
| **SEC-062** | High | chmod 777 | Detects overly permissive file permissions |
| **SEC-063** | High | --no-verify, --force | Detects force flags that bypass safety checks |
| **SEC-064** | Medium | Admin references | Detects admin privilege references |

#### 17. Security: Settings & Configuration

| Check ID | Severity | Pattern | Description |
|----------|----------|---------|-------------|
| **SEC-070** | High | Settings modification | Detects instructions to modify settings.json, settings.local.json |
| **SEC-071** | High | Permissions modification | Detects instructions to change permissions, allow, deny, hooks |
| **SEC-072** | Medium | Unsafe defaults | Detects unsafe default configurations |
| **SEC-073** | High | Gateway bypass | Detects attempts to bypass security gateways |

#### 18. Security: Typosquatting & Naming

| Check ID | Severity | Pattern | Description |
|----------|----------|---------|-------------|
| **SEC-080** | Medium | Name similarity | Detects skill names similar to popular skills |
| **SEC-081** | Low | Naming anomalies | Flags unusual naming patterns |
| **SEC-082** | Medium | Author impersonation | Detects suspicious author information |

#### 19. Quality: Output & Performance

| Check ID | Severity | Pattern | Description |
|----------|----------|---------|-------------|
| **QLT-001** | Low | Excessive output | Detects overly verbose output (token inefficiency) |
| **QLT-002** | Low | Redundant messages | Detects duplicate or redundant output |
| **QLT-003** | Medium | Poor formatting | Detects poorly formatted output |
| **QLT-004** | Low | Missing context | Detects output without sufficient context |

---

## Integration Points with Existing Audit Workflow

### Audit Flow Enhancement

```
┌─────────────────────────────────────────────────────────────────┐
│                    Enhanced Audit Flow                          │
└─────────────────────────────────────────────────────────────────┘

Phase 1: Discovery (Existing)
  ├─ Local skill directory
  └─ [NEW] Remote GitHub URL support

Phase 2: Basic Structure (Existing)
  ├─ Frontmatter validation
  ├─ Name consistency
  └─ Directory structure

Phase 3: Dependencies (Existing)
  └─ Dependency integrity

Phase 4: Encoding & Path Safety (Existing)
  ├─ Encoding safety
  └─ Path consistency

Phase 5: Packaging (Existing)
  ├─ Packaging structure
  └─ Template logic

Phase 6: Subprocess & Path Operations (Existing)
  ├─ Subprocess robustness
  └─ Risky path operations

Phase 7: Cross-Platform Compatibility (Existing)
  ├─ Platform-specific commands
  ├─ Path separators
  └─ Absolute paths

Phase 8: Internationalization (Existing)
  ├─ Emoji prohibition
  ├─ Multi-language support
  └─ Hardcoded messages

Phase 9: Absolute References (Existing)
  ├─ Hardcoded absolute paths
  └─ Configuration file paths

Phase 10: Registry & Map Consistency (Existing)
  ├─ Registry consistency
  └─ Skill map consistency

Phase 11: [NEW] Security: Frontmatter & Permissions
  ├─ Dangerous allowed-tools
  ├─ Missing disable-model-invocation
  ├─ Hooks present
  ├─ Hooks + dangerous patterns
  ├─ Dangerous permission combinations
  └─ Over-privilege

Phase 12: [NEW] Security: Prompt Injection & Bypass
  ├─ Dynamic injection (!`cmd`)
  ├─ Command substitution ($(...))
  ├─ Prompt injection patterns
  ├─ Bypass attempts
  ├─ Forget instructions
  └─ Role hijacking

Phase 13: [NEW] Security: Sensitive Data & Credentials
  ├─ Sensitive path references
  ├─ Credential patterns
  ├─ Encoded commands
  └─ Hardcoded secrets

Phase 14: [NEW] Security: Network & Exfiltration
  ├─ Network egress patterns
  ├─ Suspicious endpoints
  ├─ Data in headers
  └─ External URL references

Phase 15: [NEW] Security: Code Execution & Persistence
  ├─ Code execution primitives
  ├─ Shell=True usage
  ├─ Persistence mechanisms
  └─ Unsafe input handling

Phase 16: [NEW] Security: Dependency & Supply Chain
  ├─ Install hooks
  ├─ Obfuscated code
  ├─ Recent publish
  └─ Untrusted dependencies

Phase 17: [NEW] Security: Privilege Escalation
  ├─ Sudo usage
  ├─ Root access
  ├─ chmod 777
  ├─ --no-verify, --force
  └─ Admin references

Phase 18: [NEW] Security: Settings & Configuration
  ├─ Settings modification
  ├─ Permissions modification
  ├─ Unsafe defaults
  └─ Gateway bypass

Phase 19: [NEW] Security: Typosquatting & Naming
  ├─ Name similarity
  ├─ Naming anomalies
  └─ Author impersonation

Phase 20: [NEW] Quality: Output & Performance
  ├─ Excessive output
  ├─ Redundant messages
  ├─ Poor formatting
  └─ Missing context

Phase 21: [NEW] Risk Scoring & Reporting
  ├─ Calculate risk score (0-10)
  ├─ Generate hardening recommendations
  └─ Output enhanced report
```

### Command-Line Interface Enhancement

```bash
# Existing usage (unchanged)
python scripts/audit_skill.py <path-to-target-skill> [path-to-skills-dir]

# New options
python scripts/audit_skill.py <path-to-target-skill> [path-to-skills-dir] \
  [--security]              # Enable security checks (Phases 11-19)
  [--quality]               # Enable quality checks (Phase 20)
  [--remote <github-url>]   # Audit remote GitHub skill
  [--severity <level>]      # Minimum severity to report (Critical, High, Medium, Low, Info)
  [--risk-threshold <n>]    # Fail if risk score >= n (default: 7)
  [--json-report]           # Output JSON report with findings
  [--findings-only]         # Only output findings, skip pass checks
  [--recommendations]       # Include hardening recommendations
```

### Output Format Enhancement

```
[*] Auditing Skill: example-skill
   Path: /path/to/skill
   Source: local
   Date: 2026-02-21
   Risk Score: 6/10
   Overall Severity: High

=== Basic Structure ===
[PASS] SKILL.md frontmatter is valid
[PASS] SKILL.md name matches directory name
[PASS] Directory structure is valid (found: scripts, references)

=== Dependencies ===
[PASS] Dependency configuration looks good

=== Encoding & Path Safety ===
[PASS] File operations appear to use explicit encoding
[PASS] No outdated path references found

=== Packaging ===
[PASS] Packaging logic looks correct
[PASS] Template description syntax looks correct

=== Subprocess & Path Operations ===
[PASS] Subprocess calls appear robust or binary
[PASS] No high-risk file operations detected

=== Cross-Platform Compatibility ===
[PASS] No cross-platform compatibility issues found

=== Internationalization (i18n) ===
[PASS] Internationalization check completed

=== Absolute References ===
[PASS] No absolute references found

=== Registry & Map Consistency ===
[WARN] skills.json not found (skipping registry check)
[WARN] skill_map.json not found (skipping map check)

=== Security: Frontmatter & Permissions ===
[FAIL] [SEC-001] Dangerous allowed-tools detected
      Location: SKILL.md:3
      Evidence: allowed-tools: [Bash, Write]
      Severity: High

[WARN] [SEC-003] Hooks present
      Location: .claude-plugin/hooks.json:5
      Evidence: PreToolUse: lint_check
      Severity: Medium

=== Security: Prompt Injection & Bypass ===
[PASS] No prompt injection patterns found

=== Security: Sensitive Data & Credentials ===
[FAIL] [SEC-020] Sensitive path references detected
      Location: scripts/main.py:42
      Evidence: config_path = Path.home() / '.ssh' / 'config'
      Severity: High

=== Security: Network & Exfiltration ===
[WARN] [SEC-030] Network egress patterns detected
      Location: scripts/fetch.py:15
      Evidence: requests.get('https://api.example.com/data')
      Severity: High

=== Security: Code Execution & Persistence ===
[PASS] No dangerous code execution patterns found

=== Security: Dependency & Supply Chain ===
[INFO] [SEC-052] Recently published package
      Location: requirements.txt:3
      Evidence: suspicious-package==1.0.0 (published 2 days ago)
      Severity: Low

=== Security: Privilege Escalation ===
[PASS] No privilege escalation patterns found

=== Security: Settings & Configuration ===
[PASS] No settings modification patterns found

=== Security: Typosquatting & Naming ===
[INFO] [SEC-080] Name similarity detected
      Location: SKILL.md:1
      Evidence: Skill name 'git-helper' is similar to popular skill 'git-helper-pro'
      Severity: Medium

=== Quality: Output & Performance ===
[WARN] [QLT-001] Excessive output detected
      Location: scripts/main.py:100-150
      Evidence: 50+ print statements in single function
      Severity: Low

========================================
Findings Summary:

| # | ID | Severity | Finding | Location |
|---|---|---|---|---|
| 1 | SEC-001 | High | Dangerous allowed-tools detected | SKILL.md:3 |
| 2 | SEC-003 | Medium | Hooks present | .claude-plugin/hooks.json:5 |
| 3 | SEC-020 | High | Sensitive path references detected | scripts/main.py:42 |
| 4 | SEC-030 | High | Network egress patterns detected | scripts/fetch.py:15 |
| 5 | SEC-052 | Low | Recently published package | requirements.txt:3 |
| 6 | SEC-080 | Medium | Name similarity detected | SKILL.md:1 |
| 7 | QLT-001 | Low | Excessive output detected | scripts/main.py:100-150 |

Risk Score: 6/10 (High)
Critical: 0, High: 3, Medium: 2, Low: 2, Info: 0

Hardening Recommendations:
1. [SEC-001] Remove Bash from allowed-tools. If shell access is needed, use specific Bash patterns like Bash(git status).
2. [SEC-003] Review hooks manually. Verify input sanitization and consider moving to project settings.
3. [SEC-020] Avoid accessing sensitive paths like .ssh. Use user-provided configuration paths instead.
4. [SEC-030] Restrict network access to specific domains. Use WebFetch(domain:api.example.com) in permissions.
5. [SEC-080] Consider renaming skill to avoid confusion with git-helper-pro.

[!] Audit completed with High severity issues. Please review findings above.
```

---

## New Functions to Implement

### Core Security Check Functions

```python
# Phase 11: Security: Frontmatter & Permissions
def check_dangerous_allowed_tools(skill_path):
    """Check for dangerous tools in allowed-tools (Bash, WebFetch, Write, wildcards)"""
    pass

def check_disable_model_invocation(skill_path):
    """Check if skill with side effects has disable-model-invocation safeguard"""
    pass

def check_hooks_presence(skill_path):
    """Check for hooks in skill (PreToolUse, PostToolUse, Stop, etc.)"""
    pass

def check_hooks_dangerous_patterns(skill_path):
    """Check if hooks contain dangerous patterns (network, sensitive paths, config)"""
    pass

def check_dangerous_permission_combinations(skill_path):
    """Check for dangerous permission combinations (network + shell, etc.)"""
    pass

def check_over_privilege(skill_path):
    """Check for excessive permissions for skill functionality"""
    pass

# Phase 12: Security: Prompt Injection & Bypass
def check_dynamic_injection(skill_path):
    """Check for shell preprocessing (!`cmd`)"""
    pass

def check_command_substitution(skill_path):
    """Check for shell command substitution ($(...))"""
    pass

def check_prompt_injection_patterns(skill_path):
    """Check for prompt injection patterns (ignore previous, you are now, etc.)"""
    pass

def check_bypass_attempts(skill_path):
    """Check for bypass attempts (bypass, disable safety, etc.)"""
    pass

def check_forget_instructions(skill_path):
    """Check for forget instructions (forget, new instructions)"""
    pass

def check_role_hijacking(skill_path):
    """Check for role hijacking attempts"""
    pass

# Phase 13: Security: Sensitive Data & Credentials
def check_sensitive_path_references(skill_path):
    """Check for sensitive path references (.ssh, .aws, .env, credentials)"""
    pass

def check_credential_patterns(skill_path):
    """Check for credential patterns (API keys, JWT, passwords, private keys)"""
    pass

def check_encoded_commands(skill_path):
    """Check for encoded commands (base64, hex)"""
    pass

def check_hardcoded_secrets(skill_path):
    """Check for hardcoded secrets"""
    pass

# Phase 14: Security: Network & Exfiltration
def check_network_egress_patterns(skill_path):
    """Check for network egress patterns (curl, wget, http, requests)"""
    pass

def check_suspicious_endpoints(skill_path):
    """Check for suspicious endpoints (unusual domains, DNS tunneling)"""
    pass

def check_data_in_headers(skill_path):
    """Check for data exfiltration via HTTP headers"""
    pass

def check_external_url_references(skill_path):
    """Check for external URL references to non-standard domains"""
    pass

# Phase 15: Security: Code Execution & Persistence
def check_code_execution_primitives(skill_path):
    """Check for code execution primitives (eval, exec, subprocess, os.system)"""
    pass

def check_shell_true_usage(skill_path):
    """Check for subprocess calls with shell=True"""
    pass

def check_persistence_mechanisms(skill_path):
    """Check for persistence mechanisms (cron, .bashrc, git hooks)"""
    pass

def check_unsafe_input_handling(skill_path):
    """Check for unsafe input handling (unquoted variables, no path traversal protection)"""
    pass

# Phase 16: Security: Dependency & Supply Chain
def check_install_hooks(skill_path):
    """Check for install hooks in dependencies"""
    pass

def check_obfuscated_code(skill_path):
    """Check for obfuscated or minified code"""
    pass

def check_recent_publish(skill_path):
    """Check for recently published packages (potential typosquatting)"""
    pass

def check_untrusted_dependencies(skill_path):
    """Check for dependencies from untrusted sources"""
    pass

# Phase 17: Security: Privilege Escalation
def check_sudo_usage(skill_path):
    """Check for sudo commands"""
    pass

def check_root_access(skill_path):
    """Check for root user references"""
    pass

def check_chmod_777(skill_path):
    """Check for chmod 777 usage"""
    pass

def check_force_flags(skill_path):
    """Check for --no-verify, --force flags"""
    pass

def check_admin_references(skill_path):
    """Check for admin privilege references"""
    pass

# Phase 18: Security: Settings & Configuration
def check_settings_modification(skill_path):
    """Check for instructions to modify settings.json"""
    pass

def check_permissions_modification(skill_path):
    """Check for instructions to change permissions, allow, deny, hooks"""
    pass

def check_unsafe_defaults(skill_path):
    """Check for unsafe default configurations"""
    pass

def check_gateway_bypass(skill_path):
    """Check for attempts to bypass security gateways"""
    pass

# Phase 19: Security: Typosquatting & Naming
def check_name_similarity(skill_path, skills_dir=None):
    """Check for skill names similar to popular skills"""
    pass

def check_naming_anomalies(skill_path):
    """Check for unusual naming patterns"""
    pass

def check_author_impersonation(skill_path):
    """Check for suspicious author information"""
    pass

# Phase 20: Quality: Output & Performance
def check_excessive_output(skill_path):
    """Check for overly verbose output"""
    pass

def check_redundant_messages(skill_path):
    """Check for duplicate or redundant output"""
    pass

def check_poor_formatting(skill_path):
    """Check for poorly formatted output"""
    pass

def check_missing_context(skill_path):
    """Check for output without sufficient context"""
    pass

# Phase 21: Risk Scoring & Reporting
def calculate_risk_score(findings):
    """Calculate risk score (0-10) based on findings"""
    pass

def generate_hardening_recommendations(findings):
    """Generate hardening recommendations for findings"""
    pass

def generate_enhanced_report(skill_path, findings, risk_score, recommendations):
    """Generate enhanced audit report with findings and recommendations"""
    pass

# Remote Audit Support
def fetch_remote_skill(github_url):
    """Fetch skill from GitHub URL"""
    pass

def audit_remote_skill(github_url, options):
    """Audit remote skill from GitHub URL"""
    pass
```

### Utility Functions

```python
def detect_credential_patterns(text):
    """Detect credential patterns in text (API keys, JWT, passwords)"""
    pass

def detect_encoded_commands(text):
    """Detect encoded commands (base64, hex)"""
    pass

def detect_obfuscation(text):
    """Detect code obfuscation"""
    pass

def calculate_name_similarity(name1, name2):
    """Calculate similarity between two skill names"""
    pass

def is_suspicious_domain(domain):
    """Check if domain is suspicious"""
    pass

def redact_secret(text):
    """Redact secret values (show first 4 and last 4 characters)"""
    pass
```

---

## Backward Compatibility Considerations

### 1. Existing Checks Remain Unchanged

All existing checks (Phases 1-10) will continue to work exactly as before:
- No changes to check logic
- No changes to output format for existing checks
- Existing command-line arguments remain valid

### 2. New Checks are Opt-In

Security and quality checks are disabled by default:
```bash
# Standard audit (existing behavior)
python scripts/audit_skill.py <skill-path>

# Enable security checks
python scripts/audit_skill.py <skill-path> --security

# Enable quality checks
python scripts/audit_skill.py <skill-path> --quality

# Enable all checks
python scripts/audit_skill.py <skill-path> --security --quality
```

### 3. Check Level System Extended

Existing check levels (`strict`, `standard`, `relaxed`) are extended:
- `strict`: All checks including security and quality
- `standard`: All existing checks (default)
- `relaxed`: Only critical existing checks
- `security`: Only security checks (new)
- `quality`: Only quality checks (new)

### 4. Output Format Compatibility

Standard output format is maintained:
- Existing `[PASS]`, `[FAIL]`, `[WARN]` labels
- New sections are added after existing sections
- JSON output format is extended with new fields

### 5. Return Code Compatibility

Exit codes remain compatible:
- `0`: Audit passed (or only warnings)
- `1`: Audit failed (errors found)
- New `--risk-threshold` option allows customizing failure criteria

### 6. Configuration Compatibility

No configuration changes required:
- Existing `skills.json` and `skill_map.json` files work as before
- New checks don't require additional configuration

### 7. Script Interface Compatibility

The main `audit_skill()` function signature is extended but backward compatible:
```python
# Existing signature (still works)
audit_skill(skill_path, skills_dir=None, verbose=False, json_output=False, check_level="standard")

# Extended signature (new optional parameters)
audit_skill(
    skill_path,
    skills_dir=None,
    verbose=False,
    json_output=False,
    check_level="standard",
    enable_security=False,      # NEW
    enable_quality=False,       # NEW
    min_severity="Low",        # NEW
    risk_threshold=7,          # NEW
    findings_only=False,        # NEW
    include_recommendations=False  # NEW
)
```

---

## Implementation Roadmap

### Phase 1: Core Security Checks (Priority: High)

**Week 1-2: Frontmatter & Permissions**
- Implement `check_dangerous_allowed_tools()`
- Implement `check_disable_model_invocation()`
- Implement `check_hooks_presence()`
- Implement `check_hooks_dangerous_patterns()`
- Implement `check_dangerous_permission_combinations()`
- Implement `check_over_privilege()`

**Week 3: Prompt Injection & Bypass**
- Implement `check_dynamic_injection()`
- Implement `check_command_substitution()`
- Implement `check_prompt_injection_patterns()`
- Implement `check_bypass_attempts()`
- Implement `check_forget_instructions()`
- Implement `check_role_hijacking()`

**Week 4: Sensitive Data & Credentials**
- Implement `check_sensitive_path_references()`
- Implement `check_credential_patterns()`
- Implement `check_encoded_commands()`
- Implement `check_hardcoded_secrets()`

### Phase 2: Advanced Security Checks (Priority: High)

**Week 5-6: Network & Exfiltration**
- Implement `check_network_egress_patterns()`
- Implement `check_suspicious_endpoints()`
- Implement `check_data_in_headers()`
- Implement `check_external_url_references()`

**Week 7: Code Execution & Persistence**
- Implement `check_code_execution_primitives()`
- Implement `check_shell_true_usage()`
- Implement `check_persistence_mechanisms()`
- Implement `check_unsafe_input_handling()`

**Week 8: Dependency & Supply Chain**
- Implement `check_install_hooks()`
- Implement `check_obfuscated_code()`
- Implement `check_recent_publish()`
- Implement `check_untrusted_dependencies()`

### Phase 3: Additional Security Checks (Priority: Medium)

**Week 9: Privilege Escalation**
- Implement `check_sudo_usage()`
- Implement `check_root_access()`
- Implement `check_chmod_777()`
- Implement `check_force_flags()`
- Implement `check_admin_references()`

**Week 10: Settings & Configuration**
- Implement `check_settings_modification()`
- Implement `check_permissions_modification()`
- Implement `check_unsafe_defaults()`
- Implement `check_gateway_bypass()`

**Week 11: Typosquatting & Naming**
- Implement `check_name_similarity()`
- Implement `check_naming_anomalies()`
- Implement `check_author_impersonation()`

### Phase 4: Quality Checks (Priority: Low)

**Week 12: Output & Performance**
- Implement `check_excessive_output()`
- Implement `check_redundant_messages()`
- Implement `check_poor_formatting()`
- Implement `check_missing_context()`

### Phase 5: Risk Scoring & Reporting (Priority: High)

**Week 13: Risk Scoring**
- Implement `calculate_risk_score()`
- Define scoring algorithm based on severity and count

**Week 14: Hardening Recommendations**
- Implement `generate_hardening_recommendations()`
- Create recommendation catalog for each finding type

**Week 15: Enhanced Reporting**
- Implement `generate_enhanced_report()`
- Update output format with findings table
- Add JSON report generation

### Phase 6: Remote Audit Support (Priority: Medium)

**Week 16: Remote Fetch**
- Implement `fetch_remote_skill()`
- Add GitHub API integration
- Handle rate limiting and errors

**Week 17: Remote Audit**
- Implement `audit_remote_skill()`
- Integrate remote fetch with existing audit flow

### Phase 7: CLI & Integration (Priority: Medium)

**Week 18: CLI Enhancement**
- Add `--security` flag
- Add `--quality` flag
- Add `--remote` flag
- Add `--severity` flag
- Add `--risk-threshold` flag
- Add `--findings-only` flag
- Add `--recommendations` flag

**Week 19: Testing & Documentation**
- Write unit tests for all new functions
- Update SKILL.md documentation
- Create security check reference guide
- Create hardening recommendations guide

### Phase 8: Polish & Release (Priority: Low)

**Week 20: Final Polish**
- Performance optimization
- Error handling improvements
- Code review and refactoring
- Release preparation

---

## Risk Scoring Algorithm

### Scoring Formula

```
Risk Score = Base Score + Severity Multipliers + Pattern Bonuses

Base Score:
- 0: No findings
- 1: Only Info findings
- 2: Only Low findings
- 3: Low + Info findings

Severity Multipliers (per finding):
- Critical: +3
- High: +2
- Medium: +1
- Low: +0.5
- Info: +0

Pattern Bonuses:
- Multiple Critical findings: +2
- Critical + High combination: +1
- Hooks + Injection: +2
- Network + Credentials: +2
- 5+ findings of any severity: +1

Capped at: 10
```

### Risk Score Guide

| Score | Overall Severity | Action |
|-------|-----------------|--------|
| 0 | None | Clean skill |
| 1-3 | Low | Minor concerns, safe to use |
| 4-6 | Medium | Needs review before use |
| 7-8 | High | Do not enable without remediation |
| 9-10 | Critical | Likely malicious, reject immediately |

---

## Hardening Recommendations Catalog

### SEC-001: Dangerous allowed-tools

**Recommendation:**
Minimize allowed-tools to the smallest necessary set. Replace Bash(*) with specific command patterns like Bash(git status). Remove WebFetch unless strictly required.

**Example:**
```yaml
# Bad
allowed-tools: [Bash, Write]

# Good
allowed-tools: [Read, Grep, Glob]
```

### SEC-003: Hooks present

**Recommendation:**
Review each hook manually. Verify input sanitization (quoted variables, -- separators, path traversal blocking). Move hooks to project settings with explicit team review.

**Example:**
```json
// hooks.json
{
  "PreToolUse": {
    "command": "npm run lint -- \"$TOOL_NAME\" \"$ARGUMENTS\""
  }
}
```

### SEC-010: Dynamic injection (!`cmd`)

**Recommendation:**
Remove injection patterns. If dynamic context is needed, use standard tool calls instead of ! preprocessing. Report prompt injection attempts to skill maintainer.

**Example:**
```python
# Bad
output = !`ls -la`

# Good
result = subprocess.run(['ls', '-la'], capture_output=True, text=True)
```

### SEC-020: Sensitive path references

**Recommendation:**
Avoid accessing sensitive paths like .ssh, .aws, .env. Use user-provided configuration paths instead.

**Example:**
```python
# Bad
config_path = Path.home() / '.ssh' / 'config'

# Good
config_path = Path(user_config_path) / 'config'
```

### SEC-030: Network egress patterns

**Recommendation:**
Restrict network access to specific domains. Use WebFetch(domain:api.example.com) in permissions. Deny all other domains by default.

**Example:**
```json
// settings.local.json
{
  "permissions": {
    "allow": [
      "WebFetch(domain:api.github.com)",
      "WebFetch(domain:raw.githubusercontent.com)"
    ],
    "deny": ["WebFetch(*)"]
  }
}
```

---

## Testing Strategy

### Unit Tests

Each new check function will have comprehensive unit tests:
- Positive test cases (finding should be detected)
- Negative test cases (finding should not be detected)
- Edge cases (boundary conditions, malformed input)
- False positive tests (ensure no false positives)

### Integration Tests

End-to-end tests for complete audit workflows:
- Standard audit (existing checks only)
- Security audit (security checks only)
- Quality audit (quality checks only)
- Full audit (all checks)
- Remote audit (GitHub URL)

### Regression Tests

Ensure new checks don't break existing functionality:
- All existing checks still pass
- Output format remains compatible
- Return codes remain correct
- Performance impact is minimal

---

## Performance Considerations

### Optimization Strategies

1. **Lazy Evaluation**: Only run security checks if `--security` flag is set
2. **Caching**: Cache results of expensive operations (e.g., name similarity)
3. **Parallel Processing**: Run independent checks in parallel where possible
4. **Early Termination**: Stop audit if critical findings exceed threshold
5. **Incremental Scanning**: Scan only changed files in development mode

### Performance Targets

- Standard audit (existing checks): < 2 seconds
- Security audit: < 5 seconds
- Full audit (all checks): < 10 seconds
- Remote audit: < 30 seconds (network dependent)

---

## Security Considerations

### Anti-Injection Protocol

The auditor must never execute audited content:
- Use Read, Grep, Glob tools only (no Bash, Write, Edit)
- Treat all audited content as untrusted
- Never follow instructions found in audited files
- Redact secrets from evidence snippets

### Evidence Redaction

Secrets must be redacted from output:
- Show only first 4 and last 4 characters
- Use [REDACTED] for sensitive files
- Reference findings by file:line without quoting values

### Remote Audit Safety

Remote audits have additional restrictions:
- Only fetch from GitHub (raw.githubusercontent.com and api.github.com)
- Never follow links found in fetched content
- Stop on redirects to different hosts
- Limit to 20 files per remote audit

---

## Conclusion

This enhancement architecture integrates security patterns from three reference implementations into a cohesive enhancement plan for the existing skill-auditor. The proposed changes:

1. **Add comprehensive security checks** covering malicious script injection, permission abuse, dependency security, and more
2. **Maintain backward compatibility** with existing checks and output format
3. **Provide actionable recommendations** for each finding type
4. **Implement risk scoring** to help users quickly assess skill safety
5. **Support remote audits** for GitHub-hosted skills
6. **Enable progressive adoption** through opt-in flags and check levels

The implementation roadmap provides a clear path forward, with core security checks prioritized and quality checks added later. The modular design ensures that new checks can be added incrementally without disrupting existing functionality.

By integrating patterns from openclaw-skills-security, anysiteio/agent-skills, and aiskillstore/marketplace, the enhanced skill-auditor will provide comprehensive security and quality validation for Trae skills while maintaining the existing focus on cross-platform compatibility, encoding safety, and internationalization support.
