import pytest
from app.document_intelligence.chunker import FinancialChunker
from app.document_intelligence.models import Document, DocumentMetadata

def test_financial_chunker():
    chunker = FinancialChunker(max_chunk_size=10) # Small chunk size for sub-chunk testing
    
    raw_text = """
Item 1. Business

We sell apples. Lots of apples. More apples.

Item 1A. Risk Factors

Apples might rot. 

Item 7. Management's Discussion and Analysis of Financial Condition and Results of Operations

We made a lot of money. We spent a lot of money. The net income is 5M. This is a very long section that should trigger sub chunking because it has more than ten words easily in this sentence alone right now.

Segment Information

We have 3 segments. Products, Services, and Other.
"""
    
    doc = Document(
        raw_text=raw_text,
        metadata=DocumentMetadata(source="test", doc_type="10-K", ticker="AAPL")
    )
    
    chunks = chunker.chunk_document(doc)
    
    # Check that sections were identified
    section_names = [c.section_name for c in chunks]
    assert "Business Overview" in section_names
    assert "Risk Factors" in section_names
    assert "MD&A" in section_names
    
    # Ensure MD&A was sub-chunked due to length
    mda_chunks = [c for c in chunks if c.section_name == "MD&A"]
    assert len(mda_chunks) > 1
    
    # Check text content
    risk_chunks = [c for c in chunks if c.section_name == "Risk Factors"]
    assert "Apples might rot." in risk_chunks[0].text
    
    # Check new segment detection
    assert "Segment Information" in section_names
    
    # Verify page numbers exist
    assert all(c.page_number == 1 for c in chunks)
