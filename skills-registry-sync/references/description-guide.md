# AGENTS.md 技能描述编写指南

**Version:** 1.0.0  
**Last Updated:** 2026-03-12

---

## 一、核心原则

| 原则 | 说明 | 示例 |
|------|------|------|
| **简洁精准** | 字数控制在 100-120 字以内 | ❌ "This includes but is not limited to..." → ✅ "e.g.," |
| **结构化分组** | 按操作类型/场景分组，而非罗列 | creation / update / optimization |
| **中英均衡** | 每组 1 中 + 1 英示例，避免冗余 | "创建技能", "create skill" |
| **强制触发明确** | 使用 `**MUST**` 标注必要触发场景 | `**MUST invoke for...**` |

---

## 二、描述结构模板

```
[核心功能概述]. [强制触发场景] — [分组1] (e.g., "示例"), [分组2] (e.g., "示例"), or [分组3] (e.g., "示例").
```

**拆解：**
1. **功能概述**：一句话说明技能用途
2. **强制触发**：`**MUST invoke for...**` 明确边界
3. **分组示例**：用 `—` 引导，`e.g.,` 示例，`or` 连接

---

## 三、常见问题与修正

| 问题 | 错误示例 | 正确示例 |
|------|----------|----------|
| 法律腔 | "This includes but is not limited to" | "e.g.," |
| 关键词堆砌 | 罗列 20+ 个同义词 | 每组 1-2 个代表性示例 |
| 重复强调 | 多处 `**MUST**` / `**Do NOT**` | 仅保留一处强制声明 |
| 功能后置 | 触发词在前，功能在后 | 功能概述在前，触发场景在后 |

---

## 四、检查清单

编写/更新 AGENTS.md 技能描述时，逐项检查：

- [ ] 字数 ≤ 120 字
- [ ] 功能概述在前
- [ ] 使用 `e.g.,` 而非罗列
- [ ] 中英文示例均衡（每组各 1 个）
- [ ] 仅一处 `**MUST**` 强制声明
- [ ] 无法律腔措辞

---

## 五、优化示例

### 修改前（~280字，臃肿）

```
Create new skills, modify and improve existing skills, and measure skill performance. 
**MUST use this skill whenever users request any skill creation, generation, or update operations.** 
This includes but is not limited to: "创建技能", "生成技能", "新建技能", "制作技能", "开发技能", 
"create skill", "creat skill", "generate skill", "new skill", "make skill", "build skill", 
"更新技能", "修改技能", "优化技能", "改进技能", "update skill", "modify skill", "optimize skill", 
"improve skill", "edit skill", or any similar requests involving skill development. 
Also use for running evals to test a skill, benchmark skill performance with variance analysis, 
or optimizing a skill's description for better triggering accuracy. 
**Do NOT attempt to create or modify skills manually without invoking this skill first.**
```

### 修改后（~100字，简洁专业）

```
Create, update, and optimize skills with evaluation and benchmarking support. 
**MUST invoke for all skill development requests** — creation (e.g., "创建技能", "create skill"), 
update (e.g., "更新技能", "update skill"), or optimization (e.g., "优化技能", "improve skill").
```

---

## 六、应用场景

此指南适用于：
- 新增技能到 AGENTS.md
- 优化现有技能描述
- skills-registry-sync 同步时校验描述质量
- skill-creator 创建新技能时参考

---

*This guide is maintained by skills-registry-sync skill.*
