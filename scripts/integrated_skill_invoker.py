import sys
import os
import json
from typing import Dict, Optional
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from context_aware_router import ContextAwareRouter, RoutingDecision
from routing_logger import RoutingLogger


class IntegratedSkillInvoker:
    def __init__(self, skill_map_path: str = None, log_dir: str = None):
        self.router = ContextAwareRouter(skill_map_path)
        self.logger = RoutingLogger(log_dir)
        self.skill_map = self.router.skill_map
    
    def invoke_with_routing(self, user_input: str, dry_run: bool = True) -> Dict:
        routing_decision = self.router.route_with_priority(user_input)
        
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
        
        result = {
            "user_input": user_input,
            "routing_decision": {
                "matched_type": routing_decision.matched_type,
                "selected_skill": routing_decision.selected_skill,
                "priority": routing_decision.priority,
                "confidence": routing_decision.confidence,
                "resolution_strategy": routing_decision.resolution_strategy,
                "timestamp": routing_decision.timestamp
            },
            "candidates": routing_decision.candidates,
            "conflicts": routing_decision.conflicts,
            "invocation_command": None,
            "skill_details": None,
            "success": False,
            "message": ""
        }
        
        if routing_decision.selected_skill:
            skill_name = routing_decision.selected_skill
            skill_info = self.skill_map.get(skill_name, {})
            
            result["skill_details"] = {
                "name": skill_name,
                "path": skill_info.get("path", ""),
                "keywords": skill_info.get("keywords", []),
                "context": skill_info.get("context", {}),
                "description": skill_info.get("description", "")
            }
            
            invocation_command = self._generate_invocation_command(skill_name, skill_info, user_input)
            result["invocation_command"] = invocation_command
            
            if dry_run:
                result["success"] = True
                result["message"] = f"Skill '{skill_name}' would be invoked (dry run mode)"
            else:
                success = self._execute_skill(skill_name, skill_info, user_input, routing_decision)
                result["success"] = success
                result["message"] = f"Skill '{skill_name}' {'invoked successfully' if success else 'invocation failed'}"
                
                self.logger.log_skill_invocation(
                    skill_name,
                    {
                        "user_input": user_input,
                        "priority": routing_decision.priority,
                        "confidence": routing_decision.confidence,
                        "routing_decision": routing_decision.selected_skill
                    },
                    success=success
                )
        else:
            result["message"] = "No suitable skill found for the given input"
            result["success"] = False
        
        return result
    
    def _generate_invocation_command(self, skill_name: str, skill_info: Dict, user_input: str) -> str:
        skill_path = skill_info.get("path", "")
        keywords = skill_info.get("keywords", [])
        
        if not skill_path:
            return f"# No path defined for skill '{skill_name}'"
        
        if skill_path.endswith(".py"):
            return f"python {skill_path} \"{user_input}\""
        elif skill_path.endswith(".md"):
            return f"# Reference skill documentation: {skill_path}"
        else:
            return f"# Unknown skill type for '{skill_name}' at {skill_path}"
    
    def _execute_skill(self, skill_name: str, skill_info: Dict, user_input: str, routing_decision: RoutingDecision) -> bool:
        skill_path = skill_info.get("path", "")
        
        if not skill_path:
            print(f"Warning: No path defined for skill '{skill_name}'")
            return False
        
        if not os.path.exists(skill_path):
            print(f"Warning: Skill path does not exist: {skill_path}")
            return False
        
        print(f"\n{'='*60}")
        print(f"Invoking Skill: {skill_name}")
        print(f"{'='*60}")
        print(f"Path: {skill_path}")
        print(f"User Input: {user_input}")
        print(f"Priority: {routing_decision.priority}")
        print(f"Confidence: {routing_decision.confidence:.2f}")
        print(f"{'='*60}\n")
        
        if skill_path.endswith(".py"):
            try:
                import subprocess
                result = subprocess.run(
                    [sys.executable, skill_path, user_input],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(f"Error output:\n{result.stderr}")
                
                return result.returncode == 0
            except subprocess.TimeoutExpired:
                print("Error: Skill execution timed out")
                return False
            except Exception as e:
                print(f"Error executing skill: {e}")
                return False
        else:
            print(f"Skill '{skill_name}' is not executable (path: {skill_path})")
            print("Please invoke the skill manually or update the skill configuration.")
            return True
    
    def batch_invoke(self, inputs: list, dry_run: bool = True) -> Dict:
        results = []
        success_count = 0
        failure_count = 0
        
        for user_input in inputs:
            result = self.invoke_with_routing(user_input, dry_run)
            results.append(result)
            
            if result["success"]:
                success_count += 1
            else:
                failure_count += 1
        
        return {
            "total_inputs": len(inputs),
            "success_count": success_count,
            "failure_count": failure_count,
            "success_rate": success_count / len(inputs) if inputs else 0.0,
            "results": results
        }
    
    def print_result(self, result: Dict):
        print("\n" + "="*60)
        print("SKILL ROUTING & INVOCATION RESULT")
        print("="*60)
        print(f"User Input: {result['user_input']}")
        
        routing = result["routing_decision"]
        print(f"\n--- Routing Decision ---")
        print(f"Matched Type: {routing['matched_type']}")
        print(f"Selected Skill: {routing['selected_skill'] or 'None'}")
        print(f"Priority: {routing['priority']}")
        print(f"Confidence: {routing['confidence']:.2f}")
        print(f"Resolution Strategy: {routing['resolution_strategy']}")
        print(f"Timestamp: {routing['timestamp']}")
        
        if result["candidates"]:
            print(f"\n--- Candidates ({len(result['candidates'])}) ---")
            for i, candidate in enumerate(result["candidates"], 1):
                print(f"{i}. {candidate['skill_name']} (priority: {candidate['priority']}, confidence: {candidate['confidence']:.2f})")
        
        if result["conflicts"]:
            print(f"\n--- Conflicts ({len(result['conflicts'])}) ---")
            for i, conflict in enumerate(result["conflicts"], 1):
                print(f"{i}. {conflict['conflict_type']}: {conflict['description']}")
        
        if result["skill_details"]:
            print(f"\n--- Skill Details ---")
            details = result["skill_details"]
            print(f"Name: {details['name']}")
            print(f"Path: {details['path']}")
            print(f"Keywords: {', '.join(details['keywords'])}")
            print(f"Description: {details['description']}")
        
        if result["invocation_command"]:
            print(f"\n--- Invocation Command ---")
            print(result["invocation_command"])
        
        print(f"\n--- Result ---")
        print(f"Success: {result['success']}")
        print(f"Message: {result['message']}")
        print("="*60 + "\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Integrated Skill Invoker - Route and invoke skills based on user input"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="User input to route and invoke skill"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute the skill (default is dry-run mode)"
    )
    parser.add_argument(
        "--batch",
        help="JSON file containing batch inputs"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    invoker = IntegratedSkillInvoker()
    
    if args.interactive:
        print("Integrated Skill Invoker - Interactive Mode")
        print("="*60)
        print("Enter your input (or 'quit' to exit):")
        
        while True:
            user_input = input("\n> ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_input:
                continue
            
            result = invoker.invoke_with_routing(user_input, dry_run=not args.execute)
            invoker.print_result(result)
        
        return
    
    if args.batch:
        try:
            with open(args.batch, 'r', encoding='utf-8') as f:
                batch_data = json.load(f)
            
            inputs = batch_data.get("inputs", [])
            print(f"Processing {len(inputs)} inputs in batch mode...")
            
            result = invoker.batch_invoke(inputs, dry_run=not args.execute)
            
            print("\n" + "="*60)
            print("BATCH INVOCATION SUMMARY")
            print("="*60)
            print(f"Total Inputs: {result['total_inputs']}")
            print(f"Success Count: {result['success_count']}")
            print(f"Failure Count: {result['failure_count']}")
            print(f"Success Rate: {result['success_rate']:.2%}")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"Error processing batch file: {e}")
            return
    
    if args.input:
        result = invoker.invoke_with_routing(args.input, dry_run=not args.execute)
        invoker.print_result(result)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
