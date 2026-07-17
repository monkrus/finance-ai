import logging
from typing import List, Dict, Any, Optional
from app.document_intelligence.models import DocumentChunk, RAGResponse, Citation
from app.document_intelligence.retriever import HybridRetriever
from app.ai.gateway import AIGatewayService
from google.genai import types
import json

logger = logging.getLogger(__name__)

class RAGEngine:
    """
    Orchestrates the Retrieval-Augmented Generation pipeline.
    Enforces strict grounding and hallucinaton reduction via the AI Gateway.
    """
    def __init__(self, retriever: HybridRetriever, gateway: AIGatewayService):
        self.retriever = retriever
        self.gateway = gateway
        
        # Register the prompt
        self._register_prompts()

    def _register_prompts(self):
        from app.ai.models import PromptTemplate
        
        self.gateway.prompt_manager.register(PromptTemplate(
            name="rag_grounding_prompt",
            template="""You are a strict Financial Data Extraction AI.
You will be provided with a set of CONTEXT chunks extracted from financial documents.
Answer the user's query ONLY using the provided CONTEXT. 
If the CONTEXT does not contain the answer, reply exactly with "Information not found in the provided documents." DO NOT hallucinate.

Respond ONLY in JSON format:
{{
    "answer": "Detailed answer based on context.",
    "citations": ["chunk_id_1", "chunk_id_2"],
    "confidence_score": 0.95
}}

CONTEXT:
{context}

USER QUERY:
{query}
"""
        ))

    async def query(self, query: str, top_k: int = 5, metadata_filters: Optional[Dict[str, Any]] = None) -> RAGResponse:
        # 1. Retrieve Context
        chunks = await self.retriever.search(query, top_k=top_k, metadata_filters=metadata_filters)
        
        if not chunks:
            return RAGResponse(
                answer="No relevant documents found.",
                citations=[],
                confidence_score=0.0
            )
            
        # 2. Assemble Context
        context_str = ""
        chunk_map = {}
        for idx, chunk in enumerate(chunks):
            chunk_map[chunk.id] = chunk
            context_str += f"[CHUNK ID: {chunk.id} | SOURCE: {chunk.metadata.source} | SECTION: {chunk.section_name}]\n{chunk.text}\n\n"
            
        # 3. Generate Answer (Using Gateway's Gemini Provider directly for JSON schema)
        system_prompt = self.gateway.prompt_manager.render(
            "rag_grounding_prompt", 
            context=context_str, 
            query=query
        )
        
        config = types.GenerateContentConfig(
            temperature=0.0, # Zero temp for strict grounding
            response_mime_type="application/json",
        )
        
        try:
            res = await self.gateway.provider._execute_generate(
                contents=[system_prompt],
                config=config
            )
            
            data = json.loads(res.text) if res and res.text else {}
            answer = data.get("answer", "Error generating answer.")
            citation_ids = data.get("citations", [])
            confidence = data.get("confidence_score", 0.0)
            
            # 4. Resolve Citations
            citations = []
            for cid in citation_ids:
                if cid in chunk_map:
                    c = chunk_map[cid]
                    citations.append(Citation(
                        chunk_id=c.id,
                        document_id=c.document_id,
                        text_snippet=c.text[:200] + "...",
                        page_reference=c.page_number,
                        score=1.0,
                        source=c.metadata.source
                    ))
                    
            return RAGResponse(
                answer=answer,
                citations=citations,
                confidence_score=confidence
            )
            
        except Exception as e:
            logger.error(f"RAG Engine generation failed: {e}")
            return RAGResponse(answer=f"Failed to generate answer: {e}", citations=[], confidence_score=0.0)
