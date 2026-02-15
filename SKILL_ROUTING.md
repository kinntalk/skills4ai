# Skills Routing Table

## Usage Scenarios

### Scenario 1: Creating a New Feature
1. **brainstorming** (mandatory) - Explore requirements and design
2. **writing-plans** (mandatory) - Create implementation plan
3. **using-git-worktrees** (optional) - Isolate workspace if needed
4. **executing-plans** (mandatory) - Execute with subagent delegation
5. **test-driven-development** (mandatory) - Write tests before code
6. **systematic-debugging** (as needed) - Debug any issues
7. **verification-before-completion** (mandatory) - Verify before claiming done
8. **requesting-code-review** (recommended) - Get code review
9. **finishing-a-development-branch** (mandatory) - Decide integration strategy

### Scenario 2: Fixing a Bug
1. **systematic-debugging** (mandatory) - Investigate root cause
2. **writing-plans** (recommended) - Plan the fix
3. **test-driven-development** (mandatory) - Write failing test first
4. **executing-plans** (mandatory) - Implement fix
5. **verification-before-completion** (mandatory) - Verify fix works
6. **requesting-code-review** (recommended) - Get review

### Scenario 3: Creating a New Skill
1. **find-skills** (recommended) - Check if skill already exists
2. **skill-creator** (mandatory) - Scaffold new skill
3. **skill-auditor** (mandatory) - Validate skill compliance
4. **requesting-code-review** (recommended) - Get review

### Scenario 4: Designing UI/UX
1. **brainstorming** (mandatory) - Explore design requirements
2. **ui-ux-pro-max-skill** (mandatory) - Design UI/UX
3. **behavioral-product-design** (optional) - Apply behavioral principles
4. **verification-before-completion** (mandatory) - Verify design

## Skill Dependencies

| Skill | Depends On | Required For |
|-------|------------|--------------|
| executing-plans | writing-plans | verification-before-completion |
| test-driven-development | writing-plans | verification-before-completion |
| verification-before-completion | All implementation skills | finishing-a-development-branch |
| requesting-code-review | verification-before-completion | finishing-a-development-branch |

## Skill Usage Statistics

Track skill usage to optimize routing:
```json
{
  "usage_stats": {
    "brainstorming": {"invocations": 0, "success_rate": 0},
    "writing-plans": {"invocations": 0, "success_rate": 0},
    "executing-plans": {"invocations": 0, "success_rate": 0},
    "test-driven-development": {"invocations": 0, "success_rate": 0},
    "systematic-debugging": {"invocations": 0, "success_rate": 0},
    "verification-before-completion": {"invocations": 0, "success_rate": 0},
    "requesting-code-review": {"invocations": 0, "success_rate": 0},
    "finishing-a-development-branch": {"invocations": 0, "success_rate": 0},
    "using-git-worktrees": {"invocations": 0, "success_rate": 0},
    "find-skills": {"invocations": 0, "success_rate": 0},
    "skill-creator": {"invocations": 0, "success_rate": 0},
    "skill-auditor": {"invocations": 0, "success_rate": 0},
    "ui-ux-pro-max-skill": {"invocations": 0, "success_rate": 0},
    "behavioral-product-design": {"invocations": 0, "success_rate": 0}
  }
}
```

## 🔌 Integration Guide

### 概述

智能路由系统已完全集成到现有系统中，提供以下核心功能：

1. **集成技能调用器** (integrated_skill_invoker.py) - 自动路由和调用技能
2. **反馈管理器** (feedback_manager.py) - 收集和处理用户反馈
3. **端到端测试** (test_e2e_integration.py) - 验证完整工作流

### 快速开始

#### 1. 基本路由和调用

```bash
# 单次调用（干运行模式）
python .trae/skills/scripts/integrated_skill_invoker.py "I need to brainstorm a new feature"

# 实际执行技能
python .trae/skills/scripts/integrated_skill_invoker.py "I need to debug an issue" --execute
```

#### 2. 交互式模式

```bash
python .trae/skills/scripts/integrated_skill_invoker.py --interactive
```

在交互式模式中，您可以：
- 输入自然语言请求
- 查看路由决策和推荐技能
- 获得详细的技能信息
- 查看潜在冲突和解决方案

#### 3. 批量处理

创建批量输入文件 `batch_inputs.json`：

```json
{
  "inputs": [
    "I want to brainstorm ideas",
    "I need to write a plan",
    "I want to implement a feature",
    "I need to debug a bug",
    "I want to verify my code"
  ]
}
```

运行批量处理：

```bash
python .trae/skills/scripts/integrated_skill_invoker.py --batch batch_inputs.json
```

### 反馈机制

#### 提交反馈

```bash
# 满意反馈
python .trae/skills/scripts/feedback_manager.py submit \
  --input "I need to brainstorm a new feature" \
  --skill brainstorming \
  --satisfaction satisfied \
  --reason "Perfect skill recommendation"

# 不满意反馈
python .trae/skills/scripts/feedback_manager.py submit \
  --input "I need to debug an issue" \
  --skill systematic-debugging \
  --satisfaction unsatisfied \
  --alternative "test-driven-development" \
  --reason "The skill didn't help with my specific issue"
```

#### 基于反馈的路由

创建反馈文件 `feedback.json`：

```json
{
  "previous_skill": "systematic-debugging",
  "satisfaction": "unsatisfied",
  "alternative_suggestion": "test-driven-development"
}
```

使用反馈进行路由：

```bash
python .trae/skills/scripts/feedback_manager.py route \
  --input "I need to debug an issue" \
  --feedback-file feedback.json
```

#### 查询反馈

```bash
# 查询所有反馈（最近7天）
python .trae/skills/scripts/feedback_manager.py query

# 查询特定技能的反馈
python .trae/skills/scripts/feedback_manager.py query --skill brainstorming

# 查询不满意的反馈
python .trae/skills/scripts/feedback_manager.py query --satisfaction unsatisfied

# 查询最近30天的反馈
python .trae/skills/scripts/feedback_manager.py query --days 30
```

#### 反馈摘要

```bash
# 获取最近7天的反馈摘要
python .trae/skills/scripts/feedback_manager.py summary

# 获取最近30天的反馈摘要
python .trae/skills/scripts/feedback_manager.py summary --days 30
```

### 端到端测试

#### 运行所有测试

```bash
# 运行完整测试套件
python .trae/skills/scripts/test_e2e_integration.py

# 运行测试并显示详细报告
python .trae/skills/scripts/test_e2e_integration.py --report

# 运行测试并导出结果
python .trae/skills/scripts/test_e2e_integration.py --report --export test_results.json
```

#### 运行特定测试

```bash
# 测试头脑风暴工作流
python .trae/skills/scripts/test_e2e_integration.py --test brainstorming

# 测试反馈工作流
python .trae/skills/scripts/test_e2e_integration.py --test feedback

# 测试批量路由
python .trae/skills/scripts/test_e2e_integration.py --test batch

# 测试端到端工作流
python .trae/skills/scripts/test_e2e_integration.py --test e2e
```

### 工作流示例

#### 示例 1: 创建新功能

```bash
# 1. 头脑风暴
python .trae/skills/scripts/integrated_skill_invoker.py "I need to brainstorm a new feature"

# 2. 编写计划
python .trae/skills/scripts/integrated_skill_invoker.py "I need to write a plan for feature"

# 3. 执行实现
python .trae/skills/scripts/integrated_skill_invoker.py "I want to implement a feature" --execute

# 4. 验证
python .trae/skills/scripts/integrated_skill_invoker.py "I want to verify my implementation"

# 5. 提交反馈
python .trae/skills/scripts/feedback_manager.py submit \
  --input "I need to brainstorm a new feature" \
  --skill brainstorming \
  --satisfaction satisfied
```

#### 示例 2: 修复 Bug

```bash
# 1. 系统化调试
python .trae/skills/scripts/integrated_skill_invoker.py "I need to debug this bug" --execute

# 2. 如果不满意，提交反馈
python .trae/skills/scripts/feedback_manager.py submit \
  --input "I need to debug this bug" \
  --skill systematic-debugging \
  --satisfaction unsatisfied \
  --alternative "test-driven-development" \
  --reason "Need to write tests first"

# 3. 基于反馈重新路由
python .trae/skills/scripts/feedback_manager.py route \
  --input "I need to debug this bug" \
  --feedback-file feedback.json
```

### 日志和监控

#### 查看路由报告

```bash
# 生成最近7天的路由报告
python .trae/skills/scripts/routing_logger.py report 7

# 导出报告
python .trae/skills/scripts/routing_logger.py report 7 --export routing_report.json
```

#### 清理旧日志

```bash
# 清理30天前的日志
python .trae/skills/scripts/routing_logger.py clear 30
```

### API 使用示例

#### 在 Python 代码中使用

```python
from integrated_skill_invoker import IntegratedSkillInvoker
from feedback_manager import FeedbackManager

# 初始化
invoker = IntegratedSkillInvoker()
feedback_mgr = FeedbackManager()

# 路由和调用
result = invoker.invoke_with_routing("I need to brainstorm a new feature", dry_run=True)

# 提交反馈
feedback = feedback_mgr.submit_feedback(
    user_input="I need to brainstorm a new feature",
    original_skill="brainstorming",
    user_satisfaction="satisfied",
    reason="Perfect skill recommendation"
)

# 查询反馈
query_result = feedback_mgr.query_feedback(skill_name="brainstorming", days=7)

# 获取摘要
summary = feedback_mgr.get_feedback_summary(days=7)
```

### 最佳实践

1. **始终使用路由系统** - 不要手动选择技能，让路由器根据上下文推荐
2. **提供反馈** - 定期提交反馈以改进路由准确性
3. **干运行模式** - 在实际执行前使用干运行模式验证路由
4. **批量处理** - 对于多个相似请求，使用批量处理提高效率
5. **定期测试** - 运行端到端测试确保系统正常工作
6. **监控日志** - 定期查看路由报告了解系统性能

### 故障排除

#### 问题: 路由器找不到合适的技能

**解决方案**:
- 检查技能是否在 skill_map.json 中注册
- 确保技能包含正确的 context 字段
- 验证关键词匹配规则

#### 问题: 反馈未生效

**解决方案**:
- 确认反馈已成功提交
- 检查反馈日志文件是否存在
- 验证反馈格式是否正确

#### 问题: 测试失败

**解决方案**:
- 运行单个测试以定位问题
- 检查日志文件是否正确创建
- 验证技能路径是否有效

### 扩展和自定义

#### 添加新的路由规则

编辑 `skill_map.json` 中的 `detection_rules` 部分：

```json
{
  "detection_rules": {
    "exact_match": {
      "your trigger": "your-skill-name"
    },
    "partial_match": {
      "your keyword": ["skill1", "skill2"]
    }
  }
}
```

#### 添加新的阶段

在 `context_aware_router.py` 中：

```python
class Phase(Enum):
    YOUR_NEW_PHASE = "your_new_phase"
```

然后更新关键词映射和阶段转换逻辑。
