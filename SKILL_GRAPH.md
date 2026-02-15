# Skills 关系图

本文档提供了 Trae Skills 系统的技能分类、依赖关系和使用流程的可视化说明。

---

## 目录

- [技能分类图](#技能分类图)
- [技能依赖关系图](#技能依赖关系图)
- [技能使用流程图](#技能使用流程图)
- [技能优先级](#技能优先级)
- [图例和说明](#图例和说明)

---

## 技能分类图

### 三大技能类别

```
┌─────────────────────────────────────────────────────────────────┐
│                      Trae Skills 生态系统                        │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Workflow   │    │  Management  │    │    Domain    │
│   工作流     │    │    管理      │    │    领域      │
│              │    │              │    │              │
│  • 头脑风暴  │    │  • 技能创建  │    │  • UI/UX     │
│  • 计划编写  │    │  • 技能安装  │    │  • 行为设计  │
│  • 计划执行  │    │  • 技能审计  │    │  • 产品设计  │
│  • 调试      │    │  • 技能查找  │    │  • 评估      │
│  • 测试      │    │              │    │  • 数据分析  │
│  • 验证      │    │              │    │  • 工程角色  │
│  • 完成      │    │              │    │  • 领导力    │
│  • 子代理    │    │              │    │  • 营销      │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Workflow 技能详细分类

```
Workflow 工作流技能
│
├─ Ideation 创意阶段
│  └─ brainstorming (头脑风暴)
│     • 探索需求
│     • 设计方案
│     • 创意生成
│
├─ Planning 规划阶段
│  ├─ writing-plans (编写计划)
│  │  • 创建实现计划
│  │  • 分解任务
│  │
│  └─ using-git-worktrees (使用 Git Worktrees)
│     • 隔离工作区
│     • 分支管理
│
├─ Implementation 实现阶段
│  ├─ executing-plans (执行计划)
│  │  • 逐任务执行
│  │  • 代码审查
│  │
│  ├─ test-driven-development (测试驱动开发)
│  │  • TDD 流程
│  │  • 测试优先
│  │
│  └─ subagent-driven-development (子代理驱动开发)
│     • 并行任务
│     • 独立执行
│
├─ Debugging 调试阶段
│  └─ systematic-debugging (系统化调试)
│     • 根因分析
│     • 问题追踪
│
└─ Verification 验证阶段
   ├─ verification-before-completion (完成前验证)
   │  • 运行测试
   │  • 质量检查
   │
   ├─ requesting-code-review (请求代码审查)
   │  • 代码审查
   │  • 质量保证
   │
   └─ finishing-a-development-branch (完成开发分支)
      • 合并决策
      • 分支清理
```

### Management 技能详细分类

```
Management 管理技能
│
├─ Skill Discovery 技能发现
│  └─ find-skills (查找技能)
│     • 搜索技能
│     • 发现功能
│
├─ Skill Creation 技能创建
│  └─ skill-creator (技能创建器)
│     • 创建新技能
│     • 技能模板
│     • 脚手架
│
├─ Skill Installation 技能安装
│  └─ skill-installer (技能安装器)
│     • 安装技能
│     • 更新技能
│     • 卸载技能
│
└─ Skill Validation 技能验证
   └─ skill-auditor (技能审计器)
      • 审计技能
      • 质量检查
      • 合规验证
```

### Domain 技能详细分类

```
Domain 领域技能
│
├─ Design 设计领域
│  ├─ ui-ux-pro-max-skill (UI/UX Pro Max)
│  │  • UI 设计
│  │  • UX 设计
│  │  • 设计系统
│  │
│  └─ behavioral-product-design (行为产品设计)
│     • 行为设计
│     • 心理学应用
│     • 产品优化
│
├─ Product 产品领域
│  └─ claude-skills (Claude 技能集合)
│     ├─ 产品管理
│     ├─ 产品设计
│     ├─ 产品策略
│     └─ UX 研究
│
├─ Engineering 工程领域
│  ├─ 高级架构师
│  ├─ 高级后端
│  ├─ 高级前端
│  ├─ 高级全栈
│  ├─ 高级 DevOps
│  ├─ 高级 QA
│  └─ 高级安全
│
├─ Data 数据领域
│  ├─ 数据分析师
│  ├─ 数据工程师
│  ├─ 数据科学家
│  ├─ BI 专家
│  └─ ML 工程师
│
├─ Leadership 领导力领域
│  ├─ CEO 顾问
│  ├─ CTO 顾问
│  ├─ CFO 顾问
│  ├─ CMO 顾问
│  └─ COO 顾问
│
├─ Marketing 营销领域
│  ├─ 品牌策略师
│  ├─ 内容策略师
│  ├─ 增长营销
│  ├─ SEO 专家
│  └─ 营销分析师
│
├─ Operations 运营领域
│  ├─ 项目经理
│  ├─ 敏捷教练
│  ├─ 交付经理
│  ├─ 项目经理
│  └─ Scrum Master
│
├─ Sales 销售领域
│  ├─ 销售工程师
│  ├─ 客户成功
│  ├─ 解决方案架构师
│  └─ 销售运营
│
└─ Evaluation 评估领域
   └─ evaluation (评估)
      • 代理评估
      • 质量测量
      • 测试框架
```

---

## 技能依赖关系图

### 核心依赖关系

```
                    ┌─────────────────┐
                    │  brainstorming   │
                    │   (优先级: 1)    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  writing-plans  │
                    │   (优先级: 2)   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
    ┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
    │ executing-plans │ │    TDD      │ │ using-git-      │
    │  (优先级: 3)    │ │ (优先级: 2) │ │ worktrees      │
    └────────┬────────┘ └─────────────┘ │  (优先级: 3)    │
             │                         └─────────────────┘
             │                                   │
             └──────────────┬────────────────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ systematic-debugging │
                 │    (优先级: 4)      │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ verification-before  │
                 │    completion       │
                 │    (优先级: 4)      │
                 └──────────┬──────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
    ┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
    │ requesting-code │ │ finishing-  │ │  集成到主分支   │
    │     review      │ │ a-development│ │                 │
    │  (优先级: 4)    │ │   branch    │ │                 │
    └─────────────────┘ │  (优先级: 4)│ │                 │
                        └─────────────┘ │                 │
                                       │                 │
                                       └─────────────────┘
```

### 技能创建依赖关系

```
┌─────────────────┐
│   find-skills   │
│  (优先级: 5)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ skill-creator   │
│  (优先级: 5)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  skill-auditor  │
│  (优先级: 5)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ requesting-code │
│     review      │
│  (优先级: 4)    │
└─────────────────┘
```

### UI/UX 设计依赖关系

```
┌─────────────────┐
│  brainstorming  │
│  (优先级: 1)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ui-ux-pro-max   │
│    -skill       │
│  (优先级: 6)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ behavioral-     │
│ product-design  │
│  (优先级: 6)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ verification-   │
│ before-         │
│ completion      │
│  (优先级: 4)    │
└─────────────────┘
```

---

## 技能使用流程图

### 场景 1: 创建新功能

```
开始
  │
  ▼
┌─────────────────┐
│ brainstorming   │ ◄── 必需
│ 探索需求和设计  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ writing-plans   │ ◄── 必需
│ 创建实现计划    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ using-git-      │ ◄── 可选
│ worktrees       │     隔离工作区
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ executing-plans │ ◄── 必需
│ 执行计划        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ test-driven-     │ ◄── 必需
│ development     │     TDD 开发
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ systematic-     │ ◄── 按需
│ debugging       │     调试问题
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ verification-   │ ◄── 必需
│ before-         │     验证完成
│ completion      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ requesting-code │ ◄── 推荐
│     review      │     代码审查
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ finishing-      │ ◄── 必需
│ a-development   │     完成分支
│     branch      │
└────────┬────────┘
         │
         ▼
       完成
```

### 场景 2: 修复 Bug

```
开始
  │
  ▼
┌─────────────────┐
│ systematic-     │ ◄── 必需
│ debugging       │     根因分析
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ writing-plans   │ ◄── 推荐
│ 创建修复计划    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ test-driven-     │ ◄── 必需
│ development     │     编写测试
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ executing-plans │ ◄── 必需
│ 实施修复        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ verification-   │ ◄── 必需
│ before-         │     验证修复
│ completion      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ requesting-code │ ◄── 推荐
│     review      │     代码审查
└────────┬────────┘
         │
         ▼
       完成
```

### 场景 3: 创建新技能

```
开始
  │
  ▼
┌─────────────────┐
│   find-skills   │ ◄── 推荐
│ 查找现有技能    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ skill-creator   │ ◄── 必需
│ 创建新技能      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  skill-auditor  │ ◄── 必需
│ 审计技能        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ requesting-code │ ◄── 推荐
│     review      │     代码审查
└────────┬────────┘
         │
         ▼
       完成
```

### 场景 4: 设计 UI/UX

```
开始
  │
  ▼
┌─────────────────┐
│  brainstorming  │ ◄── 必需
│ 探索设计需求    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ui-ux-pro-max   │ ◄── 必需
│    -skill       │     设计系统
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ behavioral-     │ ◄── 可选
│ product-design  │     行为设计
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ verification-   │ ◄── 必需
│ before-         │     验证设计
│ completion      │
└────────┬────────┘
         │
         ▼
       完成
```

---

## 技能优先级

### 优先级说明

优先级范围：1-10，其中 1 为最高优先级

| 优先级 | 技能 | 说明 |
|--------|------|------|
| 1 | brainstorming | 创意阶段，所有创造性工作的起点 |
| 2 | writing-plans, test-driven-development | 规划和测试阶段，关键步骤 |
| 3 | executing-plans, using-git-worktrees, subagent-driven-development | 实现阶段，执行任务 |
| 4 | systematic-debugging, verification-before-completion, requesting-code-review, finishing-a-development-branch | 调试和验证阶段，质量保证 |
| 5 | skill-creator, skill-installer, skill-auditor, find-skills | 管理阶段，技能管理 |
| 6 | ui-ux-pro-max-skill, behavioral-product-design, claude-skills, evaluation | 领域阶段，专业领域 |
| 7 | image-generation, pdf-generation | 生成阶段，文档生成 |

### 优先级排序

```
高优先级 (1-2)
├─ brainstorming (1)
├─ writing-plans (2)
└─ test-driven-development (2)

中高优先级 (3-4)
├─ executing-plans (3)
├─ using-git-worktrees (3)
├─ subagent-driven-development (3)
├─ systematic-debugging (4)
├─ verification-before-completion (4)
├─ requesting-code-review (4)
└─ finishing-a-development-branch (4)

中优先级 (5-6)
├─ skill-creator (5)
├─ skill-installer (5)
├─ skill-auditor (5)
├─ find-skills (5)
├─ ui-ux-pro-max-skill (6)
├─ behavioral-product-design (6)
├─ claude-skills (6)
└─ evaluation (6)

低优先级 (7)
├─ image-generation (7)
└─ pdf-generation (7)
```

---

## 图例和说明

### 符号说明

| 符号 | 含义 |
|------|------|
| `○` | 可选步骤 |
| `●` | 必需步骤 |
| `→` | 顺序执行 |
| `↔` | 可选执行 |
| `┌─┐` | 技能节点 |
| `│` | 连接线 |
| `▼` | 流程方向 |
| `◄──` | 标注说明 |

### 技能状态说明

| 状态 | 说明 |
|------|------|
| 必需 | 必须执行的技能，跳过可能导致问题 |
| 推荐 | 强烈建议执行的技能，可提高质量 |
| 可选 | 根据情况选择执行的技能 |
| 按需 | 在特定情况下才需要执行的技能 |

### 技能类别说明

| 类别 | 说明 | 示例 |
|------|------|------|
| Workflow | 工作流技能，用于软件开发流程 | brainstorming, writing-plans, executing-plans |
| Management | 管理技能，用于技能管理和发现 | skill-creator, skill-installer, find-skills |
| Domain | 领域技能，用于特定领域任务 | ui-ux-pro-max-skill, behavioral-product-design |

### 技能触发阶段说明

| 阶段 | 说明 | 技能 |
|------|------|------|
| ideation | 创意阶段，探索需求和设计 | brainstorming |
| planning | 规划阶段，创建计划和准备 | writing-plans, using-git-worktrees |
| implementation | 实现阶段，执行任务和开发 | executing-plans, test-driven-development, subagent-driven-development |
| debugging | 调试阶段，分析和修复问题 | systematic-debugging |
| verification | 验证阶段，验证和审查 | verification-before-completion, requesting-code-review, finishing-a-development-branch |
| management | 管理阶段，技能管理 | skill-creator, skill-installer, skill-auditor, find-skills |
| domain | 领域阶段，专业领域任务 | ui-ux-pro-max-skill, behavioral-product-design, claude-skills, evaluation |
| generation | 生成阶段，文档生成 | image-generation, pdf-generation |

### 技能依赖说明

| 依赖类型 | 说明 | 示例 |
|----------|------|------|
| 强依赖 | 必须先执行前置技能 | executing-plans 依赖 writing-plans |
| 弱依赖 | 建议先执行前置技能 | requesting-code-review 建议在 verification-before-completion 后 |
| 无依赖 | 可独立执行 | find-skills 可独立执行 |

---

## 使用建议

### 1. 选择正确的技能序列

根据任务类型选择合适的技能序列：
- **创建新功能**: brainstorming → writing-plans → executing-plans → test-driven-development → verification-before-completion → requesting-code-review → finishing-a-development-branch
- **修复 Bug**: systematic-debugging → writing-plans → test-driven-development → executing-plans → verification-before-completion → requesting-code-review
- **创建技能**: find-skills → skill-creator → skill-auditor → requesting-code-review
- **UI/UX 设计**: brainstorming → ui-ux-pro-max-skill → behavioral-product-design → verification-before-completion

### 2. 遵循技能优先级

优先使用高优先级的技能：
- 优先级 1-2: brainstorming, writing-plans, test-driven-development
- 优先级 3-4: executing-plans, systematic-debugging, verification-before-completion
- 优先级 5-6: skill-creator, ui-ux-pro-max-skill
- 优先级 7: image-generation, pdf-generation

### 3. 理解技能依赖

遵循技能依赖关系：
- executing-plans 依赖 writing-plans
- test-driven-development 依赖 writing-plans
- verification-before-completion 依赖所有实现技能
- requesting-code-review 依赖 verification-before-completion

### 4. 使用智能路由

系统会根据用户输入自动路由到合适的技能：
- 关键词匹配
- 上下文感知
- 反馈学习

### 5. 提供反馈

使用反馈系统改进路由准确性：
```bash
python .trae/skills/scripts/feedback_manager.py submit \
  --input "I need to debug this bug" \
  --skill systematic-debugging \
  --satisfaction satisfied
```

---

## 相关文档

- [EXAMPLES.md](EXAMPLES.md) - 技能使用示例
- [SKILL_ROUTING.md](SKILL_ROUTING.md) - 智能路由系统
- [SKILLS_REGISTRY.md](SKILLS_REGISTRY.md) - 技能注册表管理
- [SKILL_QUALITY_MONITOR.md](SKILL_QUALITY_MONITOR.md) - 质量监控系统
