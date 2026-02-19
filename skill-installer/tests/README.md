# Skill Installer Tests

本目录包含 skill-installer 的单元测试套件。

## 测试文件

### test_skill_catalog.py
测试 `skill_catalog.py` 模块的功能：
- `test_load_catalog()` - 测试加载有效的目录文件
- `test_load_invalid_catalog()` - 测试加载无效的目录文件
- `test_get_skill()` - 测试按名称获取技能
- `test_get_skill_with_category()` - 测试使用类别前缀获取技能
- `test_resolve_alias()` - 测试别名解析
- `test_list_categories()` - 测试列出类别
- `test_list_skills()` - 测试列出技能
- `test_search_skills()` - 测试搜索技能
- `test_search_skills_fuzzy()` - 测试模糊搜索

### test_install_skill.py
测试 `install_skill.py` 模块的功能：
- `test_parse_source_url()` - 测试解析完整 URL
- `test_parse_source_user_repo()` - 测试解析 user/repo 格式
- `test_parse_source_user_repo_subdir()` - 测试解析 user/repo/subdir 格式
- `test_resolve_source_name()` - 测试从目录解析技能名称
- `test_resolve_source_alias()` - 测试解析别名
- `test_parse_skill_dependencies()` - 测试从 SKILL.md 解析依赖
- `test_check_dependencies_installed()` - 测试检查已安装的依赖
- `test_resolve_install_order()` - 测试拓扑排序
- `test_detect_license()` - 测试许可证检测

### test_health_check.py
测试健康检查功能：
- `test_validate_skill_md_valid()` - 测试验证有效的 SKILL.md
- `test_validate_skill_md_missing()` - 测试缺失的 SKILL.md
- `test_validate_skill_md_invalid_yaml()` - 测试无效的 YAML
- `test_check_skill_dependencies()` - 测试依赖检查

## 运行测试

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行所有测试

```bash
# 从 tests 目录运行
cd tests
pytest

# 从 skill-installer 目录运行
cd .trae/skills/skill-installer
pytest tests/

# 使用详细输出
pytest -v

# 显示打印输出
pytest -s
```

### 运行特定测试文件

```bash
pytest test_skill_catalog.py
pytest test_install_skill.py
pytest test_health_check.py
```

### 运行特定测试

```bash
# 运行单个测试
pytest test_skill_catalog.py::test_load_catalog

# 运行匹配模式的测试
pytest -k "test_load"
```

### 测试覆盖率

```bash
# 生成覆盖率报告
pytest --cov=../scripts --cov-report=html

# 在终端显示覆盖率
pytest --cov=../scripts --cov-report=term

# 生成 XML 报告（用于 CI）
pytest --cov=../scripts --cov-report=xml
```

## 测试覆盖要求

- **最低覆盖率**: 80%
- **目标覆盖率**: 90%+

### 覆盖率目标

| 模块 | 目标覆盖率 |
|------|-----------|
| skill_catalog.py | 90%+ |
| install_skill.py | 85%+ |
| manage_skills.py | 80%+ |

## 测试结构

```
tests/
├── test_skill_catalog.py    # 目录管理测试
├── test_install_skill.py    # 安装功能测试
├── test_health_check.py      # 健康检查测试
├── requirements.txt          # 测试依赖
└── README.md                 # 本文件
```

## 测试最佳实践

1. **使用 fixtures**: 使用 pytest fixtures 创建可重用的测试数据
2. **隔离测试**: 每个测试应该独立运行，不依赖其他测试
3. **清理资源**: 使用 `tempfile.TemporaryDirectory()` 自动清理临时文件
4. **清晰的断言**: 使用有意义的断言消息
5. **测试边界情况**: 包含正常情况和异常情况的测试

## 添加新测试

1. 在相应的测试文件中添加新的测试函数
2. 使用 `@pytest.fixture` 创建必要的测试数据
3. 测试函数名称应以 `test_` 开头
4. 使用描述性的测试名称
5. 包含文档字符串说明测试目的

## CI/CD 集成

测试可以在 CI/CD 流程中自动运行：

```yaml
# 示例 GitHub Actions 配置
- name: Run tests
  run: |
    cd .trae/skills/skill-installer/tests
    pip install -r requirements.txt
    pytest --cov=../scripts --cov-report=xml
```

## 故障排除

### 导入错误

如果遇到导入错误，确保从正确的目录运行测试：

```bash
cd .trae/skills/skill-installer/tests
pytest
```

### 依赖问题

确保所有测试依赖已安装：

```bash
pip install -r requirements.txt
```

### 路径问题

测试使用相对路径导入脚本模块。如果遇到路径问题，检查 `sys.path.insert(0, ...)` 行。

## 贡献

在提交代码之前，请确保：

1. 所有测试通过
2. 代码覆盖率不低于 80%
3. 新功能包含相应的测试
4. 测试名称清晰描述测试内容
