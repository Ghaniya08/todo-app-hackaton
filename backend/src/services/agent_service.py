"""
Agent service for OpenAI Agents SDK integration.

[Task]: T010
[From]: specs/004-ai-chat-agent/plan.md §Architecture Overview
[From]: specs/004-ai-chat-agent/research.md §Research Item 1
"""

import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI

from ..config import settings

logger = logging.getLogger(__name__)

# System prompt for the todo assistant agent
SYSTEM_PROMPT = """You are a helpful todo assistant. You help users manage their tasks through natural conversation.

You can perform the following actions:
- Create new tasks: When a user wants to add, create, or remember something, use the add_task tool
- List tasks: When a user wants to see, view, or show their tasks, use the list_tasks tool
- Complete tasks: When a user wants to mark something as done or complete, use the complete_task tool
- Delete tasks: When a user wants to remove or delete a task, use the delete_task tool

Guidelines:
- Be concise and friendly in your responses
- Always confirm actions you've taken (e.g., "I've created a task...")
- If a user's request is ambiguous, ask for clarification
- When listing tasks, format them in a readable way
- If a task operation fails, explain what went wrong

Remember: You can only manage the authenticated user's tasks. All task operations are scoped to their account."""


class AgentService:
    """
    Service for managing AI agent interactions.

    [Task]: T010
    [From]: specs/004-ai-chat-agent/spec.md §FR-002
    """

    def __init__(self):
        """Initialize the AI client (supports OpenAI, Gemini, Groq)."""
        # Configure client based on provider
        client_kwargs = {"api_key": settings.ai_api_key}
        if settings.ai_base_url:
            client_kwargs["base_url"] = settings.ai_base_url

        self.client = OpenAI(**client_kwargs)
        self.model = settings.ai_model
        self.provider = settings.ai_provider
        self.tools: List[Dict[str, Any]] = []
        logger.info(f"AgentService initialized with provider={self.provider}, model={self.model}")

    def register_tool(self, tool_definition: Dict[str, Any]) -> None:
        """
        Register an MCP tool with the agent.

        [Task]: T010, T022, T026, T030, T034
        [From]: specs/004-ai-chat-agent/plan.md §Architecture Overview

        Args:
            tool_definition: OpenAI function tool definition
        """
        self.tools.append(tool_definition)
        logger.info(f"Registered tool: {tool_definition.get('function', {}).get('name', 'unknown')}")

    async def run(
        self,
        messages: List[Dict[str, str]],
        user_id: str,
        tool_executor: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Run the agent with conversation history and user message.

        [Task]: T010
        [From]: specs/004-ai-chat-agent/spec.md §FR-002

        Args:
            messages: Conversation history in OpenAI format
            user_id: Authenticated user ID for tool context
            tool_executor: Function to execute tool calls

        Returns:
            Dict containing response content and any tool calls made
        """
        # Build messages with system prompt
        full_messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *messages
        ]

        logger.info(f"Running agent for user={user_id}, messages={len(messages)}, tools={len(self.tools)}")

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                tools=self.tools if self.tools else None,
                tool_choice="auto" if self.tools else None,
                timeout=settings.chat_timeout_seconds
            )

            assistant_message = response.choices[0].message
            tool_calls_made = []

            # Handle tool calls if present
            if assistant_message.tool_calls and tool_executor:
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = tool_call.function.arguments

                    logger.info(f"Executing tool: {tool_name}")

                    try:
                        import json
                        args = json.loads(tool_args)
                        result = await tool_executor(tool_name, args, user_id)
                        tool_calls_made.append({
                            "tool": tool_name,
                            "input": args,
                            "output": result
                        })
                    except Exception as e:
                        logger.error(f"Tool execution failed: {tool_name}, error={e}")
                        tool_calls_made.append({
                            "tool": tool_name,
                            "input": args if 'args' in locals() else {},
                            "output": {"error": str(e)}
                        })

                # If tools were called, get final response with tool results
                if tool_calls_made:
                    # Add tool results to messages
                    tool_messages = full_messages + [
                        {"role": "assistant", "content": None, "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                            }
                            for tc in assistant_message.tool_calls
                        ]}
                    ]

                    for i, tc in enumerate(assistant_message.tool_calls):
                        import json
                        tool_messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": json.dumps(tool_calls_made[i].get("output", {}))
                        })

                    # Get final response
                    final_response = self.client.chat.completions.create(
                        model=self.model,
                        messages=tool_messages,
                        timeout=settings.chat_timeout_seconds
                    )
                    content = final_response.choices[0].message.content
                else:
                    content = assistant_message.content
            else:
                content = assistant_message.content

            return {
                "content": content or "I'm sorry, I couldn't generate a response.",
                "tool_calls": tool_calls_made if tool_calls_made else None
            }

        except Exception as e:
            logger.error(f"Agent execution failed: {e}", exc_info=True)
            return {
                "content": "I'm sorry, I encountered an error processing your request. Please try again.",
                "tool_calls": None,
                "error": str(e)
            }


# Global agent service instance
agent_service = AgentService()
