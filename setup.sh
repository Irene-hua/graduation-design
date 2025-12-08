#!/bin/bash

# Setup script for Privacy-Preserving RAG System

set -e

echo "=========================================="
echo "Privacy-Preserving RAG System Setup"
echo "=========================================="

# Check Python version
echo ""
echo "[1] Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "    Found Python $python_version"

# Create virtual environment
echo ""
echo "[2] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "    ✓ Virtual environment created"
else
    echo "    ✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "[3] Activating virtual environment..."
source venv/bin/activate
echo "    ✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "[4] Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo ""
echo "[5] Installing Python dependencies..."
pip install -r requirements.txt
echo "    ✓ Dependencies installed"

# Check Docker
echo ""
echo "[6] Checking Docker..."
if command -v docker &> /dev/null; then
    echo "    ✓ Docker is installed"
    
    # Start Qdrant
    echo ""
    echo "[7] Starting Qdrant vector database..."
    docker-compose up -d
    echo "    ✓ Qdrant started"
    
    # Wait for Qdrant to be ready
    echo "    Waiting for Qdrant to be ready..."
    sleep 5
    
    # Check Qdrant status
    if curl -s http://localhost:6333/health > /dev/null 2>&1; then
        echo "    ✓ Qdrant is ready"
    else
        echo "    ⚠ Qdrant may not be ready yet. Please check manually."
    fi
else
    echo "    ⚠ Docker not found. Please install Docker and run:"
    echo "      docker-compose up -d"
fi

# Check Ollama
echo ""
echo "[8] Checking Ollama..."
if command -v ollama &> /dev/null; then
    echo "    ✓ Ollama is installed"
    
    # Check if llama3.2:3b is available
    if ollama list | grep -q "llama3.2:3b"; then
        echo "    ✓ llama3.2:3b model is available"
    else
        echo "    ⚠ llama3.2:3b model not found"
        echo "    Pulling model (this may take a while)..."
        ollama pull llama3.2:3b
        echo "    ✓ Model downloaded"
    fi
else
    echo "    ⚠ Ollama not found. Please install from https://ollama.ai"
    echo "      Then run: ollama pull llama3.2:3b"
fi

# Create directories
echo ""
echo "[9] Creating data directories..."
mkdir -p data/documents data/encrypted data/vectors logs
echo "    ✓ Directories created"

# Generate encryption key
echo ""
echo "[10] Setting up encryption key..."
if [ ! -f "config/encryption.key" ]; then
    python3 << EOF
from src.encryption import generate_key, save_key
key = generate_key()
save_key(key, "config/encryption.key")
print("    ✓ Encryption key generated")
EOF
else
    echo "    ✓ Encryption key already exists"
fi

echo ""
echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Start the web interface: streamlit run src/web/app.py"
echo "3. Or run the example: python examples/basic_usage.py"
echo ""
echo "Documentation:"
echo "- README.md - Project overview and usage"
echo "- docs/ARCHITECTURE.md - System architecture"
echo ""
echo "=========================================="
