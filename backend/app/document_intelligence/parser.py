import logging
from typing import Dict, Any, Optional
from app.document_intelligence.models import Document, DocumentMetadata

logger = logging.getLogger(__name__)

class DocumentParser:
    """
    Parses various document formats (PDF, HTML, TXT) into a standard Document object.
    Currently heavily reliant on text extraction.
    Architecture is ready for future OCR / PDFPlumber integration.
    """
    def __init__(self):
        pass

    async def parse(self, content: bytes, file_type: str, source_name: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        """
        Main entry point for parsing. 
        In production, this would use pdfplumber for PDFs, BeautifulSoup for HTML, etc.
        For now, we decode bytes to string (mocking the extraction layer) to prevent 
        heavy external binary dependencies during the initial build phase.
        """
        logger.info(f"Parsing document {source_name} of type {file_type}")
        
        try:
            # Simulated extraction: assume content is UTF-8 text for now
            raw_text = content.decode('utf-8')
        except UnicodeDecodeError:
            # Fallback for mock binary files
            raw_text = "[Simulated OCR Text Extracted from Binary]"

        # Mock advanced parsing for validation
        extracted_ticker = metadata.get("ticker") if metadata else None
        if "AAPL" in raw_text or "Apple Inc." in raw_text:
            extracted_ticker = "AAPL"
            
        currency = "USD"
        if "€" in raw_text or "EUR" in raw_text:
            currency = "EUR"
            
        has_tables = "|" in raw_text or "Table of Contents" in raw_text

        custom_meta = metadata or {}
        custom_meta["currency"] = currency
        custom_meta["has_tables"] = has_tables

        doc_meta = DocumentMetadata(
            source=source_name,
            doc_type=metadata.get("doc_type", "Unknown") if metadata else "Unknown",
            ticker=extracted_ticker,
            date=metadata.get("date") if metadata else None,
            fiscal_year=metadata.get("fiscal_year") if metadata else None,
            user_id=metadata.get("user_id") if metadata else None,
            custom=custom_meta
        )
        
        return Document(raw_text=raw_text, metadata=doc_meta)
