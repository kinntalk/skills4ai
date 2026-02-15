import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class UsageTracker:
    def __init__(self, stats_file: str = None):
        if stats_file is None:
            self.stats_file = Path(__file__).parent.parent / "skill_usage_stats.json"
        else:
            self.stats_file = Path(stats_file)
        
        self.stats_data = self._load_stats()

    def _load_stats(self) -> Dict[str, Any]:
        if not self.stats_file.exists():
            return {
                "version": "1.0.0",
                "last_updated": None,
                "skills": {}
            }
        
        with open(self.stats_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_stats(self):
        self.stats_data["last_updated"] = datetime.now().isoformat()
        
        self.stats_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats_data, f, indent=2, ensure_ascii=False)

    def record_invocation(self, skill: str, context: Dict[str, Any], result: Dict[str, Any]) -> bool:
        try:
            start_time = context.get('start_time', datetime.now().isoformat())
            end_time = datetime.now().isoformat()
            
            execution_time = self._calculate_execution_time(start_time, end_time)
            success = result.get('success', True)
            
            if skill not in self.stats_data["skills"]:
                self.stats_data["skills"][skill] = {
                    "invocations": 0,
                    "success_count": 0,
                    "failure_count": 0,
                    "total_execution_time": 0.0,
                    "last_used": None,
                    "first_used": None,
                    "execution_history": []
                }
            
            skill_stats = self.stats_data["skills"][skill]
            skill_stats["invocations"] += 1
            skill_stats["total_execution_time"] += execution_time
            
            if success:
                skill_stats["success_count"] += 1
            else:
                skill_stats["failure_count"] += 1
            
            skill_stats["last_used"] = end_time
            if skill_stats["first_used"] is None:
                skill_stats["first_used"] = start_time
            
            skill_stats["execution_history"].append({
                "timestamp": end_time,
                "execution_time": execution_time,
                "success": success,
                "context": {
                    "user": context.get('user', 'unknown'),
                    "session": context.get('session', 'unknown')
                }
            })
            
            if len(skill_stats["execution_history"]) > 100:
                skill_stats["execution_history"] = skill_stats["execution_history"][-100:]
            
            self._save_stats()
            return True
            
        except Exception as e:
            print(f"Error recording invocation: {e}")
            return False

    def _calculate_execution_time(self, start_time: str, end_time: str) -> float:
        try:
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            return (end - start).total_seconds()
        except:
            return 0.0

    def calculate_success_rate(self, skill: str) -> float:
        if skill not in self.stats_data["skills"]:
            return 0.0
        
        skill_stats = self.stats_data["skills"][skill]
        total = skill_stats["success_count"] + skill_stats["failure_count"]
        
        if total == 0:
            return 0.0
        
        return (skill_stats["success_count"] / total) * 100

    def calculate_avg_execution_time(self, skill: str) -> float:
        if skill not in self.stats_data["skills"]:
            return 0.0
        
        skill_stats = self.stats_data["skills"][skill]
        if skill_stats["invocations"] == 0:
            return 0.0
        
        return skill_stats["total_execution_time"] / skill_stats["invocations"]

    def get_most_used_skills(self, limit: int = 10) -> List[Dict[str, Any]]:
        skills_list = []
        
        for skill_name, stats in self.stats_data["skills"].items():
            skills_list.append({
                "name": skill_name,
                "invocations": stats["invocations"],
                "success_rate": self.calculate_success_rate(skill_name),
                "avg_execution_time": self.calculate_avg_execution_time(skill_name),
                "last_used": stats["last_used"]
            })
        
        skills_list.sort(key=lambda x: x["invocations"], reverse=True)
        return skills_list[:limit]

    def get_least_used_skills(self, limit: int = 10) -> List[Dict[str, Any]]:
        skills_list = []
        
        for skill_name, stats in self.stats_data["skills"].items():
            skills_list.append({
                "name": skill_name,
                "invocations": stats["invocations"],
                "success_rate": self.calculate_success_rate(skill_name),
                "avg_execution_time": self.calculate_avg_execution_time(skill_name),
                "last_used": stats["last_used"]
            })
        
        skills_list.sort(key=lambda x: x["invocations"])
        return skills_list[:limit]

    def analyze_usage_stats(self) -> Dict[str, Any]:
        total_invocations = 0
        total_success = 0
        total_failures = 0
        total_execution_time = 0.0
        
        skill_count = len(self.stats_data["skills"])
        
        for skill_name, stats in self.stats_data["skills"].items():
            total_invocations += stats["invocations"]
            total_success += stats["success_count"]
            total_failures += stats["failure_count"]
            total_execution_time += stats["total_execution_time"]
        
        overall_success_rate = 0.0
        if total_invocations > 0:
            overall_success_rate = (total_success / total_invocations) * 100
        
        avg_execution_time = 0.0
        if total_invocations > 0:
            avg_execution_time = total_execution_time / total_invocations
        
        return {
            "total_skills": skill_count,
            "total_invocations": total_invocations,
            "total_success": total_success,
            "total_failures": total_failures,
            "overall_success_rate": round(overall_success_rate, 2),
            "avg_execution_time": round(avg_execution_time, 2),
            "last_updated": self.stats_data["last_updated"]
        }

    def generate_usage_report(self) -> str:
        analysis = self.analyze_usage_stats()
        most_used = self.get_most_used_skills(5)
        least_used = self.get_least_used_skills(5)
        
        report = []
        report.append("=" * 80)
        report.append("技能使用统计报告")
        report.append("=" * 80)
        report.append("")
        
        report.append("【总体统计】")
        report.append(f"总技能数: {analysis['total_skills']}")
        report.append(f"总调用次数: {analysis['total_invocations']}")
        report.append(f"成功次数: {analysis['total_success']}")
        report.append(f"失败次数: {analysis['total_failures']}")
        report.append(f"整体成功率: {analysis['overall_success_rate']}%")
        report.append(f"平均执行时间: {analysis['avg_execution_time']}秒")
        report.append(f"最后更新: {analysis['last_updated']}")
        report.append("")
        
        report.append("【最常用技能 TOP 5】")
        for i, skill in enumerate(most_used, 1):
            report.append(f"{i}. {skill['name']}")
            report.append(f"   调用次数: {skill['invocations']}")
            report.append(f"   成功率: {skill['success_rate']}%")
            report.append(f"   平均执行时间: {skill['avg_execution_time']}秒")
            report.append(f"   最后使用: {skill['last_used']}")
            report.append("")
        
        report.append("【最少使用技能 TOP 5】")
        for i, skill in enumerate(least_used, 1):
            report.append(f"{i}. {skill['name']}")
            report.append(f"   调用次数: {skill['invocations']}")
            report.append(f"   成功率: {skill['success_rate']}%")
            report.append(f"   平均执行时间: {skill['avg_execution_time']}秒")
            report.append(f"   最后使用: {skill['last_used']}")
            report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)

    def get_skill_stats(self, skill: str) -> Optional[Dict[str, Any]]:
        if skill not in self.stats_data["skills"]:
            return None
        
        stats = self.stats_data["skills"][skill]
        return {
            "name": skill,
            "invocations": stats["invocations"],
            "success_count": stats["success_count"],
            "failure_count": stats["failure_count"],
            "success_rate": self.calculate_success_rate(skill),
            "total_execution_time": stats["total_execution_time"],
            "avg_execution_time": self.calculate_avg_execution_time(skill),
            "first_used": stats["first_used"],
            "last_used": stats["last_used"],
            "execution_history": stats["execution_history"]
        }

    def get_all_skills(self) -> List[str]:
        return list(self.stats_data["skills"].keys())


def record_invocation(skill: str, context: Dict[str, Any], result: Dict[str, Any]) -> bool:
    tracker = UsageTracker()
    return tracker.record_invocation(skill, context, result)


def analyze_usage_stats() -> Dict[str, Any]:
    tracker = UsageTracker()
    return tracker.analyze_usage_stats()


def calculate_success_rate(skill: str) -> float:
    tracker = UsageTracker()
    return tracker.calculate_success_rate(skill)


def get_most_used_skills(limit: int = 10) -> List[Dict[str, Any]]:
    tracker = UsageTracker()
    return tracker.get_most_used_skills(limit)


def get_least_used_skills(limit: int = 10) -> List[Dict[str, Any]]:
    tracker = UsageTracker()
    return tracker.get_least_used_skills(limit)


def generate_usage_report() -> str:
    tracker = UsageTracker()
    return tracker.generate_usage_report()