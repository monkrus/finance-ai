import pytest
from app.document_intelligence.parser import DocumentParser

@pytest.mark.asyncio
async def test_document_parser_success():
    parser = DocumentParser()
    content = b"This is a test 10-K document."
    
    doc = await parser.parse(
        content=content,
        file_type="txt",
        source_name="test.txt",
        metadata={"doc_type": "10-K", "ticker": "AAPL", "fiscal_year": "2023"}
    )
    
    assert doc.raw_text == "This is a test 10-K document."
    assert doc.metadata.source == "test.txt"
    assert doc.metadata.doc_type == "10-K"
    assert doc.metadata.ticker == "AAPL"
    assert doc.metadata.fiscal_year == "2023"
    
@pytest.mark.asyncio
async def test_document_parser_custom_extraction():
    parser = DocumentParser()
    content = b"Apple Inc. generated 5M EUR. Table of Contents | Revenue | Cost |"
    
    doc = await parser.parse(
        content=content,
        file_type="txt",
        source_name="test.txt",
        metadata={"doc_type": "Annual Report"}
    )
    
    assert doc.metadata.ticker == "AAPL"
    assert doc.metadata.custom.get("currency") == "EUR"
    assert doc.metadata.custom.get("has_tables") is True

@pytest.mark.asyncio
async def test_document_parser_unicode_error():
    parser = DocumentParser()
    # Invalid utf-8 sequence to trigger UnicodeDecodeError
    content = b"\xff\xfe\xff" 
    
    doc = await parser.parse(
        content=content,
        file_type="pdf",
        source_name="bad.pdf",
        metadata=None
    )
    
    assert doc.raw_text == "[Simulated OCR Text Extracted from Binary]"
    assert doc.metadata.source == "bad.pdf"
    assert doc.metadata.doc_type == "Unknown"
    assert doc.metadata.ticker is None
