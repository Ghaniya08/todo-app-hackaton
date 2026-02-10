"""
Chat service layer for conversation management.

[Task]: T008
[From]: specs/004-ai-chat-agent/data-model.md §Query Patterns
[From]: specs/004-ai-chat-agent/spec.md §Functional Requirements
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from sqlmodel import Session, select

from ..models.conversation import Conversation
from ..models.message import Message

logger = logging.getLogger(__name__)


class ChatService:
    """Service layer for chat/conversation business logic."""

    @staticmethod
    def create_conversation(
        session: Session,
        user_id: str,
        title: Optional[str] = None
    ) -> Conversation:
        """
        Create a new conversation for a user.

        [Task]: T008
        [From]: specs/004-ai-chat-agent/data-model.md §Query Patterns

        Args:
            session: Database session
            user_id: User identifier
            title: Optional conversation title

        Returns:
            Conversation: Created conversation object
        """
        conversation = Conversation(
            user_id=user_id,
            title=title
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        logger.info(f"Created conversation: id={conversation.id}, user_id={user_id}")
        return conversation

    @staticmethod
    def get_conversation(
        session: Session,
        conversation_id: UUID,
        user_id: str
    ) -> Optional[Conversation]:
        """
        Get a conversation by ID, ensuring it belongs to the user.

        [Task]: T008
        [From]: specs/004-ai-chat-agent/data-model.md §Security Constraints

        Args:
            session: Database session
            conversation_id: Conversation identifier
            user_id: User identifier (for ownership verification)

        Returns:
            Optional[Conversation]: Conversation if found and owned by user
        """
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        return session.exec(statement).first()

    @staticmethod
    def get_or_create_conversation(
        session: Session,
        user_id: str,
        conversation_id: Optional[UUID] = None
    ) -> Conversation:
        """
        Get existing conversation or create a new one.

        [Task]: T008, T037
        [From]: specs/004-ai-chat-agent/spec.md §FR-004

        Args:
            session: Database session
            user_id: User identifier
            conversation_id: Optional existing conversation ID

        Returns:
            Conversation: Existing or new conversation
        """
        if conversation_id:
            conversation = ChatService.get_conversation(session, conversation_id, user_id)
            if conversation:
                return conversation
            logger.warning(f"Conversation not found: id={conversation_id}, user_id={user_id}")

        # Create new conversation
        return ChatService.create_conversation(session, user_id)

    @staticmethod
    def list_conversations(
        session: Session,
        user_id: str,
        limit: int = 20
    ) -> List[Conversation]:
        """
        List all conversations for a user, ordered by most recent.

        [Task]: T008
        [From]: specs/004-ai-chat-agent/data-model.md §Query Patterns

        Args:
            session: Database session
            user_id: User identifier
            limit: Maximum number of conversations to return

        Returns:
            List[Conversation]: List of conversations
        """
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )
        return list(session.exec(statement).all())

    @staticmethod
    def add_message(
        session: Session,
        conversation_id: UUID,
        role: str,
        content: str,
        tool_calls: Optional[List[Dict[str, Any]]] = None
    ) -> Message:
        """
        Add a new message to a conversation.

        [Task]: T008
        [From]: specs/004-ai-chat-agent/data-model.md §Query Patterns

        Args:
            session: Database session
            conversation_id: Parent conversation ID
            role: Message role ('user', 'assistant', 'tool')
            content: Message content
            tool_calls: Optional tool call details

        Returns:
            Message: Created message object
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls
        )
        session.add(message)

        # Update conversation updated_at
        conversation = session.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
            session.add(conversation)

        session.commit()
        session.refresh(message)
        logger.debug(f"Added message: id={message.id}, role={role}, conversation={conversation_id}")
        return message

    @staticmethod
    def get_messages(
        session: Session,
        conversation_id: UUID,
        user_id: str,
        limit: int = 20
    ) -> List[Message]:
        """
        Get recent messages for a conversation.

        [Task]: T008
        [From]: specs/004-ai-chat-agent/data-model.md §Query Patterns

        Args:
            session: Database session
            conversation_id: Conversation identifier
            user_id: User identifier (for ownership verification)
            limit: Maximum number of messages to return

        Returns:
            List[Message]: List of messages in chronological order
        """
        # First verify conversation belongs to user
        conversation = ChatService.get_conversation(session, conversation_id, user_id)
        if not conversation:
            logger.warning(f"Conversation access denied: id={conversation_id}, user_id={user_id}")
            return []

        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = list(session.exec(statement).all())
        return list(reversed(messages))  # Return in chronological order

    @staticmethod
    def get_context_messages(
        session: Session,
        conversation_id: UUID,
        limit: int = 20
    ) -> List[Dict[str, str]]:
        """
        Get messages formatted for agent context.

        [Task]: T008
        [From]: specs/004-ai-chat-agent/research.md §Conversation State Management

        Args:
            session: Database session
            conversation_id: Conversation identifier
            limit: Maximum number of messages

        Returns:
            List[Dict]: Messages formatted for OpenAI API
        """
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = list(session.exec(statement).all())
        messages = list(reversed(messages))  # Chronological order

        # Format for OpenAI API
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
            if msg.role in ("user", "assistant")  # Exclude tool messages from context
        ]
