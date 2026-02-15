#!/usr/bin/env python3
"""
Skill Initializer - Creates a new skill from template

Usage:
    init_skill.py <skill-name> --path <path>

Examples:
    init_skill.py my-new-skill --path skills/public
    init_skill.py my-api-helper --path skills/private
    init_skill.py custom-skill --path /custom/location
"""

import sys
import os
import json
import datetime
from pathlib import Path
try:
    from messages import *
except ImportError:
    # Fallback if messages.py not found in same dir
    ICON_FAIL = "[FAIL]"
    ICON_PASS = "[PASS]"
    ICON_INFO = "[*]"
    COLOR_GREEN = "\033[92m"
    COLOR_RED = "\033[91m"
    COLOR_YELLOW = "\033[93m"
    COLOR_BLUE = "\033[94m"
    COLOR_CYAN = "\033[96m"
    COLOR_RESET = "\033[0m"
    MSG_INITIALIZING = f"{ICON_INFO} Initializing skill: {skill_name}"
    MSG_LOCATION = f"   Location: {path}"
    MSG_DIR_EXISTS = f"{COLOR_RED}[FAIL] Error: Skill directory already exists: {skill_dir}{COLOR_RESET}"
    MSG_DIR_CREATED = f"{COLOR_GREEN}[PASS] Created skill directory: {skill_dir}{COLOR_RESET}"
    MSG_DIR_CREATE_ERROR = f"{COLOR_RED}[FAIL] Error creating directory: {e}{COLOR_RESET}"
    MSG_SKILL_MD_CREATED = f"{COLOR_GREEN}[PASS] Created SKILL.md{COLOR_RESET}"
    MSG_SKILL_MD_ERROR = f"{COLOR_RED}[FAIL] Error creating SKILL.md: {e}{COLOR_RESET}"
    MSG_SCRIPT_CREATED = f"{COLOR_GREEN}[PASS] Created scripts/example.py{COLOR_RESET}"
    MSG_REQUIREMENTS_CREATED = f"{COLOR_GREEN}[PASS] Created scripts/requirements.txt{COLOR_RESET}"
    MSG_REFERENCE_CREATED = f"{COLOR_GREEN}[PASS] Created references/api_reference.md{COLOR_RESET}"
    MSG_ASSET_CREATED = f"{COLOR_GREEN}[PASS] Created assets/example_asset.txt{COLOR_RESET}"
    MSG_RESOURCE_ERROR = f"{COLOR_RED}[FAIL] Error creating resource directories: {e}{COLOR_RESET}"
    MSG_INIT_SUCCESS = f"{COLOR_GREEN}[PASS] Skill '{skill_name}' initialized successfully at {skill_dir}{COLOR_RESET}"
    MSG_NEXT_STEPS = f"\n{ICON_INFO} Next steps:"
    MSG_STEP_1 = "1. Edit SKILL.md to complete TODO items and update description"
    MSG_STEP_2 = "2. Customize or delete example files in scripts/, references/, and assets/"
    MSG_STEP_3 = "3. Run validator when ready to check skill structure"
    MSG_USAGE = "Usage: init_skill.py <skill-name> --path <path>"
    MSG_SKILL_NAME_REQ = "\nSkill name requirements:"
    MSG_REQ_HYPHEN = "  - Hyphen-case identifier (e.g., 'data-analyzer')"
    MSG_REQ_LOWERCASE = "  - Lowercase letters, digits, and hyphens only"
    MSG_REQ_MAX_CHARS = "  - Max 40 characters"
    MSG_REQ_MATCH = "  - Must match directory name exactly"
    MSG_EXAMPLES = "\nExamples:"
    MSG_EXAMPLE_1 = "  init_skill.py my-new-skill --path skills/public"
    MSG_EXAMPLE_2 = "  init_skill.py my-api-helper --path skills/private"
    MSG_EXAMPLE_3 = "  init_skill.py custom-skill --path /custom/location"

SKILL_TEMPLATE = """---
name: {skill_name}
description: "TODO: Complete and informative explanation of what this skill does and when to use it. Include WHEN to use this skill - specific scenarios, file types, or tasks that trigger it."
---

# {skill_title}

## Overview

[TODO: 1-2 sentences explaining what this skill enables]

## Structuring This Skill

[TODO: Choose the structure that best fits this skill's purpose. Common patterns:

**1. Workflow-Based** (best for sequential processes)
- Works well when there are clear step-by-step procedures
- Example: DOCX skill with "Workflow Decision Tree" → "Reading" → "Creating" → "Editing"
- Structure: ## Overview → ## Workflow Decision Tree → ## Step 1 → ## Step 2...

**2. Task-Based** (best for tool collections)
- Works well when skill offers different operations/capabilities
- Example: PDF skill with "Quick Start" → "Merge PDFs" → "Split PDFs" → "Extract Text"
- Structure: ## Overview → ## Quick Start → ## Task Category 1 → ## Task Category 2...

**3. Reference/Guidelines** (best for standards or specifications)
- Works well for brand guidelines, coding standards, or requirements
- Example: Brand styling with "Brand Guidelines" → "Colors" → "Typography" → "Features"
- Structure: ## Overview → ## Guidelines → ## Specifications → ## Usage...

**4. Capabilities-Based** (best for integrated systems)
- Works well when skill provides multiple interrelated features
- Example: Product Management with "Core Capabilities" → numbered capability list
- Structure: ## Overview → ## Core Capabilities → ### 1. Feature → ### 2. Feature...

Patterns can be mixed and matched as needed. Most skills combine patterns (e.g., start with task-based, add workflow for complex operations).

Delete this entire "Structuring This Skill" section when done - it's just guidance.

## [TODO: Replace with first main section based on chosen structure]

[TODO: Add content here. See examples in existing skills:
- Code samples for technical skills
- Decision trees for complex workflows
- Concrete examples with realistic user requests
- References to scripts/templates/references as needed]

## Resources

This skill includes example resource directories that demonstrate how to organize different types of bundled resources:

### scripts/
Executable code (Python/Bash/etc.) that can be run directly to perform specific operations.

**Examples from other skills:**
- PDF skill: `fill_fillable_fields.py`, `extract_form_field_info.py` - utilities for PDF manipulation
- DOCX skill: `document.py`, `utilities.py` - Python modules for document processing

**Appropriate for:** Python scripts, shell scripts, or any executable code that performs automation, data processing, or specific operations.

**Note:** Scripts may be executed without loading into context, but can still be read by Claude for patching or environment adjustments.

### references/
Documentation and reference material intended to be loaded into context to inform Claude's process and thinking.

**Examples from other skills:**
- Product management: `communication.md`, `context_building.md` - detailed workflow guides
- BigQuery: API reference documentation and query examples
- Finance: Schema documentation, company policies

**Appropriate for:** In-depth documentation, API references, database schemas, comprehensive guides, or any detailed information that Claude should reference while working.

### assets/
Files not intended to be loaded into context, but rather used within output Claude produces.

**Examples from other skills:**
- Brand styling: PowerPoint template files (.pptx), logo files
- Frontend builder: HTML/React boilerplate project directories
- Typography: Font files (.ttf, .woff2)

**Appropriate for:** Templates, boilerplate code, document templates, images, icons, fonts, or any files meant to be copied or used in the final output.

## System Requirements

[TODO: List any external tools or system packages required for this skill.
Examples:
- `pandoc` (for document conversion)
- `ffmpeg` (for media processing)
- `node` (for JS runtime)
]

## Internationalization (I18n)

[TODO: If this skill involves text processing or file generation, consider internationalization support:
- Does it handle non-ASCII characters (e.g., Chinese, Japanese, Emoji)?
- Are file operations explicitly using `encoding='utf-8'`?
- Do external tools require font configuration (e.g., Pandoc CJK fonts)?
]

---
**Any unneeded directories can be deleted.** Not every skill requires all three types of resources.
"""

EXAMPLE_SCRIPT = """#!/usr/bin/env python3
"""
Example helper script for {skill_name}

This is a placeholder script that can be executed directly.
Replace with actual implementation or delete if not needed.

Example real scripts from other skills:
- pdf/scripts/fill_fillable_fields.py - Fills PDF form fields
- pdf/scripts/convert_pdf_to_images.py - Converts PDF pages to images
"""

def main():
    print(f"Running {{Path(__file__).name}}...")
    print(f"Assets directory: {{assets_dir}}")
    
    # TODO: Add actual script logic here
    # This could be data processing, file conversion, API calls, etc.

if __name__ == "__main__":
    main()
"""

EXAMPLE_REFERENCE = """# Reference Documentation for {skill_title}

This is a placeholder for detailed reference documentation.
Replace with actual reference content or delete if not needed.

Example real reference docs from other skills:
- product-management/references/communication.md - Comprehensive guide for status updates
- product-management/references/context_building.md - Deep-dive on gathering context
- bigquery/references/ - API references and query examples

## When Reference Docs Are Useful

Reference docs are ideal for:
- Comprehensive API documentation
- Detailed workflow guides
- Complex multi-step processes
- Information too lengthy for main SKILL.md
- Content that's only needed for specific use cases

## Structure Suggestions

### API Reference Example
- Overview
- Authentication
- Endpoints with examples
- Error codes
- Rate limits

### Workflow Guide Example
- Prerequisites
- Step-by-step instructions
- Common patterns
- Troubleshooting
- Best practices
"""

EXAMPLE_ASSET = """# Example Asset File

This placeholder represents where asset files would be stored.
Replace with actual asset files (templates, images, fonts, etc.) or delete if not needed.

Asset files are NOT intended to be loaded into context, but rather used within
the output Claude produces.

Example asset files from other skills:
- Brand guidelines: logo.png, slides_template.pptx
- Frontend builder: hello-world/ directory with HTML/React boilerplate
- Typography: custom-font.ttf, font-family.woff2
- Data: sample_data.csv, test_dataset.json

## Common Asset Types

- Templates: .pptx, .docx, boilerplate directories
- Images: .png, .jpg, .svg, .gif
- Fonts: .ttf, .otf, .woff, .woff2
- Boilerplate code: Project directories, starter files
- Icons: .ico, .svg
- Data files: .csv, .json, .xml, .yaml

Note: This is a text placeholder. Actual assets can be any file type.
"""

EXAMPLE_REQUIREMENTS = """# Dependencies for {skill_name}
# Add your Python dependencies here (one per line)
# Example:
# requests>=2.25.0
# pandas>=1.2.0
"""

def title_case_skill_name(skill_name):
    """Convert hyphenated skill name to Title Case for display."""
    return ' '.join(word.capitalize() for word in skill_name.split('-'))

def update_registry(dest_root, skill_name):
    """Update the skills.json registry file with new skill."""
    registry_path = dest_root / 'skills.json'
    registry = {'skills': {}}
    
    if registry_path.exists():
        try:
            content = registry_path.read_text(encoding='utf-8')
            registry = json.loads(content)
        except Exception as e:
            print(f"Warning: Could not read skills.json: {e}")
    
    registry['skills'][skill_name] = {
        'source': 'local',
        'subdir': '',
        'version': 'unknown',
        'updated_at': datetime.datetime.now().isoformat()
    }
    
    try:
        registry_path.write_text(json.dumps(registry, indent=2), encoding='utf-8')
        print(f"Updated skills.json with '{skill_name}'")
    except Exception as e:
        print(f"Warning: Could not update skills.json: {e}")

def update_skill_map(dest_root, skill_name, skill_dir):
    """Update the skill_map.json file with new skill metadata."""
    skill_map_path = dest_root / 'skill_map.json'
    skill_map = {'skills': {}, 'detection_rules': {'priority_order': [], 'exact_match': {}, 'partial_match': {}}}
    
    if skill_map_path.exists():
        try:
            content = skill_map_path.read_text(encoding='utf-8')
            skill_map = json.loads(content)
        except Exception as e:
            print(f"Warning: Could not read skill_map.json: {e}")
    
    skill_map['skills'][skill_name] = {
        'name': skill_name,
        'description': f"TODO: Add description for {skill_name}",
        'keywords': [skill_name.replace('-', ' ')],
        'aliases': [skill_name]
    }
    
    if skill_name not in skill_map['detection_rules']['priority_order']:
        skill_map['detection_rules']['priority_order'].append(skill_name)
    
    skill_name_lower = skill_name.lower().replace('-', ' ')
    skill_map['detection_rules']['exact_match'][skill_name_lower] = skill_name
    
    try:
        skill_map_path.write_text(json.dumps(skill_map, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"Updated skill_map.json with '{skill_name}'")
    except Exception as e:
        print(f"Warning: Could not update skill_map.json: {e}")

def init_skill(skill_name, path):
    """
    Initialize a new skill directory with template SKILL.md.

    Args:
        skill_name: Name of the skill
        path: Path where the skill directory should be created

    Returns:
        Path to created skill directory, or None if error
    """
    # Determine skill directory path
    skill_dir = Path(path).resolve() / skill_name

    # Check if directory already exists
    if skill_dir.exists():
        print(MSG_DIR_EXISTS.format(skill_dir=skill_dir))
        return None

    # Create skill directory
    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        print(MSG_DIR_CREATED.format(skill_dir=skill_dir))
    except Exception as e:
        print(MSG_DIR_CREATE_ERROR.format(e=e))
        return None

    # Create SKILL.md from template
    skill_title = title_case_skill_name(skill_name)
    skill_content = SKILL_TEMPLATE.format(
        skill_name=skill_name,
        skill_title=skill_title
    )

    skill_md_path = skill_dir / 'SKILL.md'
    try:
        skill_md_path.write_text(skill_content, encoding='utf-8')
        print(MSG_SKILL_MD_CREATED)
    except Exception as e:
        print(MSG_SKILL_MD_ERROR.format(e=e))
        return None

    # Create resource directories with example files
    try:
        # Create scripts/ directory with example script
        scripts_dir = skill_dir / 'scripts'
        scripts_dir.mkdir(exist_ok=True)
        example_script = scripts_dir / 'example.py'
        example_script.write_text(EXAMPLE_SCRIPT.format(skill_name=skill_name), encoding='utf-8')
        if os.name != 'nt':
            example_script.chmod(0o755)
        print(MSG_SCRIPT_CREATED)

        # Create scripts/requirements.txt
        requirements_file = scripts_dir / 'requirements.txt'
        requirements_file.write_text(EXAMPLE_REQUIREMENTS.format(skill_name=skill_name), encoding='utf-8')
        print(MSG_REQUIREMENTS_CREATED)

        # Create references/ directory with example reference doc
        references_dir = skill_dir / 'references'
        references_dir.mkdir(exist_ok=True)
        example_reference = references_dir / 'api_reference.md'
        example_reference.write_text(EXAMPLE_REFERENCE.format(skill_title=skill_title), encoding='utf-8')
        print(MSG_REFERENCE_CREATED)

        # Create assets/ directory with example asset placeholder
        assets_dir = skill_dir / 'assets'
        assets_dir.mkdir(exist_ok=True)
        example_asset = assets_dir / 'example_asset.txt'
        example_asset.write_text(EXAMPLE_ASSET, encoding='utf-8')
        print(MSG_ASSET_CREATED)
    except Exception as e:
        print(MSG_RESOURCE_ERROR.format(e=e))
        return None

    # Update skills.json and skill_map.json
    dest_root = Path(path).resolve()
    update_registry(dest_root, skill_name)
    update_skill_map(dest_root, skill_name, skill_dir)

    # Print next steps
    print(MSG_INIT_SUCCESS.format(skill_name=skill_name, skill_dir=skill_dir))
    print(MSG_NEXT_STEPS)
    print(MSG_STEP_1)
    print(MSG_STEP_2)
    print(MSG_STEP_3)

    return skill_dir

def main():
    if len(sys.argv) < 4 or sys.argv[2] != '--path':
        print(MSG_USAGE)
        print(MSG_SKILL_NAME_REQ)
        print(MSG_REQ_HYPHEN)
        print(MSG_REQ_LOWERCASE)
        print(MSG_REQ_MAX_CHARS)
        print(MSG_REQ_MATCH)
        print(MSG_EXAMPLES)
        print(MSG_EXAMPLE_1)
        print(MSG_EXAMPLE_2)
        print(MSG_EXAMPLE_3)
        sys.exit(1)

    skill_name = sys.argv[1]
    path = sys.argv[3]

    print(MSG_INITIALIZING.format(skill_name=skill_name))
    print(MSG_LOCATION.format(path=path))
    print()

    result = init_skill(skill_name, path)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
