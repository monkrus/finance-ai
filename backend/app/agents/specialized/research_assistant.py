from app.agents.base import BaseAgent
from app.agents.models import AgentConfig
from app.ai.gateway import AIGatewayService

class ResearchAssistantAgent(BaseAgent):
    def __init__(self, gateway: AIGatewayService):
        config = AgentConfig(
            name="research_assistant",
            description="General finance research, industry research",
            system_prompt_name="agent_research_assistant",
            allowed_tools=[], # Standard LLM capability + memory
            temperature=0.7
        )
        super().__init__(config, gateway)
