# Skills Quality Monitoring

## 质量指标

### Skill Success Rate（技能成功率）

跟踪每个技能成功完成任务的频率：

| 技能名称 | 目标成功率 | 当前成功率 | 状态 |
|---------|-----------|-----------|------|
| brainstorming | > 95% | - | 待跟踪 |
| writing-plans | > 90% | - | 待跟踪 |
| executing-plans | > 85% | - | 待跟踪 |
| systematic-debugging | > 80% | - | 待跟踪 |
| test-driven-development | > 85% | - | 待跟踪 |
| verification-before-completion | > 90% | - | 待跟踪 |
| requesting-code-review | > 85% | - | 待跟踪 |
| finishing-a-development-branch | > 85% | - | 待跟踪 |
| using-git-worktrees | > 80% | - | 待跟踪 |
| subagent-driven-development | > 80% | - | 待跟踪 |
| skill-creator | > 85% | - | 待跟踪 |
| skill-installer | > 90% | - | 待跟踪 |
| skill-auditor | > 90% | - | 待跟踪 |
| find-skills | > 90% | - | 待跟踪 |
| image-generation | > 85% | - | 待跟踪 |
| pdf-generation | > 85% | - | 待跟踪 |
| behavioral-product-design | > 85% | - | 待跟踪 |
| ui-ux-pro-max-skill | > 85% | - | 待跟踪 |
| claude-skills | > 85% | - | 待跟踪 |
| evaluation | > 85% | - | 待跟踪 |

### Skill Usage Frequency（技能使用频率）

跟踪每个技能被调用的频率：

| 频率级别 | 阈值 | 技能列表 |
|---------|------|---------|
| 高频率 | > 10/天 | brainstorming, verification-before-completion |
| 中频率 | 5-10/天 | writing-plans, executing-plans, test-driven-development |
| 低频率 | < 5/天 | skill-creator, skill-auditor, skill-installer, find-skills, image-generation, pdf-generation |

### Skill Error Patterns（技能错误模式）

跟踪常见错误并添加到 AGENTS.md：

#### brainstorming
- **错误**: 跳过"简单"任务的头脑风暴
- **修复**: 添加到 AGENTS.md: "NEVER skip brainstorming, even for simple tasks"
- **发生频率**: 中
- **影响范围**: 高

#### test-driven-development
- **错误**: 在测试之前编写实现代码
- **修复**: 添加到 AGENTS.md: "ALWAYS write tests first, even if they fail"
- **发生频率**: 中
- **影响范围**: 高

#### writing-plans
- **错误**: 为小任务编写过于详细的计划
- **修复**: 添加到 AGENTS.md: "Adjust plan detail based on task complexity"
- **发生频率**: 低
- **影响范围**: 中

#### systematic-debugging
- **错误**: 在没有充分调查的情况下假设根本原因
- **修复**: 添加到 AGENTS.md: "NEVER assume root cause without investigation"
- **发生频率**: 中
- **影响范围**: 高

## 持续改进

### Weekly Review（每周审查）

**审查内容**:
1. 审查技能使用统计
2. 识别表现不佳的技能
3. 更新技能描述和关键词
4. 将新的错误模式添加到 AGENTS.md
5. 审查技能路由准确性
6. 检查技能依赖关系

**审查步骤**:
1. 运行 `quality_check.py` 脚本生成质量报告
2. 分析技能成功率和使用频率
3. 识别成功率低于目标的技能
4. 更新 `skill_map.json` 中的关键词和描述
5. 将新发现的错误模式添加到相应的 AGENTS.md
6. 更新此文档中的错误模式部分

**审查时间**: 每周一上午

**审查负责人**: Skills Team

### Monthly Review（每月审查）

**审查内容**:
1. 使用 skill-auditor 审计所有技能
2. 更新 skills.json 中的最新版本
3. 审查和优化技能路由
4. 归档未使用的技能
5. 更新质量目标
6. 审查技能生态系统健康度

**审查步骤**:
1. 对所有技能运行 skill-auditor
2. 检查 skills.json 中的版本信息
3. 分析技能路由表 (SKILL_ROUTING.md)
4. 识别低使用率技能（< 1次/月）
5. 评估是否需要归档或更新
6. 根据实际表现调整质量目标
7. 生成月度质量报告

**审查时间**: 每月第一个工作日

**审查负责人**: Skills Team Lead

### Error Pattern Tracking（错误模式跟踪）

**跟踪流程**:
1. **识别错误**: 在技能执行过程中记录错误
2. **分类错误**: 按技能类型和错误严重程度分类
3. **分析原因**: 确定错误的根本原因
4. **制定修复方案**: 开发修复方案
5. **实施修复**: 更新相关文档和代码
6. **预防措施**: 添加预防措施到 AGENTS.md
7. **验证修复**: 确保修复有效

**跟踪工具**:
- 错误日志: `.trae/skills/error_log.json`
- 错误模式数据库: `.trae/skills/error_patterns.json`
- 质量报告: `.trae/skills/quality_report.json`

## 质量目标

### Workflow Skills（工作流技能）

| 技能名称 | 目标成功率 | 目标使用频率 | 优先级 |
|---------|-----------|-------------|--------|
| brainstorming | > 95% | 高 | 高 |
| writing-plans | > 90% | 中 | 高 |
| executing-plans | > 85% | 中 | 高 |
| systematic-debugging | > 80% | 低 | 高 |
| test-driven-development | > 85% | 中 | 高 |
| verification-before-completion | > 90% | 高 | 高 |
| subagent-driven-development | > 80% | 低 | 中 |

### Management Skills（管理技能）

| 技能名称 | 目标成功率 | 目标使用频率 | 优先级 |
|---------|-----------|-------------|--------|
| skill-creator | > 85% | 低 | 中 |
| skill-installer | > 90% | 低 | 高 |
| skill-auditor | > 90% | 低 | 高 |
| find-skills | > 90% | 低 | 中 |

### Development Process Skills（开发流程技能）

| 技能名称 | 目标成功率 | 目标使用频率 | 优先级 |
|---------|-----------|-------------|--------|
| requesting-code-review | > 85% | 低 | 中 |
| verification-before-completion | > 90% | 高 | 高 |
| finishing-a-development-branch | > 85% | 低 | 中 |
| using-git-worktrees | > 80% | 低 | 低 |

### Generation Skills（生成技能）

| 技能名称 | 目标成功率 | 目标使用频率 | 优先级 |
|---------|-----------|-------------|--------|
| image-generation | > 85% | 低 | 低 |
| pdf-generation | > 85% | 低 | 低 |

### Domain Skills（专业领域技能）

| 技能名称 | 目标成功率 | 目标使用频率 | 优先级 |
|---------|-----------|-------------|--------|
| behavioral-product-design | > 85% | 低 | 中 |
| ui-ux-pro-max-skill | > 85% | 低 | 中 |
| claude-skills | > 85% | 低 | 中 |
| evaluation | > 85% | 低 | 中 |

## 错误模式模板

### 错误模式跟踪表

| 错误ID | 技能名称 | 错误描述 | 发生频率 | 影响范围 | 修复方案 | 预防措施 | 状态 |
|--------|---------|---------|---------|---------|---------|---------|------|
| ERR-001 | brainstorming | 跳过"简单"任务的头脑风暴 | 中 | 高 | 添加到 AGENTS.md: "NEVER skip brainstorming, even for simple tasks" | 在技能调用前检查任务复杂度 | 已修复 |
| ERR-002 | test-driven-development | 在测试之前编写实现代码 | 中 | 高 | 添加到 AGENTS.md: "ALWAYS write tests first, even if they fail" | 强制执行测试优先原则 | 已修复 |
| ERR-003 | writing-plans | 为小任务编写过于详细的计划 | 低 | 中 | 添加到 AGENTS.md: "Adjust plan detail based on task complexity" | 根据任务复杂度调整计划粒度 | 已修复 |
| ERR-004 | systematic-debugging | 在没有充分调查的情况下假设根本原因 | 中 | 高 | 添加到 AGENTS.md: "NEVER assume root cause without investigation" | 强制执行系统化调试流程 | 已修复 |

### 错误模式详情模板

```markdown
## 错误模式: ERR-XXX

### 基本信息
- **错误ID**: ERR-XXX
- **技能名称**: [skill-name]
- **发现日期**: YYYY-MM-DD
- **发现人**: [name]

### 错误描述
[详细描述错误现象和表现]

### 发生频率
- **频率级别**: 高/中/低
- **发生次数**: [number]
- **发生场景**: [description]

### 影响范围
- **影响技能**: [list of affected skills]
- **影响用户**: [description]
- **影响程度**: 高/中/低

### 根本原因分析
[分析错误的根本原因]

### 修复方案
- **短期修复**: [description]
- **长期修复**: [description]
- **实施日期**: YYYY-MM-DD

### 预防措施
- **文档更新**: [description]
- **代码更新**: [description]
- **流程改进**: [description]

### 验证结果
- **验证日期**: YYYY-MM-DD
- **验证方法**: [description]
- **验证结果**: 通过/失败

### 状态
- [ ] 待修复
- [ ] 修复中
- [ ] 已修复
- [ ] 已验证
- [ ] 已关闭
```

## 质量报告

### 报告生成

运行以下命令生成质量报告：

```bash
python .trae/skills/scripts/quality_check.py
```

### 报告内容

质量报告包含以下信息：

```json
{
  "timestamp": "2026-02-15T00:00:00",
  "summary": {
    "total_skills": 20,
    "skills_below_target": 3,
    "high_frequency_skills": 2,
    "medium_frequency_skills": 3,
    "low_frequency_skills": 15
  },
  "skill_performance": [
    {
      "skill_name": "brainstorming",
      "success_rate": 96.5,
      "usage_count": 15,
      "error_count": 1,
      "status": "above_target"
    }
  ],
  "error_patterns": [
    {
      "error_id": "ERR-001",
      "skill_name": "brainstorming",
      "frequency": "medium",
      "impact": "high",
      "status": "resolved"
    }
  ],
  "recommendations": [
    "Update skill_map.json keywords for better detection",
    "Add new error patterns to AGENTS.md",
    "Consider archiving unused skills"
  ]
}
```

## 质量改进行动项

### 短期行动项（1-2周）

- [ ] 实现技能使用统计跟踪
- [ ] 创建错误模式数据库
- [ ] 更新所有 AGENTS.md 文件
- [ ] 实施每周审查流程

### 中期行动项（1-2个月）

- [ ] 实现自动化质量检查
- [ ] 优化技能路由算法
- [ ] 建立技能性能基准
- [ ] 创建技能使用示例库

### 长期行动项（3-6个月）

- [ ] 实现技能生态系统可视化
- [ ] 建立技能社区反馈机制
- [ ] 开发技能推荐系统
- [ ] 实现技能自动更新机制

## 质量指标监控仪表板

### 关键指标

| 指标 | 当前值 | 目标值 | 状态 |
|-----|-------|-------|------|
| 整体技能成功率 | - | > 85% | 待跟踪 |
| 技能自动检测准确率 | - | > 85% | 待跟踪 |
| 技能使用错误率 | - | < 10% | 待跟踪 |
| 技能文档覆盖率 | 100% | 100% | ✅ |
| 技能质量监控覆盖率 | - | 100% | 待跟踪 |

### 趋势分析

| 月份 | 技能成功率 | 使用频率 | 错误率 |
|-----|-----------|---------|--------|
| 2026-01 | - | - | - |
| 2026-02 | - | - | - |
| 2026-03 | - | - | - |

## 附录

### A. 技能性能基准测试

基准测试用于评估技能性能：

```python
# 基准测试脚本示例
def run_skill_benchmark(skill_name, test_cases):
    """
    运行技能基准测试
    
    Args:
        skill_name: 技能名称
        test_cases: 测试用例列表
    
    Returns:
        dict: 包含成功率、平均执行时间等指标
    """
    results = {
        'skill_name': skill_name,
        'total_tests': len(test_cases),
        'passed_tests': 0,
        'failed_tests': 0,
        'average_time': 0,
        'success_rate': 0
    }
    
    for test_case in test_cases:
        start_time = time.time()
        result = invoke_skill(skill_name, test_case)
        end_time = time.time()
        
        if result['success']:
            results['passed_tests'] += 1
        else:
            results['failed_tests'] += 1
    
    results['success_rate'] = (results['passed_tests'] / results['total_tests']) * 100
    
    return results
```

### B. 技能健康度评分

技能健康度评分计算公式：

```
健康度评分 = (成功率权重 × 成功率) + 
             (使用频率权重 × 使用频率分数) + 
             (错误率权重 × (1 - 错误率)) + 
             (文档完整性权重 × 文档完整性分数)
```

其中：
- 成功率权重: 0.4
- 使用频率权重: 0.2
- 错误率权重: 0.3
- 文档完整性权重: 0.1

### C. 技能优化建议

根据质量监控结果，提供技能优化建议：

1. **成功率低于目标的技能**:
   - 审查技能实现逻辑
   - 更新技能文档和示例
   - 增加错误处理机制

2. **使用频率过低的技能**:
   - 评估技能必要性
   - 更新技能描述和关键词
   - 考虑归档或合并

3. **错误率过高的技能**:
   - 分析错误模式
   - 修复根本原因
   - 更新 AGENTS.md 预防措施

4. **文档不完整的技能**:
   - 补充 SKILL.md 文档
   - 添加使用示例
   - 创建参考文档

---

**文档版本**: 1.0.0
**最后更新**: 2026-02-15
**维护者**: Skills Team
**下次审查**: 2026-02-22
