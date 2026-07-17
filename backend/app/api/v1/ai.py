from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.ai.gateway import AIGatewayService
from app.agents.router import AgentRouter
from app.agents.tools import register_all_tools
from app.agents.prompts import register_agent_prompts
from app.market_data.service import MarketDataService
from app.api.deps import get_current_user
from app.schemas.user import UserProfileResponse

router = APIRouter()

# Initialize core services
gateway = AIGatewayService()
md_service = MarketDataService()

# Import the RAGEngine instance from documents router
from app.api.v1.documents import rag_engine

# Register agent tools and prompts
register_all_tools(gateway.tool_registry, md_service, rag_engine)
register_agent_prompts(gateway.prompt_manager)

# Initialize router
agent_router = AgentRouter(gateway)

class ChatRequest(BaseModel):
    session_id: str
    message: str
    stream: bool = False

@router.post("/chat")
async def chat_endpoint(request: ChatRequest, current_user: UserProfileResponse = Depends(get_current_user)):
    """
    Generic chat endpoint using the AI Gateway.
    """
    if request.stream:
        async def generator():
            async for chunk in agent_router.chat_stream(request.session_id, request.message):
                yield chunk
        return StreamingResponse(generator(), media_type="text/event-stream")
    
    response = await agent_router.chat(request.session_id, request.message)
    return {"response": response}
