#!/usr/bin/env python3
"""
Scheduled Quality Check Script for Trae Skills

This script provides automated scheduling for quality checks:
- Weekly quality checks
- Monthly quality checks
- Quality alerts based on thresholds
- Integration with usage_tracker for comprehensive reporting
"""

import json
import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass


@dataclass
class QualityThresholds:
    """Quality threshold configuration"""
    min_success_rate: float = 70.0
    min_overall_score: float = 70.0
    max_keyword_overlaps: int = 10
    max_consistency_issues: int = 5
    warning_success_rate: float = 85.0
    warning_overall_score: float = 85.0


class QualityAlertManager:
    """Manages quality alerts and notifications"""
    
    def __init__(self, thresholds: QualityThresholds):
        self.thresholds = thresholds
        self.alerts: List[Dict[str, Any]] = []
    
    def check_quality_report(self, quality_report: Dict[str, Any], usage_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check quality report against thresholds and generate alerts"""
        self.alerts = []
        
        overall_score = quality_report.get('summary', {}).get('overall_score', 0)
        consistency_issues = quality_report.get('summary', {}).get('consistency_issues', 0)
        keyword_issues = quality_report.get('summary', {}).get('keyword_issues', 0)
        overall_success_rate = usage_stats.get('overall_success_rate', 0)
        
        if overall_score < self.thresholds.min_overall_score:
            self.alerts.append({
                'level': 'critical',
                'type': 'quality_score',
                'message': f'Overall quality score ({overall_score}) below threshold ({self.thresholds.min_overall_score})',
                'value': overall_score,
                'threshold': self.thresholds.min_overall_score
            })
        elif overall_score < self.thresholds.warning_overall_score:
            self.alerts.append({
                'level': 'warning',
                'type': 'quality_score',
                'message': f'Overall quality score ({overall_score}) approaching threshold',
                'value': overall_score,
                'threshold': self.thresholds.warning_overall_score
            })
        
        if overall_success_rate < self.thresholds.min_success_rate:
            self.alerts.append({
                'level': 'critical',
                'type': 'success_rate',
                'message': f'Overall success rate ({overall_success_rate}%) below threshold ({self.thresholds.min_success_rate}%)',
                'value': overall_success_rate,
                'threshold': self.thresholds.min_success_rate
            })
        elif overall_success_rate < self.thresholds.warning_success_rate:
            self.alerts.append({
                'level': 'warning',
                'type': 'success_rate',
                'message': f'Overall success rate ({overall_success_rate}%) approaching threshold',
                'value': overall_success_rate,
                'threshold': self.thresholds.warning_success_rate
            })
        
        if consistency_issues > self.thresholds.max_consistency_issues:
            self.alerts.append({
                'level': 'error',
                'type': 'consistency',
                'message': f'Too many consistency issues ({consistency_issues})',
                'value': consistency_issues,
                'threshold': self.thresholds.max_consistency_issues
            })
        
        if keyword_issues > self.thresholds.max_keyword_overlaps:
            self.alerts.append({
                'level': 'error',
                'type': 'keywords',
                'message': f'Too many keyword overlaps ({keyword_issues})',
                'value': keyword_issues,
                'threshold': self.thresholds.max_keyword_overlaps
            })
        
        return self.alerts
    
    def send_alerts(self, report_path: str = None):
        """Send alerts (console output, can be extended for email/webhook)"""
        if not self.alerts:
            print("✓ No quality alerts - all metrics within thresholds")
            return
        
        print("\n" + "="*80)
        print("QUALITY ALERTS")
        print("="*80)
        
        for alert in self.alerts:
            level_icon = {
                'critical': '[CRITICAL]',
                'error': '[ERROR]',
                'warning': '[WARNING]'
            }.get(alert['level'], '[INFO]')
            
            print(f"\n{level_icon} [{alert['level'].upper()}] {alert['type']}")
            print(f"   {alert['message']}")
            print(f"   Current: {alert['value']} | Threshold: {alert['threshold']}")
        
        print("="*80 + "\n")
        
        if report_path:
            self._save_alerts(report_path)
    
    def _save_alerts(self, report_path: str):
        """Save alerts to file"""
        alert_file = Path(report_path).parent / f"alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(alert_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'alerts': self.alerts
            }, f, indent=2, ensure_ascii=False)
        print(f"Alerts saved to: {alert_file}")


class ScheduledQualityChecker:
    """Main class for scheduled quality checks"""
    
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            self.base_dir = Path(__file__).parent.parent
        else:
            self.base_dir = Path(base_dir)
        
        self.scripts_dir = self.base_dir / "scripts"
        self.config_dir = self.base_dir / "config"
        self.reports_dir = self.base_dir / "reports"
        
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.thresholds = self._load_thresholds()
        self.alert_manager = QualityAlertManager(self.thresholds)
        
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_file = self.reports_dir / f"scheduled_check_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_thresholds(self) -> QualityThresholds:
        """Load quality thresholds from config file"""
        config_file = self.config_dir / "quality_thresholds.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return QualityThresholds(**config)
            except Exception as e:
                print(f"Warning: Failed to load thresholds config, using defaults: {e}")
        
        return QualityThresholds()
    
    def _run_quality_check(self) -> Dict[str, Any]:
        """Run quality check script and return results"""
        self.logger.info("Running quality check...")
        
        quality_check_script = self.scripts_dir / "quality_check.py"
        
        try:
            result = subprocess.run(
                [sys.executable, str(quality_check_script), "--check", "all", "--verbose"],
                capture_output=True,
                text=True,
                cwd=str(self.base_dir)
            )
            
            self.logger.info(f"Quality check completed with return code: {result.returncode}")
            
            output_file = self.reports_dir / f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            subprocess.run(
                [sys.executable, str(quality_check_script), "--check", "all", "--output", str(output_file)],
                capture_output=True,
                cwd=str(self.base_dir)
            )
            
            if output_file.exists():
                with open(output_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Error running quality check: {e}")
            return {}
    
    def _generate_usage_report(self) -> Dict[str, Any]:
        """Generate usage statistics report"""
        self.logger.info("Generating usage report...")
        
        try:
            sys.path.insert(0, str(self.scripts_dir))
            from usage_tracker import UsageTracker
            
            tracker = UsageTracker()
            stats = tracker.analyze_usage_stats()
            
            report_file = self.reports_dir / f"usage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Usage report saved to: {report_file}")
            return stats
            
        except Exception as e:
            self.logger.error(f"Error generating usage report: {e}")
            return {}
    
    def _generate_comprehensive_report(
        self,
        quality_report: Dict[str, Any],
        usage_stats: Dict[str, Any],
        alerts: List[Dict[str, Any]]
    ) -> str:
        """Generate comprehensive report combining all data"""
        report_lines = []
        report_lines.append("="*80)
        report_lines.append("SCHEDULED QUALITY CHECK REPORT")
        report_lines.append("="*80)
        report_lines.append(f"Timestamp: {datetime.now().isoformat()}")
        report_lines.append("")
        
        report_lines.append("--- QUALITY METRICS ---")
        if quality_report:
            report_lines.append(f"Overall Score: {quality_report.get('summary', {}).get('overall_score', 'N/A')}/100")
            report_lines.append(f"Total Skills: {quality_report.get('summary', {}).get('total_skills', 'N/A')}")
            report_lines.append(f"Consistency Issues: {quality_report.get('summary', {}).get('consistency_issues', 'N/A')}")
            report_lines.append(f"Keyword Issues: {quality_report.get('summary', {}).get('keyword_issues', 'N/A')}")
        
        report_lines.append("")
        report_lines.append("--- USAGE METRICS ---")
        if usage_stats:
            report_lines.append(f"Total Invocations: {usage_stats.get('total_invocations', 'N/A')}")
            report_lines.append(f"Overall Success Rate: {usage_stats.get('overall_success_rate', 'N/A')}%")
            report_lines.append(f"Average Execution Time: {usage_stats.get('avg_execution_time', 'N/A')}s")
        
        report_lines.append("")
        report_lines.append("--- ALERTS ---")
        if alerts:
            for alert in alerts:
                report_lines.append(f"[{alert['level'].upper()}] {alert['type']}: {alert['message']}")
        else:
            report_lines.append("No alerts - all metrics within thresholds")
        
        report_lines.append("")
        report_lines.append("="*80)
        
        return "\n".join(report_lines)
    
    def schedule_weekly_check(self) -> bool:
        """Execute weekly quality check"""
        self.logger.info("="*80)
        self.logger.info("STARTING WEEKLY QUALITY CHECK")
        self.logger.info("="*80)
        
        try:
            quality_report = self._run_quality_check()
            usage_stats = self._generate_usage_report()
            
            alerts = self.alert_manager.check_quality_report(quality_report, usage_stats)
            
            comprehensive_report = self._generate_comprehensive_report(
                quality_report,
                usage_stats,
                alerts
            )
            
            report_file = self.reports_dir / f"weekly_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(comprehensive_report)
            
            print(comprehensive_report)
            self.logger.info(f"Weekly report saved to: {report_file}")
            
            self.alert_manager.send_alerts(str(report_file))
            
            self.logger.info("Weekly quality check completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Weekly quality check failed: {e}")
            return False
    
    def schedule_monthly_check(self) -> bool:
        """Execute monthly quality check with extended analysis"""
        self.logger.info("="*80)
        self.logger.info("STARTING MONTHLY QUALITY CHECK")
        self.logger.info("="*80)
        
        try:
            quality_report = self._run_quality_check()
            usage_stats = self._generate_usage_report()
            
            alerts = self.alert_manager.check_quality_report(quality_report, usage_stats)
            
            comprehensive_report = self._generate_comprehensive_report(
                quality_report,
                usage_stats,
                alerts
            )
            
            report_file = self.reports_dir / f"monthly_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(comprehensive_report)
            
            print(comprehensive_report)
            self.logger.info(f"Monthly report saved to: {report_file}")
            
            self.alert_manager.send_alerts(str(report_file))
            
            self.logger.info("Monthly quality check completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Monthly quality check failed: {e}")
            return False
    
    def run_check(self, check_type: str = "weekly") -> bool:
        """Run specified type of quality check"""
        if check_type == "weekly":
            return self.schedule_weekly_check()
        elif check_type == "monthly":
            return self.schedule_monthly_check()
        else:
            self.logger.error(f"Unknown check type: {check_type}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Scheduled quality check for Trae skills"
    )
    parser.add_argument(
        "--type",
        choices=["weekly", "monthly"],
        default="weekly",
        help="Type of scheduled check to run"
    )
    parser.add_argument(
        "--base-dir",
        type=str,
        default=None,
        help="Base directory for skills"
    )
    
    args = parser.parse_args()
    
    checker = ScheduledQualityChecker(base_dir=args.base_dir)
    success = checker.run_check(check_type=args.type)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
