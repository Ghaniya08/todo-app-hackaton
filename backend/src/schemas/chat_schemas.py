"""
Chat request/response schemas for AI Chat Agent.

[Task]: T009
[From]: specs/004-ai-chat-agent/contracts/chat-api.yaml
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    Request schema for sending a chat message.

    [Task]: T009
    [From]: specs/004-ai-chat-agent/contracts/chat-api.yaml §ChatRequest
    """
    conversation_id: Optional[UUID] = Field(
        default=None,
        description="Existing conversation ID to continue. If not provided, a new conversation is created."
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's message to the AI agent"
    )


class ToolCall(BaseModel):
    """
    Tool call details for assistant responses.

    [Task]: T009
    [From]: specs/004-ai-chat-agent/contracts/chat-api.yaml §ToolCall
    """
    tool: str = Field(
        ...,
        description="Name of the MCP tool called"
    )
    input: Dict[str, Any] = Field(
        default_factory=dict,
        description="Input parameters passed to the tool"
    )
    output: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Output returned by the tool"
    )


class MessageResponse(BaseModel):
    """
    Message response schema.

    [Task]: T009
    [From]: specs/004-ai-chat-agent/contracts/chat-api.yaml §Message
    """
    id: UUID = Field(..., description="Unique message identifier")
    role: str = Field(..., description="Message role: user, assistant, or tool")
    content: str = Field(..., description="Message content")
    tool_calls: Optional[List[ToolCall]] = Field(
        default=None,
        description="Tool calls made during message processing"
    )
    created_at: datetime = Field(..., description="When the message was created")

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    """
    Response schema for chat endpoint.

    [Task]: T009
    [From]: specs/004-ai-chat-agent/contracts/chat-api.yaml §ChatResponse
    """
    conversation_id: UUID = Field(
        ...,
        description="ID of the conversation (new or existing)"
    )
    message: MessageResponse = Field(
        ...,
        description="Assistant's response message"
    )
    tool_calls: Optional[List[ToolCall]] = Field(
        default=None,
        description="MCP tools called during message processing"
    )


class ConversationSummary(BaseModel):
    """
    Conversation summary for listing.

    [Task]: T009
    [From]: specs/004-ai-chat-agent/contracts/chat-api.yaml §ConversationSummary
    """
    id: UUID = Field(..., description="Unique conversation identifier")
    title: Optional[str] = Field(default=None, description="Conversation title")
    created_at: datetime = Field(..., description="When the conversation was created")
    updated_at: datetime = Field(..., description="When the conversation was last updated")

    class Config:
        from_attributes = True
