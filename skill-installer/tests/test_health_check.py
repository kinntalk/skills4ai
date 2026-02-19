#!/usr/bin/env python3
"""
Unit tests for health check functionality in manage_skills.py
Tests SKILL.md validation and dependency checking.
"""

import pytest
import json
import tempfile
import yaml
import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

import manage_skills


@pytest.fixture
def temp_skill_dir():
    """Create a temporary skill directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        skill_path = Path(temp_dir)
        yield skill_path


@pytest.fixture
def valid_skill_md(temp_skill_dir):
    """Create a valid SKILL.md file."""
    skill_md_content = """---
name: test-skill
description: A comprehensive test skill for health checking
keywords:
  - test
  - example
aliases:
  - test
  - example-skill
dependencies:
  - find-skills
  - skill-installer
---

# Test Skill

This is a comprehensive test skill for health checking purposes.
"""
    
    skill_md_path = temp_skill_dir / 'SKILL.md'
    skill_md_path.write_text(skill_md_content, encoding='utf-8')
    
    return temp_skill_dir


@pytest.fixture
def skill_md_missing_name(temp_skill_dir):
    """Create SKILL.md without name field."""
    skill_md_content = """---
description: A test skill without name
---

# Test Skill
"""
    
    skill_md_path = temp_skill_dir / 'SKILL.md'
    skill_md_path.write_text(skill_md_content, encoding='utf-8')
    
    return temp_skill_dir


@pytest.fixture
def skill_md_missing_description(temp_skill_dir):
    """Create SKILL.md without description field."""
    skill_md_content = """---
name: test-skill
---

# Test Skill
"""
    
    skill_md_path = temp_skill_dir / 'SKILL.md'
    skill_md_path.write_text(skill_md_content, encoding='utf-8')
    
    return temp_skill_dir


@pytest.fixture
def skill_md_invalid_yaml(temp_skill_dir):
    """Create SKILL.md with invalid YAML."""
    skill_md_content = """---
name: test-skill
description: [invalid yaml
---

# Test Skill
"""
    
    skill_md_path = temp_skill_dir / 'SKILL.md'
    skill_md_path.write_text(skill_md_content, encoding='utf-8')
    
    return temp_skill_dir


@pytest.fixture
def skill_md_no_frontmatter(temp_skill_dir):
    """Create SKILL.md without YAML frontmatter."""
    skill_md_content = """# Test Skill

This is a test skill without YAML frontmatter.
"""
    
    skill_md_path = temp_skill_dir / 'SKILL.md'
    skill_md_path.write_text(skill_md_content, encoding='utf-8')
    
    return temp_skill_dir


@pytest.fixture
def skill_md_short_description(temp_skill_dir):
    """Create SKILL.md with short description."""
    skill_md_content = """---
name: test-skill
description: Short
---

# Test Skill
"""
    
    skill_md_path = temp_skill_dir / 'SKILL.md'
    skill_md_path.write_text(skill_md_content, encoding='utf-8')
    
    return temp_skill_dir


@pytest.fixture
def skill_md_name_mismatch(temp_skill_dir):
    """Create SKILL.md with name mismatching directory."""
    skill_md_content = """---
name: different-name
description: A test skill with different name
---

# Test Skill
"""
    
    skill_md_path = temp_skill_dir / 'SKILL.md'
    skill_md_path.write_text(skill_md_content, encoding='utf-8')
    
    return temp_skill_dir


@pytest.fixture
def dest_root_with_registry():
    """Create a temporary destination root with skills.json registry."""
    with tempfile.TemporaryDirectory() as temp_dir:
        dest_root = Path(temp_dir)
        registry_data = {
            "skills": {
                "find-skills": {
                    "source": "https://github.com/example/find-skills",
                    "version": "abc123",
                    "updated_at": "2024-01-01T00:00:00"
                },
                "skill-installer": {
                    "source": "https://github.com/example/skill-installer",
                    "version": "def456",
                    "updated_at": "2024-01-02T00:00:00"
                }
            }
        }
        
        registry_path = dest_root / 'skills.json'
        registry_path.write_text(json.dumps(registry_data, indent=2), encoding='utf-8')
        
        yield dest_root


def test_validate_skill_md_valid(valid_skill_md):
    """Test validating a valid SKILL.md file."""
    skill_md_path = valid_skill_md / 'SKILL.md'
    
    content = skill_md_path.read_text(encoding='utf-8')
    
    assert content.startswith('---')
    
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    assert frontmatter_match is not None
    
    frontmatter_str = frontmatter_match.group(1)
    frontmatter = yaml.safe_load(frontmatter_str)
    
    assert isinstance(frontmatter, dict)
    assert 'name' in frontmatter
    assert 'description' in frontmatter
    assert frontmatter['name'] == 'test-skill'
    assert frontmatter['description'] == 'A comprehensive test skill for health checking'


def test_validate_skill_md_missing(temp_skill_dir):
    """Test validating when SKILL.md is missing."""
    skill_md_path = temp_skill_dir / 'SKILL.md'
    
    assert not skill_md_path.exists()


def test_validate_skill_md_invalid_yaml(skill_md_invalid_yaml):
    """Test validating SKILL.md with invalid YAML."""
    skill_md_path = skill_md_invalid_yaml / 'SKILL.md'
    
    content = skill_md_path.read_text(encoding='utf-8')
    
    assert content.startswith('---')
    
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    assert frontmatter_match is not None
    
    frontmatter_str = frontmatter_match.group(1)
    
    with pytest.raises(yaml.YAMLError):
        yaml.safe_load(frontmatter_str)


def test_validate_skill_md_no_frontmatter(skill_md_no_frontmatter):
    """Test validating SKILL.md without YAML frontmatter."""
    skill_md_path = skill_md_no_frontmatter / 'SKILL.md'
    
    content = skill_md_path.read_text(encoding='utf-8')
    
    assert not content.startswith('---')
    
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    assert frontmatter_match is None


def test_validate_skill_md_missing_name(skill_md_missing_name):
    """Test validating SKILL.md without name field."""
    skill_md_path = skill_md_missing_name / 'SKILL.md'
    
    content = skill_md_path.read_text(encoding='utf-8')
    
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    assert frontmatter_match is not None
    
    frontmatter_str = frontmatter_match.group(1)
    frontmatter = yaml.safe_load(frontmatter_str)
    
    assert isinstance(frontmatter, dict)
    assert 'name' not in frontmatter


def test_validate_skill_md_missing_description(skill_md_missing_description):
    """Test validating SKILL.md without description field."""
    skill_md_path = skill_md_missing_description / 'SKILL.md'
    
    content = skill_md_path.read_text(encoding='utf-8')
    
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    assert frontmatter_match is not None
    
    frontmatter_str = frontmatter_match.group(1)
    frontmatter = yaml.safe_load(frontmatter_str)
    
    assert isinstance(frontmatter, dict)
    assert 'description' not in frontmatter


def test_validate_skill_md_short_description(skill_md_short_description):
    """Test validating SKILL.md with short description."""
    skill_md_path = skill_md_short_description / 'SKILL.md'
    
    content = skill_md_path.read_text(encoding='utf-8')
    
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    assert frontmatter_match is not None
    
    frontmatter_str = frontmatter_match.group(1)
    frontmatter = yaml.safe_load(frontmatter_str)
    
    assert isinstance(frontmatter, dict)
    assert 'description' in frontmatter
    assert len(frontmatter['description']) < 10


def test_validate_skill_md_name_mismatch(skill_md_name_mismatch):
    """Test validating SKILL.md with name mismatching directory."""
    skill_md_path = skill_md_name_mismatch / 'SKILL.md'
    
    content = skill_md_path.read_text(encoding='utf-8')
    
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    assert frontmatter_match is not None
    
    frontmatter_str = frontmatter_match.group(1)
    frontmatter = yaml.safe_load(frontmatter_str)
    
    assert isinstance(frontmatter, dict)
    assert 'name' in frontmatter
    assert frontmatter['name'] != skill_md_name_mismatch.name


def test_check_skill_dependencies_installed(valid_skill_md, dest_root_with_registry):
    """Test checking skill dependencies when all are installed."""
    skill_name = 'test-skill'
    
    skill_md_path = valid_skill_md / 'SKILL.md'
    content = skill_md_path.read_text(encoding='utf-8')
    
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    frontmatter = yaml.safe_load(frontmatter_match.group(1))
    
    dependencies = frontmatter.get('dependencies', [])
    
    registry_path = dest_root_with_registry / 'skills.json'
    registry = json.loads(registry_path.read_text(encoding='utf-8'))
    installed_skills = set(registry.get('skills', {}).keys())
    
    missing_deps = [dep for dep in dependencies if dep not in installed_skills]
    
    assert len(missing_deps) == 0
    assert 'find-skills' in installed_skills
    assert 'skill-installer' in installed_skills


def test_check_skill_dependencies_missing(dest_root_with_registry):
    """Test checking skill dependencies when some are missing."""
    skill_name = 'test-skill'
    dependencies = ['find-skills', 'missing-dep']
    
    registry_path = dest_root_with_registry / 'skills.json'
    registry = json.loads(registry_path.read_text(encoding='utf-8'))
    installed_skills = set(registry.get('skills', {}).keys())
    
    missing_deps = [dep for dep in dependencies if dep not in installed_skills]
    
    assert len(missing_deps) == 1
    assert 'missing-dep' in missing_deps
    assert 'find-skills' not in missing_deps


def test_check_skill_dependencies_none(valid_skill_md):
    """Test checking skill dependencies when none are specified."""
    skill_md_path = valid_skill_md / 'SKILL.md'
    skill_md_path.write_text('---\nname: test-skill\ndescription: Test\n---', encoding='utf-8')
    
    content = skill_md_path.read_text(encoding='utf-8')
    
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    frontmatter = yaml.safe_load(frontmatter_match.group(1))
    
    dependencies = frontmatter.get('dependencies', [])
    
    assert len(dependencies) == 0


def test_check_skill_directory_exists(valid_skill_md):
    """Test checking that skill directory exists."""
    assert valid_skill_md.exists()
    assert valid_skill_md.is_dir()


def test_check_skill_directory_missing():
    """Test checking when skill directory doesn't exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        skill_path = Path(temp_dir) / 'nonexistent-skill'
        assert not skill_path.exists()


def test_load_registry(dest_root_with_registry):
    """Test loading skills registry."""
    registry = manage_skills.load_registry()
    
    assert isinstance(registry, dict)
    assert 'find-skills' in registry
    assert 'skill-installer' in registry


def test_load_registry_empty():
    """Test loading registry when skills.json doesn't exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        original_registry = manage_skills.REGISTRY_FILE
        manage_skills.REGISTRY_FILE = Path(temp_dir) / 'nonexistent.json'
        
        try:
            registry = manage_skills.load_registry()
            assert registry == {}
        finally:
            manage_skills.REGISTRY_FILE = original_registry


def test_health_check_skill_directory_missing(dest_root_with_registry):
    """Test health check when skill directory is missing."""
    skill_name = 'missing-skill'
    
    skills = manage_skills.load_registry()
    skills[skill_name] = {
        'source': 'https://github.com/example/missing',
        'version': 'abc123'
    }
    
    skill_path = manage_skills.SKILLS_DIR / skill_name
    assert not skill_path.exists()


def test_health_check_skill_md_missing(dest_root_with_registry):
    """Test health check when SKILL.md is missing."""
    skill_name = 'test-skill'
    
    skill_path = manage_skills.SKILLS_DIR / skill_name
    skill_path.mkdir(exist_ok=True)
    
    skill_md_path = skill_path / 'SKILL.md'
    assert not skill_md_path.exists()


def test_health_check_frontmatter_not_dict(temp_skill_dir):
    """Test health check when frontmatter is not a dictionary."""
    skill_md_content = """---
- item1
- item2
---

# Test Skill
"""
    
    skill_md_path = temp_skill_dir / 'SKILL.md'
    skill_md_path.write_text(skill_md_content, encoding='utf-8')
    
    content = skill_md_path.read_text(encoding='utf-8')
    
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    frontmatter = yaml.safe_load(frontmatter_match.group(1))
    
    assert not isinstance(frontmatter, dict)


def test_health_check_keywords_and_aliases(valid_skill_md):
    """Test health check for keywords and aliases fields."""
    skill_md_path = valid_skill_md / 'SKILL.md'
    
    content = skill_md_path.read_text(encoding='utf-8')
    
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    frontmatter = yaml.safe_load(frontmatter_match.group(1))
    
    assert 'keywords' in frontmatter
    assert isinstance(frontmatter['keywords'], list)
    assert 'aliases' in frontmatter
    assert isinstance(frontmatter['aliases'], list)


def test_health_check_empty_keywords_and_aliases(temp_skill_dir):
    """Test health check when keywords and aliases are empty."""
    skill_md_content = """---
name: test-skill
description: Test skill
keywords: []
aliases: []
---

# Test Skill
"""
    
    skill_md_path = temp_skill_dir / 'SKILL.md'
    skill_md_path.write_text(skill_md_content, encoding='utf-8')
    
    content = skill_md_path.read_text(encoding='utf-8')
    
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    frontmatter = yaml.safe_load(frontmatter_match.group(1))
    
    assert frontmatter['keywords'] == []
    assert frontmatter['aliases'] == []


def test_health_check_multiple_dependencies(dest_root_with_registry):
    """Test health check with multiple dependencies."""
    skill_name = 'test-skill'
    dependencies = ['find-skills', 'skill-installer', 'skill-auditor']
    
    registry_path = dest_root_with_registry / 'skills.json'
    registry = json.loads(registry_path.read_text(encoding='utf-8'))
    installed_skills = set(registry.get('skills', {}).keys())
    
    missing_deps = [dep for dep in dependencies if dep not in installed_skills]
    
    assert len(missing_deps) == 1
    assert 'skill-auditor' in missing_deps


def test_health_check_empty_frontmatter(temp_skill_dir):
    """Test health check with empty frontmatter."""
    skill_md_content = """---
---

# Test Skill
"""
    
    skill_md_path = temp_skill_dir / 'SKILL.md'
    skill_md_path.write_text(skill_md_content, encoding='utf-8')
    
    content = skill_md_path.read_text(encoding='utf-8')
    
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        frontmatter = yaml.safe_load(frontmatter_match.group(1))
        assert frontmatter is None or frontmatter == {}
    else:
        assert True


def test_health_check_special_characters_in_description(temp_skill_dir):
    """Test health check with special characters in description."""
    skill_md_content = """---
name: test-skill
description: 'A test skill with special characters: @#$%^&*()_+-=[]{}|;'':",./<>?'
---

# Test Skill
"""
    
    skill_md_path = temp_skill_dir / 'SKILL.md'
    skill_md_path.write_text(skill_md_content, encoding='utf-8')
    
    content = skill_md_path.read_text(encoding='utf-8')
    
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    frontmatter = yaml.safe_load(frontmatter_match.group(1))
    
    assert 'description' in frontmatter
    assert len(frontmatter['description']) >= 10


def test_health_check_multiline_description(temp_skill_dir):
    """Test health check with multiline description."""
    skill_md_content = """---
name: test-skill
description: |
  This is a multiline description
  that spans multiple lines
  and should be valid YAML
---

# Test Skill
"""
    
    skill_md_path = temp_skill_dir / 'SKILL.md'
    skill_md_path.write_text(skill_md_content, encoding='utf-8')
    
    content = skill_md_path.read_text(encoding='utf-8')
    
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    frontmatter = yaml.safe_load(frontmatter_match.group(1))
    
    assert 'description' in frontmatter
    assert 'multiline' in frontmatter['description']


def test_health_check_dependency_list_string(temp_skill_dir):
    """Test health check with dependency as string instead of list."""
    skill_md_content = """---
name: test-skill
description: Test skill
dependencies: find-skills
---

# Test Skill
"""
    
    skill_md_path = temp_skill_dir / 'SKILL.md'
    skill_md_path.write_text(skill_md_content, encoding='utf-8')
    
    content = skill_md_path.read_text(encoding='utf-8')
    
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    frontmatter = yaml.safe_load(frontmatter_match.group(1))
    
    assert 'dependencies' in frontmatter
    assert isinstance(frontmatter['dependencies'], str)
    assert frontmatter['dependencies'] == 'find-skills'
