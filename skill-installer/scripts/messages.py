# Internationalization strings for Skill Installer
# This file centralizes all user-facing messages to support i18n and avoid hardcoded strings in logic.

# Icons / Text-based Labels
ICON_PACKAGE = "[PKG]"
ICON_DOWN = "[DOWN]"
ICON_WARN = "[WARN]"
ICON_ERROR = "[FAIL]"
ICON_SUCCESS = "[PASS]"
ICON_INFO = "[INFO]"
ICON_SEARCH = "[SEARCH]"
ICON_MEMO = "[NOTE]"
ICON_LIST = "[LIST]"
ICON_BACKUP = "[BACKUP]"
ICON_RESTORE = "[RESTORE]"
ICON_CLEAN = "[CLEAN]"
ICON_UPDATE = "[UPDATE]"

# Colors (ANSI)
COLOR_GREEN = "\033[92m"
COLOR_RED = "\033[91m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_CYAN = "\033[96m"
COLOR_RESET = "\033[0m"

# Messages
MSG_INSTALLING = f"{ICON_PACKAGE} Installing from: {{url}}"
MSG_SUBDIR = f"   Subdirectory: {{subdir}}"
MSG_DESTINATION = f"   To: {{path}}"
MSG_CLONING = f"{ICON_DOWN}  Cloning repository..."
MSG_RETRY = f"{COLOR_YELLOW}Retry {{attempt}}/{{max_retries}}...{COLOR_RESET}"
MSG_CLONE_FAILED = f"{COLOR_RED}Failed to clone repository after {{max_retries}} attempts.{COLOR_RESET}"
MSG_VERSION = f"   Version: {{version}}"
MSG_SUBDIR_NOT_FOUND = f"{COLOR_RED}Error: Subdirectory '{{subdir}}' not found in repository.{COLOR_RESET}"
MSG_SUBDIR_FOUND_ALT = f"{COLOR_YELLOW}Warning: Subdirectory '{{subdir}}' not found. Found at '{{alt_path}}' instead.{COLOR_RESET}"
MSG_DEST_EXISTS = f"{COLOR_YELLOW}Warning: Destination '{{path}}' already exists.{COLOR_RESET}"
MSG_FORCE_OVERWRITE = f"{COLOR_YELLOW}Force mode enabled. Overwriting...{COLOR_RESET}"
MSG_OVERWRITE_PROMPT = "Overwrite? (y/N): "
MSG_INSTALL_ABORTED = "Installation aborted."
MSG_INSTALLED_SUCCESS = f"{COLOR_GREEN}{ICON_SUCCESS} Installed '{{name}}' to {{path}}{COLOR_RESET}"
MSG_AUDIT_RUNNING = f"\n{ICON_SEARCH} Running skill-auditor..."
MSG_AUDIT_FAILED = f"{COLOR_YELLOW}Warning: Audit failed: {{error}}{COLOR_RESET}"
MSG_AUDIT_SKIPPED = f"{COLOR_YELLOW}Warning: skill-auditor not found. Skipping audit.{COLOR_RESET}"
MSG_COMMAND_FAILED = f"{COLOR_RED}Command failed: {{error}}{COLOR_RESET}"
MSG_STDERR = f"Stderr: {{stderr}}"

# Manage Skills Messages
MSG_NO_SKILLS_REGISTRY = "No skills found in registry (skills.json)."
MSG_INSTALLED_HEADER = f"\n{COLOR_BLUE}Installed Skills:{COLOR_RESET}"
MSG_CHECKING_UPDATES = f"\n{COLOR_BLUE}Checking for updates...{COLOR_RESET}"
MSG_SKIPPING_SKILL = f"{COLOR_YELLOW}Skipping {{name}}: Missing source or version info.{COLOR_RESET}"
MSG_CHECKING_SKILL = f"Checking {{name}}..."
MSG_UPDATE_AVAILABLE = f" {COLOR_GREEN}Update available!{COLOR_RESET} ({{current}} -> {{remote}})"
MSG_UP_TO_DATE = f" {COLOR_GREEN}Up to date.{COLOR_RESET}"
MSG_CHECK_FAILED = f" {COLOR_RED}Failed to check remote.{COLOR_RESET}"
MSG_UPDATES_FOUND = f"\n{COLOR_YELLOW}Updates available for: {{skills}}{COLOR_RESET}"
MSG_RUN_UPDATE_HINT = f"Run 'python manage_skills.py update <name>' to update."
MSG_ALL_UP_TO_DATE = f"\n{COLOR_GREEN}All skills are up to date.{COLOR_RESET}"
MSG_SKILL_NOT_FOUND = f"{COLOR_RED}Error: Skill '{{name}}' not found in registry.{COLOR_RESET}"
MSG_SKILL_LOCAL = f"{COLOR_YELLOW}Skipping {{name}}: Local skill or no source URL.{COLOR_RESET}"
MSG_UPDATING_FROM = f"Updating {{name}} from: {{source}}"
MSG_BACKUP_CREATED = f"{COLOR_YELLOW}Backed up existing skill to {{path}}{COLOR_RESET}"
MSG_BACKUP_ERROR = f"{COLOR_RED}Error backing up skill: {{error}}{COLOR_RESET}"
MSG_UPDATE_SUCCESS = f"{COLOR_GREEN}Successfully updated {{name}}.{COLOR_RESET}"
MSG_BACKUP_REMOVED = f"{COLOR_GREEN}Removed backup.{COLOR_RESET}"
MSG_UPDATE_FAILED = f"{COLOR_RED}Failed to update {{name}}. Restoring backup...{COLOR_RESET}"
MSG_RESTORE_SUCCESS = f"{COLOR_GREEN}Restored previous version.{COLOR_RESET}"
MSG_RESTORE_FAILED = f"{COLOR_RED}Critical Error: Failed to restore backup! Manual intervention required at {{path}}{COLOR_RESET}"
MSG_DELETE_ERROR = f"{COLOR_RED}Error deleting {{path}}: {{error}}{COLOR_RESET}"
MSG_DELETE_LOCKED = f"{COLOR_RED}Error: Could not delete {{path}}. Is it in use?{COLOR_RESET}"

# Sync Messages
MSG_SYNCED_SUCCESS = f"{COLOR_GREEN}{ICON_SUCCESS} Synced {{count}} skills to registry{COLOR_RESET}"
MSG_REGISTRY_FILE = f"   Registry file: {{path}}"
MSG_SKILLS_LIST = f"\n{ICON_LIST} Skills List:"
MSG_DRY_RUN = f"{ICON_SEARCH} Dry run: Would sync {{count}} skills"

# Backup Messages
MSG_BACKING_UP = f"{COLOR_CYAN}Backing up {{name}}...{COLOR_RESET}"
MSG_BACKING_UP_ALL = f"{COLOR_CYAN}Backing up all skills...{COLOR_RESET}"
MSG_BACKUP_SUCCESS = f"{COLOR_GREEN}{ICON_SUCCESS} Backed up {{name}} to {{path}}{COLOR_RESET}"
MSG_BACKUP_ALL_SUCCESS = f"{COLOR_GREEN}{ICON_SUCCESS} Backed up all skills to {{path}}{COLOR_RESET}"
MSG_BACKUP_SIZE = f"Backup size: {{size:.2f}} MB"
MSG_NO_BACKUPS = "No backups found."
MSG_AVAILABLE_BACKUPS = f"\n{COLOR_BLUE}Available Backups:{COLOR_RESET}"
MSG_RESTORING = f"{COLOR_CYAN}Restoring from {{name}}...{COLOR_RESET}"
MSG_RESTORE_CANCELLED = "Restore cancelled."
MSG_RESTORE_CONFIRM = "This will overwrite existing skills. Continue? (y/N): "
MSG_RESTORE_SKILL_EXISTS = f"Skill '{{name}}' already exists. Overwrite? (y/N): "
MSG_RESTORED_SINGLE = f"{COLOR_GREEN}{ICON_SUCCESS} Restored {{name}}{COLOR_RESET}"
MSG_RESTORED_ALL = f"{COLOR_GREEN}{ICON_SUCCESS} Restored all skills{COLOR_RESET}"
MSG_CLEANING_BACKUPS = f"{COLOR_CYAN}Cleaning up old backups (keeping {{keep}} most recent)...{COLOR_RESET}"
MSG_REMOVED_BACKUP = f"{COLOR_GREEN}Removed: {{name}}{COLOR_RESET}"

# Update All Messages
MSG_START_UPDATE = f"{COLOR_BLUE}Starting skills update process{COLOR_RESET}"
MSG_PHASE_CHECK = f"{COLOR_CYAN}Phase 1: Checking for updates...{COLOR_RESET}"
MSG_PHASE_UPDATE = f"{COLOR_CYAN}Phase 2: Updating skills...{COLOR_RESET}"
MSG_NO_UPDATES = f"\n{COLOR_GREEN}No updates available.{COLOR_RESET}"
MSG_FOUND_UPDATES = f"\n{COLOR_CYAN}Found {{count}} skill(s) with updates:{COLOR_RESET}"
MSG_FORCE_HINT = f"\n{COLOR_YELLOW}Use --force to proceed with updates{COLOR_RESET}"
MSG_UPDATE_SUMMARY = f"{COLOR_BLUE}Update Summary{COLOR_RESET}"
MSG_TOTAL_CHECKED = f"Total skills checked: {{count}}"
MSG_UPDATES_AVAILABLE_COUNT = f"Updates available: {{count}}"
MSG_SUCCESS_COUNT = f"{COLOR_GREEN}Successfully updated: {{count}}{COLOR_RESET}"
MSG_FAILED_COUNT = f"{COLOR_RED}Failed to update: {{count}}{COLOR_RESET}"

# Catalog Messages
MSG_CATALOG_LOADED = f"{COLOR_GREEN}{ICON_SUCCESS} Catalog loaded successfully{COLOR_RESET}"
MSG_CATALOG_VERSION = f"   Catalog version: {{version}}"
MSG_CATEGORIES_HEADER = f"\n{COLOR_BLUE}Available Categories:{COLOR_RESET}"
MSG_CATEGORY_NAME = f"  {COLOR_CYAN}{{name}}{COLOR_RESET}"
MSG_CATEGORY_DESC = f"    {{description}}"
MSG_SKILLS_HEADER = f"\n{COLOR_BLUE}Skills in category '{{category}}':{COLOR_RESET}"
MSG_ALL_SKILLS_HEADER = f"\n{COLOR_BLUE}All Skills:{COLOR_RESET}"
MSG_SKILL_NAME = f"  {COLOR_GREEN}{{name}}{COLOR_RESET}"
MSG_SKILL_DESC = f"    {{description}}"
MSG_SKILL_SOURCE = f"    Source: {{source}}"
MSG_SKILL_LICENSE = f"    License: {{license}}"
MSG_SKILL_ALIASES = f"    Aliases: {{aliases}}"
MSG_SKILL_DEPENDENCIES = f"    Dependencies: {{dependencies}}"
MSG_SKILL_INFO_HEADER = f"\n{COLOR_BLUE}Skill Information:{COLOR_RESET}"
MSG_SKILL_NOT_FOUND_CATALOG = f"{COLOR_YELLOW}Skill '{{name}}' not found in catalog{COLOR_RESET}"
MSG_SEARCH_RESULTS = f"\n{COLOR_BLUE}Search results for '{{query}}':{COLOR_RESET}"
MSG_NO_SEARCH_RESULTS = f"{COLOR_YELLOW}No skills found matching '{{query}}'{COLOR_RESET}"
MSG_ALIAS_RESOLVED = f"{COLOR_GREEN}Alias '{{alias}}' resolves to: {{skill_name}}{COLOR_RESET}"
MSG_ALIAS_NOT_FOUND = f"{COLOR_YELLOW}Alias '{{alias}}' not found in catalog{COLOR_RESET}"
MSG_CATALOG_UPDATE_NOT_IMPLEMENTED = f"{COLOR_YELLOW}Remote catalog update not yet implemented.{COLOR_RESET}"
MSG_CATALOG_VERSION_INFO = f"Catalog remains at local version: {{version}}"
MSG_CATALOG_ERROR = f"{COLOR_RED}Catalog error: {{error}}{COLOR_RESET}"
MSG_CATALOG_NOT_FOUND = f"{COLOR_RED}Catalog file not found: {{path}}{COLOR_RESET}"
MSG_CATALOG_INVALID = f"{COLOR_RED}Invalid catalog format: {{error}}{COLOR_RESET}"
MSG_RESOLVING_SKILL = f"{ICON_SEARCH} Resolving skill '{{name}}' from catalog..."
MSG_SKILL_RESOLVED = f"{COLOR_GREEN}{ICON_SUCCESS} Resolved '{{name}}' to {{source}}{COLOR_RESET}"
MSG_SKILL_NOT_FOUND_CATALOG_FULL = f"{COLOR_RED}Error: Skill '{{name}}' not found in catalog.{COLOR_RESET}"
MSG_CATEGORY_NOT_FOUND = f"{COLOR_RED}Error: Category '{{category}}' not found in catalog.{COLOR_RESET}"
MSG_ALIAS_NOT_FOUND_FULL = f"{COLOR_RED}Error: Alias '{{alias}}' not recognized.{COLOR_RESET}"
MSG_TRY_SEARCH = f"{COLOR_YELLOW}Tip: Use 'python find-skills.py search <query>' to find available skills.{COLOR_RESET}"
MSG_AVAILABLE_CATEGORIES = f"{COLOR_BLUE}Available categories: {{categories}}{COLOR_RESET}"

# Search Messages
MSG_SEARCHING = f"{COLOR_CYAN}{ICON_SEARCH} Searching for skills matching '{{query}}'...{COLOR_RESET}"
MSG_SEARCH_RESULTS_HEADER = f"\n{COLOR_BLUE}Search Results for '{{query}}':{COLOR_RESET}"
MSG_NO_SEARCH_RESULTS = f"\n{COLOR_YELLOW}No skills found matching '{{query}}'{COLOR_RESET}"
MSG_SEARCH_RESULT_ITEM = f"  {COLOR_GREEN}{{name}}{COLOR_RESET}"
MSG_SEARCH_RESULT_DESC = f"    {COLOR_CYAN}{{description}}{COLOR_RESET}"
MSG_SEARCH_RESULT_CATEGORY = f"    Category: {{category}}"
MSG_SEARCH_RESULT_ALIASES = f"    Aliases: {{aliases}}"
MSG_SEARCH_RESULT_SOURCE = f"    Source: {{source}}"
MSG_SEARCH_SUGGESTIONS = f"\n{COLOR_YELLOW}Suggestions:{COLOR_RESET}"
MSG_SEARCH_SUGGESTION = f"  - {{suggestion}}"

# Info Messages
MSG_INFO_HEADER = f"\n{COLOR_BLUE}════════════════════════════════════════════════════════════════{COLOR_RESET}"
MSG_INFO_TITLE = f"{COLOR_BLUE}Skill Information:{COLOR_RESET}"
MSG_INFO_NAME = f"  {COLOR_CYAN}Name:{COLOR_RESET} {{name}}"
MSG_INFO_CATEGORY = f"  {COLOR_CYAN}Category:{COLOR_RESET} {{category}}"
MSG_INFO_DESCRIPTION = f"  {COLOR_CYAN}Description:{COLOR_RESET} {{description}}"
MSG_INFO_SOURCE = f"  {COLOR_CYAN}Source:{COLOR_RESET} {{source}}"
MSG_INFO_LICENSE = f"  {COLOR_CYAN}License:{COLOR_RESET} {{license}}"
MSG_INFO_ALIASES = f"  {COLOR_CYAN}Aliases:{COLOR_RESET} {{aliases}}"
MSG_INFO_DEPENDENCIES = f"  {COLOR_CYAN}Dependencies:{COLOR_RESET}"
MSG_INFO_DEPENDENCY_INSTALLED = f"    {COLOR_GREEN}✓{{dep}}{COLOR_RESET} (installed)"
MSG_INFO_DEPENDENCY_MISSING = f"    {COLOR_YELLOW}✗{{dep}}{COLOR_RESET} (not installed)"
MSG_INFO_VERSION = f"  {COLOR_CYAN}Installed Version:{COLOR_RESET} {{version}}"
MSG_INFO_UPDATED = f"  {COLOR_CYAN}Last Updated:{COLOR_RESET} {{updated}}"
MSG_INFO_STATUS_INSTALLED = f"  {COLOR_CYAN}Status:{COLOR_RESET} {COLOR_GREEN}Installed{COLOR_RESET}"
MSG_INFO_STATUS_NOT_INSTALLED = f"  {COLOR_CYAN}Status:{COLOR_RESET} {COLOR_YELLOW}Not Installed{COLOR_RESET}"
MSG_SKILL_NOT_FOUND = f"{COLOR_RED}Error: Skill '{{name}}' not found in catalog.{COLOR_RESET}"
MSG_INFO_FOOTER = f"{COLOR_BLUE}════════════════════════════════════════════════════════════════{COLOR_RESET}"

# Catalog/Browse Messages
MSG_CATALOG_HEADER = f"\n{COLOR_BLUE}════════════════════════════════════════════════════════════════{COLOR_RESET}"
MSG_CATALOG_TITLE = f"{COLOR_BLUE}Skill Catalog{COLOR_RESET}"
MSG_CATEGORY_HEADER = f"\n{COLOR_CYAN}{{category}}{COLOR_RESET}"
MSG_CATEGORY_DESCRIPTION = f"  {{description}}"
MSG_SKILL_IN_CATALOG = f"  {COLOR_GREEN}{{name}}{COLOR_RESET}"
MSG_SKILL_ALIASES_IN_CATALOG = f"    Aliases: {{aliases}}"
MSG_SKILL_DESC_IN_CATALOG = f"    {{description}}"
MSG_CATEGORIES_LIST = f"\n{COLOR_BLUE}Available Categories:{COLOR_RESET}"
MSG_NO_SKILLS_IN_CATEGORY = f"{COLOR_YELLOW}No skills found in category '{{category}}'{COLOR_RESET}"
MSG_CATEGORY_NOT_FOUND = f"{COLOR_RED}Error: Category '{{category}}' not found in catalog.{COLOR_RESET}"
MSG_CATALOG_FOOTER = f"{COLOR_BLUE}════════════════════════════════════════════════════════════════{COLOR_RESET}"


# Dependency Management Messages
MSG_CHECKING_DEPENDENCIES = f"\n{ICON_SEARCH} Checking dependencies for '{{skill_name}}'..."
MSG_DEPENDENCIES_FOUND = f"   Found {{count}} dependenc{{ies}}: {{deps}}"
MSG_NO_DEPENDENCIES = f"   No dependencies found"
MSG_DEPENDENCY_INSTALLED = f"   {COLOR_GREEN}✓{{dep}}{COLOR_RESET} already installed"
MSG_DEPENDENCY_MISSING = f"   {COLOR_YELLOW}✗{{dep}}{COLOR_RESET} not installed"
MSG_MISSING_DEPENDENCIES = f"\n{COLOR_YELLOW}Missing dependencies: {{deps}}{COLOR_RESET}"
MSG_INSTALL_DEPENDENCIES_PROMPT = "Install missing dependencies? (y/N): "
MSG_AUTO_INSTALLING_DEPS = f"{COLOR_CYAN}Auto-installing dependencies (--yes flag){{deps}}{COLOR_RESET}"
MSG_INSTALLING_DEPENDENCY = f"\n{ICON_PACKAGE} Installing dependency: {{dep}}"
MSG_DEPENDENCY_INSTALL_FAILED = f"{COLOR_RED}Failed to install dependency '{{dep}}'{COLOR_RESET}"
MSG_ALL_DEPENDENCIES_INSTALLED = f"{COLOR_GREEN}{ICON_SUCCESS} All dependencies installed{COLOR_RESET}"
MSG_CIRCULAR_DEPENDENCY = f"{COLOR_RED}Circular dependency detected: {{cycle}}{COLOR_RESET}"
MSG_DEPENDENCY_RESOLUTION_FAILED = f"{COLOR_RED}Failed to resolve dependency order{COLOR_RESET}"
MSG_INSTALL_ORDER = f"   Install order: {{order}}"

# Auto-Confirmation Messages
MSG_AUTO_CONFIRM_ENABLED = f"{COLOR_CYAN}Auto-confirmation enabled (--yes flag). All prompts will be skipped.{COLOR_RESET}"

# Interactive Mode Messages
MSG_INTERACTIVE_WELCOME = f"""
{COLOR_BLUE}╔════════════════════════════════════════════════════════════════╗
║              Trae Skill Installer - Interactive Mode              ║
╚════════════════════════════════════════════════════════════════╝{COLOR_RESET}

Browse and install skills from the catalog interactively.
Follow the prompts to navigate categories and select skills to install.
"""
MSG_INTERACTIVE_CATEGORIES_HEADER = f"\n{COLOR_BLUE}Available Categories:{COLOR_RESET}"
MSG_INTERACTIVE_CATEGORY_ITEM = "  {index}. {COLOR_CYAN}{name}{COLOR_RESET} - {description}"
MSG_INTERACTIVE_SELECT_CATEGORY = "\nSelect a category by number or name (or 'back'/'exit' to quit): "
MSG_INTERACTIVE_SKILLS_HEADER = f"\n{COLOR_BLUE}Skills in '{{category}}':{COLOR_RESET}"
MSG_INTERACTIVE_SKILL_ITEM = "  {index}. {COLOR_GREEN}{name}{COLOR_RESET} - {description}"
MSG_INTERACTIVE_SKILL_ALIASES = "       Aliases: {aliases}"
MSG_INTERACTIVE_SELECT_SKILL = "\nSelect a skill by number or name (or 'back'/'exit' to quit): "
MSG_INTERACTIVE_PREVIEW_HEADER = f"\n{COLOR_BLUE}════════════════════════════════════════════════════════════════{COLOR_RESET}"
MSG_INTERACTIVE_PREVIEW_TITLE = f"{COLOR_BLUE}Skill Preview:{COLOR_RESET}"
MSG_INTERACTIVE_PREVIEW_NAME = "  Name: {COLOR_CYAN}{name}{COLOR_RESET}"
MSG_INTERACTIVE_PREVIEW_DESC = "  Description: {description}"
MSG_INTERACTIVE_PREVIEW_SOURCE = "  Source: {source}"
MSG_INTERACTIVE_PREVIEW_LICENSE = "  License: {license}"
MSG_INTERACTIVE_PREVIEW_DEPS = "  Dependencies: {dependencies}"
MSG_INTERACTIVE_PREVIEW_NO_DEPS = "  Dependencies: None"
MSG_INTERACTIVE_PREVIEW_FOOTER = f"{COLOR_BLUE}════════════════════════════════════════════════════════════════{COLOR_RESET}"
MSG_INTERACTIVE_CONFIRM_INSTALL = "\nInstall this skill? (y/N): "
MSG_INTERACTIVE_INSTALL_ANOTHER = "\nInstall another skill? (y/N): "
MSG_INTERACTIVE_EXIT = f"\n{COLOR_YELLOW}Exiting interactive mode.{COLOR_RESET}"
MSG_INTERACTIVE_INVALID_CHOICE = f"{COLOR_RED}Invalid choice. Please try again.{COLOR_RESET}"
MSG_INTERACTIVE_SKILL_INSTALLED = f"{COLOR_GREEN}{ICON_SUCCESS} Skill '{{name}}' installed successfully!{COLOR_RESET}"
MSG_INTERACTIVE_SKILL_INSTALL_FAILED = f"{COLOR_RED}Failed to install skill '{{name}}'{COLOR_RESET}"

# Batch Installation Messages
MSG_BATCH_INSTALL_START = f"\n{COLOR_BLUE}════════════════════════════════════════════════════════════════{COLOR_RESET}"
MSG_BATCH_INSTALL_TITLE = f"{COLOR_BLUE}Batch Installation: {{count}} skill(s){COLOR_RESET}"
MSG_BATCH_INSTALL_PROGRESS = f"[{{current}}/{{total}}] Installing: {{source}}"
MSG_BATCH_INSTALL_SUCCESS = f"   {COLOR_GREEN}{ICON_SUCCESS} Successfully installed: {{source}}{COLOR_RESET}"
MSG_BATCH_INSTALL_FAILED = f"   {COLOR_RED}{ICON_ERROR} Failed to install: {{source}}{COLOR_RESET}"
MSG_BATCH_INSTALL_ERROR = f"      Error: {{error}}"
MSG_BATCH_INSTALL_SUMMARY = f"\n{COLOR_BLUE}════════════════════════════════════════════════════════════════{COLOR_RESET}"
MSG_BATCH_INSTALL_SUMMARY_TITLE = f"{COLOR_BLUE}Batch Installation Summary{COLOR_RESET}"
MSG_BATCH_INSTALL_TOTAL = f"   Total skills attempted: {{total}}"
MSG_BATCH_INSTALL_SUCCESS_COUNT = f"   {COLOR_GREEN}Successfully installed: {{count}}{COLOR_RESET}"
MSG_BATCH_INSTALL_FAILED_COUNT = f"   {COLOR_RED}Failed to install: {{count}}{COLOR_RESET}"
MSG_BATCH_INSTALL_FAILED_LIST = f"   Failed skills: {{skills}}"
MSG_BATCH_INSTALL_ALL_SUCCESS = f"   {COLOR_GREEN}{ICON_SUCCESS} All skills installed successfully!{COLOR_RESET}"
MSG_BATCH_INSTALL_SOME_FAILED = f"   {COLOR_YELLOW}Some installations failed. See details above.{COLOR_RESET}"
MSG_BATCH_INSTALL_ALL_FAILED = f"   {COLOR_RED}All installations failed.{COLOR_RESET}"

# Health Check Messages
MSG_HEALTH_CHECK_START = f"\n{COLOR_CYAN}{ICON_SEARCH} Starting health check...{COLOR_RESET}"
MSG_HEALTH_CHECK_SKILL = f"   Checking {{skill_name}}..."
MSG_HEALTH_STATUS_HEALTHY = f"   {COLOR_GREEN}✓ Status: Healthy{COLOR_RESET}"
MSG_HEALTH_STATUS_WARNING = f"   {COLOR_YELLOW}⚠ Status: Warning{COLOR_RESET}"
MSG_HEALTH_STATUS_ERROR = f"   {COLOR_RED}✗ Status: Error{COLOR_RESET}"
MSG_HEALTH_ISSUES_FOUND = f"   {COLOR_YELLOW}Issues found:{{issues}}{COLOR_RESET}"
MSG_HEALTH_NO_ISSUES = f"   {COLOR_GREEN}No issues found{COLOR_RESET}"
MSG_HEALTH_RECOMMENDATIONS = f"   {COLOR_CYAN}Recommendations:{{recommendations}}{COLOR_RESET}"
MSG_HEALTH_CHECK_SKILL_MD_MISSING = f"   {COLOR_RED}✗ SKILL.md file not found{COLOR_RESET}"
MSG_HEALTH_CHECK_SKILL_MD_INVALID = f"   {COLOR_RED}✗ SKILL.md format invalid: {{error}}{COLOR_RESET}"
MSG_HEALTH_CHECK_DEPENDENCY_MISSING = f"   {COLOR_YELLOW}✗ Missing dependency: {{dep}}{COLOR_RESET}"

# Health Validation Messages
MSG_VALIDATING_SKILLS = f"\n{COLOR_CYAN}{ICON_SEARCH} Validating skills...{COLOR_RESET}"
MSG_SKILL_VALID = f"   {COLOR_GREEN}{ICON_SUCCESS} {{name}}: Valid{COLOR_RESET}"
MSG_SKILL_INVALID = f"   {COLOR_RED}{ICON_ERROR} {{name}}: Invalid - {{error}}{COLOR_RESET}"
MSG_DEPENDENCIES_CHECK = f"\n{ICON_SEARCH} Checking dependencies..."
MSG_DEPENDENCY_OK = f"   {COLOR_GREEN}{ICON_SUCCESS} {{name}}: All dependencies satisfied{COLOR_RESET}"
MSG_DEPENDENCY_MISSING = f"   {COLOR_YELLOW}{ICON_WARN} {{name}}: Missing dependencies: {{deps}}{COLOR_RESET}"
MSG_HEALTH_SUMMARY = f"\n{COLOR_BLUE}════════════════════════════════════════════════════════════════{COLOR_RESET}"
MSG_HEALTH_SUMMARY_TITLE = f"{COLOR_BLUE}Health Summary{COLOR_RESET}"
MSG_HEALTH_TOTAL = f"   Total skills checked: {{count}}"
MSG_HEALTH_HEALTHY = f"   {COLOR_GREEN}Healthy: {{count}}{COLOR_RESET}"
MSG_HEALTH_WARNINGS = f"   {COLOR_YELLOW}Warnings: {{count}}{COLOR_RESET}"
MSG_HEALTH_ERRORS = f"   {COLOR_RED}Errors: {{count}}{COLOR_RESET}"
MSG_HEALTH_ISSUES_HEADER = f"\n{COLOR_YELLOW}Skills with issues:{COLOR_RESET}"
MSG_HEALTH_RECOMMENDATIONS = f"\n{COLOR_CYAN}Recommendations:{COLOR_RESET}"
MSG_HEALTH_RECOMMENDATION_FIX_MD = f"   - Fix SKILL.md files for skills with validation errors"
MSG_HEALTH_RECOMMENDATION_INSTALL_DEPS = f"   - Install missing dependencies to resolve dependency warnings"

# Rollback Messages
MSG_ROLLBACK_START = f"\n{COLOR_CYAN}{ICON_RESTORE} Starting rollback for skill: {{name}}{COLOR_RESET}"
MSG_ROLLBACK_VERSION_HISTORY = f"\n{COLOR_BLUE}Version History:{COLOR_RESET}"
MSG_ROLLBACK_SELECT_VERSION = "\nSelect a version to rollback to (enter index number or 'q' to cancel): "
MSG_ROLLBACK_TO_VERSION = f"\n{COLOR_CYAN}Rolling back to version {{version}}...{COLOR_RESET}"
MSG_ROLLBACK_SUCCESS = f"{COLOR_GREEN}{ICON_SUCCESS} Successfully rolled back '{{name}}' to version {{version}}{COLOR_RESET}"
MSG_ROLLBACK_FAILED = f"{COLOR_RED}{ICON_ERROR} Failed to rollback '{{name}}'{COLOR_RESET}"
MSG_ROLLBACK_NOT_GIT_REPO = f"{COLOR_YELLOW}Warning: Skill '{{name}}' is not a git repository. Rollback not available.{COLOR_RESET}"
MSG_ROLLBACK_NO_HISTORY = f"{COLOR_YELLOW}No version history available for '{{name}}'{COLOR_RESET}"
MSG_ROLLBACK_BACKUP_CREATED = f"{COLOR_YELLOW}Created backup before rollback: {{path}}{COLOR_RESET}"
MSG_ROLLBACK_BACKUP_RESTORED = f"{COLOR_GREEN}Restored from backup after rollback failure{COLOR_RESET}"

# Verbose Mode Messages
MSG_VERBOSE_ENABLED = f"{COLOR_CYAN}{ICON_INFO} Verbose mode enabled. Detailed debug information will be displayed.{COLOR_RESET}"
MSG_VERBOSE_GIT_COMMAND = f"{COLOR_CYAN}[GIT] Running command: {{cmd}}{COLOR_RESET}"
MSG_VERBOSE_GIT_OUTPUT = f"{COLOR_CYAN}[GIT] Output: {{output}}{COLOR_RESET}"
MSG_VERBOSE_FILE_OP = f"{COLOR_CYAN}[FILE] {{operation}}: {{path}}{COLOR_RESET}"
MSG_VERBOSE_STATE_CHANGE = f"{COLOR_CYAN}[STATE] {{description}}{COLOR_RESET}"
MSG_VERBOSE_DEPENDENCY_CHECK = f"{COLOR_CYAN}[DEP] Checking dependency: {{dep}}{COLOR_RESET}"

# Progress Indicator Messages
MSG_PROGRESS_GIT_CLONE = f"{COLOR_CYAN}[PROGRESS] Cloning repository... {{percent}}%{COLOR_RESET}"
MSG_PROGRESS_INSTALLING = f"{COLOR_CYAN}[PROGRESS] Installing skill {{current}}/{{total}}...{COLOR_RESET}"
MSG_PROGRESS_CHECKING = f"{COLOR_CYAN}[PROGRESS] Checking for updates... {{current}}/{{total}}{COLOR_RESET}"
MSG_PROGRESS_UPDATING = f"{COLOR_CYAN}[PROGRESS] Updating skill {{current}}/{{total}}...{COLOR_RESET}"
MSG_PROGRESS_DEPENDENCIES = f"{COLOR_CYAN}[PROGRESS] Installing dependencies... {{current}}/{{total}}{COLOR_RESET}"

# Improved Error Messages
MSG_ERROR_NETWORK = f"{COLOR_RED}{ICON_ERROR} Network Error: Unable to connect to '{{url}}'.{COLOR_RESET}"
MSG_ERROR_NETWORK_SUGGESTION = f"{COLOR_YELLOW}Suggestion: Check your internet connection and try again. If using a firewall, ensure git access is allowed.{COLOR_RESET}"
MSG_ERROR_PERMISSION_DENIED = f"{COLOR_RED}{ICON_ERROR} Permission Denied: Cannot write to '{{path}}'.{COLOR_RESET}"
MSG_ERROR_PERMISSION_SUGGESTION = f"{COLOR_YELLOW}Suggestion: Run with administrator privileges or check directory permissions.{COLOR_RESET}"
MSG_ERROR_DISK_FULL = f"{COLOR_RED}{ICON_ERROR} Disk Full: Not enough space to complete operation.{COLOR_RESET}"
MSG_ERROR_DISK_SUGGESTION = f"{COLOR_YELLOW}Suggestion: Free up disk space and try again.{COLOR_RESET}"
MSG_ERROR_INVALID_URL = f"{COLOR_RED}{ICON_ERROR} Invalid URL: '{{url}}' is not a valid git repository.{COLOR_RESET}"
MSG_ERROR_INVALID_URL_SUGGESTION = f"{COLOR_YELLOW}Suggestion: Verify the URL format. Examples: https://github.com/user/repo or user/repo{COLOR_RESET}"
MSG_ERROR_REPO_NOT_FOUND = f"{COLOR_RED}{ICON_ERROR} Repository Not Found: '{{url}}' does not exist or is not accessible.{COLOR_RESET}"
MSG_ERROR_REPO_NOT_FOUND_SUGGESTION = f"{COLOR_YELLOW}Suggestion: Check the repository name and ensure it's public or you have access.{COLOR_RESET}"
MSG_ERROR_GIT_NOT_INSTALLED = f"{COLOR_RED}{ICON_ERROR} Git Not Found: Git is not installed or not in PATH.{COLOR_RESET}"
MSG_ERROR_GIT_NOT_INSTALLED_SUGGESTION = f"{COLOR_YELLOW}Suggestion: Install Git from https://git-scm.com/downloads and ensure it's in your PATH.{COLOR_RESET}"
MSG_ERROR_YAML_PARSE = f"{COLOR_RED}{ICON_ERROR} YAML Parse Error: Failed to parse '{{file}}'.{COLOR_RESET}"
MSG_ERROR_YAML_PARSE_SUGGESTION = f"{COLOR_YELLOW}Suggestion: Check YAML syntax. Ensure proper indentation and quote strings with special characters.{COLOR_RESET}"
MSG_ERROR_DEPENDENCY_CYCLE = f"{COLOR_RED}{ICON_ERROR} Circular Dependency Detected: {{cycle}}{COLOR_RESET}"
MSG_ERROR_DEPENDENCY_CYCLE_SUGGESTION = f"{COLOR_YELLOW}Suggestion: Remove circular dependencies from SKILL.md files.{COLOR_RESET}"
MSG_ERROR_MISSING_SKILL_MD = f"{COLOR_RED}{ICON_ERROR} Missing SKILL.md: Required file not found in '{{path}}'.{COLOR_RESET}"
MSG_ERROR_MISSING_SKILL_MD_SUGGESTION = f"{COLOR_YELLOW}Suggestion: Create a SKILL.md file with proper YAML frontmatter including name and description.{COLOR_RESET}"
MSG_ERROR_INVALID_SKILL_MD = f"{COLOR_RED}{ICON_ERROR} Invalid SKILL.md: File format is invalid. {{error}}{COLOR_RESET}"
MSG_ERROR_INVALID_SKILL_MD_SUGGESTION = f"{COLOR_YELLOW}Suggestion: Ensure SKILL.md starts with '---', contains valid YAML, and ends with '---'.{COLOR_RESET}"

# License Messages
MSG_LICENSE_CHECKING = f"{COLOR_CYAN}{ICON_SEARCH} Checking license compatibility...{COLOR_RESET}"
MSG_LICENSE_DETECTED = f"   {COLOR_GREEN}License detected: {{license_type}}{COLOR_RESET}"
MSG_LICENSE_NOT_FOUND = f"   {COLOR_YELLOW}No license file found{COLOR_RESET}"
MSG_LICENSE_INFO_HEADER = f"\n{COLOR_BLUE}License Information:{COLOR_RESET}"
MSG_LICENSE_INFO_TYPE = f"   Type: {{license_type}}"
MSG_LICENSE_INFO_STATUS = f"   Status: {{status}}"
MSG_LICENSE_COMPATIBLE = f"   {COLOR_GREEN}✓ Compatible{COLOR_RESET}"
MSG_LICENSE_WARNING = f"   {COLOR_YELLOW}⚠ {{message}}{COLOR_RESET}"
MSG_LICENSE_INCOMPATIBLE = f"   {COLOR_RED}✗ Incompatible{COLOR_RESET}"
MSG_LICENSE_CONFIRM_INCOMPATIBLE = "   Install anyway? (y/N): "

# Registry Sync Reminder for Installation
MSG_REGISTRY_SYNC_REQUIRED = f"""
{COLOR_GREEN}{ICON_SUCCESS} Installation completed successfully.{COLOR_RESET}

{COLOR_CYAN}╔════════════════════════════════════════════════════════════════╗{COLOR_RESET}
{COLOR_CYAN}║  [REQUIRED ACTION] Invoke skills-registry-sync skill NOW      ║{COLOR_RESET}
{COLOR_CYAN}╚════════════════════════════════════════════════════════════════╝{COLOR_RESET}

{COLOR_YELLOW}AI Assistant: You MUST invoke the 'skills-registry-sync' skill using the Skill tool.{COLOR_RESET}
{COLOR_YELLOW}Do NOT run scripts directly. Use: Skill tool with name='skills-registry-sync'{COLOR_RESET}

{COLOR_CYAN}This will synchronize:{COLOR_RESET}
   - skills.json (source, version, health status)
   - skill_map.json (description, keywords, aliases)
   - AGENTS.md (skill documentation)
"""

# Registry Sync Reminder for Uninstallation
MSG_REGISTRY_SYNC_REQUIRED_UNINSTALL = f"""
{COLOR_GREEN}{ICON_SUCCESS} Uninstallation completed successfully.{COLOR_RESET}

{COLOR_CYAN}╔════════════════════════════════════════════════════════════════╗{COLOR_RESET}
{COLOR_CYAN}║  [REQUIRED ACTION] Invoke skills-registry-sync skill NOW      ║{COLOR_RESET}
{COLOR_CYAN}╚════════════════════════════════════════════════════════════════╝{COLOR_RESET}

{COLOR_YELLOW}AI Assistant: You MUST invoke the 'skills-registry-sync' skill using the Skill tool.{COLOR_RESET}
{COLOR_YELLOW}Do NOT run scripts directly. Use: Skill tool with name='skills-registry-sync'{COLOR_RESET}

{COLOR_CYAN}This will synchronize:{COLOR_RESET}
   - skills.json (remove uninstalled skill entry)
   - skill_map.json (remove skill metadata)
   - AGENTS.md (remove skill documentation)
"""
