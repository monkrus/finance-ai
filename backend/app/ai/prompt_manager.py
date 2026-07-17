import logging
from typing import Dict, Optional
from app.ai.models import PromptTemplate
from app.core.exceptions import FinPilotException

logger = logging.getLogger(__name__)

class PromptManager:
    """
    Centralized manager for AI prompt templates.
    Ensures that prompts are strictly decoupled from business logic.
    """
    def __init__(self):
        self._templates: Dict[str, PromptTemplate] = {}
        self._load_defaults()

    def _load_defaults(self):
        # Base system prompt
        self.register(
            PromptTemplate(
                name="system_base",
                template="You are FinPilot AI, a highly intelligent financial assistant. You provide accurate, grounded financial insights based strictly on provided data.",
                variables=[]
            )
        )
        # Fallback error prompt
        self.register(
            PromptTemplate(
                name="error_recovery",
                template="An error occurred while fetching the required data: {error}. Please inform the user gracefully.",
                variables=["error"]
            )
        )

    def register(self, template: PromptTemplate):
        key = f"{template.name}:{template.version}"
        self._templates[key] = template
        # Also store as latest default if no version provided
        self._templates[template.name] = template
        logger.debug(f"Registered prompt template: {template.name} v{template.version}")

    def get_template(self, name: str, version: str = None) -> str:
        key = f"{name}:{version}" if version else name
        if key not in self._templates:
            raise FinPilotException(message=f"Prompt template '{key}' not found.", status_code=404)
        return self._templates[key].template

    def render(self, name: str, version: str = None, **kwargs) -> str:
        template_str = self.get_template(name, version)
        try:
            return template_str.format(**kwargs)
        except KeyError as e:
            raise FinPilotException(message=f"Missing variable {str(e)} for prompt '{name}'", status_code=400)
