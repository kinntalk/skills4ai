#!/usr/bin/env python3
"""
Skill Catalog - Manage skill catalog with categories and metadata
Provides functions to load, query, and manage the skill catalog.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    from messages import *
except ImportError:
    try:
        sys.path.append(str(Path(__file__).parent))
        from messages import *
    except ImportError:
        COLOR_GREEN = "\033[92m"
        COLOR_RED = "\033[91m"
        COLOR_YELLOW = "\033[93m"
        COLOR_BLUE = "\033[94m"
        COLOR_RESET = "\033[0m"

CATALOG_VERSION = "1.0"
CATALOG_FILE = Path(__file__).parent.parent / 'skill_catalog.json'


class CatalogError(Exception):
    """Base exception for catalog-related errors"""
    pass


class CatalogValidationError(CatalogError):
    """Raised when catalog validation fails"""
    pass


class CatalogNotFoundError(CatalogError):
    """Raised when catalog file is not found"""
    pass


def load_catalog(catalog_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load and validate skill_catalog.json
    
    Args:
        catalog_path: Optional path to catalog file. Defaults to CATALOG_FILE
    
    Returns:
        Dictionary containing the catalog data
    
    Raises:
        CatalogNotFoundError: If catalog file doesn't exist
        CatalogValidationError: If catalog format is invalid
    """
    if catalog_path is None:
        catalog_path = CATALOG_FILE
    
    if not catalog_path.exists():
        raise CatalogNotFoundError(f"Catalog file not found: {catalog_path}")
    
    try:
        content = catalog_path.read_text(encoding='utf-8')
        catalog = json.loads(content)
    except json.JSONDecodeError as e:
        raise CatalogValidationError(f"Invalid JSON in catalog file: {e}")
    except Exception as e:
        raise CatalogError(f"Error reading catalog file: {e}")
    
    _validate_catalog(catalog)
    
    return catalog


def _validate_catalog(catalog: Dict[str, Any]) -> None:
    """
    Validate catalog structure and content
    
    Args:
        catalog: Catalog dictionary to validate
    
    Raises:
        CatalogValidationError: If catalog structure is invalid
    """
    if not isinstance(catalog, dict):
        raise CatalogValidationError("Catalog must be a dictionary")
    
    if 'version' not in catalog:
        raise CatalogValidationError("Missing 'version' field in catalog")
    
    if catalog['version'] != CATALOG_VERSION:
        raise CatalogValidationError(f"Unsupported catalog version: {catalog['version']}. Expected: {CATALOG_VERSION}")
    
    if 'categories' not in catalog:
        raise CatalogValidationError("Missing 'categories' field in catalog")
    
    if not isinstance(catalog['categories'], dict):
        raise CatalogValidationError("'categories' must be a dictionary")
    
    for category_name, category_data in catalog['categories'].items():
        if not isinstance(category_data, dict):
            raise CatalogValidationError(f"Category '{category_name}' must be a dictionary")
        
        if 'description' not in category_data:
            raise CatalogValidationError(f"Missing 'description' in category '{category_name}'")
        
        if 'skills' not in category_data:
            raise CatalogValidationError(f"Missing 'skills' in category '{category_name}'")
        
        if not isinstance(category_data['skills'], list):
            raise CatalogValidationError(f"'skills' in category '{category_name}' must be a list")
        
        for skill in category_data['skills']:
            _validate_skill(skill, category_name)


def _validate_skill(skill: Dict[str, Any], category_name: str) -> None:
    """
    Validate a single skill entry
    
    Args:
        skill: Skill dictionary to validate
        category_name: Name of the category (for error messages)
    
    Raises:
        CatalogValidationError: If skill structure is invalid
    """
    if not isinstance(skill, dict):
        raise CatalogValidationError(f"Skill in category '{category_name}' must be a dictionary")
    
    required_fields = ['name', 'description', 'source', 'license']
    for field in required_fields:
        if field not in skill:
            raise CatalogValidationError(f"Missing required field '{field}' in skill")
    
    if not isinstance(skill['name'], str) or not skill['name']:
        raise CatalogValidationError(f"Invalid 'name' field in skill")
    
    if not isinstance(skill['description'], str) or not skill['description']:
        raise CatalogValidationError(f"Invalid 'description' field in skill '{skill['name']}'")
    
    if not isinstance(skill['source'], str) or not skill['source']:
        raise CatalogValidationError(f"Invalid 'source' field in skill '{skill['name']}'")
    
    if not isinstance(skill['license'], str) or not skill['license']:
        raise CatalogValidationError(f"Invalid 'license' field in skill '{skill['name']}'")
    
    if 'aliases' in skill and not isinstance(skill['aliases'], list):
        raise CatalogValidationError(f"Invalid 'aliases' field in skill '{skill['name']}'")
    
    if 'dependencies' in skill and not isinstance(skill['dependencies'], list):
        raise CatalogValidationError(f"Invalid 'dependencies' field in skill '{skill['name']}'")


def get_skill(skill_name: str, catalog_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """
    Get skill info by name, supporting category prefixes (e.g., experimental/create-plan)
    
    Args:
        skill_name: Name of the skill, optionally with category prefix
        catalog_path: Optional path to catalog file
    
    Returns:
        Skill dictionary if found, None otherwise
    """
    catalog = load_catalog(catalog_path)
    
    category = None
    name = skill_name
    
    if '/' in skill_name:
        parts = skill_name.split('/', 1)
        if len(parts) == 2:
            category, name = parts
    
    if category:
        if category not in catalog['categories']:
            return None
        
        for skill in catalog['categories'][category]['skills']:
            if skill['name'] == name:
                return skill
    else:
        for category_data in catalog['categories'].values():
            for skill in category_data['skills']:
                if skill['name'] == name:
                    return skill
    
    return None


def resolve_alias(alias: str, catalog_path: Optional[Path] = None) -> Optional[str]:
    """
    Resolve skill aliases to actual skill names
    
    Args:
        alias: Alias to resolve
        catalog_path: Optional path to catalog file
    
    Returns:
        Actual skill name if alias is found, None otherwise
    """
    catalog = load_catalog(catalog_path)
    
    for category_data in catalog['categories'].values():
        for skill in category_data['skills']:
            if skill['name'] == alias:
                return skill['name']
            
            if 'aliases' in skill:
                if alias in skill['aliases']:
                    return skill['name']
    
    return None


def list_categories(catalog_path: Optional[Path] = None) -> List[Dict[str, str]]:
    """
    List all available categories
    
    Args:
        catalog_path: Optional path to catalog file
    
    Returns:
        List of category dictionaries with 'name' and 'description' keys
    """
    catalog = load_catalog(catalog_path)
    
    categories = []
    for category_name, category_data in catalog['categories'].items():
        categories.append({
            'name': category_name,
            'description': category_data['description']
        })
    
    return categories


def list_skills(category: Optional[str] = None, catalog_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    List skills, optionally filtered by category
    
    Args:
        category: Optional category name to filter skills
        catalog_path: Optional path to catalog file
    
    Returns:
        List of skill dictionaries
    """
    catalog = load_catalog(catalog_path)
    
    if category:
        if category not in catalog['categories']:
            return []
        
        skills = catalog['categories'][category]['skills']
    else:
        skills = []
        for category_data in catalog['categories'].values():
            skills.extend(category_data['skills'])
    
    return skills


def update_catalog(catalog_path: Optional[Path] = None) -> bool:
    """
    Fetch and update catalog from remote sources (placeholder for now)
    
    Args:
        catalog_path: Optional path to catalog file
    
    Returns:
        True if update was successful, False otherwise
    """
    print(MSG_CATALOG_UPDATE_NOT_IMPLEMENTED)
    print(MSG_CATALOG_VERSION_INFO.format(version=CATALOG_VERSION))
    return False


def search_skills(query: str, catalog_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Search for skills by name or description
    
    Args:
        query: Search query string
        catalog_path: Optional path to catalog file
    
    Returns:
        List of matching skill dictionaries
    """
    query_lower = query.lower()
    skills = list_skills(catalog_path=catalog_path)
    
    results = []
    for skill in skills:
        if query_lower in skill['name'].lower():
            results.append(skill)
        elif query_lower in skill['description'].lower():
            results.append(skill)
        elif 'aliases' in skill:
            for alias in skill['aliases']:
                if query_lower in alias.lower():
                    results.append(skill)
                    break
    
    return results


def get_skill_dependencies(skill_name: str, catalog_path: Optional[Path] = None) -> List[str]:
    """
    Get list of dependencies for a skill
    
    Args:
        skill_name: Name of the skill
        catalog_path: Optional path to catalog file
    
    Returns:
        List of dependency skill names
    """
    skill = get_skill(skill_name, catalog_path)
    
    if not skill:
        return []
    
    return skill.get('dependencies', [])


def is_skill_available(skill_name: str, catalog_path: Optional[Path] = None) -> bool:
    """
    Check if a skill is available in the catalog
    
    Args:
        skill_name: Name of the skill
        catalog_path: Optional path to catalog file
    
    Returns:
        True if skill exists in catalog, False otherwise
    """
    return get_skill(skill_name, catalog_path) is not None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Skill Catalog Manager")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    subparsers.add_parser('list-categories', help='List all categories')
    
    list_parser = subparsers.add_parser('list', help='List skills')
    list_parser.add_argument('--category', '-c', help='Filter by category')
    
    search_parser = subparsers.add_parser('search', help='Search for skills')
    search_parser.add_argument('query', help='Search query')
    
    get_parser = subparsers.add_parser('get', help='Get skill information')
    get_parser.add_argument('name', help='Skill name (with optional category prefix)')
    
    resolve_parser = subparsers.add_parser('resolve', help='Resolve an alias to skill name')
    resolve_parser.add_argument('alias', help='Alias to resolve')
    
    subparsers.add_parser('update', help='Update catalog from remote sources')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'list-categories':
            categories = list_categories()
            print(MSG_CATEGORIES_HEADER)
            for cat in categories:
                print(MSG_CATEGORY_NAME.format(name=cat['name']))
                print(MSG_CATEGORY_DESC.format(description=cat['description']))
        
        elif args.command == 'list':
            skills = list_skills(category=args.category)
            if args.category:
                print(MSG_SKILLS_HEADER.format(category=args.category))
            else:
                print(MSG_ALL_SKILLS_HEADER)
            
            for skill in skills:
                print(MSG_SKILL_NAME.format(name=skill['name']))
                print(MSG_SKILL_DESC.format(description=skill['description']))
                if skill.get('aliases'):
                    print(MSG_SKILL_ALIASES.format(aliases=', '.join(skill['aliases'])))
                print()
        
        elif args.command == 'search':
            results = search_skills(args.query)
            if results:
                print(MSG_SEARCH_RESULTS.format(query=args.query))
                for skill in results:
                    print(MSG_SKILL_NAME.format(name=skill['name']))
                    print(MSG_SKILL_DESC.format(description=skill['description']))
                    print()
            else:
                print(MSG_NO_SEARCH_RESULTS.format(query=args.query))
        
        elif args.command == 'get':
            skill = get_skill(args.name)
            if skill:
                print(MSG_SKILL_INFO_HEADER)
                print(f"  Name: {skill['name']}")
                print(MSG_SKILL_DESC.format(description=skill['description']))
                print(MSG_SKILL_SOURCE.format(source=skill['source']))
                print(MSG_SKILL_LICENSE.format(license=skill['license']))
                if skill.get('aliases'):
                    print(MSG_SKILL_ALIASES.format(aliases=', '.join(skill['aliases'])))
                if skill.get('dependencies'):
                    print(MSG_SKILL_DEPENDENCIES.format(dependencies=', '.join(skill['dependencies'])))
            else:
                print(MSG_SKILL_NOT_FOUND_CATALOG.format(name=args.name))
        
        elif args.command == 'resolve':
            skill_name = resolve_alias(args.alias)
            if skill_name:
                print(MSG_ALIAS_RESOLVED.format(alias=args.alias, skill_name=skill_name))
            else:
                print(MSG_ALIAS_NOT_FOUND.format(alias=args.alias))
        
        elif args.command == 'update':
            update_catalog()
        
        else:
            parser.print_help()
    
    except CatalogError as e:
        print(MSG_CATALOG_ERROR.format(error=e))
        sys.exit(1)
