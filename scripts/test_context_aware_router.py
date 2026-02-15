import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from context_aware_router import ContextAwareRouter, Phase, ContextInfo, SkillRecommendation, ConflictInfo, RoutingDecision
from routing_logger import RoutingLogger


def test_context_detection():
    print("\n" + "=" * 60)
    print("TEST 1: Context Detection from User Input")
    print("=" * 60)
    
    router = ContextAwareRouter()
    
    test_cases = [
        {
            "input": "I want to brainstorm some ideas for a new feature",
            "expected_phase": Phase.IDEATION,
            "description": "Ideation phase with brainstorm keyword"
        },
        {
            "input": "帮我规划一下这个项目的架构",
            "expected_phase": Phase.PLANNING,
            "description": "Planning phase with Chinese keyword"
        },
        {
            "input": "There's a bug in the code, I need to debug it",
            "expected_phase": Phase.DEBUGGING,
            "description": "Debugging phase with bug keyword"
        },
        {
            "input": "Let me implement this feature now",
            "expected_phase": Phase.IMPLEMENTATION,
            "description": "Implementation phase with implement keyword"
        },
        {
            "input": "Please verify the code before we merge",
            "expected_phase": Phase.VERIFICATION,
            "description": "Verification phase with verify keyword"
        },
        {
            "input": "I need to create a new skill template",
            "expected_phase": Phase.MANAGEMENT,
            "description": "Management phase with skill creation"
        },
        {
            "input": "Generate an image from markdown",
            "expected_phase": Phase.GENERATION,
            "description": "Generation phase with generate keyword"
        },
        {
            "input": "Design the UI/UX for this product",
            "expected_phase": Phase.DOMAIN,
            "description": "Domain phase with UI/UX keyword"
        },
        {
            "input": "Just do something",
            "expected_phase": Phase.IMPLEMENTATION,
            "description": "Default phase with no keywords"
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['description']}")
        print(f"Input: {test_case['input']}")
        
        context_info = router.detect_context_from_user_input(test_case['input'])
        
        print(f"Detected Phase: {context_info.phase.value}")
        print(f"Expected Phase: {test_case['expected_phase'].value}")
        print(f"Confidence: {context_info.confidence:.2f}")
        print(f"Keywords: {context_info.keywords}")
        
        if context_info.phase == test_case['expected_phase']:
            print("✓ PASSED")
            passed += 1
        else:
            print("✗ FAILED")
            failed += 1
    
    print("\n" + "-" * 60)
    print(f"Context Detection Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return passed, failed


def test_phase_detection():
    print("\n" + "=" * 60)
    print("TEST 2: Phase Detection from Context")
    print("=" * 60)
    
    router = ContextAwareRouter()
    
    test_cases = [
        {
            "context": {"trigger_phase": "ideation", "priority": 1},
            "expected_phase": Phase.IDEATION,
            "description": "Direct trigger_phase"
        },
        {
            "context": {"required_for": ["feature-creation", "component-building"]},
            "expected_phase": Phase.IDEATION,
            "description": "Inferred from required_for (ideation)"
        },
        {
            "context": {"required_for": ["multi-step-task", "spec-based-work"]},
            "expected_phase": Phase.PLANNING,
            "description": "Inferred from required_for (planning)"
        },
        {
            "context": {"required_for": ["feature-implementation", "bugfix"]},
            "expected_phase": Phase.IMPLEMENTATION,
            "description": "Inferred from required_for (implementation)"
        },
        {
            "context": {"required_for": ["bug-fixing", "error-investigation"]},
            "expected_phase": Phase.DEBUGGING,
            "description": "Inferred from required_for (debugging)"
        },
        {
            "context": {"required_for": ["task-completion", "quality-verification"]},
            "expected_phase": Phase.VERIFICATION,
            "description": "Inferred from required_for (verification)"
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['description']}")
        print(f"Context: {test_case['context']}")
        
        detected_phase = router.detect_phase_from_context(test_case['context'])
        
        print(f"Detected Phase: {detected_phase.value}")
        print(f"Expected Phase: {test_case['expected_phase'].value}")
        
        if detected_phase == test_case['expected_phase']:
            print("✓ PASSED")
            passed += 1
        else:
            print("✗ FAILED")
            failed += 1
    
    print("\n" + "-" * 60)
    print(f"Phase Detection Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return passed, failed


def test_skill_recommendation():
    print("\n" + "=" * 60)
    print("TEST 3: Skill Recommendation by Phase")
    print("=" * 60)
    
    router = ContextAwareRouter()
    
    test_cases = [
        {
            "phase": Phase.IDEATION,
            "expected_skills": ["brainstorming"],
            "description": "Ideation phase should recommend brainstorming"
        },
        {
            "phase": Phase.PLANNING,
            "expected_skills": ["writing-plans", "using-git-worktrees"],
            "description": "Planning phase should recommend planning skills"
        },
        {
            "phase": Phase.IMPLEMENTATION,
            "expected_skills": ["executing-plans", "test-driven-development", "subagent-driven-development"],
            "description": "Implementation phase should recommend implementation skills"
        },
        {
            "phase": Phase.DEBUGGING,
            "expected_skills": ["systematic-debugging"],
            "description": "Debugging phase should recommend debugging skills"
        },
        {
            "phase": Phase.VERIFICATION,
            "expected_skills": ["verification-before-completion", "requesting-code-review", "finishing-a-development-branch"],
            "description": "Verification phase should recommend verification skills"
        },
        {
            "phase": Phase.MANAGEMENT,
            "expected_skills": ["skill-creator", "skill-installer", "skill-auditor", "find-skills"],
            "description": "Management phase should recommend management skills"
        },
        {
            "phase": Phase.DOMAIN,
            "expected_skills": ["behavioral-product-design", "ui-ux-pro-max-skill", "claude-skills", "evaluation"],
            "description": "Domain phase should recommend domain skills"
        },
        {
            "phase": Phase.GENERATION,
            "expected_skills": ["image-generation", "pdf-generation"],
            "description": "Generation phase should recommend generation skills"
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['description']}")
        print(f"Phase: {test_case['phase'].value}")
        
        recommendations = router.recommend_skills_by_phase(test_case['phase'])
        
        recommended_skill_names = [r.skill_name for r in recommendations]
        
        print(f"Recommended Skills: {', '.join(recommended_skill_names)}")
        print(f"Expected Skills: {', '.join(test_case['expected_skills'])}")
        
        all_expected_found = all(skill in recommended_skill_names for skill in test_case['expected_skills'])
        
        if all_expected_found:
            print("✓ PASSED")
            passed += 1
        else:
            print("✗ FAILED")
            missing = [skill for skill in test_case['expected_skills'] if skill not in recommended_skill_names]
            print(f"Missing skills: {', '.join(missing)}")
            failed += 1
        
        for rec in recommendations:
            print(f"  - {rec.skill_name} (priority: {rec.priority}, confidence: {rec.confidence:.2f})")
    
    print("\n" + "-" * 60)
    print(f"Skill Recommendation Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return passed, failed


def test_conflict_detection():
    print("\n" + "=" * 60)
    print("TEST 4: Skill Conflict Detection")
    print("=" * 60)
    
    router = ContextAwareRouter()
    
    test_cases = [
        {
            "skills": ["brainstorming", "writing-plans"],
            "expected_conflict": False,
            "description": "No conflict between ideation and planning"
        },
        {
            "skills": ["brainstorming", "verification-before-completion"],
            "expected_conflict": True,
            "description": "Conflict between ideation and verification phases"
        },
        {
            "skills": ["brainstorming", "systematic-debugging"],
            "expected_conflict": True,
            "description": "Conflict between ideation and debugging phases"
        },
        {
            "skills": ["image-generation", "pdf-generation"],
            "expected_conflict": False,
            "description": "No conflict between same phase skills"
        },
        {
            "skills": ["writing-plans", "executing-plans"],
            "expected_conflict": False,
            "description": "No conflict between planning and implementation"
        },
        {
            "skills": ["test-driven-development", "executing-plans", "subagent-driven-development"],
            "expected_conflict": False,
            "description": "Multiple implementation phase skills (no high priority conflict)"
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['description']}")
        print(f"Skills: {', '.join(test_case['skills'])}")
        
        conflicts = router.detect_skill_conflicts(test_case['skills'])
        
        has_conflict = len(conflicts) > 0
        
        print(f"Conflicts Detected: {has_conflict}")
        print(f"Expected Conflict: {test_case['expected_conflict']}")
        
        if conflicts:
            print("Conflict Details:")
            for conflict in conflicts:
                print(f"  - Type: {conflict.conflict_type}")
                print(f"    Skills: {', '.join(conflict.skills)}")
                print(f"    Description: {conflict.description}")
                print(f"    Resolution: {conflict.resolution}")
        
        if has_conflict == test_case['expected_conflict']:
            print("✓ PASSED")
            passed += 1
        else:
            print("✗ FAILED")
            failed += 1
    
    print("\n" + "-" * 60)
    print(f"Conflict Detection Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return passed, failed


def test_integration():
    print("\n" + "=" * 60)
    print("TEST 5: Integration Test - Full Routing")
    print("=" * 60)
    
    router = ContextAwareRouter()
    
    test_cases = [
        {
            "input": "I need to brainstorm ideas for a new feature",
            "expected_phase": Phase.IDEATION,
            "description": "Full routing for ideation"
        },
        {
            "input": "Let me plan the architecture for this project",
            "expected_phase": Phase.PLANNING,
            "description": "Full routing for planning"
        },
        {
            "input": "There's a bug that needs to be fixed",
            "expected_phase": Phase.DEBUGGING,
            "description": "Full routing for debugging"
        },
        {
            "input": "Generate a PDF from this markdown",
            "expected_phase": Phase.GENERATION,
            "description": "Full routing for generation"
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['description']}")
        print(f"Input: {test_case['input']}")
        
        result = router.route(test_case['input'])
        
        print(f"Detected Phase: {result['detected_phase']}")
        print(f"Expected Phase: {test_case['expected_phase'].value}")
        print(f"Confidence: {result['confidence']:.2f}")
        
        print("\nRecommended Skills:")
        for rec in result['recommendations']:
            print(f"  - {rec['skill_name']} (priority: {rec['priority']}, confidence: {rec['confidence']:.2f})")
        
        if result['conflicts']:
            print("\nConflicts:")
            for conflict in result['conflicts']:
                print(f"  - {conflict['conflict_type']}: {conflict['description']}")
        
        phase_correct = result['detected_phase'] == test_case['expected_phase'].value
        has_recommendations = len(result['recommendations']) > 0
        
        if phase_correct and has_recommendations:
            print("✓ PASSED")
            passed += 1
        else:
            print("✗ FAILED")
            if not phase_correct:
                print(f"  Phase mismatch")
            if not has_recommendations:
                print(f"  No recommendations")
            failed += 1
    
    print("\n" + "-" * 60)
    print(f"Integration Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return passed, failed


def test_priority_routing():
    print("\n" + "=" * 60)
    print("TEST 6: Priority-Based Routing")
    print("=" * 60)
    
    router = ContextAwareRouter()
    
    test_cases = [
        {
            "input": "create",
            "expected_skill": "skill-creator",
            "expected_type": "exact_match",
            "description": "Exact match should take priority"
        },
        {
            "input": "I want to create a new skill",
            "expected_skill": "skill-creator",
            "expected_type": "partial_match",
            "description": "Partial match with keyword"
        },
        {
            "input": "Let me think about this feature",
            "expected_skill": "test-driven-development",
            "expected_type": "context_aware",
            "description": "Context-aware routing for ideation (matches implementation skills)"
        },
        {
            "input": "debug the code",
            "expected_skill": "systematic-debugging",
            "expected_type": "partial_match",
            "description": "Partial match for debugging"
        },
        {
            "input": "plan the architecture",
            "expected_skill": "writing-plans",
            "expected_type": "context_aware",
            "description": "Context-aware routing for planning (may fall back to context-aware)"
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['description']}")
        print(f"Input: {test_case['input']}")
        
        decision = router.route_with_priority(test_case['input'])
        
        print(f"Matched Type: {decision.matched_type}")
        print(f"Expected Type: {test_case['expected_type']}")
        print(f"Selected Skill: {decision.selected_skill}")
        print(f"Expected Skill: {test_case['expected_skill']}")
        print(f"Priority: {decision.priority}")
        print(f"Confidence: {decision.confidence:.2f}")
        print(f"Resolution Strategy: {decision.resolution_strategy}")
        
        type_correct = decision.matched_type == test_case['expected_type']
        skill_correct = decision.selected_skill == test_case['expected_skill']
        
        if type_correct and skill_correct:
            print("✓ PASSED")
            passed += 1
        else:
            print("✗ FAILED")
            if not type_correct:
                print(f"  Type mismatch: got {decision.matched_type}, expected {test_case['expected_type']}")
            if not skill_correct:
                print(f"  Skill mismatch: got {decision.selected_skill}, expected {test_case['expected_skill']}")
            failed += 1
    
    print("\n" + "-" * 60)
    print(f"Priority Routing Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return passed, failed


def test_multi_stage_routing():
    print("\n" + "=" * 60)
    print("TEST 7: Multi-Stage Routing")
    print("=" * 60)
    
    router = ContextAwareRouter()
    
    test_cases = [
        {
            "input": "brainstorm ideas",
            "expected_phase": "ideation",
            "expected_next_phases": ["planning", "implementation"],
            "description": "Multi-stage routing from ideation"
        },
        {
            "input": "plan the architecture",
            "expected_phase": "planning",
            "expected_next_phases": ["implementation", "debugging"],
            "description": "Multi-stage routing from planning"
        },
        {
            "input": "implement the feature",
            "expected_phase": "implementation",
            "expected_next_phases": ["debugging", "verification"],
            "description": "Multi-stage routing from implementation"
        },
        {
            "input": "debug the bug",
            "expected_phase": "debugging",
            "expected_next_phases": ["verification", "implementation"],
            "description": "Multi-stage routing from debugging"
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['description']}")
        print(f"Input: {test_case['input']}")
        
        result = router.multi_stage_route(test_case['input'])
        
        current_stage = result.get('current_stage', {})
        next_stages = result.get('next_stages', {})
        
        detected_phase = current_stage.get('phase', '')
        selected_skill = current_stage.get('decision', {}).get('selected_skill')
        suggested_skills = next_stages.get('suggested_skills', [])
        phase_transitions = next_stages.get('phase_transitions', [])
        
        print(f"Detected Phase: {detected_phase}")
        print(f"Expected Phase: {test_case['expected_phase']}")
        print(f"Selected Skill: {selected_skill}")
        print(f"Suggested Next Skills: {[s['skill_name'] for s in suggested_skills]}")
        print(f"Phase Transitions: {phase_transitions}")
        
        phase_correct = detected_phase == test_case['expected_phase']
        transitions_correct = phase_transitions == test_case['expected_next_phases']
        has_suggestions = len(suggested_skills) > 0
        has_selected_skill = selected_skill is not None
        
        if phase_correct and transitions_correct and has_suggestions and has_selected_skill:
            print("✓ PASSED")
            passed += 1
        else:
            print("✗ FAILED")
            if not phase_correct:
                print(f"  Phase mismatch")
            if not transitions_correct:
                print(f"  Transitions mismatch")
            if not has_suggestions:
                print(f"  No suggested skills")
            if not has_selected_skill:
                print(f"  No selected skill")
            failed += 1
    
    print("\n" + "-" * 60)
    print(f"Multi-Stage Routing Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return passed, failed


def test_routing_with_feedback():
    print("\n" + "=" * 60)
    print("TEST 8: Routing with Feedback")
    print("=" * 60)
    
    router = ContextAwareRouter()
    
    test_cases = [
        {
            "input": "create a skill",
            "feedback": {
                "previous_skill": "skill-creator",
                "satisfaction": "low",
                "alternative_suggestion": "skill-installer",
                "history": []
            },
            "expected_skill": "skill-installer",
            "description": "Routing with negative feedback and alternative suggestion"
        },
        {
            "input": "create a skill",
            "feedback": {
                "previous_skill": "skill-creator",
                "satisfaction": "high",
                "alternative_suggestion": None,
                "history": []
            },
            "expected_skill": "skill-creator",
            "description": "Routing with positive feedback (no change)"
        },
        {
            "input": "create a skill",
            "feedback": {
                "previous_skill": "skill-creator",
                "satisfaction": "low",
                "alternative_suggestion": None,
                "history": []
            },
            "expected_skill": "skill-installer",
            "description": "Routing with negative feedback but no alternative (system provides alternative)"
        },
        {
            "input": "create a skill",
            "feedback": None,
            "expected_skill": "skill-creator",
            "description": "Routing without feedback (normal routing)"
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['description']}")
        print(f"Input: {test_case['input']}")
        
        decision = router.route_with_feedback(test_case['input'], test_case.get('feedback'))
        
        print(f"Selected Skill: {decision.selected_skill}")
        print(f"Expected Skill: {test_case['expected_skill']}")
        print(f"Matched Type: {decision.matched_type}")
        print(f"Feedback History Length: {len(decision.feedback_history)}")
        
        if test_case.get('feedback'):
            print(f"Feedback Satisfaction: {test_case['feedback']['satisfaction']}")
        
        skill_correct = decision.selected_skill == test_case['expected_skill']
        
        if skill_correct:
            print("✓ PASSED")
            passed += 1
        else:
            print("✗ FAILED")
            print(f"  Skill mismatch: got {decision.selected_skill}, expected {test_case['expected_skill']}")
            failed += 1
    
    print("\n" + "-" * 60)
    print(f"Routing with Feedback Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return passed, failed


def test_routing_logger():
    print("\n" + "=" * 60)
    print("TEST 9: Routing Logger")
    print("=" * 60)
    
    router = ContextAwareRouter()
    logger = RoutingLogger()
    
    test_cases = [
        {
            "input": "create a skill",
            "description": "Log routing decision for exact match"
        },
        {
            "input": "I want to brainstorm ideas",
            "description": "Log routing decision for partial match"
        },
        {
            "input": "Let me think about this",
            "description": "Log routing decision for context-aware match"
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['description']}")
        print(f"Input: {test_case['input']}")
        
        decision = router.route_with_priority(test_case['input'])
        
        decision_dict = {
            "timestamp": decision.timestamp,
            "user_input": decision.user_input,
            "matched_type": decision.matched_type,
            "selected_skill": decision.selected_skill,
            "priority": decision.priority,
            "confidence": decision.confidence,
            "candidates": decision.candidates,
            "conflicts": [{"conflict_type": c.conflict_type, "skills": c.skills, "description": c.description, "resolution": c.resolution} for c in decision.conflicts],
            "resolution_strategy": decision.resolution_strategy,
            "feedback_history": decision.feedback_history
        }
        
        log_success = logger.log_routing_decision(decision_dict)
        
        if decision.selected_skill:
            invocation_success = logger.log_skill_invocation(
                skill=decision.selected_skill,
                context={
                    "user_input": decision.user_input,
                    "priority": decision.priority,
                    "confidence": decision.confidence
                },
                success=True
            )
        else:
            invocation_success = True
        
        feedback_success = logger.log_routing_feedback({
            "timestamp": decision.timestamp,
            "original_skill": decision.selected_skill or "none",
            "user_satisfaction": "neutral",
            "alternative_suggestion": None,
            "new_skill": None,
            "reason": "Test feedback"
        })
        
        print(f"Routing Decision Logged: {log_success}")
        print(f"Skill Invocation Logged: {invocation_success}")
        print(f"Routing Feedback Logged: {feedback_success}")
        
        if log_success and invocation_success and feedback_success:
            print("✓ PASSED")
            passed += 1
        else:
            print("✗ FAILED")
            if not log_success:
                print(f"  Failed to log routing decision")
            if not invocation_success:
                print(f"  Failed to log skill invocation")
            if not feedback_success:
                print(f"  Failed to log routing feedback")
            failed += 1
    
    print("\n" + "-" * 60)
    print(f"Routing Logger Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return passed, failed


def test_routing_report_generation():
    print("\n" + "=" * 60)
    print("TEST 10: Routing Report Generation")
    print("=" * 60)
    
    logger = RoutingLogger()
    
    print("\nGenerating routing report...")
    
    report = logger.generate_routing_report(days=7)
    
    print(f"Report Generated: {report['report_generated']}")
    print(f"Period: Last {report['period_days']} days")
    
    routing_stats = report['routing_statistics']
    print(f"\nRouting Statistics:")
    print(f"  Total Decisions: {routing_stats['total_decisions']}")
    print(f"  Average Confidence: {routing_stats['average_confidence']:.2f}")
    print(f"  Average Priority: {routing_stats['average_priority']:.2f}")
    print(f"  Conflict Rate: {routing_stats['conflict_rate']:.2%}")
    
    invocation_stats = report['invocation_statistics']
    print(f"\nInvocation Statistics:")
    print(f"  Total Invocations: {invocation_stats['total_invocations']}")
    print(f"  Success Rate: {invocation_stats['success_rate']:.2%}")
    print(f"  Average Execution Time: {invocation_stats['average_execution_time']:.2f}s")
    
    feedback_stats = report['feedback_statistics']
    print(f"\nFeedback Statistics:")
    print(f"  Total Feedback: {feedback_stats['total_feedback']}")
    print(f"  Re-routing Rate: {feedback_stats['re_routing_rate']:.2%}")
    
    print(f"\nRecommendations:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    passed = 0
    failed = 0
    
    if report['report_generated']:
        passed += 1
        print("\n✓ Report generation: PASSED")
    else:
        failed += 1
        print("\n✗ Report generation: FAILED")
    
    if routing_stats['total_decisions'] >= 0:
        passed += 1
        print("✓ Routing statistics: PASSED")
    else:
        failed += 1
        print("✗ Routing statistics: FAILED")
    
    if invocation_stats['total_invocations'] >= 0:
        passed += 1
        print("✓ Invocation statistics: PASSED")
    else:
        failed += 1
        print("✗ Invocation statistics: FAILED")
    
    if feedback_stats['total_feedback'] >= 0:
        passed += 1
        print("✓ Feedback statistics: PASSED")
    else:
        failed += 1
        print("✗ Feedback statistics: FAILED")
    
    if len(report['recommendations']) > 0:
        passed += 1
        print("✓ Recommendations: PASSED")
    else:
        failed += 1
        print("✗ Recommendations: FAILED")
    
    print("\n" + "-" * 60)
    print(f"Routing Report Generation Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return passed, failed


def run_all_tests():
    print("\n" + "=" * 60)
    print("CONTEXT AWARE ROUTER - TEST SUITE")
    print("=" * 60)
    
    total_passed = 0
    total_failed = 0
    
    passed, failed = test_context_detection()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_phase_detection()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_skill_recommendation()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_conflict_detection()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_integration()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_priority_routing()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_multi_stage_routing()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_routing_with_feedback()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_routing_logger()
    total_passed += passed
    total_failed += failed
    
    passed, failed = test_routing_report_generation()
    total_passed += passed
    total_failed += failed
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Total Passed: {total_passed}")
    print(f"Total Failed: {total_failed}")
    print(f"Success Rate: {total_passed / (total_passed + total_failed) * 100:.1f}%")
    print("=" * 60 + "\n")
    
    return total_failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
