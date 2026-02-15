import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from usage_tracker import UsageTracker, generate_usage_report
from datetime import datetime
import time


def example_basic_usage():
    print("=" * 80)
    print("示例 1: 基本使用")
    print("=" * 80)
    
    tracker = UsageTracker()
    
    # 模拟技能调用
    skills = ["code-review", "debug-assistant", "refactor-helper"]
    
    for skill in skills:
        for i in range(3):
            context = {
                "user": f"demo_user",
                "session": f"demo_session_{i}",
                "start_time": datetime.now().isoformat()
            }
            
            result = {
                "success": i < 2,  # 前两次成功，第三次失败
                "message": "Demo execution"
            }
            
            tracker.record_invocation(skill, context, result)
            time.sleep(0.01)
    
    print("\n✓ 已记录 9 次技能调用")
    print(f"✓ 总技能数: {len(tracker.get_all_skills())}")


def example_analyze_stats():
    print("\n" + "=" * 80)
    print("示例 2: 分析统计信息")
    print("=" * 80)
    
    tracker = UsageTracker()
    
    # 获取总体统计
    analysis = tracker.analyze_usage_stats()
    print(f"\n总体统计:")
    print(f"  总技能数: {analysis['total_skills']}")
    print(f"  总调用次数: {analysis['total_invocations']}")
    print(f"  成功次数: {analysis['total_success']}")
    print(f"  失败次数: {analysis['total_failures']}")
    print(f"  整体成功率: {analysis['overall_success_rate']}%")
    print(f"  平均执行时间: {analysis['avg_execution_time']}秒")
    
    # 获取最常用技能
    most_used = tracker.get_most_used_skills(3)
    print(f"\n最常用技能 TOP 3:")
    for i, skill in enumerate(most_used, 1):
        print(f"  {i}. {skill['name']} - {skill['invocations']} 次调用")


def example_skill_details():
    print("\n" + "=" * 80)
    print("示例 3: 查看技能详情")
    print("=" * 80)
    
    tracker = UsageTracker()
    all_skills = tracker.get_all_skills()
    
    if all_skills:
        skill_name = all_skills[0]
        stats = tracker.get_skill_stats(skill_name)
        
        print(f"\n技能: {stats['name']}")
        print(f"  调用次数: {stats['invocations']}")
        print(f"  成功次数: {stats['success_count']}")
        print(f"  失败次数: {stats['failure_count']}")
        print(f"  成功率: {stats['success_rate']}%")
        print(f"  平均执行时间: {stats['avg_execution_time']}秒")
        print(f"  首次使用: {stats['first_used']}")
        print(f"  最后使用: {stats['last_used']}")
        print(f"  历史记录数: {len(stats['execution_history'])}")


def example_generate_report():
    print("\n" + "=" * 80)
    print("示例 4: 生成使用报告")
    print("=" * 80)
    
    report = generate_usage_report()
    print("\n" + report)


def main():
    print("\n" + "=" * 80)
    print("技能使用统计系统 - 使用示例")
    print("=" * 80)
    
    try:
        example_basic_usage()
        example_analyze_stats()
        example_skill_details()
        example_generate_report()
        
        print("\n" + "=" * 80)
        print("✓ 所有示例运行完成!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ 示例运行失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)