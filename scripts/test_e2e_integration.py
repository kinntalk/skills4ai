import sys
import os
import json
import time
from typing import Dict, List
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from integrated_skill_invoker import IntegratedSkillInvoker
from feedback_manager import FeedbackManager
from routing_logger import RoutingLogger


class E2EIntegrationTester:
    def __init__(self):
        self.invoker = IntegratedSkillInvoker()
        self.feedback_manager = FeedbackManager()
        self.logger = RoutingLogger()
        self.test_results = []
    
    def run_test_workflow(self, workflow_name: str, workflow_steps: List[Dict]) -> Dict:
        print(f"\n{'='*60}")
        print(f"Running Test Workflow: {workflow_name}")
        print(f"{'='*60}")
        
        workflow_result = {
            "workflow_name": workflow_name,
            "start_time": datetime.now().isoformat(),
            "steps": [],
            "success": True,
            "errors": []
        }
        
        for i, step in enumerate(workflow_steps, 1):
            print(f"\n--- Step {i}: {step['description']} ---")
            
            step_result = {
                "step_number": i,
                "description": step['description'],
                "action": step['action'],
                "success": False,
                "result": None,
                "error": None
            }
            
            try:
                if step['action'] == 'route_and_invoke':
                    result = self.invoker.invoke_with_routing(
                        step['user_input'],
                        dry_run=step.get('dry_run', True)
                    )
                    step_result['result'] = result
                    step_result['success'] = result['success']
                    
                    if not result['success']:
                        workflow_result['success'] = False
                        workflow_result['errors'].append(
                            f"Step {i}: {result['message']}"
                        )
                    
                    print(f"✓ Routed to: {result['routing_decision']['selected_skill']}")
                    print(f"✓ Confidence: {result['routing_decision']['confidence']:.2f}")
                
                elif step['action'] == 'submit_feedback':
                    result = self.feedback_manager.submit_feedback(
                        user_input=step['user_input'],
                        original_skill=step['original_skill'],
                        user_satisfaction=step['satisfaction'],
                        alternative_suggestion=step.get('alternative_suggestion'),
                        reason=step.get('reason', '')
                    )
                    step_result['result'] = result
                    step_result['success'] = result['success']
                    
                    if not result['success']:
                        workflow_result['success'] = False
                        workflow_result['errors'].append(
                            f"Step {i}: {result['message']}"
                        )
                    
                    print(f"✓ Feedback submitted: {step['satisfaction']}")
                
                elif step['action'] == 'route_with_feedback':
                    previous_feedback = step.get('previous_feedback')
                    result = self.feedback_manager.route_with_feedback(
                        step['user_input'],
                        previous_feedback
                    )
                    step_result['result'] = {
                        "selected_skill": result.selected_skill,
                        "matched_type": result.matched_type,
                        "confidence": result.confidence,
                        "resolution_strategy": result.resolution_strategy
                    }
                    step_result['success'] = result.selected_skill is not None
                    
                    if not step_result['success']:
                        workflow_result['success'] = False
                        workflow_result['errors'].append(
                            f"Step {i}: No skill selected with feedback"
                        )
                    
                    print(f"✓ Routed with feedback to: {result.selected_skill}")
                    print(f"✓ Confidence: {result.confidence:.2f}")
                
                elif step['action'] == 'verify_routing':
                    expected_skill = step.get('expected_skill')
                    actual_skill = step.get('actual_skill')
                    
                    if expected_skill and actual_skill:
                        step_result['success'] = expected_skill == actual_skill
                        step_result['result'] = {
                            "expected": expected_skill,
                            "actual": actual_skill,
                            "match": step_result['success']
                        }
                        
                        if step_result['success']:
                            print(f"✓ Routing verification passed: {expected_skill}")
                        else:
                            print(f"✗ Routing verification failed")
                            print(f"  Expected: {expected_skill}")
                            print(f"  Actual: {actual_skill}")
                            workflow_result['success'] = False
                            workflow_result['errors'].append(
                                f"Step {i}: Expected {expected_skill}, got {actual_skill}"
                            )
                    else:
                        print(f"✗ Missing expected_skill or actual_skill in step")
                        workflow_result['success'] = False
                
                elif step['action'] == 'verify_logging':
                    log_type = step.get('log_type')
                    expected_count = step.get('expected_count', 1)
                    
                    if log_type == 'routing':
                        logs = self.logger._read_log_file(
                            self.logger.routing_log_file
                        )
                    elif log_type == 'feedback':
                        logs = self.logger._read_log_file(
                            self.logger.feedback_log_file
                        )
                    else:
                        print(f"✗ Unknown log type: {log_type}")
                        workflow_result['success'] = False
                        continue
                    
                    actual_count = len(logs)
                    step_result['success'] = actual_count >= expected_count
                    step_result['result'] = {
                        "expected_count": expected_count,
                        "actual_count": actual_count,
                        "log_type": log_type
                    }
                    
                    if step_result['success']:
                        print(f"✓ Logging verification passed: {actual_count} {log_type} logs")
                    else:
                        print(f"✗ Logging verification failed")
                        print(f"  Expected at least: {expected_count}")
                        print(f"  Actual: {actual_count}")
                        workflow_result['success'] = False
                        workflow_result['errors'].append(
                            f"Step {i}: Expected at least {expected_count} {log_type} logs, got {actual_count}"
                        )
                
                elif step['action'] == 'wait':
                    wait_seconds = step.get('seconds', 1)
                    print(f"Waiting {wait_seconds} second(s)...")
                    time.sleep(wait_seconds)
                    step_result['success'] = True
                    step_result['result'] = {"waited_seconds": wait_seconds}
                
                else:
                    print(f"✗ Unknown action: {step['action']}")
                    workflow_result['success'] = False
                    workflow_result['errors'].append(
                        f"Step {i}: Unknown action {step['action']}"
                    )
            
            except Exception as e:
                step_result['error'] = str(e)
                step_result['success'] = False
                workflow_result['success'] = False
                workflow_result['errors'].append(f"Step {i}: {str(e)}")
                print(f"✗ Error: {e}")
            
            workflow_result['steps'].append(step_result)
        
        workflow_result['end_time'] = datetime.now().isoformat()
        
        print(f"\n{'='*60}")
        if workflow_result['success']:
            print(f"✓ Workflow '{workflow_name}' PASSED")
        else:
            print(f"✗ Workflow '{workflow_name}' FAILED")
        print(f"{'='*60}")
        
        return workflow_result
    
    def test_brainstorming_workflow(self) -> Dict:
        workflow_steps = [
            {
                "action": "route_and_invoke",
                "description": "Route brainstorming request",
                "user_input": "I need to brainstorm a new feature",
                "dry_run": True
            },
            {
                "action": "verify_logging",
                "description": "Verify routing log was created",
                "log_type": "routing",
                "expected_count": 1
            }
        ]
        
        return self.run_test_workflow("Brainstorming Workflow", workflow_steps)
    
    def test_feedback_workflow(self) -> Dict:
        workflow_steps = [
            {
                "action": "route_and_invoke",
                "description": "Route initial request",
                "user_input": "I need to debug an issue",
                "dry_run": True
            },
            {
                "action": "verify_logging",
                "description": "Verify routing log was created",
                "log_type": "routing",
                "expected_count": 1
            },
            {
                "action": "route_with_feedback",
                "description": "Route with previous feedback",
                "user_input": "I need to debug an issue",
                "previous_feedback": {
                    "previous_skill": None,
                    "satisfaction": "unsatisfied"
                }
            },
            {
                "action": "verify_logging",
                "description": "Verify routing log was created",
                "log_type": "routing",
                "expected_count": 2
            }
        ]
        
        return self.run_test_workflow("Feedback Workflow", workflow_steps)
    
    def test_batch_routing_workflow(self) -> Dict:
        batch_inputs = [
            "I want to brainstorm ideas",
            "I need to write a plan",
            "I want to implement a feature",
            "I need to debug a bug",
            "I want to verify my code"
        ]
        
        workflow_steps = [
            {
                "action": "route_and_invoke",
                "description": "Route batch of inputs",
                "user_input": batch_inputs[0],
                "dry_run": True
            }
        ]
        
        for i, user_input in enumerate(batch_inputs[1:], 2):
            workflow_steps.append({
                "action": "route_and_invoke",
                "description": f"Route input {i}",
                "user_input": user_input,
                "dry_run": True
            })
        
        workflow_steps.append({
            "action": "verify_logging",
            "description": "Verify all routing logs were created",
            "log_type": "routing",
            "expected_count": len(batch_inputs)
        })
        
        return self.run_test_workflow("Batch Routing Workflow", workflow_steps)
    
    def test_end_to_end_workflow(self) -> Dict:
        workflow_steps = [
            {
                "action": "route_and_invoke",
                "description": "Route feature creation request",
                "user_input": "I need to create a new feature",
                "dry_run": True
            },
            {
                "action": "verify_logging",
                "description": "Verify routing log was created",
                "log_type": "routing",
                "expected_count": 1
            },
            {
                "action": "wait",
                "description": "Wait for logs to be written",
                "seconds": 1
            },
            {
                "action": "route_and_invoke",
                "description": "Route planning request",
                "user_input": "I need to write a plan for the feature",
                "dry_run": True
            },
            {
                "action": "verify_logging",
                "description": "Verify second routing log was created",
                "log_type": "routing",
                "expected_count": 2
            }
        ]
        
        return self.run_test_workflow("End-to-End Workflow", workflow_steps)
    
    def run_all_tests(self) -> Dict:
        print("\n" + "="*60)
        print("E2E INTEGRATION TEST SUITE")
        print("="*60)
        print(f"Started at: {datetime.now().isoformat()}")
        
        test_results = []
        
        test_results.append(self.test_brainstorming_workflow())
        test_results.append(self.test_feedback_workflow())
        test_results.append(self.test_batch_routing_workflow())
        test_results.append(self.test_end_to_end_workflow())
        
        total_tests = len(test_results)
        passed_tests = sum(1 for t in test_results if t['success'])
        failed_tests = total_tests - passed_tests
        
        summary = {
            "test_suite": "E2E Integration Tests",
            "started_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0.0,
            "test_results": test_results,
            "all_passed": passed_tests == total_tests
        }
        
        print("\n" + "="*60)
        print("TEST SUITE SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {summary['success_rate']:.2%}")
        
        if summary['all_passed']:
            print("\n✓ ALL TESTS PASSED")
        else:
            print("\n✗ SOME TESTS FAILED")
            print("\nFailed Workflows:")
            for result in test_results:
                if not result['success']:
                    print(f"  - {result['workflow_name']}")
                    for error in result['errors']:
                        print(f"    • {error}")
        
        print("="*60 + "\n")
        
        return summary
    
    def print_test_report(self, summary: Dict):
        print("\n" + "="*60)
        print("DETAILED TEST REPORT")
        print("="*60)
        
        for result in summary['test_results']:
            print(f"\n--- {result['workflow_name']} ---")
            print(f"Status: {'✓ PASSED' if result['success'] else '✗ FAILED'}")
            print(f"Duration: {result['start_time']} to {result['end_time']}")
            
            if result['errors']:
                print(f"\nErrors:")
                for error in result['errors']:
                    print(f"  • {error}")
            
            print(f"\nSteps ({len(result['steps'])}):")
            for step in result['steps']:
                status = "✓" if step['success'] else "✗"
                print(f"  {status} Step {step['step_number']}: {step['description']}")
        
        print("\n" + "="*60 + "\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="E2E Integration Tester - Test the complete skill routing system"
    )
    parser.add_argument(
        "--test",
        choices=["brainstorming", "feedback", "batch", "e2e", "all"],
        default="all",
        help="Specific test to run (default: all)"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Print detailed test report"
    )
    parser.add_argument(
        "--export",
        help="Export test results to JSON file"
    )
    
    args = parser.parse_args()
    
    tester = E2EIntegrationTester()
    
    if args.test == "brainstorming":
        summary = {
            "test_suite": "E2E Integration Tests",
            "started_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
            "total_tests": 1,
            "test_results": [tester.test_brainstorming_workflow()]
        }
    elif args.test == "feedback":
        summary = {
            "test_suite": "E2E Integration Tests",
            "started_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
            "total_tests": 1,
            "test_results": [tester.test_feedback_workflow()]
        }
    elif args.test == "batch":
        summary = {
            "test_suite": "E2E Integration Tests",
            "started_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
            "total_tests": 1,
            "test_results": [tester.test_batch_routing_workflow()]
        }
    elif args.test == "e2e":
        summary = {
            "test_suite": "E2E Integration Tests",
            "started_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
            "total_tests": 1,
            "test_results": [tester.test_end_to_end_workflow()]
        }
    else:
        summary = tester.run_all_tests()
    
    if args.report:
        tester.print_test_report(summary)
    
    if args.export:
        try:
            with open(args.export, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            print(f"\n✓ Test results exported to {args.export}")
        except Exception as e:
            print(f"\n✗ Failed to export test results: {e}")
    
    return 0 if summary.get('all_passed', False) else 1


if __name__ == "__main__":
    sys.exit(main())
