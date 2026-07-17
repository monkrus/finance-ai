import re
import logging
from typing import List
from app.document_intelligence.models import Document, DocumentChunk

logger = logging.getLogger(__name__)

class FinancialChunker:
    """
    Financial-aware chunking engine.
    Instead of arbitrarily splitting tokens, it uses heuristics and regexes
    to identify logical boundaries in financial documents (e.g. 10-K, Earnings Calls).
    """
    def __init__(self, max_chunk_size: int = 1500):
        self.max_chunk_size = max_chunk_size
        
        # Regex patterns to detect standard SEC filing sections and common report headers
        self.section_patterns = {
            "Business Overview": re.compile(r"(?i)^(?:Item 1\.|Part I\s+Item 1\.)\s*Business\s*$"),
            "Risk Factors": re.compile(r"(?i)^(?:Item 1A\.)\s*Risk Factors\s*$"),
            "MD&A": re.compile(r"(?i)^(?:Item 7\.)\s*Management.*?Discussion and Analysis.*$"),
            "Financial Statements": re.compile(r"(?i)^(?:Item 8\.)\s*Financial Statements and Supplementary Data\s*$"),
            "Income Statement": re.compile(r"(?i)^.*(?:Consolidated )?Statement[s]? of (?:Operations|Income|Comprehensive Income).*$"),
            "Balance Sheet": re.compile(r"(?i)^.*(?:Consolidated )?Balance Sheet[s]?.*$"),
            "Cash Flow Statement": re.compile(r"(?i)^.*(?:Consolidated )?Statement[s]? of Cash Flow[s]?.*$"),
            "Notes to Accounts": re.compile(r"(?i)^.*Notes to (?:Consolidated )?Financial Statements.*$"),
            "Executive Summary": re.compile(r"(?i)^Executive Summary\s*$"),
            "Auditor Report": re.compile(r"(?i)^Report of Independent Registered Public Accounting Firm\s*$"),
            "Segment Information": re.compile(r"(?i)^.*Segment Information.*$")
        }

    def _split_into_paragraphs(self, text: str) -> List[str]:
        # Split by double newline or similar paragraph markers
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text)]
        return [p for p in paragraphs if p]

    def _sub_chunk(self, section_name: str, text: str, doc: Document) -> List[DocumentChunk]:
        """Sub-chunk large sections that exceed max_chunk_size."""
        words = text.split()
        chunks = []
        current_chunk_words = []
        
        for word in words:
            current_chunk_words.append(word)
            if len(current_chunk_words) >= self.max_chunk_size:
                chunks.append(DocumentChunk(
                    document_id=doc.id,
                    text=" ".join(current_chunk_words),
                    section_name=section_name,
                    page_number=1, # Mock page number
                    metadata=doc.metadata
                ))
                # Explicit overlap of 50 words
                current_chunk_words = current_chunk_words[-50:]
                
        if current_chunk_words:
            chunks.append(DocumentChunk(
                document_id=doc.id,
                text=" ".join(current_chunk_words),
                section_name=section_name,
                page_number=1, # Mock page number
                metadata=doc.metadata
            ))
            
        return chunks

    def chunk_document(self, doc: Document) -> List[DocumentChunk]:
        logger.info(f"Chunking document {doc.id} ({doc.metadata.source})")
        paragraphs = self._split_into_paragraphs(doc.raw_text)
        
        chunks = []
        current_section = "General"
        current_section_text = []
        
        for p in paragraphs:
            # Check if this paragraph is a section header
            matched_section = None
            for sec_name, pattern in self.section_patterns.items():
                if pattern.match(p[:200]): # only check start of paragraph
                    matched_section = sec_name
                    break
                    
            if matched_section:
                # Flush the old section
                if current_section_text:
                    full_text = "\n\n".join(current_section_text)
                    chunks.extend(self._sub_chunk(current_section, full_text, doc))
                current_section = matched_section
                current_section_text = [p]
            else:
                current_section_text.append(p)
                
        # Flush the last section
        if current_section_text:
            full_text = "\n\n".join(current_section_text)
            chunks.extend(self._sub_chunk(current_section, full_text, doc))
            
        return chunks
