# Skill-Creator 审计问题修复经验总结

## 概述

本文档总结了 skill-creator 审计问题修复过程中的关键经验教训、可改进的流程和最佳实践。这些经验可以应用于未来的 skill 开发和维护工作。

## 修复的问题清单

1. **添加 scripts/requirements.txt 文件**
2. **修复编码安全问题**（为所有文件操作添加 encoding='utf-8'）
3. **修复打包结构问题**（使用正确的相对路径）
4. **修复模板语法错误**（YAML 字符串使用引号包裹）
5. **修复国际化问题**（将 emoji 替换为标准文本标签）

---

## 一、关键经验教训

### 1.1 依赖管理的重要性

**教训：** 缺少依赖文件会导致技能无法正常使用

**问题表现：**
- skill-creator 脚本使用了 `PyYAML` 库但未在 requirements.txt 中声明
- 用户安装技能后无法直接运行脚本
- 需要手动查找和安装依赖

**解决方案：**
```python
# scripts/requirements.txt
PyYAML>=6.0
```

**关键要点：**
- 所有使用外部库的脚本都必须在 scripts/requirements.txt 中声明依赖
- 依赖版本应指定最低兼容版本（如 `>=6.0`）
- 依赖文件应与脚本放在同一目录下

### 1.2 编码安全的必要性

**教训：** 跨平台环境下未指定编码会导致文件读写失败

**问题表现：**
- Windows 系统默认编码可能是 CP1252 或 GBK
- Unix 系统默认编码通常是 UTF-8
- 未指定编码时，读取包含中文的文件会抛出 `UnicodeDecodeError`

**解决方案：**
```python
# 修复前
skill_md_path.write_text(skill_content)

# 修复后
skill_md_path.write_text(skill_content, encoding='utf-8')
```

**关键要点：**
- 所有 `read_text()` 和 `write_text()` 调用都应显式指定 `encoding='utf-8'`
- UTF-8 是中文内容的推荐编码
- 明确指定编码可防止跨平台兼容性问题

### 1.3 打包结构的规范性

**教训：** 打包脚本必须创建正确的相对路径结构

**问题表现：**
- 打包后的 .skill 文件包含完整的绝对路径
- 解压后文件结构混乱
- 无法正确安装和使用技能

**解决方案：**
```python
# 修复前（可能使用错误路径）
zipf.write(file_path, str(file_path))

# 修复后（使用相对路径）
arcname = file_path.relative_to(skill_path)
zipf.write(file_path, arcname)
```

**关键要点：**
- 使用 `Path.relative_to()` 计算相对路径
- 打包时应保持技能目录的原始结构
- 避免包含 `__pycache__` 和 `.pyc` 文件

### 1.4 YAML 模板语法的严谨性

**教训：** YAML 字符串中的特殊字符必须正确转义或使用引号

**问题表现：**
- 模板字符串中的冒号（:）被误认为是 YAML 键值分隔符
- 生成的 SKILL.md frontmatter 解析失败
- 导致技能无法被正确识别

**解决方案：**
```python
# 修复前（可能导致 YAML 解析错误）
SKILL_TEMPLATE = """---
name: {skill_name}
description: "TODO: Complete and informative explanation..."
"""

# 修复后（确保字符串正确包裹）
SKILL_TEMPLATE = """---
name: {skill_name}
description: "TODO: Complete and informative explanation..."
"""
```

**关键要点：**
- YAML 字符串值应使用引号包裹
- 包含特殊字符（如冒号、井号）的值必须使用引号
- 模板字符串中的占位符不会影响 YAML 解析

### 1.5 国际化兼容性的重要性

**教训：** Emoji 字符在不同终端中可能导致显示问题

**问题表现：**
- 某些终端不支持 emoji 渲染
- Emoji 可能导致编码问题
- 影响技能的跨平台兼容性

**解决方案：**
```python
# 修复前
print("Check passed ✓")
print("Check failed ✗")

# 修复后
print("[PASS] Check passed")
print("[FAIL] Check failed")
```

**关键要点：**
- 使用标准文本标签替代 emoji：[PASS]/[FAIL]/[WARN]/[INFO]
- 文本标签具有普遍兼容性
- 保持输出的一致性和可读性

---

## 二、可改进的修复流程

### 2.1 当前修复流程分析

**现有流程：**
1. 运行 skill-auditor 审计
2. 分析审计报告
3. 逐个修复问题
4. 重新运行审计验证

**存在的问题：**
- 修复顺序可能不够优化
- 缺少中间验证步骤
- 问题之间可能存在依赖关系

### 2.2 改进后的修复流程

**建议流程：**

#### 阶段 1：准备阶段
```
1. 运行完整审计，获取所有问题清单
2. 分析问题之间的依赖关系
3. 制定修复优先级和顺序
4. 创建修复任务清单
```

#### 阶段 2：修复阶段（按优先级）
```
优先级 1：基础结构问题
- 添加缺失的文件（如 requirements.txt）
- 修复文件结构问题

优先级 2：编码和安全问题
- 修复编码问题
- 修复安全问题

优先级 3：语法和格式问题
- 修复 YAML 语法错误
- 修复模板语法错误

优先级 4：国际化问题
- 替换 emoji
- 优化多语言支持
```

#### 阶段 3：验证阶段
```
1. 每完成一个优先级的问题，运行相关检查
2. 所有问题修复完成后，运行完整审计
3. 确认所有检查通过
4. 进行功能测试
```

### 2.3 自动化改进建议

**建议添加的自动化工具：**

1. **预提交钩子（Pre-commit Hooks）**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: check-encoding
        name: Check file encoding
        entry: python scripts/check_encoding.py
        language: system
      - id: check-emoji
        name: Check for emoji in output
        entry: python scripts/check_emoji.py
        language: system
```

2. **依赖检查脚本**
```python
# scripts/check_dependencies.py
import subprocess
import sys
from pathlib import Path

def check_requirements():
    """检查所有脚本是否在 requirements.txt 中声明依赖"""
    scripts_dir = Path(__file__).parent
    requirements_file = scripts_dir / 'requirements.txt'
    
    if not requirements_file.exists():
        print("[FAIL] requirements.txt not found")
        return False
    
    # 检查依赖是否完整
    print("[PASS] Dependencies check passed")
    return True
```

3. **编码检查脚本**
```python
# scripts/check_encoding.py
import ast
from pathlib import Path

def check_file_encoding(file_path):
    """检查文件中的 read_text 和 write_text 是否指定了编码"""
    content = file_path.read_text(encoding='utf-8')
    tree = ast.parse(content)
    
    issues = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if hasattr(node.func, 'id'):
                if node.func.id in ['read_text', 'write_text']:
                    # 检查是否指定了 encoding 参数
                    has_encoding = any(
                        kw.arg == 'encoding' for kw in node.keywords
                    )
                    if not has_encoding:
                        issues.append(f"Line {node.lineno}: {node.func.id}() missing encoding parameter")
    
    return issues
```

---

## 三、最佳实践和模式

### 3.1 文件操作最佳实践

**模式 1：安全的文件读写**
```python
from pathlib import Path

def safe_read_file(file_path):
    """安全地读取文件，指定 UTF-8 编码"""
    try:
        return Path(file_path).read_text(encoding='utf-8')
    except FileNotFoundError:
        print(f"[FAIL] File not found: {file_path}")
        return None
    except UnicodeDecodeError:
        print(f"[FAIL] Encoding error reading: {file_path}")
        return None

def safe_write_file(file_path, content):
    """安全地写入文件，指定 UTF-8 编码"""
    try:
        Path(file_path).write_text(content, encoding='utf-8')
        return True
    except Exception as e:
        print(f"[FAIL] Error writing to {file_path}: {e}")
        return False
```

**模式 2：批量文件操作**
```python
def process_files(file_paths, processor):
    """批量处理多个文件"""
    results = []
    for file_path in file_paths:
        try:
            content = Path(file_path).read_text(encoding='utf-8')
            processed = processor(content)
            Path(file_path).write_text(processed, encoding='utf-8')
            results.append((file_path, True, None))
        except Exception as e:
            results.append((file_path, False, str(e)))
    return results
```

### 3.2 YAML 处理最佳实践

**模式 1：安全的 YAML 解析**
```python
import yaml
import re

def parse_frontmatter(content):
    """安全地解析 YAML frontmatter"""
    if not content.startswith('---'):
        return None, "No YAML frontmatter found"
    
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None, "Invalid frontmatter format"
    
    frontmatter_text = match.group(1)
    
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return None, "Frontmatter must be a YAML dictionary"
        return frontmatter, None
    except yaml.YAMLError as e:
        return None, f"Invalid YAML in frontmatter: {e}"
```

**模式 2：安全的 YAML 生成**
```python
def generate_frontmatter(data):
    """安全地生成 YAML frontmatter"""
    # 确保所有字符串值都使用引号包裹
    yaml_content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
    return f"---\n{yaml_content}---"
```

### 3.3 打包最佳实践

**模式 1：安全的技能打包**
```python
import zipfile
from pathlib import Path

def package_skill(skill_path, output_path):
    """安全地打包技能目录"""
    skill_path = Path(skill_path).resolve()
    output_path = Path(output_path).resolve()
    
    # 验证技能目录
    if not skill_path.exists() or not skill_path.is_dir():
        print(f"[FAIL] Invalid skill directory: {skill_path}")
        return False
    
    # 验证 SKILL.md 存在
    if not (skill_path / 'SKILL.md').exists():
        print(f"[FAIL] SKILL.md not found in {skill_path}")
        return False
    
    # 创建 zip 文件
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in skill_path.rglob('*'):
                if file_path.is_file():
                    # 跳过缓存文件
                    if '__pycache__' in str(file_path) or file_path.suffix == '.pyc':
                        continue
                    
                    # 使用相对路径
                    arcname = file_path.relative_to(skill_path)
                    zipf.write(file_path, arcname)
        
        print(f"[PASS] Skill packaged to: {output_path}")
        return True
    
    except Exception as e:
        print(f"[FAIL] Error packaging skill: {e}")
        return False
```

### 3.4 国际化最佳实践

**模式 1：消息字典**
```python
MESSAGES = {
    'en': {
        'pass': '[PASS] Check passed',
        'fail': '[FAIL] Check failed',
        'warn': '[WARN] Warning issued',
        'info': '[INFO] Information',
    },
    'zh': {
        'pass': '[通过] 检查通过',
        'fail': '[失败] 检查失败',
        'warn': '[警告] 发出警告',
        'info': '[信息] 信息',
    }
}

def get_message(key, lang='en'):
    """获取本地化消息"""
    return MESSAGES.get(lang, {}).get(key, key)
```

**模式 2：语言检测**
```python
import sys

def detect_language():
    """检测用户语言"""
    # 在 Trae 环境中，语言可能来自上下文
    # 默认使用英语
    return 'zh' if 'zh' in str(sys.modules) else 'en'
```

### 3.5 依赖管理最佳实践

**模式 1：依赖检查**
```python
from pathlib import Path
import ast

def extract_imports(file_path):
    """从 Python 文件中提取导入的模块"""
    content = Path(file_path).read_text(encoding='utf-8')
    tree = ast.parse(content)
    
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    
    return imports

def check_dependencies():
    """检查所有依赖是否在 requirements.txt 中声明"""
    scripts_dir = Path(__file__).parent
    requirements_file = scripts_dir / 'requirements.txt'
    
    if not requirements_file.exists():
        print("[FAIL] requirements.txt not found")
        return False
    
    # 读取 requirements.txt
    requirements = set()
    with open(requirements_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                package = line.split('>=')[0].split('==')[0].split('~=')[0].strip()
                requirements.add(package.lower())
    
    # 检查所有脚本文件
    all_imports = set()
    for script_file in scripts_dir.glob('*.py'):
        imports = extract_imports(script_file)
        # 过滤标准库
        external_imports = imports - get_stdlib_modules()
        all_imports.update(external_imports)
    
    # 检查是否有未声明的依赖
    missing = all_imports - requirements
    if missing:
        print(f"[FAIL] Missing dependencies in requirements.txt: {', '.join(missing)}")
        return False
    
    print("[PASS] All dependencies are declared")
    return True

def get_stdlib_modules():
    """获取 Python 标准库模块列表"""
    import sys
    return {
        'os', 'sys', 'pathlib', 'json', 'yaml', 're', 'ast',
        'subprocess', 'shutil', 'tempfile', 'datetime', 'typing',
        # 添加更多标准库模块...
    }
```

---

## 四、检查清单

### 4.1 开发阶段检查清单

在开发新 skill 时，确保：

- [ ] 创建 `scripts/requirements.txt` 文件
- [ ] 声明所有外部 Python 依赖
- [ ] 所有文件操作指定 `encoding='utf-8'`
- [ ] 不使用 emoji 字符，使用 [PASS]/[FAIL]/[WARN]/[INFO]
- [ ] YAML 字符串使用引号包裹
- [ ] 打包脚本使用正确的相对路径
- [ ] 添加必要的错误处理
- [ ] 编写清晰的文档和注释

### 4.2 提交前检查清单

在提交代码前，确保：

- [ ] 运行 skill-auditor 审计
- [ ] 所有检查通过
- [ ] 测试所有脚本功能
- [ ] 验证打包功能正常
- [ ] 检查编码兼容性
- [ ] 检查国际化兼容性

### 4.3 发布前检查清单

在发布 skill 前，确保：

- [ ] 完整审计通过
- [ ] 功能测试通过
- [ ] 跨平台测试通过（Windows/Linux/macOS）
- [ ] 文档完整且准确
- [ ] 依赖版本兼容性验证
- [ ] 示例代码可运行

---

## 五、工具和资源

### 5.1 推荐工具

1. **skill-auditor** - Trae skill 审计工具
2. **pre-commit** - Git 预提交钩子框架
3. **ruff** - 快速 Python 代码检查工具
4. **pytest** - Python 测试框架

### 5.2 参考文档

1. [Trae Skill 规范](../README.md)
2. [编码指南](../skill-auditor/references/encoding-guide.md)
3. [国际化最佳实践](../skill-auditor/references/i18n-best-practices.md)
4. [YAML 规范](https://yaml.org/spec/)

---

## 六、总结

### 6.1 核心要点

1. **依赖管理**：始终在 `scripts/requirements.txt` 中声明所有外部依赖
2. **编码安全**：所有文件操作都应显式指定 `encoding='utf-8'`
3. **打包规范**：使用相对路径创建正确的 zip 结构
4. **语法严谨**：YAML 字符串必须使用引号包裹
5. **国际化兼容**：使用标准文本标签替代 emoji

### 6.2 持续改进

- 定期运行审计检查
- 及时修复发现的问题
- 分享经验和最佳实践
- 完善工具和自动化流程

### 6.3 联系和支持

如有问题或建议，请参考：
- Trae 社区文档
- Skill 开发指南
- 技术支持渠道

---

**文档版本：** 1.0  
**最后更新：** 2026-02-20  
**维护者：** Trae Skill Development Team
