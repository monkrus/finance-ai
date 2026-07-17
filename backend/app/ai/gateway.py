import time
import logging
from typing import List, Dict, Any, AsyncGenerator

from app.core.exceptions import FinPilotException
from app.ai.models import AIMessage, AIResponse
from app.ai.providers.gemini import GeminiProvider
from app.ai.prompt_manager import PromptManager
from app.ai.memory_manager import MemoryManager
from app.ai.tool_registry import ToolRegistry
from app.ai.safety import SafetyFilter
from app.ai.metrics import MetricsTracker

logger = logging.getLogger(__name__)

class AIGatewayService:
    def __init__(self):
        self.provider = GeminiProvider()
        self.prompt_manager = PromptManager()
        self.memory_manager = MemoryManager()
        self.tool_registry = ToolRegistry()
        self.safety_filter = SafetyFilter()
        self.metrics = MetricsTracker()
        
        # Register tools
        from app.ai.tools.notifications import register_notification_tools
        register_notification_tools(self.tool_registry)

    async def chat(self, session_id: str, user_input: str, system_prompt_name: str = "system_base", allowed_tools: List[str] = None) -> str:
        start_time = time.time()
        
        # 1. Safety Filter Input
        safe_input = self.safety_filter.validate_input(user_input)
        
        # 2. Memory & Context
        await self.memory_manager.compress_context_if_needed(session_id)
        history = await self.memory_manager.get_history(session_id)
        
        # Add new user message to history
        user_msg = AIMessage(role="user", content=safe_input)
        history.append(user_msg)
        await self.memory_manager.add_message(session_id, user_msg)
        
        # 3. System Prompt
        system_content = self.prompt_manager.render(system_prompt_name)
        # Create a new list for the provider that includes the system prompt at the beginning
        provider_messages = [AIMessage(role="system", content=system_content)] + history
        
        # 4. Generate Response
        all_tools = self.tool_registry.get_all_tools()
        tools = [t for t in all_tools if t.name in allowed_tools] if allowed_tools is not None else all_tools
        
        try:
            response = await self.provider.generate_content(
                messages=provider_messages,
                tools=tools
            )
            
            # Handle Tool Calls
            if response.raw_response and response.raw_response.function_calls:
                import asyncio
                
                async def run_tool(fc):
                    start_t = time.time()
                    try:
                        result = await self.tool_registry.execute_tool(fc.name, fc.args)
                        self.metrics.track_tool_call(fc.name, (time.time() - start_t) * 1000)
                        return AIMessage(role="tool", name=fc.name, content=result)
                    except Exception as e:
                        logger.error(f"Tool {fc.name} failed: {e}")
                        return AIMessage(role="tool", name=fc.name, content=f"Error: {e}")
                        
                # Execute all parallel tools
                tool_results = await asyncio.gather(*[run_tool(fc) for fc in response.raw_response.function_calls])
                
                # Append all tool messages to history
                provider_messages.extend(tool_results)
                
                # Re-prompt model with tool results
                response = await self.provider.generate_content(
                    messages=provider_messages,
                    tools=tools
                )
            
            # 5. Output Validation
            safe_output = self.safety_filter.validate_output(response.content)
            
            # 6. Metrics & Persist
            latency = (time.time() - start_time) * 1000
            self.metrics.track(self.provider.default_model, response.tokens_used, latency)
            
            ai_msg = AIMessage(role="model", content=safe_output)
            await self.memory_manager.add_message(session_id, ai_msg)
            
            return safe_output
            
        except Exception as e:
            logger.error(f"AIGateway error: {str(e)}")
            error_msg = self.prompt_manager.render("error_recovery", error=str(e))
            return error_msg
            
    async def chat_stream(self, session_id: str, user_input: str, system_prompt_name: str = "system_base", allowed_tools: List[str] = None) -> AsyncGenerator[str, None]:
        safe_input = self.safety_filter.validate_input(user_input)
        
        await self.memory_manager.compress_context_if_needed(session_id)
        history = await self.memory_manager.get_history(session_id)
        
        user_msg = AIMessage(role="user", content=safe_input)
        history.append(user_msg)
        await self.memory_manager.add_message(session_id, user_msg)
        
        system_content = self.prompt_manager.render(system_prompt_name)
        provider_messages = [AIMessage(role="system", content=system_content)] + history
        
        all_tools = self.tool_registry.get_all_tools()
        tools = [t for t in all_tools if t.name in allowed_tools] if allowed_tools is not None else all_tools
        
        full_content = ""
        try:
            async for chunk in self.provider.generate_stream(messages=provider_messages, tools=tools):
                full_content += chunk
                yield chunk
                
            safe_output = self.safety_filter.validate_output(full_content)
            ai_msg = AIMessage(role="model", content=safe_output)
            await self.memory_manager.add_message(session_id, ai_msg)
            
        except Exception as e:
            logger.error(f"AIGateway stream error: {str(e)}")
            error_msg = self.prompt_manager.render("error_recovery", error=str(e))
            yield error_msg
