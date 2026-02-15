#!/usr/bin/env python3
"""
Unit tests for quality_check.py

Tests all major functions:
- Skill consistency check
- Keyword overlap detection
- Quality report generation
- Command line argument handling
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, str(Path(__file__).parent))
from quality_check import (
    load_skill_map,
    check_skill_consistency,
    check_keyword_overlap,
    generate_quality_report,
    print_report,
    fix_issues
)


class TestLoadSkillMap(unittest.TestCase):
    """Test skill_map.json loading functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skill_map_path = Path(self.temp_dir) / "skill_map.json"
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_load_valid_skill_map(self):
        """Test loading a valid skill_map.json"""
        test_data = {
            "skills": {
                "test-skill": {
                    "name": "test-skill",
                    "keywords": ["test"]
                }
            }
        }
        self.skill_map_path.write_text(json.dumps(test_data), encoding='utf-8')
        
        result = load_skill_map(str(self.skill_map_path))
        self.assertEqual(result, test_data)
    
    def test_load_missing_file(self):
        """Test loading when file doesn't exist"""
        with self.assertRaises(SystemExit):
            load_skill_map(str(Path(self.temp_dir) / "nonexistent.json"))
    
    def test_load_invalid_json(self):
        """Test loading invalid JSON"""
        self.skill_map_path.write_text("{invalid json}", encoding='utf-8')
        
        with self.assertRaises(SystemExit):
            load_skill_map(str(self.skill_map_path))


class TestCheckSkillConsistency(unittest.TestCase):
    """Test skill consistency checking"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skills_dir = Path(self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_all_skills_present(self):
        """Test when all skills exist and have SKILL.md"""
        skill1_dir = self.skills_dir / "skill1"
        skill1_dir.mkdir()
        (skill1_dir / "SKILL.md").write_text("# Skill 1", encoding='utf-8')
        
        skill_map = {
            "skills": {
                "skill1": {
                    "name": "skill1",
                    "path": "skill1"
                }
            }
        }
        
        result = check_skill_consistency(skill_map, str(self.skills_dir))
        
        self.assertEqual(len(result["missing_skills"]), 0)
        self.assertEqual(len(result["missing_skill_md"]), 0)
        self.assertEqual(len(result["path_errors"]), 0)
    
    def test_missing_skill_directory(self):
        """Test when skill directory is missing"""
        skill_map = {
            "skills": {
                "missing-skill": {
                    "name": "missing-skill",
                    "path": "missing-skill"
                }
            }
        }
        
        result = check_skill_consistency(skill_map, str(self.skills_dir))
        
        self.assertEqual(len(result["missing_skills"]), 1)
        self.assertEqual(result["missing_skills"][0]["name"], "missing-skill")
    
    def test_missing_skill_md(self):
        """Test when SKILL.md is missing"""
        skill1_dir = self.skills_dir / "skill1"
        skill1_dir.mkdir()
        
        skill_map = {
            "skills": {
                "skill1": {
                    "name": "skill1",
                    "path": "skill1"
                }
            }
        }
        
        result = check_skill_consistency(skill_map, str(self.skills_dir))
        
        self.assertEqual(len(result["missing_skill_md"]), 1)
        self.assertEqual(result["missing_skill_md"][0]["name"], "skill1")
    
    def test_nested_skill_path(self):
        """Test skills with nested paths"""
        nested_dir = self.skills_dir / "management" / "skill-creator"
        nested_dir.mkdir(parents=True)
        (nested_dir / "SKILL.md").write_text("# Skill Creator", encoding='utf-8')
        
        skill_map = {
            "skills": {
                "skill-creator": {
                    "name": "skill-creator",
                    "path": "management/skill-creator"
                }
            }
        }
        
        result = check_skill_consistency(skill_map, str(self.skills_dir))
        
        self.assertEqual(len(result["missing_skills"]), 0)
        self.assertEqual(len(result["missing_skill_md"]), 0)


class TestCheckKeywordOverlap(unittest.TestCase):
    """Test keyword overlap detection"""
    
    def test_no_overlaps(self):
        """Test when there are no keyword overlaps"""
        skill_map = {
            "skills": {
                "skill1": {
                    "keywords": ["unique1"],
                    "aliases": ["alias1"]
                },
                "skill2": {
                    "keywords": ["unique2"],
                    "aliases": ["alias2"]
                }
            }
        }
        
        result = check_keyword_overlap(skill_map)
        
        self.assertEqual(len(result["exact_matches"]), 0)
        self.assertEqual(len(result["partial_matches"]), 0)
        self.assertEqual(result["statistics"]["total_skills"], 2)
        self.assertEqual(result["statistics"]["unique_keywords"], 4)
    
    def test_exact_keyword_match(self):
        """Test detection of exact keyword matches"""
        skill_map = {
            "skills": {
                "skill1": {
                    "keywords": ["shared", "unique1"]
                },
                "skill2": {
                    "keywords": ["shared", "unique2"]
                }
            }
        }
        
        result = check_keyword_overlap(skill_map)
        
        self.assertEqual(len(result["exact_matches"]), 1)
        self.assertEqual(result["exact_matches"][0]["keyword"], "shared")
        self.assertEqual(len(result["exact_matches"][0]["skills"]), 2)
    
    def test_partial_keyword_match(self):
        """Test detection of partial keyword matches"""
        skill_map = {
            "skills": {
                "skill1": {
                    "keywords": ["test"]
                },
                "skill2": {
                    "keywords": ["testing"]
                }
            }
        }
        
        result = check_keyword_overlap(skill_map)
        
        self.assertEqual(len(result["partial_matches"]), 1)
        self.assertEqual(result["partial_matches"][0]["keyword1"], "test")
        self.assertEqual(result["partial_matches"][0]["keyword2"], "testing")
    
    def test_case_insensitive_matching(self):
        """Test that matching is case insensitive"""
        skill_map = {
            "skills": {
                "skill1": {
                    "keywords": ["Test"]
                },
                "skill2": {
                    "keywords": ["test"]
                }
            }
        }
        
        result = check_keyword_overlap(skill_map)
        
        self.assertEqual(len(result["exact_matches"]), 1)
    
    def test_statistics_calculation(self):
        """Test statistics calculation"""
        skill_map = {
            "skills": {
                "skill1": {
                    "keywords": ["a", "b"],
                    "aliases": ["c"]
                },
                "skill2": {
                    "keywords": ["a", "d"],
                    "aliases": ["e"]
                }
            }
        }
        
        result = check_keyword_overlap(skill_map)
        
        self.assertEqual(result["statistics"]["total_skills"], 2)
        self.assertEqual(result["statistics"]["total_keywords"], 6)
        self.assertEqual(result["statistics"]["unique_keywords"], 5)
        self.assertEqual(result["statistics"]["overlap_count"], 1)


class TestGenerateQualityReport(unittest.TestCase):
    """Test quality report generation"""
    
    def test_perfect_score(self):
        """Test report with perfect score"""
        skill_map = {
            "skills": {
                "skill1": {
                    "keywords": ["unique1"]
                }
            }
        }
        
        consistency_result = {
            "missing_skills": [],
            "missing_skill_md": [],
            "path_errors": []
        }
        
        overlap_result = {
            "exact_matches": [],
            "partial_matches": [],
            "statistics": {
                "total_skills": 1,
                "total_keywords": 1,
                "unique_keywords": 1,
                "overlap_count": 0
            }
        }
        
        report = generate_quality_report(skill_map, consistency_result, overlap_result)
        
        self.assertEqual(report["overall_score"], 100)
        self.assertEqual(report["summary"]["status"], "excellent")
        self.assertIn("timestamp", report)
    
    def test_low_score(self):
        """Test report with low score due to issues"""
        skill_map = {
            "skills": {
                "skill1": {
                    "keywords": ["shared"]
                },
                "skill2": {
                    "keywords": ["shared"]
                }
            }
        }
        
        consistency_result = {
            "missing_skills": [{"name": "missing", "expected_path": "/path"}],
            "missing_skill_md": [],
            "path_errors": []
        }
        
        overlap_result = {
            "exact_matches": [{"keyword": "shared", "skills": ["skill1", "skill2"]}],
            "partial_matches": [],
            "statistics": {
                "total_skills": 2,
                "total_keywords": 2,
                "unique_keywords": 1,
                "overlap_count": 1
            }
        }
        
        report = generate_quality_report(skill_map, consistency_result, overlap_result)
        
        self.assertLess(report["overall_score"], 100)
        self.assertGreater(len(report["recommendations"]), 0)
    
    def test_recommendations_generation(self):
        """Test that recommendations are generated correctly"""
        skill_map = {"skills": {}}
        
        consistency_result = {
            "missing_skills": [{"name": "skill1"}],
            "missing_skill_md": [{"name": "skill2"}],
            "path_errors": []
        }
        
        overlap_result = {
            "exact_matches": [{"keyword": "test"}],
            "partial_matches": [],
            "statistics": {}
        }
        
        report = generate_quality_report(skill_map, consistency_result, overlap_result)
        
        self.assertGreater(len(report["recommendations"]), 0)
        
        categories = [rec["category"] for rec in report["recommendations"]]
        self.assertIn("consistency", categories)
        self.assertIn("keywords", categories)
    
    def test_status_determination(self):
        """Test status determination based on score"""
        skill_map = {"skills": {}}
        
        consistency_result = {
            "missing_skills": [],
            "missing_skill_md": [],
            "path_errors": []
        }
        
        overlap_result = {
            "exact_matches": [],
            "partial_matches": [],
            "statistics": {}
        }
        
        report = generate_quality_report(skill_map, consistency_result, overlap_result)
        
        self.assertEqual(report["summary"]["status"], "excellent")


class TestPrintReport(unittest.TestCase):
    """Test report printing functionality"""
    
    @patch('builtins.print')
    def test_print_report_basic(self, mock_print):
        """Test basic report printing"""
        report = {
            "timestamp": "2024-01-01T00:00:00",
            "overall_score": 100,
            "summary": {
                "total_skills": 1,
                "consistency_issues": 0,
                "keyword_issues": 0,
                "status": "excellent"
            },
            "consistency": {
                "missing_skills": [],
                "missing_skill_md": [],
                "path_errors": []
            },
            "keyword_overlap": {
                "exact_matches": [],
                "partial_matches": [],
                "statistics": {}
            },
            "recommendations": []
        }
        
        print_report(report, verbose=False)
        
        self.assertTrue(mock_print.called)
    
    @patch('builtins.print')
    def test_print_report_verbose(self, mock_print):
        """Test verbose report printing"""
        report = {
            "timestamp": "2024-01-01T00:00:00",
            "overall_score": 85,
            "summary": {
                "total_skills": 2,
                "consistency_issues": 1,
                "keyword_issues": 1,
                "status": "good"
            },
            "consistency": {
                "missing_skills": [{"name": "missing", "expected_path": "/path"}],
                "missing_skill_md": [],
                "path_errors": []
            },
            "keyword_overlap": {
                "exact_matches": [{"keyword": "test", "skills": ["skill1", "skill2"]}],
                "partial_matches": [],
                "statistics": {
                    "total_keywords": 4,
                    "unique_keywords": 3,
                    "overlap_count": 1
                }
            },
            "recommendations": [
                {
                    "priority": "high",
                    "category": "consistency",
                    "issue": "Test issue",
                    "suggestion": "Fix it",
                    "details": []
                }
            ]
        }
        
        print_report(report, verbose=True)
        
        self.assertTrue(mock_print.called)


class TestFixIssues(unittest.TestCase):
    """Test issue fixing functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skills_dir = Path(self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_fix_missing_skill_directory(self):
        """Test fixing missing skill directory"""
        report = {
            "consistency": {
                "missing_skills": [
                    {
                        "name": "new-skill",
                        "expected_path": str(self.skills_dir / "new-skill")
                    }
                ],
                "missing_skill_md": [],
                "path_errors": []
            },
            "keyword_overlap": {
                "exact_matches": [],
                "partial_matches": []
            },
            "recommendations": []
        }
        
        skill_map = {"skills": {}}
        
        result = fix_issues(skill_map, str(self.skills_dir), report)
        
        self.assertTrue(result)
        self.assertTrue((self.skills_dir / "new-skill").exists())
        self.assertTrue((self.skills_dir / "new-skill" / "SKILL.md").exists())
    
    def test_fix_missing_skill_md(self):
        """Test fixing missing SKILL.md"""
        skill_dir = self.skills_dir / "existing-skill"
        skill_dir.mkdir()
        
        report = {
            "consistency": {
                "missing_skills": [],
                "missing_skill_md": [
                    {
                        "name": "existing-skill",
                        "path": str(skill_dir)
                    }
                ],
                "path_errors": []
            },
            "keyword_overlap": {
                "exact_matches": [],
                "partial_matches": []
            },
            "recommendations": []
        }
        
        skill_map = {"skills": {}}
        
        result = fix_issues(skill_map, str(self.skills_dir), report)
        
        self.assertTrue(result)
        self.assertTrue((skill_dir / "SKILL.md").exists())
    
    def test_no_issues_to_fix(self):
        """Test when there are no issues to fix"""
        report = {
            "consistency": {
                "missing_skills": [],
                "missing_skill_md": [],
                "path_errors": []
            },
            "keyword_overlap": {
                "exact_matches": [],
                "partial_matches": []
            },
            "recommendations": []
        }
        
        skill_map = {"skills": {}}
        
        result = fix_issues(skill_map, str(self.skills_dir), report)
        
        self.assertFalse(result)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skills_dir = Path(self.temp_dir)
        
        skill1_dir = self.skills_dir / "skill1"
        skill1_dir.mkdir()
        (skill1_dir / "SKILL.md").write_text("# Skill 1", encoding='utf-8')
        
        self.skill_map = {
            "skills": {
                "skill1": {
                    "name": "skill1",
                    "path": "skill1",
                    "keywords": ["test", "unique"],
                    "aliases": []
                },
                "skill2": {
                    "name": "skill2",
                    "path": "skill2",
                    "keywords": ["test"],
                    "aliases": []
                }
            }
        }
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_full_workflow(self):
        """Test complete workflow from check to report"""
        consistency_result = check_skill_consistency(self.skill_map, str(self.skills_dir))
        overlap_result = check_keyword_overlap(self.skill_map)
        report = generate_quality_report(self.skill_map, consistency_result, overlap_result)
        
        self.assertIn("timestamp", report)
        self.assertIn("overall_score", report)
        self.assertIn("consistency", report)
        self.assertIn("keyword_overlap", report)
        self.assertIn("summary", report)
        self.assertIn("recommendations", report)
        
        self.assertLessEqual(report["overall_score"], 100)
        self.assertGreaterEqual(report["overall_score"], 0)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestLoadSkillMap))
    suite.addTests(loader.loadTestsFromTestCase(TestCheckSkillConsistency))
    suite.addTests(loader.loadTestsFromTestCase(TestCheckKeywordOverlap))
    suite.addTests(loader.loadTestsFromTestCase(TestGenerateQualityReport))
    suite.addTests(loader.loadTestsFromTestCase(TestPrintReport))
    suite.addTests(loader.loadTestsFromTestCase(TestFixIssues))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
