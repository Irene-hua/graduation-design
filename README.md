# Privacy-Enhanced Lightweight RAG System
# 面向隐私保护的轻量级RAG系统

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Academic-green)](LICENSE)

## Overview

A Privacy-Enhanced Lightweight Retrieval-Augmented Generation (RAG) system designed for local deployment and privacy-sensitive scenarios. The system integrates end-to-end data encryption mechanisms to protect private knowledge bases while optimizing inference latency and resource consumption through lightweight deep learning models.

[中文文档](README_CN.md) | [English Documentation](README.md)

## Key Features

🔐 **Privacy Protection**
- AES-256-GCM encryption for all document content
- Encrypted storage in vector database
- Local deployment with no data leakage

⚡ **Lightweight Design**
- Compact embedding model (all-MiniLM-L6-v2, 22MB)
- Optimized for CPU execution
- Support for model quantization

🔍 **Complete RAG Pipeline**
- Multi-format document support (PDF, DOCX, TXT, MD, HTML)
- Intelligent chunking and retrieval
- Context-aware answer generation

📊 **Audit & Logging**
- Comprehensive operation logging
- Privacy-preserving audit trails
- Log integrity verification

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/Irene-hua/graduation-design.git
cd graduation-design

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install Ollama
# Visit https://ollama.ai and follow instructions
ollama serve
ollama pull llama2:7b
```

### Usage

```bash
# Check system status
python main.py check

# Ingest a document
python main.py ingest --file path/to/document.pdf

# Query the system
python main.py query --question "What is the main topic?"

# Interactive mode
python main.py interactive

# Get collection info
python main.py info
```

## Architecture

The system consists of six core modules:

1. **Encryption Module**: AES-GCM encryption for document protection
2. **Document Processor**: Multi-format parsing and intelligent chunking
3. **Retrieval Module**: Lightweight embedding model and vector search
4. **Generation Module**: LLM integration via Ollama
5. **Audit Module**: Privacy-preserving operation logging
6. **RAG System**: Integration of all components

## Documentation

- [中文使用指南](README_CN.md) - Comprehensive Chinese documentation
- [API Reference](docs/API.md) - API documentation (to be added)
- [Deployment Guide](docs/DEPLOYMENT.md) - Deployment instructions (to be added)

## Performance

- **Model Size**: Embedding model ~22MB, LLM depends on selection
- **Inference Speed**: <100ms retrieval, 1-5s generation
- **Resource Usage**: 2-4GB RAM, CPU-friendly

## Security

- ✅ AES-256-GCM encryption
- ✅ Local-only data storage and processing
- ✅ Privacy-preserving audit logs
- ✅ Secure key management
- ✅ No external API calls

## Project Structure

```
graduation-design/
├── config/              # Configuration files
├── data/               # Data directory
│   ├── documents/      # Raw documents
│   └── vector_db/      # Vector database storage
├── logs/               # Log files
├── src/                # Source code
│   ├── encryption/     # Encryption module
│   ├── retrieval/      # Retrieval module
│   ├── generation/     # Generation module
│   ├── audit/          # Audit module
│   ├── utils/          # Utilities
│   └── rag_system.py   # Main RAG system
├── tests/              # Test files
├── main.py             # Entry point
└── requirements.txt    # Dependencies
```

## Contributing

This project is part of an undergraduate thesis. Contributions are welcome through GitHub Issues and Pull Requests.

## License

This project is for academic research and educational purposes.

## Acknowledgments

Built with:
- Sentence Transformers
- Qdrant Vector Database
- Ollama
- Cryptography Library
- And other open-source projects

## Contact

For questions and issues, please use GitHub Issues.

---

**Undergraduate Graduation Design Project**  
**Topic**: Privacy-Enhanced Lightweight RAG System Design and Development
