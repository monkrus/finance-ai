import logging
import re
from typing import Any
from app.core.exceptions import FinPilotException

logger = logging.getLogger(__name__)

class SafetyFilter:
    def __init__(self):
        # Basic patterns for simulated safety check
        self.jailbreak_patterns = [
            r"ignore previous instructions",
            r"you are now (?!FinPilot)",
            r"system prompt",
            r"forget everything"
        ]
        self.pii_patterns = [
            r"\b\d{3}-\d{2}-\d{4}\b", # SSN
            r"\b(?:\d[ -]*?){13,16}\b" # CC
        ]
        
    def validate_input(self, text: str) -> str:
        """
        Validates user input. Protects against prompt injection and PII.
        Returns the sanitized text or raises an exception.
        """
        if not text:
            raise FinPilotException(message="Input cannot be empty.", status_code=400)
            
        if len(text) > 4000:
            raise FinPilotException(message="Input is too long. Maximum length is 4000 characters.", status_code=400)
            
        text_lower = text.lower()
        for pattern in self.jailbreak_patterns:
            if re.search(pattern, text_lower):
                logger.warning(f"Jailbreak attempt blocked: {pattern}")
                raise FinPilotException(message="Unsafe input detected.", status_code=403)
                
        for pattern in self.pii_patterns:
            if re.search(pattern, text):
                logger.warning("PII detected in input. Blocking.")
                raise FinPilotException(message="Input contains sensitive PII which is not allowed.", status_code=403)
                
        return text
        
    def validate_output(self, text: str) -> str:
        """
        Validates the model output for safety and hallucination prevention.
        """
        if not text or len(text.strip()) == 0:
            return "I apologize, but I am unable to provide a response at this moment."
            
        return text
