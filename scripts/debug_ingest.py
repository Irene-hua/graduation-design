import os
import traceback
from src.rag_system import PrivacyEnhancedRAG

# Force offline HF envs
os.environ.setdefault('TRANSFORMERS_OFFLINE', '1')
os.environ.setdefault('HF_DATASETS_OFFLINE', '1')
os.environ.setdefault('HUGGINGFACE_HUB_OFFLINE', '1')

rag = PrivacyEnhancedRAG(config_path='config/config.yaml')

try:
    res = rag.ingest_document('data/documents/example.txt')
    print('INGEST OK:', res)
except Exception as e:
    print('INGEST FAILED:')
    traceback.print_exc()
    raise

