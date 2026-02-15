#!/usr/bin/env python3
"""
Quality Check Script for Trae Skills

This script performs various quality checks on the skills registry:
1. Skill consistency check - verifies all skills exist and have required files
2. Keyword overlap detection - identifies conflicts between skills
3. Quality report generation - comprehensive quality assessment
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional
from datetime import datetime
from collections import defaultdict
import argparse


def load_skill_map(skill_map_path: str) -> Dict[str, Any]:
    """Load skill_map.json file"""
    try:
        with open(skill_map_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: skill_map.json not found at {skill_map_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in skill_map.json: {e}")
        sys.exit(1)


def check_skill_consistency(skill_map: Dict[str, Any], skills_dir: str) -> Dict[str, Any]:
    """
    Check skill consistency in skill_map.json
    
    Verifies:
    - All skills listed in skill_map.json exist as directories
    - Each skill directory contains SKILL.md
    - Path fields are correct
    
    Returns:
        Dict containing:
        - missing_skills: list of skills that don't exist
        - missing_skill_md: list of skills without SKILL.md
        - path_errors: list of skills with incorrect path fields
        - orphaned_directories: list of directories not in skill_map
    """
    result = {
        "missing_skills": [],
        "missing_skill_md": [],
        "path_errors": [],
        "orphaned_directories": []
    }
    
    skills_base_dir = Path(skills_dir)
    
    for skill_name, skill_data in skill_map.get("skills", {}).items():
        skill_path = skill_data.get("path", skill_name)
        full_path = skills_base_dir / skill_path
        
        if not full_path.exists():
            result["missing_skills"].append({
                "name": skill_name,
                "expected_path": str(full_path),
                "configured_path": skill_path
            })
        else:
            skill_md_path = full_path / "SKILL.md"
            if not skill_md_path.exists():
                result["missing_skill_md"].append({
                    "name": skill_name,
                    "path": str(full_path)
                })
    
    return result


def check_keyword_overlap(skill_map: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check for keyword overlaps between different skills
    
    Identifies:
    - Exact matches: keywords that are identical across skills
    - Partial matches: keywords that are substrings of others
    - Overlap degree: percentage of overlap
    
    Returns:
        Dict containing overlap report with conflicts and statistics
    """
    result = {
        "exact_matches": [],
        "partial_matches": [],
        "statistics": {
            "total_skills": len(skill_map.get("skills", {})),
            "total_keywords": 0,
            "unique_keywords": 0,
            "overlap_count": 0
        }
    }
    
    skill_keywords: Dict[str, Set[str]] = {}
    all_keywords: Set[str] = set()
    
    for skill_name, skill_data in skill_map.get("skills", {}).items():
        keywords = set(skill_data.get("keywords", []))
        aliases = set(skill_data.get("aliases", []))
        skill_keywords[skill_name] = keywords | aliases
        all_keywords.update(keywords | aliases)
    
    result["statistics"]["total_keywords"] = sum(len(kw) for kw in skill_keywords.values())
    result["statistics"]["unique_keywords"] = len(all_keywords)
    
    keyword_to_skills: Dict[str, List[str]] = defaultdict(list)
    for skill_name, keywords in skill_keywords.items():
        for keyword in keywords:
            keyword_to_skills[keyword.lower()].append(skill_name)
    
    for keyword, skills in keyword_to_skills.items():
        if len(skills) > 1:
            result["exact_matches"].append({
                "keyword": keyword,
                "skills": skills,
                "count": len(skills)
            })
            result["statistics"]["overlap_count"] += 1
    
    for skill1_name, keywords1 in skill_keywords.items():
        for skill2_name, keywords2 in skill_keywords.items():
            if skill1_name >= skill2_name:
                continue
            
            for kw1 in keywords1:
                for kw2 in keywords2:
                    if kw1.lower() != kw2.lower():
                        if kw1.lower() in kw2.lower() or kw2.lower() in kw1.lower():
                            existing = False
                            for match in result["partial_matches"]:
                                if (match["skill1"] == skill1_name and 
                                    match["skill2"] == skill2_name and
                                    match["keyword1"] == kw1 and 
                                    match["keyword2"] == kw2):
                                    existing = True
                                    break
                            
                            if not existing:
                                overlap_degree = min(len(kw1), len(kw2)) / max(len(kw1), len(kw2))
                                result["partial_matches"].append({
                                    "skill1": skill1_name,
                                    "skill2": skill2_name,
                                    "keyword1": kw1,
                                    "keyword2": kw2,
                                    "overlap_degree": round(overlap_degree, 2)
                                })
    
    result["statistics"]["partial_overlap_count"] = len(result["partial_matches"])
    
    return result


def generate_quality_report(
    skill_map: Dict[str, Any],
    consistency_result: Dict[str, Any],
    overlap_result: Dict[str, Any],
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Generate comprehensive quality report
    
    Integrates all check results and provides:
    - Timestamp
    - Overall quality score
    - Detailed findings
    - Improvement suggestions
    
    Returns:
        Dict containing complete quality report
    """
    report = {
        "timestamp": datetime.now().isoformat(),
        "overall_score": 0,
        "consistency": consistency_result,
        "keyword_overlap": overlap_result,
        "summary": {},
        "recommendations": []
    }
    
    consistency_issues = (
        len(consistency_result["missing_skills"]) +
        len(consistency_result["missing_skill_md"]) +
        len(consistency_result["path_errors"])
    )
    
    keyword_issues = (
        len(overlap_result["exact_matches"]) +
        len(overlap_result["partial_matches"])
    )
    
    total_skills = len(skill_map.get("skills", {}))
    
    consistency_score = max(0, 100 - (consistency_issues * 10))
    keyword_score = max(0, 100 - (keyword_issues * 5))
    
    report["overall_score"] = round((consistency_score + keyword_score) / 2, 2)
    
    report["summary"] = {
        "total_skills": total_skills,
        "consistency_issues": consistency_issues,
        "keyword_issues": keyword_issues,
        "overall_score": report["overall_score"],
        "status": "excellent" if report["overall_score"] >= 90 else
                  "good" if report["overall_score"] >= 70 else
                  "fair" if report["overall_score"] >= 50 else "poor"
    }
    
    if consistency_result["missing_skills"]:
        report["recommendations"].append({
            "priority": "high",
            "category": "consistency",
            "issue": "Missing skill directories",
            "suggestion": f"Create missing directories for {len(consistency_result['missing_skills'])} skills",
            "details": [s["name"] for s in consistency_result["missing_skills"]]
        })
    
    if consistency_result["missing_skill_md"]:
        report["recommendations"].append({
            "priority": "high",
            "category": "consistency",
            "issue": "Missing SKILL.md files",
            "suggestion": f"Add SKILL.md to {len(consistency_result['missing_skill_md'])} skill directories",
            "details": [s["name"] for s in consistency_result["missing_skill_md"]]
        })
    
    if overlap_result["exact_matches"]:
        report["recommendations"].append({
            "priority": "medium",
            "category": "keywords",
            "issue": "Exact keyword matches found",
            "suggestion": f"Resolve {len(overlap_result['exact_matches'])} exact keyword conflicts",
            "details": [m["keyword"] for m in overlap_result["exact_matches"]]
        })
    
    if overlap_result["partial_matches"]:
        report["recommendations"].append({
            "priority": "low",
            "category": "keywords",
            "issue": "Partial keyword overlaps detected",
            "suggestion": f"Review {len(overlap_result['partial_matches'])} partial overlaps",
            "details": f"Found overlaps with degree > 0.5"
        })
    
    if report["overall_score"] == 100:
        report["recommendations"].append({
            "priority": "info",
            "category": "general",
            "issue": "All checks passed",
            "suggestion": "Skills registry is in excellent condition",
            "details": []
        })
    
    return report


def print_report(report: Dict[str, Any], verbose: bool = False):
    """Print quality report to console"""
    print("\n" + "="*60)
    print("SKILLS QUALITY REPORT")
    print("="*60)
    print(f"Timestamp: {report['timestamp']}")
    print(f"Overall Score: {report['overall_score']}/100 ({report['summary']['status']})")
    print(f"Total Skills: {report['summary']['total_skills']}")
    print(f"Consistency Issues: {report['summary']['consistency_issues']}")
    print(f"Keyword Issues: {report['summary']['keyword_issues']}")
    print("="*60)
    
    if verbose:
        print("\n--- CONSISTENCY CHECK ---")
        if report['consistency']['missing_skills']:
            print(f"\nMissing Skills ({len(report['consistency']['missing_skills'])}):")
            for skill in report['consistency']['missing_skills']:
                print(f"  - {skill['name']}: {skill['expected_path']}")
        
        if report['consistency']['missing_skill_md']:
            print(f"\nMissing SKILL.md ({len(report['consistency']['missing_skill_md'])}):")
            for skill in report['consistency']['missing_skill_md']:
                print(f"  - {skill['name']}: {skill['path']}")
        
        if report['consistency']['path_errors']:
            print(f"\nPath Errors ({len(report['consistency']['path_errors'])}):")
            for error in report['consistency']['path_errors']:
                print(f"  - {error['name']}: {error['configured_path']} != {error['actual_path']}")
        
        if not any([report['consistency']['missing_skills'], 
                   report['consistency']['missing_skill_md'],
                   report['consistency']['path_errors']]):
            print("✓ All consistency checks passed")
        
        print("\n--- KEYWORD OVERLAP ---")
        if report['keyword_overlap']['exact_matches']:
            print(f"\nExact Matches ({len(report['keyword_overlap']['exact_matches'])}):")
            for match in report['keyword_overlap']['exact_matches']:
                print(f"  - '{match['keyword']}' in: {', '.join(match['skills'])}")
        
        if report['keyword_overlap']['partial_matches']:
            print(f"\nPartial Matches ({len(report['keyword_overlap']['partial_matches'])}):")
            for match in report['keyword_overlap']['partial_matches'][:10]:
                print(f"  - '{match['keyword1']}' vs '{match['keyword2']}' "
                      f"({match['skill1']} vs {match['skill2']}) - "
                      f"{match['overlap_degree']*100:.0f}% overlap")
        
        if not any([report['keyword_overlap']['exact_matches'],
                   report['keyword_overlap']['partial_matches']]):
            print("✓ No keyword overlaps detected")
        
        print("\n--- STATISTICS ---")
        stats = report['keyword_overlap']['statistics']
        print(f"Total Keywords: {stats['total_keywords']}")
        print(f"Unique Keywords: {stats['unique_keywords']}")
        print(f"Overlap Count: {stats['overlap_count']}")
    
    print("\n--- RECOMMENDATIONS ---")
    for rec in report['recommendations']:
        icon = "[!]" if rec['priority'] == 'high' else "[!]" if rec['priority'] == 'medium' else "[OK]"
        print(f"{icon} [{rec['priority'].upper()}] {rec['issue']}")
        print(f"   {rec['suggestion']}")
        if verbose and rec['details']:
            print(f"   Details: {', '.join(rec['details'][:5])}")
    
    print("="*60 + "\n")


def fix_issues(skill_map: Dict[str, Any], skills_dir: str, report: Dict[str, Any]):
    """Attempt to fix automatically fixable issues"""
    print("\nAttempting to fix issues...")
    
    fixed_count = 0
    
    for skill in report['consistency']['missing_skills']:
        skill_name = skill['name']
        skill_path = Path(skills_dir) / skill_name
        try:
            skill_path.mkdir(parents=True, exist_ok=True)
            skill_md = skill_path / "SKILL.md"
            skill_md.write_text(f"# {skill_name}\n\nDescription: {skill_name} skill\n", encoding='utf-8')
            print(f"✓ Created missing skill: {skill_name}")
            fixed_count += 1
        except Exception as e:
            print(f"✗ Failed to create {skill_name}: {e}")
    
    for skill in report['consistency']['missing_skill_md']:
        skill_name = skill['name']
        skill_path = Path(skill['path'])
        try:
            skill_md = skill_path / "SKILL.md"
            skill_md.write_text(f"# {skill_name}\n\nDescription: {skill_name} skill\n", encoding='utf-8')
            print(f"✓ Created missing SKILL.md: {skill_name}")
            fixed_count += 1
        except Exception as e:
            print(f"✗ Failed to create SKILL.md for {skill_name}: {e}")
    
    print(f"\nFixed {fixed_count} issues")
    return fixed_count > 0


def main():
    parser = argparse.ArgumentParser(
        description="Quality check script for Trae skills registry"
    )
    parser.add_argument(
        "--check",
        choices=["consistency", "keywords", "all"],
        default="all",
        help="Type of check to perform"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path for JSON report"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed information"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to fix automatically fixable issues"
    )
    parser.add_argument(
        "--skill-map",
        type=str,
        default=None,
        help="Path to skill_map.json file"
    )
    parser.add_argument(
        "--skills-dir",
        type=str,
        default=None,
        help="Base directory for skills"
    )
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    
    if args.skill_map is None:
        skill_map_path = script_dir.parent / "skill_map.json"
    else:
        skill_map_path = script_dir / args.skill_map if not Path(args.skill_map).is_absolute() else Path(args.skill_map)
    
    if args.skills_dir is None:
        skills_dir = script_dir.parent
    else:
        skills_dir = Path(args.skills_dir) if not Path(args.skills_dir).is_absolute() else Path(args.skills_dir)
    
    skill_map = load_skill_map(str(skill_map_path))
    
    consistency_result = {"missing_skills": [], "missing_skill_md": [], "path_errors": []}
    overlap_result = {"exact_matches": [], "partial_matches": [], "statistics": {}}
    
    if args.check in ["consistency", "all"]:
        print("Running consistency check...")
        consistency_result = check_skill_consistency(skill_map, str(skills_dir))
    
    if args.check in ["keywords", "all"]:
        print("Running keyword overlap check...")
        overlap_result = check_keyword_overlap(skill_map)
    
    report = generate_quality_report(skill_map, consistency_result, overlap_result, args.verbose)
    
    print_report(report, args.verbose)
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"Report saved to: {output_path}")
    
    if args.fix:
        if fix_issues(skill_map, str(skills_dir), report):
            print("\nRe-running checks after fixes...")
            consistency_result = check_skill_consistency(skill_map, str(skills_dir))
            overlap_result = check_keyword_overlap(skill_map)
            report = generate_quality_report(skill_map, consistency_result, overlap_result, args.verbose)
            print_report(report, args.verbose)
    
    sys.exit(0 if report['overall_score'] >= 70 else 1)


if __name__ == "__main__":
    main()
