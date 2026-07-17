from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AIMessage(BaseModel):
    role: str  # "system", "user", "model", "tool"
    content: str
    name: Optional[str] = None
    
    # Optionally hold parsed tool calls if the model asked to call a tool
    tool_calls: Optional[List[Dict[str, Any]]] = None

class AIResponse(BaseModel):
    content: str
    tokens_used: int = 0
    finish_reason: str = "stop"
    raw_response: Optional[Any] = None

class AITool(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any] # JSON Schema

class PromptTemplate(BaseModel):
    name: str
    template: str
    version: str = "1.0.0"
    variables: List[str] = []
