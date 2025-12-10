from src.utils.document_processor import DocumentProcessor
from pathlib import Path

p = Path('data/documents/example.txt')
print('exists', p.exists())
print('path', p)

proc = DocumentProcessor(chunk_size=500, chunk_overlap=50)
text = proc.load_document(str(p))
print('text length', len(text))
print('first 200 chars:\n', text[:200])
chunks = proc.process_document(str(p))
print('num chunks', len(chunks))
for i, c in enumerate(chunks[:5]):
    print('chunk', i, 'len', c['length'])
    print(c['text'][:200])

