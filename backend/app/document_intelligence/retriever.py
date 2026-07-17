import logging
from typing import List, Dict, Any, Optional
from app.document_intelligence.models import DocumentChunk
from app.document_intelligence.vector_store import VectorStoreInterface
from app.document_intelligence.embedder import EmbedderInterface

logger = logging.getLogger(__name__)

class HybridRetriever:
    """
    Combines semantic (vector) and keyword (lexical) search.
    Provides Reciprocal Rank Fusion (RRF) for combining results.
    """
    def __init__(self, vector_store: VectorStoreInterface, embedder: EmbedderInterface):
        self.vector_store = vector_store
        self.embedder = embedder

    async def search(self, query: str, top_k: int = 5, metadata_filters: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        logger.info(f"Retrieving chunks for query: '{query}'")
        
        # 1. Semantic Search
        query_embedding = await self.embedder.embed_text(query)
        semantic_results = await self.vector_store.semantic_search(
            query_embedding=query_embedding, 
            top_k=top_k * 2, # Oversample
            metadata_filters=metadata_filters
        )
        
        # 2. Keyword Search
        keyword_results = await self.vector_store.keyword_search(
            query=query, 
            top_k=top_k * 2,
            metadata_filters=metadata_filters
        )
        
        # 3. Reciprocal Rank Fusion (RRF)
        # For simplicity, if we have chunks in both, they score higher.
        chunk_scores = {}
        chunks_map = {}
        
        def add_to_rrf(results, weight=1.0):
            for rank, chunk in enumerate(results):
                score = weight / (60 + rank) # 60 is standard RRF constant
                if chunk.id not in chunk_scores:
                    chunk_scores[chunk.id] = 0.0
                    chunks_map[chunk.id] = chunk
                chunk_scores[chunk.id] += score
                
        add_to_rrf(semantic_results, weight=1.0)
        add_to_rrf(keyword_results, weight=0.5) # Slight preference to semantic
        
        # Sort and return top_k
        sorted_ids = sorted(chunk_scores.keys(), key=lambda k: chunk_scores[k], reverse=True)
        final_chunks = [chunks_map[cid] for cid in sorted_ids[:top_k]]
        
        logger.info(f"Retrieved {len(final_chunks)} chunks using Hybrid RRF.")
        return final_chunks
