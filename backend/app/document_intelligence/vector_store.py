import math
import logging
from typing import List, Dict, Any, Optional
from app.document_intelligence.models import DocumentChunk

logger = logging.getLogger(__name__)

class VectorStoreInterface:
    async def add_chunks(self, chunks: List[DocumentChunk]):
        raise NotImplementedError
        
    async def semantic_search(self, query_embedding: List[float], top_k: int = 5, metadata_filters: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        raise NotImplementedError
        
    async def keyword_search(self, query: str, top_k: int = 5, metadata_filters: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        raise NotImplementedError
        
    async def delete_document(self, document_id: str):
        raise NotImplementedError
        
    async def update_document(self, document_id: str, new_chunks: List[DocumentChunk]):
        raise NotImplementedError

class InMemoryVectorStore(VectorStoreInterface):
    """
    A lightweight, in-memory vector database.
    Abstracts vector math natively to avoid heavy dependencies (like Pinecone/Qdrant) 
    during development, but satisfies the interface for future drop-in replacement.
    """
    def __init__(self):
        self._store: List[DocumentChunk] = []
        
    async def add_chunks(self, chunks: List[DocumentChunk]):
        self._store.extend(chunks)
        logger.info(f"Added {len(chunks)} chunks to vector store. Total: {len(self._store)}")
        
    async def delete_document(self, document_id: str):
        initial_count = len(self._store)
        self._store = [chunk for chunk in self._store if chunk.document_id != document_id]
        logger.info(f"Deleted {initial_count - len(self._store)} chunks for document {document_id}")
        
    async def update_document(self, document_id: str, new_chunks: List[DocumentChunk]):
        await self.delete_document(document_id)
        await self.add_chunks(new_chunks)

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
            
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)

    def _apply_filters(self, chunk: DocumentChunk, filters: Dict[str, Any]) -> bool:
        for k, v in filters.items():
            if k == "section_name":
                if chunk.section_name != v: return False
            elif k == "doc_type":
                if chunk.metadata.doc_type != v: return False
            elif k == "ticker":
                if chunk.metadata.ticker != v: return False
            elif k == "user_id":
                # Tenant isolation: only chunks owned by this user match.
                if chunk.metadata.user_id != v: return False
            # Can extend to support arbitrary custom metadata matching
        return True

    async def semantic_search(self, query_embedding: List[float], top_k: int = 5, metadata_filters: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        results = []
        for chunk in self._store:
            if metadata_filters and not self._apply_filters(chunk, metadata_filters):
                continue
                
            if chunk.embedding:
                score = self._cosine_similarity(query_embedding, chunk.embedding)
                results.append((score, chunk))
                
        # Sort by score descending
        results.sort(key=lambda x: x[0], reverse=True)
        
        # Return top_k chunks
        return [chunk for score, chunk in results[:top_k]]

    async def keyword_search(self, query: str, top_k: int = 5, metadata_filters: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        results = []
        query_terms = set(query.lower().split())
        
        for chunk in self._store:
            if metadata_filters and not self._apply_filters(chunk, metadata_filters):
                continue
                
            # Basic BM25-like mock (term overlap)
            chunk_terms = set(chunk.text.lower().split())
            overlap = len(query_terms.intersection(chunk_terms))
            
            if overlap > 0:
                score = overlap / len(query_terms)
                results.append((score, chunk))
                
        results.sort(key=lambda x: x[0], reverse=True)
        return [chunk for score, chunk in results[:top_k]]
