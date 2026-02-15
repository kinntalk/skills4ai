# Context Aware Skill Router

上下文感知技能路由器 - 基于用户输入和项目阶段智能推荐技能。

## 功能特性

### 1. 上下文检测
- 从用户输入中检测关键词和意图
- 支持8个开发阶段：ideation, planning, implementation, debugging, verification, management, domain, generation
- 支持中英文关键词
- 计算检测置信度

### 2. 阶段检测
- 从技能的 context 字段中检测触发阶段
- 根据 required_for 字段推断阶段
- 支持直接 trigger_phase 和间接推断

### 3. 技能推荐
- 基于阶段推荐相关技能
- 根据 priority 排序推荐结果
- 根据 required_for 过滤相关技能
- 计算推荐置信度

### 4. 冲突检测
- 检测同一阶段的高优先级技能冲突
- 检测依赖关系冲突
- 检测不兼容阶段的技能冲突
- 提供冲突解决建议

## 文件结构

```
.trae/skills/scripts/
├── context_aware_router.py      # 主路由器实现
├── test_context_aware_router.py  # 测试套件
└── demo_router.py               # 演示脚本
```

## 使用方法

### 1. 交互式模式

```bash
python .trae/skills/scripts/context_aware_router.py
```

然后输入你的需求，系统会：
- 检测上下文和阶段
- 推荐相关技能
- 检测潜在冲突
- 提供解决建议

### 2. 演示模式

```bash
python .trae/skills/scripts/demo_router.py
```

运行预设的测试用例，展示所有功能。

### 3. 测试模式

```bash
python .trae/skills/scripts/test_context_aware_router.py
```

运行完整的测试套件，验证所有功能。

## API 使用

### 基本用法

```python
from context_aware_router import ContextAwareRouter

router = ContextAwareRouter()

result = router.route("I want to brainstorm some ideas")
print(result)
```

### 返回结果

```python
{
    "user_input": "I want to brainstorm some ideas",
    "detected_phase": "ideation",
    "confidence": 0.67,
    "keywords": ["brainstorm", "idea"],
    "detected_intents": ["ideation:brainstorm", "ideation:idea"],
    "recommendations": [
        {
            "skill_name": "brainstorming",
            "priority": 1,
            "required_for": ["feature-creation", "component-building"],
            "confidence": 0.90,
            "reason": "Phase ideation requires skills for: feature-creation, component-building"
        }
    ],
    "conflicts": []
}
```

### 单独使用各个功能

```python
router = ContextAwareRouter()

# 1. 检测上下文
context_info = router.detect_context_from_user_input("I need to debug this bug")
print(context_info.phase)  # Phase.DEBUGGING

# 2. 检测阶段
phase = router.detect_phase_from_context({"trigger_phase": "planning"})
print(phase)  # Phase.PLANNING

# 3. 推荐技能
recommendations = router.recommend_skills_by_phase(Phase.IMPLEMENTATION)
for rec in recommendations:
    print(f"{rec.skill_name} (priority: {rec.priority})")

# 4. 检测冲突
conflicts = router.detect_skill_conflicts(["brainstorming", "verification-before-completion"])
for conflict in conflicts:
    print(f"{conflict.conflict_type}: {conflict.resolution}")
```

## 支持的阶段

| 阶段 | 描述 | 关键词示例 |
|------|------|-----------|
| ideation | 创意构思 | brainstorm, idea, creative, 头脑风暴, 创意 |
| planning | 规划设计 | plan, architecture, spec, 计划, 规划, 架构 |
| implementation | 实现开发 | implement, code, develop, feature, 实现, 开发 |
| debugging | 调试修复 | debug, bug, fix, error, 调试, 修复 |
| verification | 验证审查 | verify, test, review, 验证, 测试, 审查 |
| management | 技能管理 | skill, install, manage, 技能, 安装, 管理 |
| domain | 领域专业 | ui, ux, product, behavioral, 界面, 产品 |
| generation | 生成转换 | generate, image, pdf, render, 生成, 渲染 |

## 冲突检测规则

### 1. 高优先级冲突
- 同一阶段有多个 priority <= 2 的技能
- 建议：选择其中一个技能

### 2. 依赖冲突
- 多个技能有相同的 required_for
- 建议：使用一个覆盖需求的技能或顺序使用

### 3. 阶段冲突
- 不兼容阶段的技能组合：
  - ideation ↔ verification
  - ideation ↔ debugging
  - generation ↔ debugging
- 建议：按阶段顺序使用技能

## 测试结果

当前测试套件包含 33 个测试用例，成功率 100%：

- 上下文检测：9/9 通过
- 阶段检测：6/6 通过
- 技能推荐：8/8 通过
- 冲突检测：6/6 通过
- 集成测试：4/4 通过

## 扩展和自定义

### 添加新阶段

```python
class Phase(Enum):
    YOUR_NEW_PHASE = "your_new_phase"
```

### 添加新关键词

```python
router.phase_keywords[Phase.YOUR_NEW_PHASE] = [
    "keyword1", "keyword2", "关键词1", "关键词2"
]
```

### 自定义冲突规则

```python
incompatible_phases = [
    (Phase.PHASE1, Phase.PHASE2),
    (Phase.PHASE3, Phase.PHASE4)
]
```

## 依赖项

- Python 3.7+
- skill_map.json (位于 .trae/skills/)

## 注意事项

1. 确保 skill_map.json 文件存在且格式正确
2. 技能必须包含 context 字段才能被正确路由
3. 关键词检测是大小写不敏感的
4. 默认阶段是 implementation（当无法检测时）
