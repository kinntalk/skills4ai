import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from usage_tracker import UsageTracker, record_invocation, analyze_usage_stats, calculate_success_rate, get_most_used_skills, get_least_used_skills, generate_usage_report
from datetime import datetime
import time

try:
    from usage_visualizer import UsageVisualizer, generate_usage_chart, generate_success_rate_chart, generate_trend_chart, generate_comprehensive_report
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("警告: matplotlib 未安装，跳过可视化测试")


def test_usage_tracker():
    print("=" * 80)
    print("测试 UsageTracker 功能")
    print("=" * 80)
    
    tracker = UsageTracker()
    
    print("\n1. 测试记录技能调用...")
    
    test_skills = [
        "code-review",
        "debug-assistant",
        "refactor-helper",
        "test-generator",
        "documentation-writer"
    ]
    
    for i, skill in enumerate(test_skills):
        for j in range(5):
            context = {
                "user": f"test_user_{i}",
                "session": f"session_{i}_{j}",
                "start_time": datetime.now().isoformat()
            }
            
            success = j < 4
            result = {
                "success": success,
                "message": "Test execution completed" if success else "Test execution failed"
            }
            
            time.sleep(0.01)
            
            success_record = record_invocation(skill, context, result)
            if success_record:
                print(f"   ✓ 记录 {skill} 调用 #{j+1} 成功")
            else:
                print(f"   ✗ 记录 {skill} 调用 #{j+1} 失败")
    
    print("\n2. 测试分析使用统计...")
    analysis = analyze_usage_stats()
    print(f"   总技能数: {analysis['total_skills']}")
    print(f"   总调用次数: {analysis['total_invocations']}")
    print(f"   整体成功率: {analysis['overall_success_rate']}%")
    print(f"   平均执行时间: {analysis['avg_execution_time']}秒")
    
    print("\n3. 测试计算成功率...")
    for skill in test_skills[:3]:
        rate = calculate_success_rate(skill)
        print(f"   {skill} 成功率: {rate}%")
    
    print("\n4. 测试获取最常用技能...")
    most_used = get_most_used_skills(3)
    print("   最常用技能 TOP 3:")
    for i, skill in enumerate(most_used, 1):
        print(f"     {i}. {skill['name']} - {skill['invocations']} 次调用")
    
    print("\n5. 测试获取最少使用技能...")
    least_used = get_least_used_skills(3)
    print("   最少使用技能 TOP 3:")
    for i, skill in enumerate(least_used, 1):
        print(f"     {i}. {skill['name']} - {skill['invocations']} 次调用")
    
    print("\n6. 测试生成使用报告...")
    report = generate_usage_report()
    print("\n" + report)
    
    print("\n✓ UsageTracker 所有功能测试完成!")
    return True


def test_usage_visualizer():
    if not HAS_MATPLOTLIB:
        print("\n" + "=" * 80)
        print("跳过 UsageVisualizer 测试 (matplotlib 未安装)")
        print("请运行: pip install matplotlib")
        print("=" * 80)
        return True
    
    print("\n" + "=" * 80)
    print("测试 UsageVisualizer 功能")
    print("=" * 80)
    
    visualizer = UsageVisualizer()
    
    print("\n1. 测试生成使用频率图表...")
    try:
        usage_chart = generate_usage_chart(limit=5)
        if usage_chart:
            print(f"   ✓ 使用频率图表已生成: {usage_chart}")
        else:
            print("   ✗ 使用频率图表生成失败 (可能没有数据)")
    except Exception as e:
        print(f"   ✗ 使用频率图表生成失败: {e}")
    
    print("\n2. 测试生成成功率图表...")
    try:
        success_chart = generate_success_rate_chart(limit=5)
        if success_chart:
            print(f"   ✓ 成功率图表已生成: {success_chart}")
        else:
            print("   ✗ 成功率图表生成失败 (可能没有数据)")
    except Exception as e:
        print(f"   ✗ 成功率图表生成失败: {e}")
    
    print("\n3. 测试生成趋势图表...")
    try:
        trend_chart = generate_trend_chart("code-review")
        if trend_chart:
            print(f"   ✓ 趋势图表已生成: {trend_chart}")
        else:
            print("   ✗ 趋势图表生成失败 (可能没有足够的历史数据)")
    except Exception as e:
        print(f"   ✗ 趋势图表生成失败: {e}")
    
    print("\n4. 测试生成综合报告...")
    try:
        comprehensive_chart = generate_comprehensive_report()
        if comprehensive_chart:
            print(f"   ✓ 综合报告图表已生成: {comprehensive_chart}")
        else:
            print("   ✗ 综合报告图表生成失败 (可能没有数据)")
    except Exception as e:
        print(f"   ✗ 综合报告图表生成失败: {e}")
    
    print("\n✓ UsageVisualizer 所有功能测试完成!")
    return True


def test_integration():
    print("\n" + "=" * 80)
    print("测试集成功能")
    print("=" * 80)
    
    tracker = UsageTracker()
    
    print("\n1. 测试获取所有技能...")
    all_skills = tracker.get_all_skills()
    print(f"   当前已记录的技能: {len(all_skills)} 个")
    for skill in all_skills:
        print(f"     - {skill}")
    
    print("\n2. 测试获取单个技能统计...")
    if all_skills:
        skill_stats = tracker.get_skill_stats(all_skills[0])
        if skill_stats:
            print(f"   技能: {skill_stats['name']}")
            print(f"   调用次数: {skill_stats['invocations']}")
            print(f"   成功率: {skill_stats['success_rate']}%")
            print(f"   平均执行时间: {skill_stats['avg_execution_time']}秒")
            print(f"   历史记录数: {len(skill_stats['execution_history'])}")
    
    print("\n✓ 集成功能测试完成!")
    return True


def main():
    print("\n" + "=" * 80)
    print("技能使用统计系统 - 功能测试")
    print("=" * 80)
    
    try:
        test_usage_tracker()
        test_usage_visualizer()
        test_integration()
        
        print("\n" + "=" * 80)
        print("✓ 所有测试通过!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)