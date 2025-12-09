# Installation Guide

## Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.8 or higher
- **RAM**: Minimum 4GB, Recommended 8GB
- **Storage**: At least 10GB free space
- **CPU**: 2+ cores recommended

### Required Software

1. Python 3.8+
2. pip package manager
3. Ollama (for LLM functionality)
4. Git (for cloning repository)

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Irene-hua/graduation-design.git
cd graduation-design
```

### 2. Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install all required packages including:
- sentence-transformers (embedding models)
- qdrant-client (vector database)
- cryptography (encryption)
- pypdf (PDF processing)
- ollama (LLM integration)
- and more...

### 4. Install Ollama

#### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### macOS
```bash
brew install ollama
```

#### Windows
Download the installer from [https://ollama.ai/download/windows](https://ollama.ai/download/windows)

### 5. Start Ollama Service

```bash
ollama serve
```

This starts the Ollama server on `localhost:11434`.

### 6. Download LLM Model

In a new terminal (keep Ollama server running):

```bash
# Download Llama 2 7B model (recommended)
ollama pull llama2:7b

# Or download other models
ollama pull mistral:7b
ollama pull codellama:7b
```

### 7. Verify Installation

Run the system check:

```bash
python main.py check
```

Expected output:
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

## Troubleshooting

### Ollama Connection Issues

**Problem**: "LLM Server: ✗ Not connected"

**Solution**:
1. Ensure Ollama is running: `ollama serve`
2. Check if port 11434 is available
3. Verify model is downloaded: `ollama list`

### Import Errors

**Problem**: ModuleNotFoundError for various packages

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

## Next Steps

After successful installation:

1. Read the [Usage Guide](USAGE.md)
2. Try ingesting your first document
3. Start querying!

## Getting Help

If you encounter issues:
1. Check this troubleshooting section
2. Open an issue on GitHub
3. Check Ollama documentation: https://ollama.ai/docs
