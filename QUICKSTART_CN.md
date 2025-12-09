# 快速开始指南

## 一、环境准备

### 1.1 系统要求
- Python 3.8 或更高版本
- 4GB RAM（推荐8GB）
- 10GB 磁盘空间

### 1.2 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/Irene-hua/graduation-design.git
cd graduation-design

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. 安装Python依赖
pip install -r requirements.txt
```

### 1.3 安装Ollama

访问 https://ollama.ai 下载并安装Ollama

```bash
# 启动Ollama服务
ollama serve

# 在另一个终端下载模型
ollama pull llama2:7b
```

## 二、快速体验

### 2.1 检查系统状态

```bash
python main.py check
```

预期输出：
```
Checking system components...

1. LLM Server (Ollama):
   ✓ Connected
   Available models: llama2:7b

2. Vector Store:
   ✓ Collection 'private_documents' ready
   Documents: 0

3. Encryption:
   ✓ Encryption/decryption working

4. Embedding Model:
   ✓ Model loaded (dimension: 384)
```

### 2.2 导入示例文档

```bash
python main.py ingest --file data/documents/example.txt
```

输出示例：
```
Ingesting document: data/documents/example.txt
✓ Document ingested successfully!
  File: example.txt
  Chunks created: 15
  Document IDs: 15
```

### 2.3 查询系统

```bash
python main.py query --question "这个系统使用什么加密算法？"
```

### 2.4 交互式模式

```bash
python main.py interactive
```

然后可以连续提问：
```
🤔 Question: 系统有哪些主要功能？
⏳ Processing...
💡 Answer: [系统会根据文档内容生成答案]
```

## 三、导入自己的文档

### 3.1 支持的文档格式

- PDF文件 (.pdf)
- Word文档 (.docx)
- 文本文件 (.txt)
- Markdown (.md)
- HTML (.html)

### 3.2 导入文档

```bash
# 导入单个文档
python main.py ingest --file /path/to/your/document.pdf

# 批量导入（使用脚本）
for file in data/documents/*.pdf; do
    python main.py ingest --file "$file"
done
```

## 四、使用Python API

### 4.1 基本使用

```python
from src.rag_system import PrivacyEnhancedRAG

# 初始化系统
rag = PrivacyEnhancedRAG(config_path='config/config.yaml')

# 导入文档
result = rag.ingest_document('your_document.pdf')
print(f"已创建 {result['num_chunks']} 个文档块")

# 查询
response = rag.query("你的问题")
print(f"答案: {response['answer']}")
print(f"用时: {response['total_time']:.3f}秒")
```

### 4.2 批量导入

```python
from pathlib import Path
from src.rag_system import PrivacyEnhancedRAG

rag = PrivacyEnhancedRAG()

# 获取所有PDF文件
doc_dir = Path('data/documents')
pdf_files = list(doc_dir.glob('*.pdf'))

# 导入每个文档
for pdf_file in pdf_files:
    try:
        result = rag.ingest_document(str(pdf_file))
        print(f"✓ {pdf_file.name}: {result['num_chunks']} 块")
    except Exception as e:
        print(f"✗ {pdf_file.name}: {e}")
```

## 五、配置调整

### 5.1 主要配置项

编辑 `config/config.yaml`:

```yaml
# 调整检索数量
retrieval:
  top_k: 5  # 增加检索结果数量
  
# 调整分块大小
document_processing:
  chunk_size: 1000  # 更大的块
  chunk_overlap: 100

# 更换模型
llm:
  model_name: "mistral:7b"  # 使用不同的模型
```

### 5.2 使用GPU加速

```yaml
embedding:
  device: "cuda"  # 使用GPU
```

需要安装CUDA版本的PyTorch：
```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

## 六、常见问题

### Q1: 连接Ollama失败？

**问题**: 显示"LLM Server: ✗ Not connected"

**解决**:
1. 确保Ollama正在运行: `ollama serve`
2. 检查端口11434是否被占用
3. 验证模型已下载: `ollama list`

### Q2: 内存不足？

**解决**:
1. 使用更小的模型
2. 减少chunk_size
3. 关闭其他程序
4. 使用量化模型

### Q3: 查询结果不准确？

**解决**:
1. 增加top_k值获取更多上下文
2. 调整chunk_size和chunk_overlap
3. 使用更强大的LLM模型
4. 确保文档已正确导入

### Q4: 导入文档失败？

**解决**:
1. 检查文件格式是否支持
2. 确保文件路径正确
3. 查看错误日志了解详细信息

## 七、查看日志

系统会自动记录所有操作：

```bash
# 查看今天的日志
cat logs/audit_$(date +%Y%m%d).log

# 实时监控日志
tail -f logs/audit_$(date +%Y%m%d).log
```

## 八、运行示例

### 8.1 加密演示

```bash
python examples/encryption_demo.py
```

### 8.2 基本使用示例

```bash
python examples/basic_usage.py
```

## 九、性能优化建议

1. **首次运行较慢**: 第一次运行时需要下载模型，请耐心等待
2. **使用SSD**: 将向量数据库存储在SSD上可提升性能
3. **批量导入**: 一次导入多个文档比单独导入效率更高
4. **调整top_k**: 根据实际需求调整检索数量

## 十、下一步

- 阅读完整文档: [README_CN.md](README_CN.md)
- 查看API文档: [docs/](docs/)
- 尝试自己的文档
- 调整配置以优化性能

## 十一、获取帮助

如遇到问题：
1. 查看日志文件
2. 阅读文档
3. 在GitHub上提Issue

---

**祝您使用愉快！** 🎉
