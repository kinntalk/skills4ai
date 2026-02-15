#!/usr/bin/env python3
"""
Test Automation Script for Quality Check System

This script tests all automated quality check components:
- Scheduled task execution
- CI/CD integration
- Alert notifications
- Threshold validation
- Report generation
"""

import json
import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import unittest
import logging


class TestQualityCheckAutomation(unittest.TestCase):
    """Test suite for quality check automation"""
    
    @classmethod
    def setUpClass(cls):
        """Setup test environment"""
        cls.test_dir = Path(__file__).parent.parent / "test_automation"
        cls.test_dir.mkdir(parents=True, exist_ok=True)
        
        cls.scripts_dir = Path(__file__).parent
        cls.config_dir = Path(__file__).parent.parent / "config"
        cls.reports_dir = cls.test_dir / "reports"
        cls.reports_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        cls.logger = logging.getLogger(__name__)
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup test environment"""
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir)
    
    def test_01_quality_check_script_exists(self):
        """Test that quality_check.py exists and is executable"""
        quality_check = self.scripts_dir / "quality_check.py"
        self.assertTrue(quality_check.exists(), "quality_check.py should exist")
        self.assertTrue(quality_check.is_file(), "quality_check.py should be a file")
        self.logger.info("✓ quality_check.py exists and is accessible")
    
    def test_02_usage_tracker_script_exists(self):
        """Test that usage_tracker.py exists"""
        usage_tracker = self.scripts_dir / "usage_tracker.py"
        self.assertTrue(usage_tracker.exists(), "usage_tracker.py should exist")
        self.assertTrue(usage_tracker.is_file(), "usage_tracker.py should be a file")
        self.logger.info("✓ usage_tracker.py exists and is accessible")
    
    def test_03_scheduled_quality_check_script_exists(self):
        """Test that scheduled_quality_check.py exists"""
        scheduled_check = self.scripts_dir / "scheduled_quality_check.py"
        self.assertTrue(scheduled_check.exists(), "scheduled_quality_check.py should exist")
        self.assertTrue(scheduled_check.is_file(), "scheduled_quality_check.py should be a file")
        self.logger.info("✓ scheduled_quality_check.py exists and is accessible")
    
    def test_04_quality_thresholds_config_exists(self):
        """Test that quality_thresholds.json exists and is valid"""
        config_file = self.config_dir / "quality_thresholds.json"
        self.assertTrue(config_file.exists(), "quality_thresholds.json should exist")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self.assertIn('min_success_rate', config)
        self.assertIn('min_overall_score', config)
        self.assertIn('max_keyword_overlaps', config)
        self.assertIn('max_consistency_issues', config)
        self.logger.info("✓ quality_thresholds.json exists and is valid")
    
    def test_05_github_workflow_exists(self):
        """Test that GitHub Actions workflow exists"""
        workflow_file = Path(__file__).parent.parent / ".github" / "workflows" / "quality-check.yml"
        self.assertTrue(workflow_file.exists(), "quality-check.yml should exist")
        self.assertTrue(workflow_file.is_file(), "quality-check.yml should be a file")
        self.logger.info("✓ GitHub Actions workflow exists")
    
    def test_06_run_quality_check_consistency(self):
        """Test running quality check with consistency check"""
        self.logger.info("Testing consistency check...")
        
        result = subprocess.run(
            [sys.executable, str(self.scripts_dir / "quality_check.py"), "--check", "consistency"],
            capture_output=True,
            text=True,
            cwd=str(self.scripts_dir)
        )
        
        if result.returncode != 0:
            self.logger.error(f"Consistency check failed with return code {result.returncode}")
            self.logger.error(f"STDOUT: {result.stdout}")
            self.logger.error(f"STDERR: {result.stderr}")
        
        self.assertEqual(result.returncode, 0, "Consistency check should complete successfully")
        self.assertIn("consistency", result.stdout.lower())
        self.logger.info("✓ Consistency check executed successfully")
    
    def test_07_run_quality_check_keywords(self):
        """Test running quality check with keyword overlap check"""
        self.logger.info("Testing keyword overlap check...")
        
        result = subprocess.run(
            [sys.executable, str(self.scripts_dir / "quality_check.py"), "--check", "keywords"],
            capture_output=True,
            text=True,
            cwd=str(self.scripts_dir)
        )
        
        self.assertIn("keyword", result.stdout.lower(), "Output should contain keyword information")
        self.assertIn("SKILLS QUALITY REPORT", result.stdout, "Should generate quality report")
        self.logger.info("✓ Keyword overlap check executed successfully")
    
    def test_08_run_quality_check_all(self):
        """Test running full quality check"""
        self.logger.info("Testing full quality check...")
        
        output_file = self.reports_dir / "test_quality_report.json"
        
        result = subprocess.run(
            [sys.executable, str(self.scripts_dir / "quality_check.py"), 
             "--check", "all", "--output", str(output_file)],
            capture_output=True,
            text=True,
            cwd=str(self.scripts_dir)
        )
        
        self.assertTrue(output_file.exists(), "Quality report should be generated")
        
        with open(output_file, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        self.assertIn('timestamp', report)
        self.assertIn('overall_score', report)
        self.assertIn('consistency', report)
        self.assertIn('keyword_overlap', report)
        self.logger.info("✓ Full quality check executed successfully with report generation")
    
    def test_09_quality_report_structure(self):
        """Test that quality report has correct structure"""
        output_file = self.reports_dir / "test_quality_report.json"
        
        if not output_file.exists():
            subprocess.run(
                [sys.executable, str(self.scripts_dir / "quality_check.py"), 
                 "--check", "all", "--output", str(output_file)],
                capture_output=True,
                cwd=str(Path(__file__).parent.parent)
            )
        
        with open(output_file, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        required_fields = [
            'timestamp', 'overall_score', 'consistency', 
            'keyword_overlap', 'summary', 'recommendations'
        ]
        
        for field in required_fields:
            self.assertIn(field, report, f"Report should contain {field}")
        
        self.assertIn('total_skills', report['summary'])
        self.assertIn('consistency_issues', report['summary'])
        self.assertIn('keyword_issues', report['summary'])
        self.assertIn('status', report['summary'])
        
        self.logger.info("✓ Quality report has correct structure")
    
    def test_10_usage_tracker_functionality(self):
        """Test usage tracker functionality"""
        self.logger.info("Testing usage tracker...")
        
        sys.path.insert(0, str(self.scripts_dir))
        from usage_tracker import UsageTracker
        
        test_stats_file = self.test_dir / "test_usage_stats.json"
        tracker = UsageTracker(str(test_stats_file))
        
        context = {
            'start_time': datetime.now().isoformat(),
            'user': 'test_user',
            'session': 'test_session'
        }
        
        result = {'success': True}
        
        success = tracker.record_invocation('test_skill', context, result)
        self.assertTrue(success, "Should successfully record invocation")
        
        stats = tracker.get_skill_stats('test_skill')
        self.assertIsNotNone(stats, "Should retrieve skill stats")
        self.assertEqual(stats['invocations'], 1, "Should have 1 invocation")
        
        self.logger.info("✓ Usage tracker functionality works correctly")
    
    def test_11_scheduled_weekly_check(self):
        """Test scheduled weekly check execution"""
        self.logger.info("Testing scheduled weekly check...")
        
        result = subprocess.run(
            [sys.executable, str(self.scripts_dir / "scheduled_quality_check.py"), 
             "--type", "weekly", "--base-dir", str(Path(__file__).parent.parent)],
            capture_output=True,
            text=True,
            cwd=str(self.scripts_dir)
        )
        
        self.assertEqual(result.returncode, 0, "Weekly check should complete successfully")
        self.assertIn("weekly", result.stdout.lower())
        self.logger.info("✓ Scheduled weekly check executed successfully")
    
    def test_12_scheduled_monthly_check(self):
        """Test scheduled monthly check execution"""
        self.logger.info("Testing scheduled monthly check...")
        
        result = subprocess.run(
            [sys.executable, str(self.scripts_dir / "scheduled_quality_check.py"), 
             "--type", "monthly", "--base-dir", str(Path(__file__).parent.parent)],
            capture_output=True,
            text=True,
            cwd=str(self.scripts_dir)
        )
        
        self.assertEqual(result.returncode, 0, "Monthly check should complete successfully")
        self.assertIn("monthly", result.stdout.lower())
        self.logger.info("✓ Scheduled monthly check executed successfully")
    
    def test_13_alert_generation(self):
        """Test alert generation based on thresholds"""
        self.logger.info("Testing alert generation...")
        
        sys.path.insert(0, str(self.scripts_dir))
        from scheduled_quality_check import QualityAlertManager, QualityThresholds
        
        thresholds = QualityThresholds(
            min_success_rate=70.0,
            min_overall_score=70.0,
            max_keyword_overlaps=10,
            max_consistency_issues=5
        )
        
        alert_manager = QualityAlertManager(thresholds)
        
        quality_report = {
            'summary': {
                'overall_score': 65,
                'consistency_issues': 8,
                'keyword_issues': 15
            }
        }
        
        usage_stats = {
            'overall_success_rate': 60
        }
        
        alerts = alert_manager.check_quality_report(quality_report, usage_stats)
        
        self.assertGreater(len(alerts), 0, "Should generate alerts for low scores")
        
        alert_types = [alert['type'] for alert in alerts]
        self.assertIn('quality_score', alert_types)
        self.assertIn('success_rate', alert_types)
        
        self.logger.info("✓ Alert generation works correctly")
    
    def test_14_threshold_validation(self):
        """Test threshold validation logic"""
        self.logger.info("Testing threshold validation...")
        
        sys.path.insert(0, str(self.scripts_dir))
        from scheduled_quality_check import QualityAlertManager, QualityThresholds
        
        thresholds = QualityThresholds(
            min_success_rate=90.0,
            min_overall_score=90.0,
            max_keyword_overlaps=5,
            max_consistency_issues=3
        )
        
        alert_manager = QualityAlertManager(thresholds)
        
        quality_report = {
            'summary': {
                'overall_score': 95,
                'consistency_issues': 2,
                'keyword_issues': 3
            }
        }
        
        usage_stats = {
            'overall_success_rate': 95
        }
        
        alerts = alert_manager.check_quality_report(quality_report, usage_stats)
        
        self.assertEqual(len(alerts), 0, "Should not generate alerts for good scores")
        
        self.logger.info("✓ Threshold validation works correctly")
    
    def test_15_report_file_generation(self):
        """Test that report files are generated correctly"""
        self.logger.info("Testing report file generation...")
        
        reports = list(self.reports_dir.glob("*.json"))
        self.assertGreater(len(reports), 0, "Should generate at least one report file")
        
        for report_file in reports:
            with open(report_file, 'r', encoding='utf-8') as f:
                report = json.load(f)
            self.assertIsInstance(report, dict, "Report should be a dictionary")
        
        self.logger.info(f"✓ Generated {len(reports)} report files correctly")
    
    def test_16_github_workflow_syntax(self):
        """Test GitHub workflow YAML syntax"""
        self.logger.info("Testing GitHub workflow syntax...")
        
        workflow_file = Path(__file__).parent.parent / ".github" / "workflows" / "quality-check.yml"
        
        try:
            import yaml
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow = yaml.safe_load(f)
            
            self.assertIn('name', workflow)
            self.assertTrue('on' in workflow or True in workflow, "Workflow should have trigger configuration")
            self.assertIn('jobs', workflow)
            
            self.assertIn('quality-check', workflow['jobs'])
            self.assertIn('runs-on', workflow['jobs']['quality-check'])
            self.assertIn('steps', workflow['jobs']['quality-check'])
            
            self.logger.info("✓ GitHub workflow YAML syntax is valid")
        except ImportError:
            self.logger.warning("PyYAML not installed, skipping YAML syntax test")
    
    def test_17_integration_reliability(self):
        """Test integration reliability by running multiple checks"""
        self.logger.info("Testing integration reliability...")
        
        success_count = 0
        total_runs = 3
        
        for i in range(total_runs):
            result = subprocess.run(
                [sys.executable, str(self.scripts_dir / "quality_check.py"), 
                 "--check", "all", "--output", str(self.reports_dir / f"reliability_test_{i}.json")],
                capture_output=True,
                text=True,
                cwd=str(self.scripts_dir)
            )
            
            output_file = self.reports_dir / f"reliability_test_{i}.json"
            if output_file.exists():
                success_count += 1
        
        reliability = (success_count / total_runs) * 100
        self.assertGreaterEqual(reliability, 100, "All runs should generate reports")
        
        self.logger.info(f"✓ Integration reliability: {reliability}% success rate")


def run_tests():
    """Run all tests and generate summary"""
    print("\n" + "="*80)
    print("QUALITY CHECK AUTOMATION TEST SUITE")
    print("="*80)
    print(f"Test Directory: {Path(__file__).parent.parent / 'test_automation'}")
    print(f"Started: {datetime.now().isoformat()}")
    print("="*80 + "\n")
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestQualityCheckAutomation)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("="*80 + "\n")
    
    if result.wasSuccessful():
        print("✅ All tests passed successfully!")
        return 0
    else:
        print("❌ Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
