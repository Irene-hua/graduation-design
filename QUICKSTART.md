# 快速开始指南

## 5分钟快速体验

### 前置要求

确保已安装：
- Python 3.8+
- Docker
- Ollama

### 步骤 1: 自动安装

```bash
git clone https://github.com/Irene-hua/graduation-design.git
cd graduation-design
chmod +x setup.sh
./setup.sh
```

自动安装脚本会：
- 创建 Python 虚拟环境
- 安装所有依赖
- 启动 Qdrant 向量数据库
- 拉取 Ollama 模型
- 生成加密密钥

### 步骤 2: 启动系统

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动 Web 界面
streamlit run src/web/app.py
```

访问 http://localhost:8501

### 步骤 3: 上传文档

1. 在 Web 界面中点击 "Document Management" 标签
2. 点击 "Browse files" 选择文档（支持 PDF、TXT、DOCX）
3. 点击 "Upload & Process"

### 步骤 4: 提问

1. 切换到 "Query" 标签
2. 在文本框中输入问题
3. 点击 "Search"
4. 查看生成的答案

## 命令行使用

### 生成密钥

```bash
python cli.py setup-key
```

### 导入文档

```bash
# 单个文档
python cli.py ingest document.pdf

# 整个目录
python cli.py ingest data/documents/
```

### 查询

```bash
# 单次查询
python cli.py query -q "你的问题"

# 交互模式
python cli.py query
```

### 查看统计

```bash
python cli.py stats
```

## Python API

```python
from src.rag_pipeline import RAGSystem
from src.encryption import load_key

# 加载密钥
key = load_key("config/encryption.key")

# 初始化系统
rag = RAGSystem(encryption_key=key)

# 导入文档
rag.ingest_document("document.pdf")

# 查询
result = rag.query("你的问题")
print(result['answer'])
```

## 运行示例

```bash
python examples/basic_usage.py
```

## 运行测试

```bash
# 单元测试
pytest tests/ -v

# 性能测试
python tests/benchmark.py
```

## 常见问题

### 1. Qdrant 连接失败

```bash
docker-compose up -d
```

### 2. Ollama 模型未找到

```bash
ollama pull llama3.2:3b
```

### 3. 内存不足

使用更小的模型或启用量化。

## 下一步

- 📖 阅读 [完整文档](README.md)
- 🏗️ 了解 [系统架构](docs/ARCHITECTURE.md)
- 🔒 查看 [隐私分析](docs/PRIVACY_ANALYSIS.md)
- 🚀 参考 [部署指南](docs/DEPLOYMENT.md)
- 📚 浏览 [API 文档](docs/API.md)

## 帮助

如有问题，请提交 Issue 或查看文档。

---

**开始探索隐私保护的 RAG 系统吧！** 🚀
