# 技能使用统计系统

## 概述

技能使用统计系统是一个完整的技能调用跟踪和分析工具，用于记录、分析和可视化技能的使用情况。

## 文件结构

```
.trae/skills/
├── skill_usage_stats.json          # 统计数据存储文件
└── scripts/
    ├── usage_tracker.py            # 核心跟踪和分析模块
    ├── usage_visualizer.py         # 可视化模块
    ├── test_usage_system.py        # 测试脚本
    └── requirements.txt            # Python依赖
```

## 功能特性

### 1. 统计数据结构

`skill_usage_stats.json` 存储所有技能的使用统计信息：

- **invocations**: 调用次数
- **success_count**: 成功次数
- **failure_count**: 失败次数
- **total_execution_time**: 总执行时间
- **last_used**: 最后使用时间
- **first_used**: 首次使用时间
- **execution_history**: 执行历史记录（最多保留100条）

### 2. 核心功能 (usage_tracker.py)

#### UsageTracker 类

```python
from usage_tracker import UsageTracker

tracker = UsageTracker()
```

**主要方法：**

- `record_invocation(skill, context, result)` - 记录技能调用
- `calculate_success_rate(skill)` - 计算成功率
- `calculate_avg_execution_time(skill)` - 计算平均执行时间
- `get_most_used_skills(limit)` - 获取最常用技能
- `get_least_used_skills(limit)` - 获取最少使用技能
- `analyze_usage_stats()` - 分析使用统计
- `generate_usage_report()` - 生成使用报告
- `get_skill_stats(skill)` - 获取单个技能统计
- `get_all_skills()` - 获取所有技能列表

#### 便捷函数

```python
from usage_tracker import (
    record_invocation,
    analyze_usage_stats,
    calculate_success_rate,
    get_most_used_skills,
    get_least_used_skills,
    generate_usage_report
)
```

### 3. 可视化功能 (usage_visualizer.py)

#### UsageVisualizer 类

```python
from usage_visualizer import UsageVisualizer

visualizer = UsageVisualizer()
```

**主要方法：**

- `generate_usage_chart(limit, output_file)` - 生成使用频率图表
- `generate_success_rate_chart(limit, output_file)` - 生成成功率图表
- `generate_trend_chart(skill, output_file)` - 生成趋势图表
- `generate_comprehensive_report(output_file)` - 生成综合报告

#### 便捷函数

```python
from usage_visualizer import (
    generate_usage_chart,
    generate_success_rate_chart,
    generate_trend_chart,
    generate_comprehensive_report
)
```

## 使用示例

### 基本使用

```python
from usage_tracker import UsageTracker
from datetime import datetime

# 创建跟踪器
tracker = UsageTracker()

# 记录技能调用
context = {
    "user": "user_001",
    "session": "session_123",
    "start_time": datetime.now().isoformat()
}

result = {
    "success": True,
    "message": "Execution completed successfully"
}

tracker.record_invocation("code-review", context, result)

# 获取统计信息
stats = tracker.get_skill_stats("code-review")
print(f"调用次数: {stats['invocations']}")
print(f"成功率: {stats['success_rate']}%")
```

### 生成报告

```python
from usage_tracker import generate_usage_report

# 生成文本报告
report = generate_usage_report()
print(report)
```

### 生成图表

```python
from usage_visualizer import generate_usage_chart, generate_success_rate_chart

# 生成使用频率图表
usage_chart = generate_usage_chart(limit=10)
print(f"图表已保存到: {usage_chart}")

# 生成成功率图表
success_chart = generate_success_rate_chart(limit=10)
print(f"图表已保存到: {success_chart}")
```

### 分析统计

```python
from usage_tracker import analyze_usage_stats, get_most_used_skills

# 获取总体统计
analysis = analyze_usage_stats()
print(f"总技能数: {analysis['total_skills']}")
print(f"总调用次数: {analysis['total_invocations']}")
print(f"整体成功率: {analysis['overall_success_rate']}%")

# 获取最常用技能
most_used = get_most_used_skills(5)
for skill in most_used:
    print(f"{skill['name']}: {skill['invocations']} 次调用")
```

## 安装依赖

```bash
pip install -r .trae/skills/scripts/requirements.txt
```

或单独安装 matplotlib：

```bash
pip install matplotlib
```

## 运行测试

```bash
cd .trae/skills/scripts
python test_usage_system.py
```

## 数据格式

### skill_usage_stats.json 结构

```json
{
  "version": "1.0.0",
  "last_updated": "2026-02-15T09:35:04.665583",
  "skills": {
    "skill-name": {
      "invocations": 10,
      "success_count": 8,
      "failure_count": 2,
      "total_execution_time": 1.5,
      "last_used": "2026-02-15T09:35:04.200363",
      "first_used": "2026-02-15T09:35:04.101383",
      "execution_history": [
        {
          "timestamp": "2026-02-15T09:35:04.112514",
          "execution_time": 0.1,
          "success": true,
          "context": {
            "user": "user_001",
            "session": "session_123"
          }
        }
      ]
    }
  }
}
```

## 输出文件

### 文本报告
- 控制台输出或保存为文本文件

### 图表文件
- 保存为 PNG 格式
- 默认保存在 `.trae/skills/reports/` 目录
- 文件名格式: `chart_type_YYYYMMDD_HHMMSS.png`

## 注意事项

1. **数据持久化**: 所有统计数据自动保存到 `skill_usage_stats.json`
2. **历史记录限制**: 每个技能最多保留100条执行历史记录
3. **线程安全**: 当前实现不是线程安全的，多线程环境需要加锁
4. **错误处理**: 记录失败时会打印错误信息，但不会中断程序
5. **依赖要求**: 可视化功能需要安装 matplotlib

## 扩展建议

1. **数据库支持**: 可以扩展为使用 SQLite 或其他数据库存储
2. **Web界面**: 添加 Web 界面展示统计数据
3. **实时监控**: 实现实时监控和告警功能
4. **导出功能**: 支持导出为 CSV、Excel 等格式
5. **API接口**: 提供 REST API 供其他系统调用

## 许可证

MIT License