from pydantic import BaseModel, Field
from typing import List, Optional

class AgentConfig(BaseModel):
    name: str
    description: str
    system_prompt_name: str
    allowed_tools: List[str] = Field(default_factory=list)
    temperature: float = 0.7
