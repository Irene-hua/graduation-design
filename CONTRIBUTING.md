# 贡献指南

感谢您对本项目的关注！我们欢迎各种形式的贡献。

## 如何贡献

### 报告问题 (Bug)

如果您发现了问题：

1. 在 Issues 中搜索是否已有相同问题
2. 如果没有，创建新 Issue
3. 提供以下信息：
   - 问题描述
   - 复现步骤
   - 期望行为
   - 实际行为
   - 系统环境（OS、Python 版本等）
   - 错误日志

### 建议新功能

如果您有新想法：

1. 创建 Feature Request Issue
2. 描述功能需求和使用场景
3. 说明为什么这个功能有价值

### 提交代码

#### 1. Fork 项目

```bash
# Fork 到您的账号
# 克隆到本地
git clone https://github.com/YOUR_USERNAME/graduation-design.git
cd graduation-design
```

#### 2. 创建分支

```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
```

#### 3. 开发

- 遵循代码规范
- 添加必要的测试
- 更新文档

#### 4. 测试

```bash
# 运行测试
pytest tests/ -v

# 检查代码风格
flake8 src/
```

#### 5. 提交

```bash
git add .
git commit -m "描述您的更改"
git push origin your-branch-name
```

#### 6. 创建 Pull Request

- 在 GitHub 上创建 PR
- 描述更改内容
- 关联相关 Issue

## 代码规范

### Python 代码风格

遵循 PEP 8：

```python
# 好的例子
def process_document(file_path: str) -> dict:
    """Process a document and return results.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Dictionary containing processed results
    """
    # 实现...
    pass
```

### 文档字符串

使用 Google 风格：

```python
def function_name(param1, param2):
    """简短描述。
    
    详细描述（可选）。
    
    Args:
        param1: 参数1的描述
        param2: 参数2的描述
        
    Returns:
        返回值的描述
        
    Raises:
        ExceptionType: 异常描述
    """
```

### 命名约定

- 类名：PascalCase（如 `RAGSystem`）
- 函数/方法：snake_case（如 `process_document`）
- 常量：UPPER_CASE（如 `MAX_SIZE`）
- 私有成员：_leading_underscore

## 测试

### 编写测试

```python
# tests/test_module.py
import pytest
from src.module import Function

def test_function_basic():
    """测试基本功能。"""
    result = Function().process("input")
    assert result == "expected"

def test_function_error():
    """测试错误处理。"""
    with pytest.raises(ValueError):
        Function().process(None)
```

### 运行测试

```bash
# 所有测试
pytest

# 特定文件
pytest tests/test_module.py

# 详细输出
pytest -v

# 覆盖率
pytest --cov=src tests/
```

## 文档

### 更新文档

如果您的更改影响文档：

- 更新 README.md
- 更新相关的 docs/ 文件
- 添加示例代码

### 文档格式

- 使用 Markdown
- 保持简洁清晰
- 提供代码示例
- 包含中英文说明

## 提交消息

使用清晰的提交消息：

```
类型(范围): 简短描述

详细描述（可选）

相关 Issue: #123
```

类型：
- feat: 新功能
- fix: 修复
- docs: 文档
- style: 格式
- refactor: 重构
- test: 测试
- chore: 构建/工具

示例：
```
feat(encryption): 添加 AES-256-GCM 加密支持

实现了基于 AES-256-GCM 的加密模块，支持文本和文件加密。

相关 Issue: #42
```

## Pull Request 检查清单

在提交 PR 前确认：

- [ ] 代码遵循项目规范
- [ ] 添加了必要的测试
- [ ] 所有测试通过
- [ ] 更新了文档
- [ ] 提交消息清晰
- [ ] PR 描述详细

## 代码审查

### 审查者

审查时关注：
- 代码质量
- 测试覆盖
- 文档完整性
- 性能影响
- 安全问题

### 被审查者

收到反馈后：
- 及时响应
- 解释设计决策
- 进行必要修改
- 保持礼貌专业

## 社区准则

### 行为规范

- 尊重他人
- 建设性讨论
- 欢迎新人
- 避免歧视

### 交流方式

- 在 Issue/PR 中讨论技术问题
- 保持专业和礼貌
- 使用清晰的语言

## 许可协议

提交代码即表示您同意在 MIT 许可下发布。

## 问题求助

如有疑问：
- 查看现有文档
- 搜索已有 Issue
- 创建新 Issue 提问

## 致谢

感谢所有贡献者！

您的贡献使这个项目变得更好！ 🎉

---

**期待您的参与！**
