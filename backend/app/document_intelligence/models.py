import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class DocumentMetadata(BaseModel):
    source: str
    doc_type: str  # e.g., "10-K", "10-Q", "Earnings Call"
    ticker: Optional[str] = None
    date: Optional[str] = None
    fiscal_year: Optional[str] = None
    user_id: Optional[int] = None  # Owning tenant; enforced on retrieval for isolation
    custom: Dict[str, Any] = Field(default_factory=dict)

class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    raw_text: str
    metadata: DocumentMetadata

class DocumentChunk(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    text: str
    section_name: str  # e.g., "MD&A", "Risk Factors"
    page_number: Optional[int] = None
    metadata: DocumentMetadata
    embedding: Optional[List[float]] = None

class Citation(BaseModel):
    chunk_id: str
    document_id: str
    text_snippet: str
    page_reference: Optional[int] = None
    score: float
    source: str

class RAGResponse(BaseModel):
    answer: str
    citations: List[Citation]
    confidence_score: float
