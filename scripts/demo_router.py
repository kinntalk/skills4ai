from context_aware_router import ContextAwareRouter


def demo_router():
    router = ContextAwareRouter()
    
    test_inputs = [
        "I want to brainstorm some ideas for a new feature",
        "帮我规划一下这个项目的架构",
        "There's a bug in the code, I need to debug it",
        "Let me implement this feature now",
        "Please verify the code before we merge",
        "I need to create a new skill template",
        "Generate an image from markdown",
        "Design the UI/UX for this product"
    ]
    
    print("=" * 70)
    print("CONTEXT AWARE SKILL ROUTER - DEMONSTRATION")
    print("=" * 70)
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n{'=' * 70}")
        print(f"Example {i}: {user_input}")
        print(f"{'=' * 70}")
        
        result = router.route(user_input)
        
        print(f"\nDetected Phase: {result['detected_phase'].upper()}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Keywords: {', '.join(result['keywords'])}")
        
        print(f"\nRecommended Skills:")
        for j, rec in enumerate(result['recommendations'], 1):
            print(f"  {j}. {rec['skill_name']}")
            print(f"     Priority: {rec['priority']}, Confidence: {rec['confidence']:.2f}")
            print(f"     Required For: {', '.join(rec['required_for'])}")
        
        if result['conflicts']:
            print(f"\nConflicts Detected:")
            for j, conflict in enumerate(result['conflicts'], 1):
                print(f"  {j}. {conflict['conflict_type']}")
                print(f"     Skills: {', '.join(conflict['skills'])}")
                print(f"     Resolution: {conflict['resolution']}")
        else:
            print(f"\nNo conflicts detected")
    
    print(f"\n{'=' * 70}")
    print("DEMONSTRATION COMPLETE")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    demo_router()
