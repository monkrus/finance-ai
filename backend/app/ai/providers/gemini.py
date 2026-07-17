import logging
import asyncio
from typing import List, AsyncGenerator
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google import genai
from google.genai import types

from app.core.config import settings
from app.ai.models import AIMessage, AIResponse, AITool
from app.ai.providers.base import AIProviderInterface
from app.core.exceptions import FinPilotException

logger = logging.getLogger(__name__)

class GeminiProvider(AIProviderInterface):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            logger.warning("Gemini API key is not configured.")
            self.api_key = "dummy_api_key_for_init"
        self.client = genai.Client(api_key=self.api_key)
        self.default_model = "gemini-2.5-flash"

    def _convert_messages(self, messages: List[AIMessage]) -> tuple:
        """Converts AIMessage to google-genai types. Returns (system_instruction, contents)."""
        system_instructions = []
        contents = []

        for msg in messages:
            if msg.role == "system":
                system_instructions.append(msg.content)
            elif msg.role in ["user", "model"]:
                contents.append(
                    types.Content(
                        role=msg.role,
                        parts=[types.Part.from_text(text=msg.content)]
                    )
                )
            elif msg.role == "tool":
                contents.append(
                    types.Content(
                        role="user",
                        parts=[types.Part.from_function_response(name=msg.name, response={"result": msg.content})]
                    )
                )

        sys_inst = None
        if system_instructions:
            sys_inst = "\n".join(system_instructions)
            
        return sys_inst, contents

    def _convert_tools(self, tools: List[AITool]) -> List[types.Tool]:
        if not tools:
            return None
        
        funcs = []
        for t in tools:
            funcs.append(
                types.FunctionDeclaration(
                    name=t.name,
                    description=t.description,
                    parameters=t.parameters
                )
            )
        return [types.Tool(function_declarations=funcs)]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    async def _execute_generate(self, contents, config):
        return await self.client.aio.models.generate_content(
            model=self.default_model,
            contents=contents,
            config=config,
        )

    async def generate_content(
        self,
        messages: List[AIMessage],
        tools: List[AITool] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AIResponse:
        
        sys_inst, contents = self._convert_messages(messages)
        gemini_tools = self._convert_tools(tools)
        
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            tools=gemini_tools,
            system_instruction=sys_inst,
        )

        try:
            # Added timeout via asyncio.wait_for
            response = await asyncio.wait_for(
                self._execute_generate(contents, config),
                timeout=30.0
            )
            
            tool_calls = None
            if response.function_calls:
                tool_calls = [{"name": fc.name, "args": fc.args} for fc in response.function_calls]

            return AIResponse(
                content=response.text or "",
                tokens_used=response.usage_metadata.total_token_count if response.usage_metadata else 0,
                raw_response=response,
            )
            
        except Exception as e:
            logger.error(f"Gemini API Error: {str(e)}")
            raise FinPilotException(message=f"Gemini API Error: {str(e)}", status_code=500)

    async def generate_stream(
        self,
        messages: List[AIMessage],
        tools: List[AITool] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncGenerator[str, None]:
        
        sys_inst, contents = self._convert_messages(messages)
        gemini_tools = self._convert_tools(tools)
        
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            tools=gemini_tools,
            system_instruction=sys_inst,
        )

        try:
            response_stream = self.client.aio.models.generate_content_stream(
                model=self.default_model,
                contents=contents,
                config=config,
            )
            
            async for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Gemini API Streaming Error: {str(e)}")
            raise FinPilotException(message=f"Gemini API Streaming Error: {str(e)}", status_code=500)
