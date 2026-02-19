#!/usr/bin/env python3
"""
Unit tests for skill_catalog.py
Tests catalog loading, querying, and management functions.
"""

import pytest
import json
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

import skill_catalog


@pytest.fixture
def valid_catalog_file():
    """Create a temporary valid catalog file for testing."""
    catalog_data = {
        "version": "1.0",
        "categories": {
            "core": {
                "description": "Core skills for the system",
                "skills": [
                    {
                        "name": "find-skills",
                        "description": "Find and search for available skills",
                        "source": "https://github.com/example/find-skills",
                        "license": "MIT",
                        "aliases": ["find", "search"],
                        "dependencies": []
                    },
                    {
                        "name": "skill-installer",
                        "description": "Install skills from remote repositories",
                        "source": "https://github.com/example/skill-installer",
                        "license": "MIT",
                        "aliases": ["install"],
                        "dependencies": []
                    }
                ]
            },
            "experimental": {
                "description": "Experimental features under development",
                "skills": [
                    {
                        "name": "create-plan",
                        "description": "Create execution plans for complex tasks",
                        "source": "https://github.com/example/create-plan",
                        "license": "Apache-2.0",
                        "aliases": ["plan"],
                        "dependencies": ["find-skills"]
                    }
                ]
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(catalog_data, f, indent=2)
        temp_path = Path(f.name)
    
    yield temp_path
    
    temp_path.unlink()


@pytest.fixture
def invalid_catalog_file():
    """Create a temporary invalid catalog file for testing."""
    catalog_data = {
        "version": "2.0",
        "categories": {}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(catalog_data, f, indent=2)
        temp_path = Path(f.name)
    
    yield temp_path
    
    temp_path.unlink()


@pytest.fixture
def malformed_catalog_file():
    """Create a temporary malformed JSON file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        f.write('{"version": "1.0", "categories": {')
        temp_path = Path(f.name)
    
    yield temp_path
    
    temp_path.unlink()


def test_load_catalog(valid_catalog_file):
    """Test loading a valid catalog file."""
    catalog = skill_catalog.load_catalog(valid_catalog_file)
    
    assert catalog is not None
    assert catalog['version'] == '1.0'
    assert 'categories' in catalog
    assert 'core' in catalog['categories']
    assert 'experimental' in catalog['categories']


def test_load_invalid_catalog(invalid_catalog_file):
    """Test loading an invalid catalog file (wrong version)."""
    with pytest.raises(skill_catalog.CatalogValidationError) as exc_info:
        skill_catalog.load_catalog(invalid_catalog_file)
    
    assert 'Unsupported catalog version' in str(exc_info.value)


def test_load_malformed_catalog(malformed_catalog_file):
    """Test loading a malformed JSON catalog file."""
    with pytest.raises(skill_catalog.CatalogValidationError) as exc_info:
        skill_catalog.load_catalog(malformed_catalog_file)
    
    assert 'Invalid JSON' in str(exc_info.value)


def test_load_nonexistent_catalog():
    """Test loading a catalog file that doesn't exist."""
    with pytest.raises(skill_catalog.CatalogNotFoundError) as exc_info:
        skill_catalog.load_catalog(Path('/nonexistent/catalog.json'))
    
    assert 'not found' in str(exc_info.value)


def test_get_skill(valid_catalog_file):
    """Test getting a skill by name."""
    skill = skill_catalog.get_skill('find-skills', valid_catalog_file)
    
    assert skill is not None
    assert skill['name'] == 'find-skills'
    assert skill['description'] == 'Find and search for available skills'
    assert skill['license'] == 'MIT'


def test_get_skill_not_found(valid_catalog_file):
    """Test getting a skill that doesn't exist."""
    skill = skill_catalog.get_skill('nonexistent-skill', valid_catalog_file)
    
    assert skill is None


def test_get_skill_with_category(valid_catalog_file):
    """Test getting a skill with category prefix."""
    skill = skill_catalog.get_skill('experimental/create-plan', valid_catalog_file)
    
    assert skill is not None
    assert skill['name'] == 'create-plan'
    assert skill['description'] == 'Create execution plans for complex tasks'


def test_get_skill_with_invalid_category(valid_catalog_file):
    """Test getting a skill with invalid category prefix."""
    skill = skill_catalog.get_skill('nonexistent/find-skills', valid_catalog_file)
    
    assert skill is None


def test_resolve_alias(valid_catalog_file):
    """Test resolving an alias to skill name."""
    resolved = skill_catalog.resolve_alias('find', valid_catalog_file)
    
    assert resolved == 'find-skills'
    
    resolved = skill_catalog.resolve_alias('search', valid_catalog_file)
    
    assert resolved == 'find-skills'


def test_resolve_alias_not_found(valid_catalog_file):
    """Test resolving an alias that doesn't exist."""
    resolved = skill_catalog.resolve_alias('nonexistent-alias', valid_catalog_file)
    
    assert resolved is None


def test_resolve_alias_direct_name(valid_catalog_file):
    """Test resolving a direct skill name (not an alias)."""
    resolved = skill_catalog.resolve_alias('find-skills', valid_catalog_file)
    
    assert resolved == 'find-skills'


def test_list_categories(valid_catalog_file):
    """Test listing all categories."""
    categories = skill_catalog.list_categories(valid_catalog_file)
    
    assert len(categories) == 2
    
    category_names = [cat['name'] for cat in categories]
    assert 'core' in category_names
    assert 'experimental' in category_names
    
    core_category = next(cat for cat in categories if cat['name'] == 'core')
    assert core_category['description'] == 'Core skills for the system'


def test_list_skills_all(valid_catalog_file):
    """Test listing all skills."""
    skills = skill_catalog.list_skills(catalog_path=valid_catalog_file)
    
    assert len(skills) == 3
    
    skill_names = [skill['name'] for skill in skills]
    assert 'find-skills' in skill_names
    assert 'skill-installer' in skill_names
    assert 'create-plan' in skill_names


def test_list_skills_by_category(valid_catalog_file):
    """Test listing skills filtered by category."""
    skills = skill_catalog.list_skills(category='core', catalog_path=valid_catalog_file)
    
    assert len(skills) == 2
    
    skill_names = [skill['name'] for skill in skills]
    assert 'find-skills' in skill_names
    assert 'skill-installer' in skill_names


def test_list_skills_invalid_category(valid_catalog_file):
    """Test listing skills with invalid category."""
    skills = skill_catalog.list_skills(category='nonexistent', catalog_path=valid_catalog_file)
    
    assert skills == []


def test_search_skills_by_name(valid_catalog_file):
    """Test searching skills by name."""
    results = skill_catalog.search_skills('find', valid_catalog_file)
    
    assert len(results) == 1
    assert results[0]['name'] == 'find-skills'


def test_search_skills_by_description(valid_catalog_file):
    """Test searching skills by description."""
    results = skill_catalog.search_skills('execution', valid_catalog_file)
    
    assert len(results) == 1
    assert results[0]['name'] == 'create-plan'


def test_search_skills_by_alias(valid_catalog_file):
    """Test searching skills by alias."""
    results = skill_catalog.search_skills('install', valid_catalog_file)
    
    assert len(results) == 1
    assert results[0]['name'] == 'skill-installer'


def test_search_skills_fuzzy(valid_catalog_file):
    """Test fuzzy search skills."""
    results = skill_catalog.search_skills('skill', valid_catalog_file)
    
    assert len(results) == 2
    
    results = skill_catalog.search_skills('plan', valid_catalog_file)
    
    assert len(results) == 1
    assert results[0]['name'] == 'create-plan'


def test_search_skills_case_insensitive(valid_catalog_file):
    """Test that search is case insensitive."""
    results_lower = skill_catalog.search_skills('find', valid_catalog_file)
    results_upper = skill_catalog.search_skills('FIND', valid_catalog_file)
    results_mixed = skill_catalog.search_skills('FiNd', valid_catalog_file)
    
    assert len(results_lower) == len(results_upper) == len(results_mixed) == 1
    assert results_lower[0]['name'] == results_upper[0]['name'] == results_mixed[0]['name']


def test_search_skills_no_results(valid_catalog_file):
    """Test searching with no matching results."""
    results = skill_catalog.search_skills('nonexistent-term', valid_catalog_file)
    
    assert results == []


def test_get_skill_dependencies(valid_catalog_file):
    """Test getting dependencies for a skill."""
    deps = skill_catalog.get_skill_dependencies('create-plan', valid_catalog_file)
    
    assert len(deps) == 1
    assert 'find-skills' in deps


def test_get_skill_dependencies_none(valid_catalog_file):
    """Test getting dependencies for a skill with no dependencies."""
    deps = skill_catalog.get_skill_dependencies('find-skills', valid_catalog_file)
    
    assert deps == []


def test_get_skill_dependencies_not_found(valid_catalog_file):
    """Test getting dependencies for a skill that doesn't exist."""
    deps = skill_catalog.get_skill_dependencies('nonexistent', valid_catalog_file)
    
    assert deps == []


def test_is_skill_available(valid_catalog_file):
    """Test checking if a skill is available."""
    assert skill_catalog.is_skill_available('find-skills', valid_catalog_file) is True
    assert skill_catalog.is_skill_available('nonexistent', valid_catalog_file) is False


def test_catalog_validation_missing_version():
    """Test catalog validation with missing version field."""
    catalog_data = {
        "categories": {}
    }
    
    with pytest.raises(skill_catalog.CatalogValidationError) as exc_info:
        skill_catalog._validate_catalog(catalog_data)
    
    assert "Missing 'version' field" in str(exc_info.value)


def test_catalog_validation_missing_categories():
    """Test catalog validation with missing categories field."""
    catalog_data = {
        "version": "1.0"
    }
    
    with pytest.raises(skill_catalog.CatalogValidationError) as exc_info:
        skill_catalog._validate_catalog(catalog_data)
    
    assert "Missing 'categories' field" in str(exc_info.value)


def test_catalog_validation_invalid_categories_type():
    """Test catalog validation with invalid categories type."""
    catalog_data = {
        "version": "1.0",
        "categories": []
    }
    
    with pytest.raises(skill_catalog.CatalogValidationError) as exc_info:
        skill_catalog._validate_catalog(catalog_data)
    
    assert "'categories' must be a dictionary" in str(exc_info.value)


def test_skill_validation_missing_required_field():
    """Test skill validation with missing required field."""
    skill_data = {
        "name": "test-skill",
        "description": "Test description",
        "source": "https://github.com/example/test"
    }
    
    with pytest.raises(skill_catalog.CatalogValidationError) as exc_info:
        skill_catalog._validate_skill(skill_data, "test-category")
    
    assert "Missing required field 'license'" in str(exc_info.value)


def test_skill_validation_invalid_name():
    """Test skill validation with invalid name."""
    skill_data = {
        "name": "",
        "description": "Test description",
        "source": "https://github.com/example/test",
        "license": "MIT"
    }
    
    with pytest.raises(skill_catalog.CatalogValidationError) as exc_info:
        skill_catalog._validate_skill(skill_data, "test-category")
    
    assert "Invalid 'name' field" in str(exc_info.value)


def test_skill_validation_invalid_aliases_type():
    """Test skill validation with invalid aliases type."""
    skill_data = {
        "name": "test-skill",
        "description": "Test description",
        "source": "https://github.com/example/test",
        "license": "MIT",
        "aliases": "not-a-list"
    }
    
    with pytest.raises(skill_catalog.CatalogValidationError) as exc_info:
        skill_catalog._validate_skill(skill_data, "test-category")
    
    assert "Invalid 'aliases' field" in str(exc_info.value)
