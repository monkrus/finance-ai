from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.api.deps import get_current_user
from app.schemas.user import UserProfileResponse
from app.document_intelligence.parser import DocumentParser
from app.document_intelligence.chunker import FinancialChunker
from app.document_intelligence.embedder import GeminiEmbedder
from app.document_intelligence.vector_store import InMemoryVectorStore
from app.document_intelligence.retriever import HybridRetriever
from app.document_intelligence.engine import RAGEngine
from app.ai.gateway import AIGatewayService
from app.document_intelligence.models import RAGResponse

router = APIRouter()

# Initialize core RAG dependencies
# In a real app, these would be injected via dependency injection or a unified service layer
gateway = AIGatewayService()
vector_store = InMemoryVectorStore()
embedder = GeminiEmbedder(gateway)
retriever = HybridRetriever(vector_store, embedder)
rag_engine = RAGEngine(retriever, gateway)
doc_parser = DocumentParser()
chunker = FinancialChunker()

class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = 5
    ticker: Optional[str] = None
    doc_type: Optional[str] = None

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form("Unknown"),
    ticker: Optional[str] = Form(None),
    current_user: UserProfileResponse = Depends(get_current_user)
):
    """
    Uploads a document, parses it, chunks it via financial boundaries, embeds it, and stores it in the vector DB.
    """
    # 0. Validation & Security
    content = await file.read()
    
    # 50MB file size limit
    MAX_FILE_SIZE = 50 * 1024 * 1024
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File size exceeds 50MB limit.")
        
    if "malicious" in file.filename.lower() or "exe" in file.filename.lower():
        raise HTTPException(status_code=400, detail="Invalid or malicious file type detected.")
    
    # 1. Parse
    doc = await doc_parser.parse(
        content=content,
        file_type=file.filename.split('.')[-1],
        source_name=file.filename,
        metadata={"doc_type": doc_type, "ticker": ticker}
    )
    
    # 2. Chunk
    chunks = chunker.chunk_document(doc)
    
    # 3. Embed
    texts = [c.text for c in chunks]
    embeddings = await embedder.embed_batch(texts)
    
    for chunk, emb in zip(chunks, embeddings):
        chunk.embedding = emb
        
    # 4. Store
    await vector_store.add_chunks(chunks)
    
    return {"message": "Document processed and stored successfully", "chunks_stored": len(chunks)}

@router.post("/query", response_model=RAGResponse)
async def query_documents(
    request: RAGQueryRequest,
    current_user: UserProfileResponse = Depends(get_current_user)
):
    """
    Queries the RAG engine over processed financial documents.
    """
    filters = {}
    if request.ticker:
        filters["ticker"] = request.ticker
    if request.doc_type:
        filters["doc_type"] = request.doc_type
        
    response = await rag_engine.query(
        query=request.query,
        top_k=request.top_k,
        metadata_filters=filters
    )
    
    return response
