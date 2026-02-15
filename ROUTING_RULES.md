# 路由规则优先级文档

## 概述

本文档定义了技能路由系统的规则优先级、匹配类型和冲突解决策略，确保路由决策的一致性和可预测性。

## 技能发现和安装优先级

### 优先级等级

路由规则按以下优先级等级排序（从高到低）：

1. **精确匹配 (Exact Match)** - 优先级 1-2
   - 用户输入与技能触发词或短语完全匹配
   - 最高优先级，立即路由到指定技能
   - 示例：输入 "create skill" → 路由到 `skill-creator`
   - 优先级：1-2

2. **部分匹配 (Partial Match)** - 优先级 3-5
   - 用户输入包含技能相关的关键词，但不是精确匹配
   - 基于关键词权重计算匹配度
   - 考虑关键词在输入中的位置
   - 支持同义词和变体
   - 优先级：3-5

3. **上下文感知匹配 (Context-Aware Match)** - 优先级 6-8
   - 基于用户输入的语义和上下文信息进行匹配
   - 考虑对话历史、项目状态等因素
   - 示例：输入 "Let me think about this feature" → 路由到 `brainstorming`
   - 优先级：6-8

4. **默认路由 (Default Route)** - 优先级 9-10
   - 当没有明确匹配时的后备方案
   - 通常路由到通用技能或请求澄清
   - 优先级：9-10

### 技能发现和安装优先级

**技能发现 (Skill Discovery)**：
1. **本地管理技能** - find-skills (优先级 1)
2. **本地管理技能** - skill-installer (优先级 1)
3. **全局 Skills CLI** - npx skills find (优先级 2)
4. **直接 Git 克隆** - 最后选择 (优先级 3)

**技能安装 (Skill Installation)**：
1. **本地管理技能** - skill-installer (优先级 1)
2. **全局 Skills CLI** - npx skills add (优先级 2)
3. **直接 Git 克隆** - 最后选择 (优先级 3)

### 冲突解决策略

**场景 1：技能发现时避免触发技能安装**
- **问题**：用户搜索技能时，可能误触发 skill-installer 的关键词匹配
- **解决**：
  - 在技能发现时，临时禁用 skill-installer 的关键词匹配
  - 使用明确的 "search" 关键词，而不是 "install"
  - 提供明确的技能发现意图

**场景 2：技能安装时避免触发技能发现**
- **问题**：用户安装技能时，可能误触发 find-skills 的关键词匹配
- **解决**：
  - 在技能安装时，临时禁用 find-skills 的关键词匹配
  - 使用明确的 "install" 关键词
  - 提供明确的技能安装意图

### 上下文感知路由

**本地 vs 全局操作检测**：
- **本地技能发现**：检测到用户在查找本地技能
- **本地技能安装**：检测到用户在安装技能到本地项目
- **全局操作**：检测到用户在使用全局 Skills CLI

**优先级调整**：
- 本地管理技能操作时，临时提高其优先级
- 全局操作时，保持默认优先级

### 使用建议

**对于技能发现**：
```bash
# 优先使用本地管理技能
python .trae/skills/management/find-skills/scripts/find_skills.py "planning"

# 仅在本地管理技能不可用时使用全局 Skills CLI
npx skills find planning-with-files
```

**对于技能安装**：
```bash
# 优先使用本地管理技能
python .trae/skills/management/skill-installer/scripts/install_skill.py <source>

# 仅在本地管理技能不可用时使用全局 Skills CLI
npx skills add othmanadi/planning-with-files
```

**⚠️ 重要**：
- 使用本地管理技能（find-skills, skill-installer）可以确保自动质量检查和更好的集成
- 直接使用全局 Skills CLI 可能跳过质量检查和路由优先级

### 优先级等级

路由规则按以下优先级等级排序（从高到低）：

1. **精确匹配 (Exact Match)** - 优先级 1-2
   - 用户输入与技能触发词完全匹配
   - 最高优先级，立即路由到指定技能
   - 示例：输入 "create skill" → 路由到 `skill-creator`

2. **部分匹配 (Partial Match)** - 优先级 3-5
   - 用户输入包含技能关键词
   - 基于关键词权重计算匹配度
   - 示例：输入 "I want to create a new skill template" → 路由到 `skill-creator`

3. **上下文感知匹配 (Context-Aware Match)** - 优先级 6-8
   - 基于用户输入的语义和上下文分析
   - 考虑对话历史、项目状态等因素
   - 示例：输入 "Let me think about this feature" → 路由到 `brainstorming`

4. **默认路由 (Default Route)** - 优先级 9-10
   - 当没有明确匹配时的后备方案
   - 通常路由到通用技能或请求澄清

### 优先级数值映射

| 优先级等级 | 数值范围 | 描述 |
|-----------|---------|------|
| 关键 | 1-2 | 必须立即处理的精确匹配 |
| 高 | 3-5 | 强相关的部分匹配 |
| 中 | 6-8 | 基于上下文的合理匹配 |
| 低 | 9-10 | 默认或后备方案 |

## 匹配类型详解

### 1. 精确匹配 (Exact Match)

**定义**：用户输入与预定义的触发词或短语完全匹配。

**特征**：
- 100% 匹配度
- 不区分大小写
- 支持多语言触发词
- 优先级：1-2

**示例**：
```
输入: "create skill"
触发词: ["create skill", "create new skill", "make skill"]
匹配: 精确匹配
路由: skill-creator
优先级: 1
```

**实现要点**：
- 维护精确匹配触发词列表
- 使用正则表达式进行精确匹配
- 支持中英文双语触发词

### 2. 部分匹配 (Partial Match)

**定义**：用户输入包含技能相关的关键词，但不是精确匹配。

**特征**：
- 基于关键词权重计算匹配度
- 考虑关键词在输入中的位置
- 支持同义词和变体
- 优先级：3-5

**权重计算公式**：
```
匹配度 = Σ(关键词权重 × 出现次数) / 输入长度
优先级 = 10 - floor(匹配度 × 10) + 2
```

**示例**：
```
输入: "I want to create a new skill template for my project"
关键词: ["create", "skill", "template"]
权重: create(3), skill(5), template(2)
匹配度: (3×1 + 5×1 + 2×1) / 9 = 1.11
优先级: 3
路由: skill-creator
```

**实现要点**：
- 为每个技能定义关键词列表和权重
- 支持同义词扩展
- 考虑关键词的上下文相关性

### 3. 上下文感知匹配 (Context-Aware Match)

**定义**：基于用户输入的语义、意图和上下文信息进行匹配。

**特征**：
- 使用自然语言理解分析意图
- 考虑对话历史和项目状态
- 支持多阶段推理
- 优先级：6-8

**上下文因素**：
- **阶段检测**：识别当前开发阶段（构思、规划、实现、调试、验证）
- **关键词分析**：提取相关关键词和意图
- **置信度计算**：评估匹配的可靠性
- **历史上下文**：考虑之前的交互

**示例**：
```
输入: "Let me think about different approaches for this feature"
阶段检测: ideation
关键词: ["think", "approaches", "feature"]
置信度: 0.85
优先级: 6
路由: brainstorming
```

**实现要点**：
- 使用预训练的意图分类模型
- 维护对话历史缓冲区
- 实现阶段检测算法
- 计算置信度分数

## 优先级冲突解决策略

### 冲突类型

#### 1. 多个精确匹配冲突

**场景**：用户输入同时匹配多个精确规则。

**解决策略**：
- 选择优先级数值最低的规则
- 如果优先级相同，选择最具体的规则
- 如果仍然冲突，选择最近使用的规则

**示例**：
```
输入: "create skill"
匹配规则:
  - Rule A: "create skill" → skill-creator (priority: 1)
  - Rule B: "create" → generic-creator (priority: 1)
解决: 选择 Rule A（更具体）
```

#### 2. 不同匹配类型冲突

**场景**：精确匹配和部分匹配同时满足。

**解决策略**：
- 精确匹配优先级 > 部分匹配优先级
- 不考虑置信度差异

**示例**：
```
输入: "debug the code"
精确匹配: "debug" → systematic-debugging (priority: 2)
部分匹配: "code" → executing-plans (priority: 4)
解决: 选择 systematic-debugging
```

#### 3. 同优先级冲突

**场景**：多个规则具有相同优先级。

**解决策略**：
- 选择匹配度最高的规则
- 如果匹配度相同，选择最具体的规则
- 如果仍然冲突，选择最近使用的规则
- 如果仍然冲突，返回所有候选技能供用户选择

**示例**：
```
输入: "plan and implement the feature"
候选规则:
  - Rule A: "plan" → writing-plans (priority: 3, match: 0.9)
  - Rule B: "implement" → executing-plans (priority: 3, match: 0.85)
解决: 选择 writing-plans（更高匹配度）
```

#### 4. 阶段冲突

**场景**：推荐的技能来自不兼容的开发阶段。

**解决策略**：
- 检测阶段兼容性矩阵
- 如果冲突，选择主要阶段的技能
- 提供阶段转换建议

**不兼容阶段对**：
- ideation ↔ verification
- ideation ↔ debugging
- debugging ↔ ideation
- generation ↔ debugging

**示例**：
```
输入: "brainstorm and verify the idea"
推荐技能:
  - brainstorming (ideation phase)
  - verification-before-completion (verification phase)
冲突: ideation 和 verification 不兼容
解决: 选择 brainstorming（主要阶段），建议后续使用 verification
```

### 冲突解决算法

```
算法: resolve_conflicts(candidates)
输入: 候选技能列表
输出: 最终路由决策

1. 按优先级排序候选技能
2. 检查精确匹配
   - 如果存在精确匹配，返回最高优先级的精确匹配
3. 检查阶段冲突
   - 如果存在阶段冲突，选择主要阶段的技能
4. 检查同优先级冲突
   - 选择匹配度最高的技能
   - 如果匹配度相同，选择最具体的技能
5. 如果仍然无法解决
   - 返回所有候选技能供用户选择
   - 记录冲突日志
```

## 路由决策流程

### 完整流程图

```
用户输入
    ↓
[1] 精确匹配检查
    ├─ 匹配 → 返回结果
    └─ 不匹配 ↓
[2] 部分匹配检查
    ├─ 匹配 → 计算匹配度
    └─ 不匹配 ↓
[3] 上下文感知匹配
    ├─ 匹配 → 计算置信度
    └─ 不匹配 ↓
[4] 默认路由
    └─ 返回通用技能
    ↓
[5] 冲突检测与解决
    ├─ 无冲突 → 返回结果
    └─ 有冲突 → 应用解决策略
    ↓
[6] 返回最终路由决策
```

### 决策记录

每个路由决策应记录以下信息：
- 用户输入
- 匹配类型
- 候选技能列表
- 优先级分数
- 置信度/匹配度
- 冲突信息（如果有）
- 解决策略
- 最终决策
- 时间戳

## 配置示例

### 技能配置示例

```json
{
  "skill-creator": {
    "exact_matches": [
      "create skill",
      "create new skill",
      "make skill"
    ],
    "partial_matches": {
      "keywords": [
        {"word": "create", "weight": 3},
        {"word": "skill", "weight": 5},
        {"word": "template", "weight": 2}
      ]
    },
    "context": {
      "trigger_phase": "management",
      "priority": 1,
      "required_for": ["skill-creation", "template-management"]
    }
  },
  "brainstorming": {
    "partial_matches": {
      "keywords": [
        {"word": "brainstorm", "weight": 5},
        {"word": "idea", "weight": 4},
        {"word": "creative", "weight": 3}
      ]
    },
    "context": {
      "trigger_phase": "ideation",
      "priority": 2,
      "required_for": ["idea-generation", "creative-thinking"]
    }
  }
}
```

## 最佳实践

### 1. 规则设计原则

- **精确性优先**：为常用操作定义精确匹配规则
- **层次清晰**：保持优先级层次的清晰和一致
- **避免歧义**：确保规则之间没有不必要的重叠
- **可扩展性**：设计易于添加新规则的架构

### 2. 性能优化

- **缓存常用匹配**：缓存高频输入的匹配结果
- **提前终止**：在找到高优先级匹配后提前终止搜索
- **索引优化**：为关键词和触发词建立索引
- **并行处理**：对独立的匹配步骤进行并行处理

### 3. 监控与调优

- **记录决策日志**：记录所有路由决策用于分析
- **监控准确率**：跟踪路由决策的准确率
- **收集反馈**：收集用户反馈用于改进规则
- **定期审查**：定期审查和更新路由规则

## 附录

### A. 优先级速查表

| 匹配类型 | 优先级范围 | 典型场景 |
|---------|-----------|---------|
| 精确匹配 | 1-2 | 明确的命令或操作 |
| 部分匹配 | 3-5 | 包含关键词的自然语言输入 |
| 上下文感知 | 6-8 | 需要语义理解的复杂输入 |
| 默认路由 | 9-10 | 无明确匹配的后备方案 |

### B. 阶段兼容性矩阵

| | ideation | planning | implementation | debugging | verification | management | domain | generation |
|---|---|---|---|---|---|---|---|---|
| ideation | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ |
| planning | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| implementation | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| debugging | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| verification | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| management | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| domain | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| generation | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ |

### C. 冲突解决策略速查

| 冲突类型 | 解决策略 |
|---------|---------|
| 多个精确匹配 | 选择最具体、优先级最低的 |
| 不同匹配类型 | 精确 > 部分 > 上下文 |
| 同优先级 | 选择最高匹配度，然后最具体 |
| 阶段冲突 | 选择主要阶段，提供转换建议 |

---

**文档版本**: 1.0  
**最后更新**: 2026-02-15  
**维护者**: 技能路由系统团队
