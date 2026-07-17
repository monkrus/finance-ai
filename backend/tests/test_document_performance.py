import pytest
import time
from app.document_intelligence.chunker import FinancialChunker
from app.document_intelligence.models import Document, DocumentMetadata

def test_chunking_performance():
    chunker = FinancialChunker(max_chunk_size=1000)
    
    # Generate a large fake document with 10,000 paragraphs (approx 1M words)
    paragraphs = ["Item 1. Business"] + ["This is a test paragraph with several words. " * 20] * 5000
    paragraphs.append("Item 7. Management's Discussion and Analysis")
    paragraphs.extend(["More words for testing. " * 20] * 5000)
    
    raw_text = "\n\n".join(paragraphs)
    
    doc = Document(
        raw_text=raw_text,
        metadata=DocumentMetadata(source="perf", doc_type="10-K")
    )
    
    start_time = time.time()
    chunks = chunker.chunk_document(doc)
    duration = time.time() - start_time
    
    # Ensure chunking 1M words takes less than 2 seconds (usually takes < 0.1s in memory)
    assert duration < 2.0
    assert len(chunks) > 50 # Should have broken it down substantially
