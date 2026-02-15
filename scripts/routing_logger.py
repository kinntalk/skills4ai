import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class RoutingLog:
    timestamp: str
    user_input: str
    matched_type: str
    selected_skill: Optional[str]
    priority: int
    confidence: float
    candidates: List[Dict]
    conflicts: List[Dict]
    resolution_strategy: str
    feedback_history: List[Dict]


@dataclass
class SkillInvocationLog:
    timestamp: str
    skill_name: str
    user_input: str
    context: Dict
    priority: int
    confidence: float
    success: bool
    execution_time: Optional[float] = None


@dataclass
class RoutingFeedbackLog:
    timestamp: str
    original_skill: str
    user_satisfaction: str
    alternative_suggestion: Optional[str]
    new_skill: Optional[str]
    reason: str


class RoutingLogger:
    def __init__(self, log_dir: str = None):
        if log_dir is None:
            log_dir = "D:/workspace1/yusuan/.trae/skills/logs"
        
        self.log_dir = log_dir
        self.routing_log_file = os.path.join(log_dir, "routing_decisions.log")
        self.invocation_log_file = os.path.join(log_dir, "skill_invocations.log")
        self.feedback_log_file = os.path.join(log_dir, "routing_feedback.log")
        
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def log_routing_decision(self, decision: Dict) -> bool:
        try:
            log_entry = RoutingLog(
                timestamp=decision.get("timestamp", datetime.now().isoformat()),
                user_input=decision.get("user_input", ""),
                matched_type=decision.get("matched_type", "unknown"),
                selected_skill=decision.get("selected_skill"),
                priority=decision.get("priority", 10),
                confidence=decision.get("confidence", 0.0),
                candidates=decision.get("candidates", []),
                conflicts=decision.get("conflicts", []),
                resolution_strategy=decision.get("resolution_strategy", "unknown"),
                feedback_history=decision.get("feedback_history", [])
            )
            
            log_line = json.dumps(asdict(log_entry), ensure_ascii=False)
            
            with open(self.routing_log_file, 'a', encoding='utf-8') as f:
                f.write(log_line + '\n')
            
            return True
        except Exception as e:
            print(f"Error logging routing decision: {e}")
            return False
    
    def log_skill_invocation(self, skill: str, context: Dict, success: bool = True, execution_time: float = None) -> bool:
        try:
            log_entry = SkillInvocationLog(
                timestamp=datetime.now().isoformat(),
                skill_name=skill,
                user_input=context.get("user_input", ""),
                context=context,
                priority=context.get("priority", 10),
                confidence=context.get("confidence", 0.0),
                success=success,
                execution_time=execution_time
            )
            
            log_line = json.dumps(asdict(log_entry), ensure_ascii=False)
            
            with open(self.invocation_log_file, 'a', encoding='utf-8') as f:
                f.write(log_line + '\n')
            
            return True
        except Exception as e:
            print(f"Error logging skill invocation: {e}")
            return False
    
    def log_routing_feedback(self, feedback: Dict) -> bool:
        try:
            log_entry = RoutingFeedbackLog(
                timestamp=feedback.get("timestamp", datetime.now().isoformat()),
                original_skill=feedback.get("original_skill", ""),
                user_satisfaction=feedback.get("user_satisfaction", "neutral"),
                alternative_suggestion=feedback.get("alternative_suggestion"),
                new_skill=feedback.get("new_skill"),
                reason=feedback.get("reason", "")
            )
            
            log_line = json.dumps(asdict(log_entry), ensure_ascii=False)
            
            with open(self.feedback_log_file, 'a', encoding='utf-8') as f:
                f.write(log_line + '\n')
            
            return True
        except Exception as e:
            print(f"Error logging routing feedback: {e}")
            return False
    
    def _read_log_file(self, log_file: str) -> List[Dict]:
        if not os.path.exists(log_file):
            return []
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            logs = []
            for line in lines:
                try:
                    log_entry = json.loads(line.strip())
                    logs.append(log_entry)
                except json.JSONDecodeError:
                    continue
            
            return logs
        except Exception as e:
            print(f"Error reading log file {log_file}: {e}")
            return []
    
    def generate_routing_report(self, days: int = 7) -> Dict:
        routing_logs = self._read_log_file(self.routing_log_file)
        invocation_logs = self._read_log_file(self.invocation_log_file)
        feedback_logs = self._read_log_file(self.feedback_log_file)
        
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        filtered_routing = [
            log for log in routing_logs
            if datetime.fromisoformat(log['timestamp']).timestamp() > cutoff_date
        ]
        
        filtered_invocation = [
            log for log in invocation_logs
            if datetime.fromisoformat(log['timestamp']).timestamp() > cutoff_date
        ]
        
        filtered_feedback = [
            log for log in feedback_logs
            if datetime.fromisoformat(log['timestamp']).timestamp() > cutoff_date
        ]
        
        routing_stats = self._calculate_routing_stats(filtered_routing)
        invocation_stats = self._calculate_invocation_stats(filtered_invocation)
        feedback_stats = self._calculate_feedback_stats(filtered_feedback)
        
        report = {
            "report_generated": datetime.now().isoformat(),
            "period_days": days,
            "routing_statistics": routing_stats,
            "invocation_statistics": invocation_stats,
            "feedback_statistics": feedback_stats,
            "recommendations": self._generate_recommendations(
                routing_stats, invocation_stats, feedback_stats
            )
        }
        
        return report
    
    def _calculate_routing_stats(self, logs: List[Dict]) -> Dict:
        if not logs:
            return {
                "total_decisions": 0,
                "matched_type_distribution": {},
                "average_confidence": 0.0,
                "average_priority": 0.0,
                "conflict_rate": 0.0,
                "resolution_strategy_distribution": {},
                "top_selected_skills": {}
            }
        
        total_decisions = len(logs)
        
        matched_type_counts = {}
        total_confidence = 0.0
        total_priority = 0
        conflict_count = 0
        resolution_strategy_counts = {}
        skill_selection_counts = {}
        
        for log in logs:
            matched_type = log.get("matched_type", "unknown")
            matched_type_counts[matched_type] = matched_type_counts.get(matched_type, 0) + 1
            
            total_confidence += log.get("confidence", 0.0)
            total_priority += log.get("priority", 10)
            
            if log.get("conflicts"):
                conflict_count += 1
            
            resolution_strategy = log.get("resolution_strategy", "unknown")
            resolution_strategy_counts[resolution_strategy] = resolution_strategy_counts.get(resolution_strategy, 0) + 1
            
            selected_skill = log.get("selected_skill")
            if selected_skill:
                skill_selection_counts[selected_skill] = skill_selection_counts.get(selected_skill, 0) + 1
        
        top_skills = dict(sorted(
            skill_selection_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10])
        
        return {
            "total_decisions": total_decisions,
            "matched_type_distribution": matched_type_counts,
            "average_confidence": total_confidence / total_decisions,
            "average_priority": total_priority / total_decisions,
            "conflict_rate": conflict_count / total_decisions,
            "resolution_strategy_distribution": resolution_strategy_counts,
            "top_selected_skills": top_skills
        }
    
    def _calculate_invocation_stats(self, logs: List[Dict]) -> Dict:
        if not logs:
            return {
                "total_invocations": 0,
                "success_rate": 0.0,
                "average_execution_time": 0.0,
                "top_invoked_skills": {},
                "skill_success_rates": {}
            }
        
        total_invocations = len(logs)
        success_count = 0
        total_execution_time = 0.0
        execution_time_count = 0
        skill_invocation_counts = {}
        skill_success_counts = {}
        
        for log in logs:
            skill_name = log.get("skill_name", "unknown")
            skill_invocation_counts[skill_name] = skill_invocation_counts.get(skill_name, 0) + 1
            
            if log.get("success", False):
                success_count += 1
                skill_success_counts[skill_name] = skill_success_counts.get(skill_name, 0) + 1
            
            execution_time = log.get("execution_time")
            if execution_time is not None:
                total_execution_time += execution_time
                execution_time_count += 1
        
        top_skills = dict(sorted(
            skill_invocation_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10])
        
        skill_success_rates = {}
        for skill_name in skill_invocation_counts:
            total = skill_invocation_counts[skill_name]
            successes = skill_success_counts.get(skill_name, 0)
            skill_success_rates[skill_name] = successes / total if total > 0 else 0.0
        
        return {
            "total_invocations": total_invocations,
            "success_rate": success_count / total_invocations,
            "average_execution_time": total_execution_time / execution_time_count if execution_time_count > 0 else 0.0,
            "top_invoked_skills": top_skills,
            "skill_success_rates": skill_success_rates
        }
    
    def _calculate_feedback_stats(self, logs: List[Dict]) -> Dict:
        if not logs:
            return {
                "total_feedback": 0,
                "satisfaction_distribution": {},
                "re_routing_rate": 0.0,
                "common_alternatives": {}
            }
        
        total_feedback = len(logs)
        satisfaction_counts = {}
        re_routing_count = 0
        alternative_counts = {}
        
        for log in logs:
            satisfaction = log.get("user_satisfaction", "neutral")
            satisfaction_counts[satisfaction] = satisfaction_counts.get(satisfaction, 0) + 1
            
            if log.get("new_skill"):
                re_routing_count += 1
            
            alternative = log.get("alternative_suggestion")
            if alternative:
                alternative_counts[alternative] = alternative_counts.get(alternative, 0) + 1
        
        common_alternatives = dict(sorted(
            alternative_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10])
        
        return {
            "total_feedback": total_feedback,
            "satisfaction_distribution": satisfaction_counts,
            "re_routing_rate": re_routing_count / total_feedback,
            "common_alternatives": common_alternatives
        }
    
    def _generate_recommendations(self, routing_stats: Dict, invocation_stats: Dict, feedback_stats: Dict) -> List[str]:
        recommendations = []
        
        if routing_stats.get("conflict_rate", 0) > 0.3:
            recommendations.append(
                "High conflict rate detected. Consider reviewing and refining routing rules to reduce conflicts."
            )
        
        if routing_stats.get("average_confidence", 0) < 0.6:
            recommendations.append(
                "Low average confidence in routing decisions. Consider improving keyword matching and context detection."
            )
        
        if invocation_stats.get("success_rate", 0) < 0.8:
            recommendations.append(
                "Low skill invocation success rate. Review skill implementations and error handling."
            )
        
        if feedback_stats.get("re_routing_rate", 0) > 0.2:
            recommendations.append(
                "High re-routing rate based on user feedback. Consider adjusting priority rules or improving initial routing."
            )
        
        low_satisfaction = feedback_stats.get("satisfaction_distribution", {}).get("low", 0)
        total_feedback = feedback_stats.get("total_feedback", 1)
        if low_satisfaction / total_feedback > 0.3:
            recommendations.append(
                "High rate of low satisfaction feedback. Collect more detailed feedback to understand user needs."
            )
        
        if not recommendations:
            recommendations.append("Routing system is performing well. Continue monitoring for any changes.")
        
        return recommendations
    
    def export_report(self, report: Dict, output_file: str = None) -> bool:
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.log_dir, f"routing_report_{timestamp}.json")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting report: {e}")
            return False
    
    def clear_old_logs(self, days: int = 30) -> int:
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        files_to_clear = [
            self.routing_log_file,
            self.invocation_log_file,
            self.feedback_log_file
        ]
        
        total_cleared = 0
        
        for log_file in files_to_clear:
            if not os.path.exists(log_file):
                continue
            
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                filtered_lines = []
                for line in lines:
                    try:
                        log_entry = json.loads(line.strip())
                        log_timestamp = datetime.fromisoformat(log_entry['timestamp']).timestamp()
                        if log_timestamp > cutoff_date:
                            filtered_lines.append(line)
                    except (json.JSONDecodeError, KeyError):
                        continue
                
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.writelines(filtered_lines)
                
                total_cleared += len(lines) - len(filtered_lines)
            except Exception as e:
                print(f"Error clearing old logs from {log_file}: {e}")
        
        return total_cleared


def main():
    import sys
    
    logger = RoutingLogger()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "report":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            report = logger.generate_routing_report(days)
            
            print("\n" + "=" * 60)
            print("ROUTING SYSTEM REPORT")
            print("=" * 60)
            print(f"Period: Last {days} days")
            print(f"Generated: {report['report_generated']}")
            
            print("\n--- Routing Statistics ---")
            routing = report['routing_statistics']
            print(f"Total Decisions: {routing['total_decisions']}")
            print(f"Average Confidence: {routing['average_confidence']:.2f}")
            print(f"Average Priority: {routing['average_priority']:.2f}")
            print(f"Conflict Rate: {routing['conflict_rate']:.2%}")
            
            print("\n--- Invocation Statistics ---")
            invocation = report['invocation_statistics']
            print(f"Total Invocations: {invocation['total_invocations']}")
            print(f"Success Rate: {invocation['success_rate']:.2%}")
            print(f"Average Execution Time: {invocation['average_execution_time']:.2f}s")
            
            print("\n--- Feedback Statistics ---")
            feedback = report['feedback_statistics']
            print(f"Total Feedback: {feedback['total_feedback']}")
            print(f"Re-routing Rate: {feedback['re_routing_rate']:.2%}")
            
            print("\n--- Recommendations ---")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"{i}. {rec}")
            
            print("=" * 60 + "\n")
            
            if len(sys.argv) > 3 and sys.argv[3] == "--export":
                output_file = sys.argv[4] if len(sys.argv) > 4 else None
                if logger.export_report(report, output_file):
                    print(f"Report exported successfully")
                else:
                    print("Failed to export report")
        
        elif command == "clear":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            cleared = logger.clear_old_logs(days)
            print(f"Cleared {cleared} old log entries (older than {days} days)")
        
        else:
            print("Usage:")
            print("  python routing_logger.py report [days] [--export [output_file]]")
            print("  python routing_logger.py clear [days]")
    else:
        print("Routing Logger - Log and analyze routing decisions")
        print("\nUsage:")
        print("  python routing_logger.py report [days] [--export [output_file]]")
        print("  python routing_logger.py clear [days]")


if __name__ == "__main__":
    main()
