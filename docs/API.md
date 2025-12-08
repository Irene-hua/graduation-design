# API 文档

## Python API 使用指南

本文档介绍如何通过 Python API 使用本系统的各个模块。

## 1. 加密模块 (Encryption)

### AESEncryption

AES-256-GCM 加密器。

```python
from src.encryption import AESEncryption, generate_key, save_key, load_key

# 生成密钥
key = generate_key()

# 保存密钥
save_key(key, "encryption.key")

# 加载密钥
key = load_key("encryption.key")

# 创建加密器
encryptor = AESEncryption(key)

# 加密文本
plaintext = "敏感信息"
ciphertext = encryptor.encrypt(plaintext)
print(f"密文: {ciphertext[:50]}...")

# 解密
decrypted = encryptor.decrypt(ciphertext)
assert decrypted == plaintext
```

## 2. 文档处理模块 (Document Processor)

### DocumentParser

文档解析器，支持 PDF、TXT、DOCX。

```python
from src.document_processor import DocumentParser

# 创建解析器
parser = DocumentParser()

# 解析单个文档
text = parser.parse("document.pdf")
print(f"提取文本: {len(text)} 字符")

# 解析目录
documents = parser.parse_directory("documents/")
for filename, text in documents.items():
    print(f"{filename}: {len(text)} 字符")
```

### TextChunker

文本分块器。

```python
from src.document_processor import TextChunker

# 创建分块器
chunker = TextChunker(chunk_size=512, chunk_overlap=50)

# 分块文本
chunks = chunker.chunk_text(text, metadata={"source": "doc.pdf"})

for chunk in chunks:
    print(f"Chunk {chunk['chunk_id']}: {chunk['chunk_size']} 字符")
    print(f"内容: {chunk['text'][:100]}...")
```

## 3. 嵌入模块 (Embedding)

### EmbeddingModel

轻量级嵌入模型。

```python
from src.embedding import EmbeddingModel

# 创建模型
model = EmbeddingModel(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    device="cpu"
)

# 编码单个文本
text = "这是一个测试文本"
embedding = model.encode(text)
print(f"向量维度: {len(embedding[0])}")

# 编码多个文本
texts = ["文本1", "文本2", "文本3"]
embeddings = model.encode(texts)
print(f"生成 {len(embeddings)} 个向量")

# 计算相似度
similarity = model.similarity("文本A", "文本B")
print(f"相似度: {similarity:.4f}")
```

## 4. 向量数据库模块 (Vector DB)

### QdrantDB

Qdrant 向量数据库封装。

```python
from src.vector_db import QdrantDB
import numpy as np

# 创建数据库连接
db = QdrantDB(
    host="localhost",
    port=6333,
    collection_name="my_collection",
    dimension=384
)

# 插入向量
vectors = np.random.rand(10, 384)
encrypted_texts = ["密文1", "密文2", ...]
metadata = [{"source": "doc1.pdf"}, ...]

db.insert(vectors, encrypted_texts, metadata)

# 搜索
query_vector = np.random.rand(384)
results = db.search(query_vector, top_k=5)

for result in results:
    print(f"ID: {result['id']}, Score: {result['score']:.4f}")
    print(f"密文: {result['encrypted_text'][:50]}...")

# 获取统计
info = db.get_collection_info()
print(f"集合信息: {info}")
```

## 5. LLM 模块

### OllamaClient

Ollama 本地 LLM 客户端。

```python
from src.llm import OllamaClient

# 创建客户端
llm = OllamaClient(
    model_name="llama3.2:3b",
    temperature=0.7,
    max_tokens=512
)

# 生成文本
prompt = "请解释什么是 RAG 系统。"
response = llm.generate(prompt)
print(f"回答: {response}")

# 对话模式
messages = [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！有什么可以帮助你的？"},
    {"role": "user", "content": "介绍一下隐私保护技术"}
]
response = llm.chat(messages)
print(f"回答: {response}")

# 列出可用模型
models = llm.list_models()
print(f"可用模型: {models}")
```

## 6. 审计模块 (Audit)

### AuditLogger

审计日志记录器。

```python
from src.audit import AuditLogger

# 创建日志器
logger = AuditLogger(
    log_file="audit.log",
    enable=True,
    log_sensitive_data=False,
    integrity_check=True
)

# 记录查询事件
logger.log_query(
    query_hash="abc123",
    num_results=5,
    response_time=1.23
)

# 记录文档操作
logger.log_document_operation(
    operation="upload",
    document_id="doc123",
    success=True
)

# 记录检索
logger.log_retrieval(
    query_hash="abc123",
    num_chunks_retrieved=5,
    top_k=5
)

# 验证日志完整性
with open("audit.log", 'r') as f:
    for line in f:
        is_valid = logger.verify_log_integrity(line)
        print(f"日志完整性: {'✓' if is_valid else '✗'}")
```

## 7. RAG 系统 (RAG Pipeline)

### RAGSystem

完整的 RAG 系统。

```python
from src.rag_pipeline import RAGSystem
from src.encryption import generate_key

# 创建系统
key = generate_key()
rag = RAGSystem(
    encryption_key=key,
    embedding_model_name="sentence-transformers/all-MiniLM-L6-v2",
    llm_model_name="llama3.2:3b",
    enable_audit=True
)

# 导入文档
success = rag.ingest_document("document.pdf")
print(f"导入结果: {'成功' if success else '失败'}")

# 导入目录
results = rag.ingest_directory("documents/")
for filename, success in results.items():
    print(f"{filename}: {'✓' if success else '✗'}")

# 查询
result = rag.query(
    question="系统使用什么加密算法？",
    top_k=5,
    return_context=True
)

if result['success']:
    print(f"答案: {result['answer']}")
    print(f"响应时间: {result['response_time']:.2f}s")
    print(f"检索到 {result['num_chunks_retrieved']} 个片段")
    
    # 查看上下文
    if 'context' in result:
        for idx, chunk in enumerate(result['context'], 1):
            print(f"\n[{idx}] Score: {chunk['score']:.4f}")
            print(chunk['text'][:200])

# 获取统计
stats = rag.get_stats()
print(f"向量数量: {stats['vector_count']}")
print(f"嵌入维度: {stats['embedding_dimension']}")
```

## 8. 配置管理

### Config

配置管理器。

```python
from config import config

# 加载配置
cfg = config.load_config()

# 访问配置
embedding_cfg = config.embedding_config
print(f"嵌入模型: {embedding_cfg['model_name']}")

vector_db_cfg = config.vector_db_config
print(f"向量库: {vector_db_cfg['host']}:{vector_db_cfg['port']}")

llm_cfg = config.llm_config
print(f"LLM: {llm_cfg['model_name']}")
```

## 9. 完整示例

### 端到端 RAG 流程

```python
from pathlib import Path
from src.rag_pipeline import RAGSystem
from src.encryption import generate_key, save_key, load_key

def main():
    # 1. 设置加密密钥
    key_file = Path("encryption.key")
    if key_file.exists():
        key = load_key(key_file)
    else:
        key = generate_key()
        save_key(key, key_file)
    
    # 2. 初始化系统
    rag = RAGSystem(
        encryption_key=key,
        enable_audit=True
    )
    
    # 3. 导入文档
    print("导入文档...")
    rag.ingest_document("research.pdf")
    rag.ingest_document("notes.txt")
    
    # 4. 查询
    questions = [
        "研究的主要发现是什么？",
        "使用了哪些方法？",
        "实验结果如何？"
    ]
    
    for question in questions:
        print(f"\n问题: {question}")
        result = rag.query(question, top_k=3)
        
        if result['success']:
            print(f"答案: {result['answer']}")
            print(f"耗时: {result['response_time']:.2f}s")

if __name__ == "__main__":
    main()
```

## 10. 错误处理

```python
try:
    # 尝试操作
    rag.ingest_document("file.pdf")
except FileNotFoundError:
    print("文件未找到")
except ValueError as e:
    print(f"值错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

## 11. 性能优化技巧

### 批量处理

```python
# 批量编码
texts = ["文本1", "文本2", ...]
embeddings = model.encode(texts, batch_size=32)

# 批量插入
db.insert(vectors, encrypted_texts, metadata)
```

### 使用缓存

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_embed(text):
    return model.encode(text)
```

### 异步处理

```python
import asyncio

async def process_documents(files):
    tasks = [rag.ingest_document(f) for f in files]
    results = await asyncio.gather(*tasks)
    return results
```

## 12. 测试

```python
import pytest
from src.encryption import AESEncryption, generate_key

def test_encryption():
    key = generate_key()
    enc = AESEncryption(key)
    
    plaintext = "测试文本"
    ciphertext = enc.encrypt(plaintext)
    decrypted = enc.decrypt(ciphertext)
    
    assert decrypted == plaintext

# 运行测试
# pytest tests/
```

## 总结

本 API 文档涵盖了系统所有主要模块的使用方法。更多详细信息请参考源代码注释和 README 文档。
