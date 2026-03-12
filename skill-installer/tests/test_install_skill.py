#!/usr/bin/env python3
"""
Unit tests for install_skill.py
Tests source parsing, dependency resolution, and license detection.
"""

import pytest
import json
import tempfile
import yaml
from pathlib import Path
import sys
import os

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

import install_skill


@pytest.fixture
def temp_skill_dir():
    """Create a temporary skill directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        skill_path = Path(temp_dir)
        yield skill_path


@pytest.fixture
def skill_with_dependencies(temp_skill_dir):
    """Create a skill directory with SKILL.md containing dependencies."""
    skill_md_content = """---
name: test-skill
description: A test skill with dependencies
dependencies:
  - find-skills
  - skill-installer
---
# Test Skill
This is a test skill.
"""
    
    skill_md_path = temp_skill_dir / 'SKILL.md'
    skill_md_path.write_text(skill_md_content, encoding='utf-8')
    
    return temp_skill_dir


@pytest.fixture
def skill_with_single_dependency(temp_skill_dir):
    """Create a skill directory with SKILL.md containing single dependency."""
    skill_md_content = """---
name: test-skill
description: A test skill with single dependency
dependencies: find-skills
---
# Test Skill
This is a test skill.
"""
    
    skill_md_path = temp_skill_dir / 'SKILL.md'
    skill_md_path.write_text(skill_md_content, encoding='utf-8')
    
    return temp_skill_dir


@pytest.fixture
def skill_without_dependencies(temp_skill_dir):
    """Create a skill directory with SKILL.md without dependencies."""
    skill_md_content = """---
name: test-skill
description: A test skill without dependencies
---
# Test Skill
This is a test skill.
"""
    
    skill_md_path = temp_skill_dir / 'SKILL.md'
    skill_md_path.write_text(skill_md_content, encoding='utf-8')
    
    return temp_skill_dir


@pytest.fixture
def skill_without_skill_md(temp_skill_dir):
    """Create a skill directory without SKILL.md."""
    return temp_skill_dir


@pytest.fixture
def skill_with_invalid_yaml(temp_skill_dir):
    """Create a skill directory with invalid YAML in SKILL.md."""
    skill_md_content = """---
name: test-skill
description: A test skill
dependencies: [unclosed list
---
# Test Skill
"""
    
    skill_md_path = temp_skill_dir / 'SKILL.md'
    skill_md_path.write_text(skill_md_content, encoding='utf-8')
    
    return temp_skill_dir


@pytest.fixture
def skill_with_mit_license(temp_skill_dir):
    """Create a skill directory with MIT license."""
    license_content = """MIT License

Copyright (c) 2024 Example Author

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
"""
    
    license_path = temp_skill_dir / 'LICENSE'
    license_path.write_text(license_content, encoding='utf-8')
    
    return temp_skill_dir


@pytest.fixture
def skill_with_apache_license(temp_skill_dir):
    """Create a skill directory with Apache-2.0 license."""
    license_content = """Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
    
    license_path = temp_skill_dir / 'LICENSE'
    license_path.write_text(license_content, encoding='utf-8')
    
    return temp_skill_dir


@pytest.fixture
def skill_with_gpl_license(temp_skill_dir):
    """Create a skill directory with GPL-3.0 license."""
    license_content = """GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""
    
    license_path = temp_skill_dir / 'LICENSE'
    license_path.write_text(license_content, encoding='utf-8')
    
    return temp_skill_dir


@pytest.fixture
def skill_with_custom_license(temp_skill_dir):
    """Create a skill directory with custom license."""
    license_content = """Custom License

This is a custom license for this project.
"""
    
    license_path = temp_skill_dir / 'LICENSE'
    license_path.write_text(license_content, encoding='utf-8')
    
    return temp_skill_dir


@pytest.fixture
def skill_without_license(temp_skill_dir):
    """Create a skill directory without license file."""
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
                    "last_update_time": "2024-01-01T00:00:00"
                },
                "skill-installer": {
                    "source": "https://github.com/example/skill-installer",
                    "version": "def456",
                    "last_update_time": "2024-01-02T00:00:00"
                }
            }
        }
        
        registry_path = dest_root / 'skills.json'
        registry_path.write_text(json.dumps(registry_data, indent=2), encoding='utf-8')
        
        yield dest_root


def test_parse_source_url():
    """Test parsing a full URL."""
    url = "https://github.com/user/repo"
    repo_url, subdir = install_skill.parse_source(url)
    
    assert repo_url == url
    assert subdir == ""


def test_parse_source_url_with_subdir():
    """Test parsing a full URL with subdirectory."""
    url = "https://github.com/user/repo/tree/main/subdir"
    repo_url, subdir = install_skill.parse_source(url)
    
    assert repo_url == "https://github.com/user/repo"
    assert subdir == "subdir"


def test_parse_source_user_repo():
    """Test parsing user/repo format."""
    source = "user/repo"
    repo_url, subdir = install_skill.parse_source(source)
    
    assert repo_url == "https://github.com/user/repo.git"
    assert subdir == ""


def test_parse_source_user_repo_subdir():
    """Test parsing user/repo/subdir format."""
    source = "user/repo/subdir"
    repo_url, subdir = install_skill.parse_source(source)
    
    assert repo_url == "https://github.com/user/repo.git"
    assert subdir == "subdir"


def test_parse_source_user_repo_nested_subdir():
    """Test parsing user/repo/subdir/nested format."""
    source = "user/repo/subdir/nested"
    repo_url, subdir = install_skill.parse_source(source)
    
    assert repo_url == "https://github.com/user/repo.git"
    assert subdir == "subdir/nested"


def test_parse_source_git_ssh():
    """Test parsing git SSH URL."""
    url = "git@github.com:user/repo.git"
    repo_url, subdir = install_skill.parse_source(url)
    
    assert repo_url == url
    assert subdir == ""


def test_parse_source_with_custom_github_url():
    """Test parsing with custom GITHUB_URL environment variable."""
    original_url = os.environ.get("GITHUB_URL")
    
    try:
        os.environ["GITHUB_URL"] = "https://custom.github.com"
        source = "user/repo"
        repo_url, subdir = install_skill.parse_source(source)
        
        assert repo_url == "https://custom.github.com/user/repo.git"
        assert subdir == ""
    finally:
        if original_url is None:
            os.environ.pop("GITHUB_URL", None)
        else:
            os.environ["GITHUB_URL"] = original_url


def test_parse_skill_dependencies(skill_with_dependencies):
    """Test parsing dependencies from SKILL.md."""
    deps = install_skill.parse_skill_dependencies(skill_with_dependencies)
    
    assert len(deps) == 2
    assert 'find-skills' in deps
    assert 'skill-installer' in deps


def test_parse_skill_dependencies_single(skill_with_single_dependency):
    """Test parsing single dependency from SKILL.md."""
    deps = install_skill.parse_skill_dependencies(skill_with_single_dependency)
    
    assert len(deps) == 1
    assert 'find-skills' in deps


def test_parse_skill_dependencies_none(skill_without_dependencies):
    """Test parsing when SKILL.md has no dependencies."""
    deps = install_skill.parse_skill_dependencies(skill_without_dependencies)
    
    assert deps == []


def test_parse_skill_dependencies_no_file(skill_without_skill_md):
    """Test parsing when SKILL.md doesn't exist."""
    deps = install_skill.parse_skill_dependencies(skill_without_skill_md)
    
    assert deps == []


def test_parse_skill_dependencies_invalid_yaml(skill_with_invalid_yaml):
    """Test parsing with invalid YAML in SKILL.md."""
    deps = install_skill.parse_skill_dependencies(skill_with_invalid_yaml)
    
    assert deps == []


def test_check_dependencies_installed(dest_root_with_registry):
    """Test checking which dependencies are installed."""
    dependencies = ['find-skills', 'skill-installer', 'nonexistent-skill']
    missing, installed = install_skill.check_dependencies_installed(
        dependencies, dest_root_with_registry
    )
    
    assert len(installed) == 2
    assert 'find-skills' in installed
    assert 'skill-installer' in installed
    
    assert len(missing) == 1
    assert 'nonexistent-skill' in missing


def test_check_dependencies_installed_all_missing(dest_root_with_registry):
    """Test checking when no dependencies are installed."""
    dependencies = ['dep1', 'dep2', 'dep3']
    missing, installed = install_skill.check_dependencies_installed(
        dependencies, dest_root_with_registry
    )
    
    assert len(installed) == 0
    assert len(missing) == 3


def test_check_dependencies_installed_all_installed(dest_root_with_registry):
    """Test checking when all dependencies are installed."""
    dependencies = ['find-skills', 'skill-installer']
    missing, installed = install_skill.check_dependencies_installed(
        dependencies, dest_root_with_registry
    )
    
    assert len(installed) == 2
    assert len(missing) == 0


def test_check_dependencies_installed_empty(dest_root_with_registry):
    """Test checking with empty dependency list."""
    dependencies = []
    missing, installed = install_skill.check_dependencies_installed(
        dependencies, dest_root_with_registry
    )
    
    assert len(installed) == 0
    assert len(missing) == 0


def test_resolve_install_order_no_dependencies(dest_root_with_registry):
    """Test resolving install order with no dependencies."""
    skill_name = 'test-skill'
    dependencies = []
    
    order = install_skill.resolve_install_order(skill_name, dependencies, dest_root_with_registry)
    
    assert order is not None
    assert len(order) == 1
    assert order[0] == skill_name


def test_resolve_install_order_simple(dest_root_with_registry):
    """Test resolving install order with simple dependencies."""
    skill_name = 'test-skill'
    dependencies = ['find-skills']
    
    order = install_skill.resolve_install_order(skill_name, dependencies, dest_root_with_registry)
    
    assert order is not None
    assert len(order) == 2
    assert skill_name in order
    assert 'find-skills' in order


def test_resolve_install_order_multiple(dest_root_with_registry):
    """Test resolving install order with multiple dependencies."""
    skill_name = 'test-skill'
    dependencies = ['find-skills', 'skill-installer']
    
    order = install_skill.resolve_install_order(skill_name, dependencies, dest_root_with_registry)
    
    assert order is not None
    assert len(order) == 3
    assert skill_name in order
    assert 'find-skills' in order
    assert 'skill-installer' in order


def test_resolve_install_order_circular(dest_root_with_registry):
    """Test detecting circular dependencies."""
    skill_name = 'skill-a'
    dependencies = ['skill-b']
    
    with tempfile.TemporaryDirectory() as temp_dir:
        dest_root = Path(temp_dir)
        
        skill_a_path = dest_root / 'skill-a'
        skill_a_path.mkdir()
        skill_a_md = skill_a_path / 'SKILL.md'
        skill_a_md.write_text('---\nname: skill-a\ndependencies:\n  - skill-b\n---', encoding='utf-8')
        
        skill_b_path = dest_root / 'skill-b'
        skill_b_path.mkdir()
        skill_b_md = skill_b_path / 'SKILL.md'
        skill_b_md.write_text('---\nname: skill-b\ndependencies:\n  - skill-a\n---', encoding='utf-8')
        
        order = install_skill.resolve_install_order(skill_name, dependencies, dest_root)
        
        assert order is None


def test_resolve_install_order_complex(dest_root_with_registry):
    """Test resolving install order with complex dependency graph."""
    skill_name = 'skill-d'
    dependencies = ['skill-a', 'skill-b', 'skill-c']
    
    with tempfile.TemporaryDirectory() as temp_dir:
        dest_root = Path(temp_dir)
        
        skill_a_path = dest_root / 'skill-a'
        skill_a_path.mkdir()
        skill_a_md = skill_a_path / 'SKILL.md'
        skill_a_md.write_text('---\nname: skill-a\n---', encoding='utf-8')
        
        skill_b_path = dest_root / 'skill-b'
        skill_b_path.mkdir()
        skill_b_md = skill_b_path / 'SKILL.md'
        skill_b_md.write_text('---\nname: skill-b\ndependencies:\n  - skill-a\n---', encoding='utf-8')
        
        skill_c_path = dest_root / 'skill-c'
        skill_c_path.mkdir()
        skill_c_md = skill_c_path / 'SKILL.md'
        skill_c_md.write_text('---\nname: skill-c\ndependencies:\n  - skill-a\n  - skill-b\n---', encoding='utf-8')
        
        order = install_skill.resolve_install_order(skill_name, dependencies, dest_root)
        
        assert order is not None
        assert len(order) == 4
        assert 'skill-a' in order
        assert 'skill-b' in order
        assert 'skill-c' in order
        assert 'skill-d' in order


def test_detect_license_mit(skill_with_mit_license):
    """Test detecting MIT license."""
    license_type = install_skill.detect_license(skill_with_mit_license)
    
    assert license_type == 'MIT'


def test_detect_license_apache(skill_with_apache_license):
    """Test detecting Apache-2.0 license."""
    license_type = install_skill.detect_license(skill_with_apache_license)
    
    assert license_type == 'Apache-2.0'


def test_detect_license_gpl(skill_with_gpl_license):
    """Test detecting GPL-3.0 license."""
    license_type = install_skill.detect_license(skill_with_gpl_license)
    
    assert license_type in ['GPL', 'GPL-3.0']


def test_detect_license_custom(skill_with_custom_license):
    """Test detecting custom license."""
    license_type = install_skill.detect_license(skill_with_custom_license)
    
    assert license_type == 'Custom'


def test_detect_license_no_file(skill_without_license):
    """Test detecting license when no license file exists."""
    license_type = install_skill.detect_license(skill_without_license)
    
    assert license_type is None


def test_detect_license_alternative_filename(temp_skill_dir):
    """Test detecting license with alternative filename."""
    license_content = """MIT License

Copyright (c) 2024 Example Author
"""
    
    license_path = temp_skill_dir / 'LICENSE.txt'
    license_path.write_text(license_content, encoding='utf-8')
    
    license_type = install_skill.detect_license(temp_skill_dir)
    
    assert license_type == 'MIT'


def test_check_license_compatibility_mit():
    """Test checking MIT license compatibility."""
    status, message = install_skill.check_license_compatibility('MIT')
    
    assert status == 'compatible'
    assert message is None


def test_check_license_compatibility_apache():
    """Test checking Apache-2.0 license compatibility."""
    status, message = install_skill.check_license_compatibility('Apache-2.0')
    
    assert status == 'compatible'
    assert message is None


def test_check_license_compatibility_bsd():
    """Test checking BSD license compatibility."""
    status, message = install_skill.check_license_compatibility('BSD-3-Clause')
    
    assert status == 'compatible'
    assert message is None


def test_check_license_compatibility_gpl():
    """Test checking GPL license compatibility."""
    status, message = install_skill.check_license_compatibility('GPL-3.0')
    
    assert status == 'incompatible'
    assert message is not None
    assert 'strong copyleft' in message.lower()


def test_check_license_compatibility_lgpl():
    """Test checking LGPL license compatibility."""
    status, message = install_skill.check_license_compatibility('LGPL-3.0')
    
    assert status == 'warning'
    assert message is not None
    assert 'copyleft' in message.lower()


def test_check_license_compatibility_none():
    """Test checking when no license is found."""
    status, message = install_skill.check_license_compatibility(None)
    
    assert status == 'warning'
    assert message is not None
    assert 'unknown' in message.lower()


def test_check_license_compatibility_custom():
    """Test checking custom license compatibility."""
    status, message = install_skill.check_license_compatibility('Custom')
    
    assert status == 'warning'
    assert message is not None
    assert 'not recognized' in message.lower() or 'standard' in message.lower()


def test_set_verbose():
    """Test setting verbose mode."""
    install_skill.set_verbose(True)
    assert install_skill.verbose_mode is True
    
    install_skill.set_verbose(False)
    assert install_skill.verbose_mode is False


def test_verbose_print():
    """Test verbose print function."""
    install_skill.set_verbose(True)
    install_skill.verbose_print('git', cmd='git clone test')
    install_skill.verbose_print('file', operation='read', path='/test/file')
    install_skill.verbose_print('state', description='test state')
    install_skill.verbose_print('dep', dep='test-dep')
    
    install_skill.set_verbose(False)


def test_update_registry(dest_root_with_registry):
    """Test updating the skills.json registry."""
    install_skill.update_registry(
        dest_root_with_registry,
        'new-skill',
        'https://github.com/example/new-skill',
        'subdir',
        'abc123'
    )
    
    registry_path = dest_root_with_registry / 'skills.json'
    registry = json.loads(registry_path.read_text(encoding='utf-8'))
    
    assert 'new-skill' in registry['skills']
    assert registry['skills']['new-skill']['source'] == 'https://github.com/example/new-skill'
    assert registry['skills']['new-skill']['subdir'] == 'subdir'
    assert registry['skills']['new-skill']['version'] == 'abc123'


def test_update_skill_map(dest_root_with_registry):
    """Test updating the skill_map.json file."""
    skill_path = dest_root_with_registry / 'test-skill'
    skill_path.mkdir()
    
    skill_md = skill_path / 'SKILL.md'
    skill_md.write_text('---\nname: test-skill\ndescription: Test skill description\n---', encoding='utf-8')
    
    install_skill.update_skill_map(dest_root_with_registry, 'test-skill', skill_path)
    
    skill_map_path = dest_root_with_registry / 'skill_map.json'
    assert skill_map_path.exists()
    
    skill_map = json.loads(skill_map_path.read_text(encoding='utf-8'))
    
    assert 'test-skill' in skill_map['skills']
    assert skill_map['skills']['test-skill']['name'] == 'test-skill'
    assert skill_map['skills']['test-skill']['description'] == 'Test skill description'
