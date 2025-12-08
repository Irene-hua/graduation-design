# Usage Guide

## Quick Start

### 1. Check System Status

```bash
python main.py check
```

### 2. Ingest Documents

```bash
python main.py ingest --file path/to/document.pdf
```

Supported formats: PDF, TXT, DOCX, MD, HTML

### 3. Query the System

```bash
python main.py query --question "What is the main topic?"
```

### 4. Interactive Mode

```bash
python main.py interactive
```

## Command Reference

### `check` - System Check
```bash
python main.py check
```

### `ingest` - Document Ingestion
```bash
python main.py ingest --file FILEPATH
```

### `query` - Query System
```bash
python main.py query --question QUESTION [--top-k K]
```

### `interactive` - Interactive Mode
```bash
python main.py interactive
```

### `info` - Collection Information
```bash
python main.py info
```

## Python API

```python
from src.rag_system import PrivacyEnhancedRAG

# Initialize
rag = PrivacyEnhancedRAG()

# Ingest document
result = rag.ingest_document('document.pdf')

# Query
response = rag.query("What is this about?")
print(response['answer'])
```

## Best Practices

1. **Document Ingestion**: Use text-based formats when possible
2. **Querying**: Be specific and clear in your questions
3. **Security**: Keep encryption keys secure
4. **Performance**: Adjust `top_k` based on needs

## Examples

```bash
# Research papers
python main.py ingest --file paper.pdf
python main.py query --question "What are the main contributions?"

# Company docs
python main.py ingest --file handbook.pdf
python main.py interactive
```
