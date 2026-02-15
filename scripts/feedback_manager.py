import sys
import os
import json
from typing import Dict, List, Optional
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from context_aware_router import ContextAwareRouter, RoutingDecision
from routing_logger import RoutingLogger


class FeedbackManager:
    def __init__(self, skill_map_path: str = None, log_dir: str = None):
        self.router = ContextAwareRouter(skill_map_path)
        self.logger = RoutingLogger(log_dir)
        self.skill_map = self.router.skill_map
    
    def submit_feedback(
        self,
        user_input: str,
        original_skill: str,
        user_satisfaction: str,
        alternative_suggestion: Optional[str] = None,
        reason: str = ""
    ) -> Dict:
        if user_satisfaction not in ["satisfied", "unsatisfied", "neutral"]:
            return {
                "success": False,
                "message": f"Invalid satisfaction level: {user_satisfaction}. Must be 'satisfied', 'unsatisfied', or 'neutral'"
            }
        
        if original_skill not in self.skill_map:
            return {
                "success": False,
                "message": f"Original skill '{original_skill}' not found in skill map"
            }
        
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "original_skill": original_skill,
            "user_satisfaction": user_satisfaction,
            "alternative_suggestion": alternative_suggestion,
            "reason": reason
        }
        
        logged = self.logger.log_routing_feedback(feedback_entry)
        
        if logged:
            return {
                "success": True,
                "message": "Feedback submitted successfully",
                "feedback": feedback_entry
            }
        else:
            return {
                "success": False,
                "message": "Failed to log feedback"
            }
    
    def route_with_feedback(
        self,
        user_input: str,
        previous_feedback: Optional[Dict] = None
    ) -> RoutingDecision:
        feedback = None
        if previous_feedback:
            feedback = {
                "history": previous_feedback.get("history", []),
                "previous_skill": previous_feedback.get("previous_skill"),
                "satisfaction": previous_feedback.get("satisfaction"),
                "alternative_suggestion": previous_feedback.get("alternative_suggestion")
            }
        
        routing_decision = self.router.route_with_feedback(user_input, feedback)
        
        self.logger.log_routing_decision({
            "user_input": user_input,
            "matched_type": routing_decision.matched_type,
            "selected_skill": routing_decision.selected_skill,
            "priority": routing_decision.priority,
            "confidence": routing_decision.confidence,
            "candidates": routing_decision.candidates,
            "conflicts": routing_decision.conflicts,
            "resolution_strategy": routing_decision.resolution_strategy,
            "timestamp": routing_decision.timestamp,
            "feedback_history": routing_decision.feedback_history
        })
        
        return routing_decision
    
    def query_feedback(
        self,
        skill_name: Optional[str] = None,
        satisfaction: Optional[str] = None,
        days: int = 7
    ) -> Dict:
        feedback_logs = self.logger._read_log_file(self.logger.feedback_log_file)
        
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        filtered_feedback = []
        for log in feedback_logs:
            try:
                log_timestamp = datetime.fromisoformat(log['timestamp']).timestamp()
                if log_timestamp <= cutoff_date:
                    continue
                
                if skill_name and log.get("original_skill") != skill_name:
                    continue
                
                if satisfaction and log.get("user_satisfaction") != satisfaction:
                    continue
                
                filtered_feedback.append(log)
            except (KeyError, ValueError):
                continue
        
        stats = self._calculate_feedback_stats(filtered_feedback)
        
        return {
            "query": {
                "skill_name": skill_name,
                "satisfaction": satisfaction,
                "period_days": days
            },
            "total_feedback": len(filtered_feedback),
            "statistics": stats,
            "feedback_entries": filtered_feedback
        }
    
    def _calculate_feedback_stats(self, feedback_logs: List[Dict]) -> Dict:
        if not feedback_logs:
            return {
                "satisfaction_distribution": {},
                "re_routing_rate": 0.0,
                "common_alternatives": {},
                "common_reasons": {}
            }
        
        satisfaction_counts = {}
        re_routing_count = 0
        alternative_counts = {}
        reason_counts = {}
        
        for log in feedback_logs:
            satisfaction = log.get("user_satisfaction", "neutral")
            satisfaction_counts[satisfaction] = satisfaction_counts.get(satisfaction, 0) + 1
            
            if log.get("new_skill"):
                re_routing_count += 1
            
            alternative = log.get("alternative_suggestion")
            if alternative:
                alternative_counts[alternative] = alternative_counts.get(alternative, 0) + 1
            
            reason = log.get("reason", "")
            if reason:
                reason_counts[reason] = reason_counts.get(reason, 0) + 1
        
        common_alternatives = dict(sorted(
            alternative_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10])
        
        common_reasons = dict(sorted(
            reason_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10])
        
        return {
            "satisfaction_distribution": satisfaction_counts,
            "re_routing_rate": re_routing_count / len(feedback_logs),
            "common_alternatives": common_alternatives,
            "common_reasons": common_reasons
        }
    
    def get_feedback_summary(self, days: int = 7) -> Dict:
        report = self.logger.generate_routing_report(days)
        feedback_stats = report.get("feedback_statistics", {})
        
        return {
            "period_days": days,
            "total_feedback": feedback_stats.get("total_feedback", 0),
            "satisfaction_distribution": feedback_stats.get("satisfaction_distribution", {}),
            "re_routing_rate": feedback_stats.get("re_routing_rate", 0.0),
            "common_alternatives": feedback_stats.get("common_alternatives", {}),
            "recommendations": report.get("recommendations", [])
        }
    
    def export_feedback_report(self, output_file: str = None, days: int = 7) -> bool:
        summary = self.get_feedback_summary(days)
        detailed_query = self.query_feedback(days=days)
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": summary,
            "detailed_feedback": detailed_query
        }
        
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(
                self.logger.log_dir,
                f"feedback_report_{timestamp}.json"
            )
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting feedback report: {e}")
            return False
    
    def print_feedback_summary(self, days: int = 7):
        summary = self.get_feedback_summary(days)
        
        print("\n" + "="*60)
        print(f"FEEDBACK SUMMARY - Last {days} days")
        print("="*60)
        print(f"Total Feedback: {summary['total_feedback']}")
        
        print("\n--- Satisfaction Distribution ---")
        for satisfaction, count in summary['satisfaction_distribution'].items():
            percentage = (count / summary['total_feedback'] * 100) if summary['total_feedback'] > 0 else 0
            print(f"  {satisfaction}: {count} ({percentage:.1f}%)")
        
        print(f"\n--- Re-routing Rate ---")
        print(f"  {summary['re_routing_rate']:.2%}")
        
        if summary['common_alternatives']:
            print("\n--- Common Alternative Suggestions ---")
            for alt, count in list(summary['common_alternatives'].items())[:5]:
                print(f"  {alt}: {count}")
        
        if summary['recommendations']:
            print("\n--- Recommendations ---")
            for i, rec in enumerate(summary['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        print("="*60 + "\n")
    
    def print_feedback_query_result(self, result: Dict):
        print("\n" + "="*60)
        print("FEEDBACK QUERY RESULT")
        print("="*60)
        
        query = result["query"]
        print(f"Query Parameters:")
        print(f"  Skill: {query['skill_name'] or 'All'}")
        print(f"  Satisfaction: {query['satisfaction'] or 'All'}")
        print(f"  Period: Last {query['period_days']} days")
        
        print(f"\nTotal Feedback Entries: {result['total_feedback']}")
        
        stats = result["statistics"]
        print("\n--- Statistics ---")
        print(f"Satisfaction Distribution:")
        for satisfaction, count in stats['satisfaction_distribution'].items():
            print(f"  {satisfaction}: {count}")
        
        print(f"\nRe-routing Rate: {stats['re_routing_rate']:.2%}")
        
        if result['feedback_entries']:
            print(f"\n--- Feedback Entries ({len(result['feedback_entries'])}) ---")
            for i, entry in enumerate(result['feedback_entries'][:10], 1):
                print(f"\n{i}. {entry['timestamp']}")
                print(f"   Original Skill: {entry['original_skill']}")
                print(f"   Satisfaction: {entry['user_satisfaction']}")
                if entry.get('alternative_suggestion'):
                    print(f"   Alternative: {entry['alternative_suggestion']}")
                if entry.get('reason'):
                    print(f"   Reason: {entry['reason']}")
            
            if len(result['feedback_entries']) > 10:
                print(f"\n... and {len(result['feedback_entries']) - 10} more entries")
        
        print("="*60 + "\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Feedback Manager - Submit and query routing feedback"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    submit_parser = subparsers.add_parser("submit", help="Submit feedback")
    submit_parser.add_argument("--input", required=True, help="User input")
    submit_parser.add_argument("--skill", required=True, help="Original skill name")
    submit_parser.add_argument("--satisfaction", required=True, 
                              choices=["satisfied", "unsatisfied", "neutral"],
                              help="User satisfaction level")
    submit_parser.add_argument("--alternative", help="Alternative skill suggestion")
    submit_parser.add_argument("--reason", help="Reason for feedback")
    
    route_parser = subparsers.add_parser("route", help="Route with feedback")
    route_parser.add_argument("--input", required=True, help="User input")
    route_parser.add_argument("--feedback-file", help="JSON file with previous feedback")
    
    query_parser = subparsers.add_parser("query", help="Query feedback")
    query_parser.add_argument("--skill", help="Filter by skill name")
    query_parser.add_argument("--satisfaction", 
                             choices=["satisfied", "unsatisfied", "neutral"],
                             help="Filter by satisfaction level")
    query_parser.add_argument("--days", type=int, default=7, 
                            help="Query period in days (default: 7)")
    
    summary_parser = subparsers.add_parser("summary", help="Get feedback summary")
    summary_parser.add_argument("--days", type=int, default=7,
                               help="Summary period in days (default: 7)")
    
    export_parser = subparsers.add_parser("export", help="Export feedback report")
    export_parser.add_argument("--output", help="Output file path")
    export_parser.add_argument("--days", type=int, default=7,
                              help="Report period in days (default: 7)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = FeedbackManager()
    
    if args.command == "submit":
        result = manager.submit_feedback(
            user_input=args.input,
            original_skill=args.skill,
            user_satisfaction=args.satisfaction,
            alternative_suggestion=args.alternative,
            reason=args.reason or ""
        )
        
        if result["success"]:
            print(f"\n✓ {result['message']}")
            print(f"  User Input: {result['feedback']['user_input']}")
            print(f"  Original Skill: {result['feedback']['original_skill']}")
            print(f"  Satisfaction: {result['feedback']['user_satisfaction']}")
            if result['feedback'].get('alternative_suggestion'):
                print(f"  Alternative: {result['feedback']['alternative_suggestion']}")
            if result['feedback'].get('reason'):
                print(f"  Reason: {result['feedback']['reason']}")
            print(f"  Timestamp: {result['feedback']['timestamp']}")
        else:
            print(f"\n✗ {result['message']}")
    
    elif args.command == "route":
        previous_feedback = None
        if args.feedback_file:
            try:
                with open(args.feedback_file, 'r', encoding='utf-8') as f:
                    previous_feedback = json.load(f)
            except Exception as e:
                print(f"Error loading feedback file: {e}")
                return
        
        routing_decision = manager.route_with_feedback(args.input, previous_feedback)
        
        print("\n" + "="*60)
        print("ROUTING DECISION WITH FEEDBACK")
        print("="*60)
        print(f"User Input: {args.input}")
        print(f"Selected Skill: {routing_decision.selected_skill or 'None'}")
        print(f"Matched Type: {routing_decision.matched_type}")
        print(f"Priority: {routing_decision.priority}")
        print(f"Confidence: {routing_decision.confidence:.2f}")
        print(f"Resolution Strategy: {routing_decision.resolution_strategy}")
        
        if routing_decision.feedback_history:
            print(f"\n--- Feedback History ---")
            for i, feedback in enumerate(routing_decision.feedback_history, 1):
                print(f"{i}. Previous Skill: {feedback.get('previous_skill')}")
                print(f"   Satisfaction: {feedback.get('satisfaction')}")
                print(f"   New Selection: {feedback.get('new_selection')}")
        
        print("="*60 + "\n")
    
    elif args.command == "query":
        result = manager.query_feedback(
            skill_name=args.skill,
            satisfaction=args.satisfaction,
            days=args.days
        )
        manager.print_feedback_query_result(result)
    
    elif args.command == "summary":
        manager.print_feedback_summary(args.days)
    
    elif args.command == "export":
        success = manager.export_feedback_report(args.output, args.days)
        if success:
            print(f"\n✓ Feedback report exported successfully")
        else:
            print(f"\n✗ Failed to export feedback report")


if __name__ == "__main__":
    main()
