# Skills 使用示例

本文档提供了 Trae Skills 系统的常见使用场景和完整的技能调用序列示例。

---

## 技能发现和安装

### 推荐的工作流程

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

### 为什么使用本地管理技能？

**更好的集成**：
- find-skills 和 skill-installer 与本地技能深度集成
- 自动质量检查（skill-auditor）
- 一致的路由优先级
- 更好的错误处理

**避免的问题**：
- 直接使用 `npx skills find` 或 `npx skills add` 可能跳过质量检查
- 可能绕过路由优先级
- 缺少本地技能集成

### 何时使用全局 Skills CLI？

仅当以下情况时直接使用 `npx skills` 命令：
- 从外部仓库安装技能
- 从外部仓库更新技能
- 管理外部仓库中的技能

**对于本地技能**，始终使用本地管理技能（find-skills, skill-installer）以确保：
- 自动质量检查
- 一致的路由优先级
- 更好的本地技能集成

### ⚠️ 重要

使用本地管理技能（find-skills, skill-installer）可以确保自动质量检查和更好的集成。直接使用全局 Skills CLI 可能跳过质量检查和路由优先级。

---

## 目录

- [示例 1: 创建新功能](#示例-1-创建新功能)
- [示例 2: 修复 Bug](#示例-2-修复-bug)
- [示例 3: 创建新技能](#示例-3-创建新技能)
- [示例 4: 设计 UI/UX](#示例-4-设计-uiux)
- [示例 5: 代码审查](#示例-5-代码审查)
- [示例 6: 测试驱动开发](#示例-6-测试驱动开发)
- [示例 7: 系统化调试](#示例-7-系统化调试)

---

## 示例 1: 创建新功能

### 场景描述

用户需要为项目添加一个新功能，例如"用户认证系统"或"数据导出功能"。

### 完整技能调用序列

```
1. brainstorming (必需)
   ↓
2. writing-plans (必需)
   ↓
3. using-git-worktrees (可选)
   ↓
4. executing-plans (必需)
   ↓
5. test-driven-development (必需)
   ↓
6. systematic-debugging (按需)
   ↓
7. verification-before-completion (必需)
   ↓
8. requesting-code-review (推荐)
   ↓
9. finishing-a-development-branch (必需)
```

### 详细步骤

#### 步骤 1: brainstorming

**触发条件**: 用户请求创建新功能

**用户输入示例**:
```
我想为我的项目添加用户认证系统，支持邮箱注册、登录和密码重置。
```

**技能行为**:
- 检查当前项目状态（文件、文档、最近提交）
- 一次提出一个问题以细化需求
- 提出 2-3 种不同的实现方案及其权衡
- 领先推荐最佳方案并解释原因

**输出示例**:
```
我理解你想添加用户认证系统。让我先了解一下：

1. 你使用的是什么技术栈？（React/Vue/Next.js 等）
2. 你希望使用哪种认证方式？（JWT、Session、OAuth 等）
3. 你是否需要第三方登录（Google、GitHub 等）？
```

#### 步骤 2: writing-plans

**触发条件**: 头脑风暴完成，需求明确

**用户输入示例**:
```
我已经确定了需求，现在需要编写实现计划。
```

**技能行为**:
- 创建详细的实现计划
- 将任务分解为可执行的小步骤（每个步骤 2-5 分钟）
- 包含文件路径、代码示例、测试命令
- 保存到 `docs/plans/YYYY-MM-DD-<feature-name>.md`

**输出示例**:
```markdown
# User Authentication Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement email-based user authentication with registration, login, and password reset

**Architecture:** JWT-based authentication with bcrypt password hashing

**Tech Stack:** Next.js 14, NextAuth.js, Prisma, PostgreSQL

---

### Task 1: Setup Prisma Schema

**Files:**
- Modify: `prisma/schema.prisma`

**Step 1: Add User model**
[代码示例]

**Step 2: Run migration**
Run: `npx prisma migrate dev --name add-user-model`
Expected: Migration successful

**Step 3: Commit**
Run: `git add prisma/schema.prisma prisma/migrations/`
Run: `git commit -m "feat: add user model"`
```

#### 步骤 3: using-git-worktrees (可选)

**触发条件**: 需要隔离工作环境

**用户输入示例**:
```
我想在独立的工作树中开发这个功能。
```

**技能行为**:
- 创建新的 git worktree
- 在独立环境中工作
- 避免污染主分支

**输出示例**:
```bash
# 创建新的 worktree
git worktree add ../feature-auth feature/auth

# 切换到 worktree
cd ../feature-auth

# 开始开发
```

#### 步骤 4: executing-plans

**触发条件**: 实现计划已创建

**用户输入示例**:
```
现在开始执行实现计划。
```

**技能行为**:
- 逐个任务执行计划
- 每个任务完成后进行代码审查
- 使用子代理进行任务执行

**输出示例**:
```
正在执行 Task 1: Setup Prisma Schema...

✓ Step 1: Add User model
✓ Step 2: Run migration
✓ Step 3: Commit

Task 1 完成。代码审查通过。

正在执行 Task 2: Setup NextAuth...
```

#### 步骤 5: test-driven-development

**触发条件**: 需要编写测试

**用户输入示例**:
```
我需要为认证功能编写测试。
```

**技能行为**:
- 先编写失败的测试
- 实现代码使测试通过
- 重构代码
- 确保测试覆盖率

**输出示例**:
```typescript
// Step 1: Write failing test
describe('User Registration', () => {
  it('should register a new user', async () => {
    const response = await registerUser({
      email: 'test@example.com',
      password: 'SecurePass123!'
    });
    expect(response.success).toBe(true);
  });
});

// Step 2: Run test (should fail)
npm test -- User Registration

// Step 3: Implement minimal code
async function registerUser(data) {
  // 实现代码
}

// Step 4: Run test (should pass)
npm test -- User Registration
```

#### 步骤 6: systematic-debugging (按需)

**触发条件**: 遇到测试失败或错误

**用户输入示例**:
```
测试失败了，我需要调试这个问题。
```

**技能行为**:
- 阅读错误信息
- 重现问题
- 检查最近的更改
- 追踪数据流
- 找到根本原因
- 实施修复

**输出示例**:
```
Phase 1: Root Cause Investigation
- Error: "Email already exists"
- Reproduction: Register same email twice
- Recent changes: Added unique constraint on email
- Root cause: No duplicate check before insertion

Phase 2: Pattern Analysis
- Working example: Login endpoint checks user existence
- Difference: Registration doesn't check before insert

Phase 3: Hypothesis
- Hypothesis: Need to check if user exists before creating

Phase 4: Implementation
- Add user existence check
- Test passes
```

#### 步骤 7: verification-before-completion

**触发条件**: 实现完成，准备交付

**用户输入示例**:
```
功能已经实现完成，请验证。
```

**技能行为**:
- 运行所有测试
- 检查代码质量
- 验证功能完整性
- 确认文档更新
- 检查性能影响

**输出示例**:
```
✓ All tests passing (45/45)
✓ Code quality check passed
✓ Feature requirements met
✓ Documentation updated
✓ Performance acceptable

Verification complete. Ready for code review.
```

#### 步骤 8: requesting-code-review (推荐)

**触发条件**: 实现验证完成

**用户输入示例**:
```
请帮我进行代码审查。
```

**技能行为**:
- 检查代码风格
- 识别潜在问题
- 提供改进建议
- 确认最佳实践

**输出示例**:
```
Code Review Results:

✓ Code style consistent
✓ No security vulnerabilities
✓ Good error handling
⚠ Suggestion: Add input validation for email format
⚠ Suggestion: Consider rate limiting for registration

Overall: APPROVED with minor suggestions
```

#### 步骤 9: finishing-a-development-branch

**触发条件**: 代码审查完成

**用户输入示例**:
```
开发完成，我该如何集成这个功能？
```

**技能行为**:
- 决定集成策略（merge/rebase/squash）
- 准备 Pull Request
- 合并代码
- 清理工作树

**输出示例**:
```
Integration Strategy: Squash and Merge

Steps:
1. Create pull request with description
2. Request review from team
3. Squash commits into single feature commit
4. Merge to main branch
5. Delete feature branch
6. Clean up worktree

PR created: https://github.com/user/repo/pull/123
```

---

## 示例 2: 修复 Bug

### 场景描述

用户遇到一个 bug，需要系统化地调试和修复。

### 完整技能调用序列

```
1. systematic-debugging (必需)
   ↓
2. writing-plans (推荐)
   ↓
3. test-driven-development (必需)
   ↓
4. executing-plans (必需)
   ↓
5. verification-before-completion (必需)
   ↓
6. requesting-code-review (推荐)
```

### 详细步骤

#### 步骤 1: systematic-debugging

**触发条件**: 遇到 bug 或测试失败

**用户输入示例**:
```
我的登录功能有问题，用户无法登录，显示 "Invalid credentials" 错误，即使密码是正确的。
```

**技能行为**:
- 阅读错误信息
- 重现问题
- 检查最近的更改
- 追踪数据流
- 找到根本原因

**输出示例**:
```
Phase 1: Root Cause Investigation

1. Read Error Messages
   - Error: "Invalid credentials"
   - Location: auth/login.ts:45

2. Reproduce Consistently
   - Steps: Register user → Try login with correct password
   - Result: Error occurs every time

3. Check Recent Changes
   - Last commit: "refactor: update password hashing"
   - Changed bcrypt rounds from 10 to 12

4. Trace Data Flow
   - Registration: bcrypt.hash(password, 12)
   - Login: bcrypt.compare(password, hashedPassword)
   - Issue: Database still has old hashes (rounds=10)

Root Cause: Password hashing algorithm changed but existing passwords not rehashed
```

#### 步骤 2: writing-plans (推荐)

**触发条件**: 根本原因已找到

**用户输入示例**:
```
我已经找到根本原因了，现在需要制定修复计划。
```

**技能行为**:
- 创建修复计划
- 包含测试策略
- 考虑向后兼容性

**输出示例**:
```markdown
# Password Hashing Fix Plan

**Goal:** Fix login issue caused by bcrypt rounds change

**Root Cause:** Existing passwords hashed with rounds=10, new code expects rounds=12

**Approach:** Rehash passwords on successful login

---

### Task 1: Write failing test

**Files:**
- Create: `tests/auth/login.test.ts`

**Step 1: Add test for old password hash**
[测试代码]

**Step 2: Run test**
Expected: FAIL

### Task 2: Implement rehashing logic

**Files:**
- Modify: `src/auth/login.ts`

**Step 1: Add rehashing after successful login**
[实现代码]

**Step 2: Test**
Expected: PASS

### Task 3: Update database schema

**Files:**
- Modify: `prisma/schema.prisma`

**Step 1: Add passwordVersion field**
[Schema 更新]

**Step 2: Run migration**
Run: `npx prisma migrate dev`
```

#### 步骤 3: test-driven-development

**触发条件**: 修复计划已创建

**用户输入示例**:
```
现在开始用 TDD 方式修复这个 bug。
```

**技能行为**:
- 先编写失败的测试
- 实现修复代码
- 确保测试通过
- 添加回归测试

**输出示例**:
```typescript
// Step 1: Write failing test
describe('Login with old password hash', () => {
  it('should rehash password on successful login', async () => {
    // Create user with old hash (rounds=10)
    const oldHash = await bcrypt.hash('password123', 10);
    await createUser({ email: 'test@example.com', password: oldHash });

    // Login should succeed and rehash
    const result = await loginUser('test@example.com', 'password123');
    expect(result.success).toBe(true);

    // Verify password was rehashed
    const user = await getUser('test@example.com');
    const newHash = user.password;
    expect(await bcrypt.compare('password123', newHash)).toBe(true);
  });
});

// Step 2: Run test (fails)
npm test -- "Login with old password hash"
// FAIL: Password not rehashed

// Step 3: Implement fix
async function loginUser(email, password) {
  const user = await getUser(email);
  const isValid = await bcrypt.compare(password, user.password);

  if (isValid) {
    // Rehash if needed
    const needsRehash = !user.password.startsWith('$2b$12');
    if (needsRehash) {
      const newHash = await bcrypt.hash(password, 12);
      await updateUser(user.id, { password: newHash });
    }
    return { success: true };
  }

  return { success: false, error: 'Invalid credentials' };
}

// Step 4: Run test (passes)
npm test -- "Login with old password hash"
// PASS
```

#### 步骤 4: executing-plans

**触发条件**: 测试通过

**用户输入示例**:
```
测试通过了，现在执行完整的修复计划。
```

**技能行为**:
- 执行剩余的任务
- 更新数据库
- 运行所有测试
- 提交更改

**输出示例**:
```
✓ Task 1: Write failing test
✓ Task 2: Implement rehashing logic
✓ Task 3: Update database schema
✓ Task 4: Run all tests
✓ Task 5: Commit changes

All tasks completed successfully.
```

#### 步骤 5: verification-before-completion

**触发条件**: 修复完成

**用户输入示例**:
```
修复已完成，请验证。
```

**技能行为**:
- 验证 bug 已修复
- 检查回归测试
- 验证向后兼容性
- 确认性能影响

**输出示例**:
```
✓ Bug fixed: Users can now login with old passwords
✓ All tests passing (50/50)
✓ Backward compatibility maintained
✓ Performance impact: Negligible (rehashing only on login)
✓ No new issues introduced

Verification complete. Ready for code review.
```

#### 步骤 6: requesting-code-review (推荐)

**触发条件**: 验证完成

**用户输入示例**:
```
请审查这个修复。
```

**技能行为**:
- 审查修复代码
- 检查安全性
- 验证测试覆盖

**输出示例**:
```
Code Review Results:

✓ Root cause correctly identified
✓ Fix is minimal and targeted
✓ Tests cover edge cases
✓ Security: No vulnerabilities
✓ Performance: Acceptable

Overall: APPROVED
```

---

## 示例 3: 创建新技能

### 场景描述

用户需要创建一个新的技能来扩展 Claude 的能力。

### 完整技能调用序列

```
1. find-skills (推荐)
   ↓
2. skill-creator (必需)
   ↓
3. skill-auditor (必需)
   ↓
4. requesting-code-review (推荐)
```

### 详细步骤

#### 步骤 1: find-skills (推荐)

**触发条件**: 用户想创建新技能

**用户输入示例**:
```
我想创建一个用于生成 API 文档的技能。
```

**技能行为**:
- 搜索现有技能
- 检查是否已有类似技能
- 提供参考示例

**输出示例**:
```
搜索结果:

✓ 找到 3 个相关技能:
  1. pdf-generation - 生成 PDF 文档
  2. image-generation - 生成图片
  3. behavioral-product-design - 产品设计

建议: 没有找到专门用于 API 文档生成的技能，可以创建新技能。

参考技能:
- pdf-generation 的结构可以作为模板
- 参考 SKILL.md 格式规范
```

#### 步骤 2: skill-creator

**触发条件**: 确认需要创建新技能

**用户输入示例**:
```
请帮我创建一个 API 文档生成技能。
```

**技能行为**:
- 使用模板创建技能结构
- 生成 SKILL.md
- 创建必要的目录和文件
- 配置 skill_map.json

**输出示例**:
```bash
# 使用内置模板创建技能
python .trae/skills/management/skill-creator/scripts/init_skill.py api-doc-generator --path .trae/skills/

# 输出
✓ Created .trae/skills/management/api-doc-generator/
✓ Created SKILL.md
✓ Created scripts/example.py
✓ Created scripts/requirements.txt
✓ Created references/api_reference.md
✓ Created assets/example_asset.txt

# 生成的 SKILL.md
---
name: api-doc-generator
description: Generate API documentation from code annotations and comments
keywords:
  - api
  - documentation
  - generate
  - docs
  - swagger
  - openapi
  - rest
  - graphql
  - API
  - 文档
  - 生成
  - 接口
aliases:
  - api-doc-generator
  - api-docs
  - generate-api-docs
---

# API Documentation Generator

## Overview

Generate comprehensive API documentation from code annotations, JSDoc comments, and type definitions.

## When to Use

Use this skill when:
- User wants to generate API documentation
- User needs to create Swagger/OpenAPI specs
- User asks to document REST/GraphQL APIs
- User mentions "API docs" or "documentation"

## Usage

### Generate Documentation from Code

```bash
python .trae/skills/management/api-doc-generator/scripts/generate_docs.py --input ./src --output ./docs/api
```

### Generate OpenAPI Spec

```bash
python .trae/skills/management/api-doc-generator/scripts/generate_openapi.py --input ./src --format json
```

## Resources

- `scripts/generate_docs.py` - Main documentation generator
- `scripts/generate_openapi.py` - OpenAPI spec generator
- `references/api_reference.md` - API reference documentation
```

#### 步骤 3: skill-auditor

**触发条件**: 技能创建完成

**用户输入示例**:
```
技能已创建，请审计它。
```

**技能行为**:
- 检查 frontmatter 格式
- 验证依赖完整性
- 检查编码和路径安全
- 验证跨平台兼容性
- 检查国际化支持
- 验证质量标准

**输出示例**:
```bash
# 运行审计
python .trae/skills/management/skill-auditor/scripts/audit_skill.py .trae/skills/management/api-doc-generator

# 审计结果
✓ Frontmatter format: VALID
✓ Dependencies: COMPLETE
✓ Encoding: UTF-8
✓ Path safety: SAFE
✓ Cross-platform: COMPATIBLE
✓ i18n: SUPPORTED (English + Chinese)
✓ Quality standards: MET

Overall: PASSED

Suggestions:
- Add more keywords for better discoverability
- Consider adding example usage in SKILL.md
```

#### 步骤 4: requesting-code-review (推荐)

**触发条件**: 审计通过

**用户输入示例**:
```
请审查这个新技能。
```

**技能行为**:
- 审查技能文档
- 检查代码质量
- 验证最佳实践
- 提供改进建议

**输出示例**:
```
Skill Review Results:

✓ SKILL.md format correct
✓ Keywords comprehensive
✓ Description clear and concise
✓ Scripts well-structured
✓ References useful
⚠ Suggestion: Add more examples in SKILL.md
⚠ Suggestion: Consider adding unit tests for scripts

Overall: APPROVED with minor suggestions
```

---

## 示例 4: 设计 UI/UX

### 场景描述

用户需要设计用户界面或用户体验。

### 完整技能调用序列

```
1. brainstorming (必需)
   ↓
2. ui-ux-pro-max-skill (必需)
   ↓
3. behavioral-product-design (可选)
   ↓
4. verification-before-completion (必需)
```

### 详细步骤

#### 步骤 1: brainstorming

**触发条件**: 用户请求 UI/UX 设计

**用户输入示例**:
```
我想为我的 SaaS 产品设计一个仪表板页面。
```

**技能行为**:
- 了解产品类型和目标用户
- 探索设计需求
- 提出不同的设计方向

**输出示例**:
```
让我了解一下你的仪表板需求：

1. 你的 SaaS 产品是什么类型？（项目管理、数据分析、CRM 等）
2. 目标用户是谁？（开发者、业务人员、管理层等）
3. 仪表板需要展示哪些关键信息？
4. 你希望的设计风格是什么？（现代、专业、极简等）
```

#### 步骤 2: ui-ux-pro-max-skill

**触发条件**: 需求明确

**用户输入示例**:
```
这是一个数据分析 SaaS，目标用户是业务分析师，需要展示销售数据、用户增长和关键指标。风格要现代、专业。
```

**技能行为**:
- 生成设计系统
- 推荐颜色方案
- 推荐字体配对
- 提供组件建议
- 提供最佳实践

**输出示例**:
```bash
# 生成设计系统
python .trae/skills/domain/ui-ux-pro-max-skill/scripts/search.py "data analytics SaaS dashboard modern professional" --design-system -p "Analytics Dashboard"

# 输出
╔══════════════════════════════════════════════════════════════════════════════╗
║                    DESIGN SYSTEM: Analytics Dashboard                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 PATTERN: Dashboard with data visualization
   - Grid-based layout
   - Card-based widgets
   - Interactive charts

🎨 STYLE: Modern Professional
   - Clean, minimal design
   - High contrast for data
   - Subtle shadows and borders

🎨 COLORS:
   Primary: #3B82F6 (Blue-500)
   Secondary: #10B981 (Emerald-500)
   Background: #F8FAFC (Slate-50)
   Surface: #FFFFFF (White)
   Text: #1E293B (Slate-800)

📝 TYPOGRAPHY:
   Heading: Inter (700, 600)
   Body: Inter (400, 500)
   Monospace: JetBrains Mono

✨ EFFECTS:
   - Subtle box-shadow: 0 1px 3px rgba(0,0,0,0.1)
   - Smooth transitions: 200ms
   - Hover lift: translateY(-2px)

🚫 ANTI-PATTERNS TO AVOID:
   - Don't use low contrast colors for data
   - Don't overcrowd the dashboard
   - Don't use too many colors
   - Don't ignore accessibility
```

#### 步骤 3: behavioral-product-design (可选)

**触发条件**: 需要应用行为设计原则

**用户输入示例**:
```
我想让用户更频繁地使用仪表板。
```

**技能行为**:
- 应用行为设计原则
- 设计激励机制
- 优化用户参与度

**输出示例**:
```
Behavioral Design Principles for Dashboard:

1. Variable Rewards
   - Show different insights each visit
   - Highlight new data or trends

2. Social Proof
   - Show "X users viewed this today"
   - Display team activity

3. Progress Indicators
   - Show goal progress
   - Display achievements

4. Instant Gratification
   - Fast load times
   - Smooth animations
   - Immediate feedback

5. Loss Aversion
   - Show what's at risk
   - Highlight declining metrics
```

#### 步骤 4: verification-before-completion

**触发条件**: 设计完成

**用户输入示例**:
```
设计已完成，请验证。
```

**技能行为**:
- 检查可访问性
- 验证响应式设计
- 检查性能
- 验证用户体验

**输出示例**:
```
✓ Accessibility: Color contrast 4.5:1, focus states visible
✓ Responsive: Works on 375px, 768px, 1024px, 1440px
✓ Performance: Lighthouse score 95+
✓ UX: Clear navigation, intuitive interactions
✓ Consistency: Design system followed

Verification complete. Ready for implementation.
```

---

## 示例 5: 代码审查

### 场景描述

用户需要对代码进行审查。

### 完整技能调用序列

```
requesting-code-review (必需)
```

### 详细步骤

#### 步骤 1: requesting-code-review

**触发条件**: 用户请求代码审查

**用户输入示例**:
```
请审查我的代码。
```

**技能行为**:
- 检查代码风格
- 识别潜在问题
- 提供改进建议
- 确认最佳实践
- 检查安全性

**输出示例**:
```
Code Review Results for src/auth/login.ts:

✓ Code Style
  - Consistent with project style
  - Proper indentation and formatting
  - Meaningful variable names

✓ Functionality
  - Logic is correct
  - Error handling is comprehensive
  - Edge cases are covered

⚠ Potential Issues
  1. Line 45: Consider adding rate limiting
  2. Line 78: SQL injection risk - use parameterized queries
  3. Line 120: Unused variable 'temp'

✓ Security
  - Password hashing is secure (bcrypt)
  - No sensitive data in logs
  - Input validation present

⚠ Performance
  - Consider caching user data
  - Optimize database queries

✓ Testing
  - Tests cover main functionality
  - Consider adding edge case tests

Overall: APPROVED with minor improvements suggested

Priority Fixes:
1. Fix SQL injection risk (Line 78)
2. Remove unused variable (Line 120)

Nice to Have:
- Add rate limiting
- Add caching
- Add more edge case tests
```

---

## 示例 6: 测试驱动开发

### 场景描述

用户需要使用 TDD 方法开发功能。

### 完整技能调用序列

```
test-driven-development (必需)
   ↓
executing-plans (必需)
   ↓
verification-before-completion (必需)
```

### 详细步骤

#### 步骤 1: test-driven-development

**触发条件**: 用户想用 TDD 开发功能

**用户输入示例**:
```
我想用 TDD 方法开发一个用户注册功能。
```

**技能行为**:
- 先编写失败的测试
- 实现最小代码使测试通过
- 重构代码
- 重复循环

**输出示例**:
```typescript
// RED: Write failing test
describe('User Registration', () => {
  it('should register a new user with valid data', async () => {
    const userData = {
      email: 'test@example.com',
      password: 'SecurePass123!',
      name: 'Test User'
    };

    const result = await registerUser(userData);

    expect(result.success).toBe(true);
    expect(result.user.email).toBe(userData.email);
    expect(result.user.id).toBeDefined();
  });

  it('should reject invalid email', async () => {
    const userData = {
      email: 'invalid-email',
      password: 'SecurePass123!',
      name: 'Test User'
    };

    const result = await registerUser(userData);

    expect(result.success).toBe(false);
    expect(result.error).toContain('Invalid email');
  });

  it('should reject weak password', async () => {
    const userData = {
      email: 'test@example.com',
      password: 'weak',
      name: 'Test User'
    };

    const result = await registerUser(userData);

    expect(result.success).toBe(false);
    expect(result.error).toContain('Password too weak');
  });
});

// Run tests - RED
npm test
// FAIL: registerUser not defined

// GREEN: Implement minimal code
async function registerUser(userData) {
  // Validate email
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(userData.email)) {
    return { success: false, error: 'Invalid email' };
  }

  // Validate password
  if (userData.password.length < 8) {
    return { success: false, error: 'Password too weak' };
  }

  // Create user
  const user = await db.users.create({
    data: {
      email: userData.email,
      password: await bcrypt.hash(userData.password, 10),
      name: userData.name
    }
  });

  return { success: true, user };
}

// Run tests - GREEN
npm test
// PASS: All tests passing

// REFACTOR: Improve code
async function registerUser(userData) {
  const errors = validateUserData(userData);
  if (errors.length > 0) {
    return { success: false, error: errors.join(', ') };
  }

  const hashedPassword = await hashPassword(userData.password);
  const user = await createUser({
    ...userData,
    password: hashedPassword
  });

  return { success: true, user };
}

// Run tests - GREEN
npm test
// PASS: All tests passing
```

#### 步骤 2: executing-plans

**触发条件**: 测试通过

**用户输入示例**:
```
测试通过了，现在继续实现其他功能。
```

**技能行为**:
- 执行下一个 TDD 循环
- 持续添加功能
- 保持测试通过

#### 步骤 3: verification-before-completion

**触发条件**: 所有功能实现完成

**用户输入示例**:
```
所有功能已实现，请验证。
```

**技能行为**:
- 运行所有测试
- 检查代码覆盖率
- 验证功能完整性

**输出示例**:
```
✓ All tests passing (75/75)
✓ Code coverage: 95%
✓ All features implemented
✓ No regressions

Verification complete. Ready for code review.
```

---

## 示例 7: 系统化调试

### 场景描述

用户遇到复杂问题需要系统化调试。

### 完整技能调用序列

```
systematic-debugging (必需)
   ↓
writing-plans (推荐)
   ↓
test-driven-development (必需)
   ↓
executing-plans (必需)
   ↓
verification-before-completion (必需)
```

### 详细步骤

#### 步骤 1: systematic-debugging

**触发条件**: 遇到复杂问题

**用户输入示例**:
```
我的应用在生产环境中偶尔崩溃，错误日志显示 "Memory limit exceeded"。
```

**技能行为**:
- Phase 1: Root Cause Investigation
- Phase 2: Pattern Analysis
- Phase 3: Hypothesis and Testing
- Phase 4: Implementation

**输出示例**:
```
Phase 1: Root Cause Investigation

1. Read Error Messages
   - Error: "Memory limit exceeded"
   - Location: Unknown (production only)
   - Frequency: Occasional (1-2 times per day)

2. Reproduce Consistently
   - Cannot reproduce locally
   - Only happens in production
   - Need to gather more data

3. Check Recent Changes
   - Last deployment: 2 days ago
   - Changes: Added image processing feature
   - Suspicious: Large file uploads

4. Gather Evidence in Multi-Component System

   Add diagnostic instrumentation:
   ```javascript
   // Layer 1: Upload endpoint
   console.log('Memory before upload:', process.memoryUsage());

   // Layer 2: Image processing
   console.log('Memory during processing:', process.memoryUsage());

   // Layer 3: Database save
   console.log('Memory before save:', process.memoryUsage());
   ```

5. Trace Data Flow
   - Upload → Process → Save → Response
   - Memory spikes during processing
   - Not released after save

Root Cause: Image processing doesn't clean up memory after large files

Phase 2: Pattern Analysis

1. Find Working Examples
   - Small files (< 1MB): No memory issues
   - Large files (> 10MB): Memory spikes

2. Compare Against References
   - Sharp library docs: "Use .toBuffer() to free memory"
   - Current code: Not calling .toBuffer()

3. Identify Differences
   - Working: Explicitly free memory
   - Broken: Rely on garbage collection

4. Understand Dependencies
   - Sharp library requires manual cleanup
   - Node.js GC doesn't free immediately

Phase 3: Hypothesis and Testing

Hypothesis: Not calling .toBuffer() causes memory leak

Test: Add .toBuffer() call and monitor memory

Result: Memory usage drops by 80%

Phase 4: Implementation

1. Create failing test
   - Test memory usage with large file

2. Implement fix
   - Add .toBuffer() call
   - Add explicit cleanup

3. Verify fix
   - Memory usage stable
   - No crashes in production
```

---

## 技能使用最佳实践

### 1. 选择正确的技能

- **创建新功能**: brainstorming → writing-plans → executing-plans → test-driven-development
- **修复 Bug**: systematic-debugging → test-driven-development
- **创建技能**: find-skills → skill-creator → skill-auditor
- **UI/UX 设计**: brainstorming → ui-ux-pro-max-skill

### 2. 遵循技能依赖

某些技能有明确的依赖关系：
- `executing-plans` 依赖 `writing-plans`
- `test-driven-development` 依赖 `writing-plans`
- `verification-before-completion` 依赖所有实现技能

### 3. 使用智能路由

系统会根据用户输入自动路由到合适的技能：
- 关键词匹配
- 上下文感知
- 反馈学习

### 4. 提供反馈

使用 `feedback_manager.py` 提供反馈以改进路由准确性：
```bash
python .trae/skills/scripts/feedback_manager.py submit \
  --input "I need to debug this bug" \
  --skill systematic-debugging \
  --satisfaction satisfied
```

### 5. 定期审计

使用 `skill-auditor` 定期审计技能：
```bash
python .trae/skills/management/skill-auditor/scripts/audit_skill.py <skill-path>
```

---

## 相关文档

- [SKILL_ROUTING.md](SKILL_ROUTING.md) - 智能路由系统
- [SKILLS_REGISTRY.md](SKILLS_REGISTRY.md) - 技能注册表管理
- [SKILL_QUALITY_MONITOR.md](SKILL_QUALITY_MONITOR.md) - 质量监控系统
- [SKILL_GRAPH.md](SKILL_GRAPH.md) - 技能关系图
