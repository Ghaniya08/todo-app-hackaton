# Research: AI Chat Agent & Integration

**Feature**: 004-ai-chat-agent
**Date**: 2026-02-10
**Status**: Complete

## Research Item 1: OpenAI Agents SDK Integration

### Decision
Use OpenAI Agents SDK for agent creation and execution.

### Rationale
- Official SDK from OpenAI for building agents
- Native support for tool/function calling
- Built-in conversation management
- Integrates with MCP protocol

### Alternatives Considered
| Alternative | Why Rejected |
|-------------|--------------|
| LangChain | More complex, adds unnecessary abstraction layer |
| Custom implementation | Time-consuming, error-prone for hackathon timeline |
| Direct OpenAI API | Requires manual conversation/tool management |

### Implementation Notes
```python
from openai_agents import Agent, Runner

agent = Agent(
    name="TodoAssistant",
    model="gpt-4o-mini",  # Cost-effective for hackathon
    instructions="You are a helpful todo assistant...",
    tools=[add_task, list_tasks, complete_task, delete_task, update_task]
)

runner = Runner(agent=agent)
result = runner.run(messages=conversation_history)
```

## Research Item 2: MCP Tool Protocol Integration

### Decision
Use Official MCP SDK for tool definitions, adapting existing TaskService methods.

### Rationale
- Constitution v2.0.0 mandates MCP tools for all data mutations
- Official SDK ensures protocol compliance
- Clean separation between agent and data layer

### Implementation Notes
MCP tools will wrap existing TaskService methods:

```python
@mcp_tool
def add_task(title: str, description: str = None) -> dict:
    """Create a new task."""
    # Calls TaskService.create_task internally
    pass

@mcp_tool
def list_tasks(filter: str = "all") -> dict:
    """List user's tasks."""
    # Calls TaskService.list_tasks internally
    pass
```

### Security Consideration
- User_id must be injected from JWT, not from agent
- Tools must not accept user_id as parameter
- User context passed via tool execution context

## Research Item 3: Conversation State Management

### Decision
Store conversation state in PostgreSQL using Conversation and Message tables.

### Rationale
- Constitution requires stateless backend
- Database persistence ensures data survives restarts
- Enables conversation history feature

### Schema Design
```sql
-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'tool')),
    content TEXT NOT NULL,
    tool_calls JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
```

### Context Window Management
- Load last 20 messages for agent context
- Older messages available but not sent to agent
- Prevents token limit issues

## Research Item 4: ChatKit Frontend Integration

### Decision
Use OpenAI ChatKit components for chat UI.

### Rationale
- Pre-built chat UI components
- Consistent with OpenAI ecosystem
- Reduces frontend development time

### Implementation Notes
```tsx
import { ChatContainer, MessageList, MessageInput } from '@openai/chatkit';

export default function ChatPage() {
  return (
    <ChatContainer>
      <MessageList messages={messages} />
      <MessageInput onSend={handleSend} />
    </ChatContainer>
  );
}
```

### Fallback Plan
If ChatKit is not available or complex to integrate:
- Build simple chat UI with existing components (Input, Button)
- Use standard message list pattern
- Focus on functionality over UI polish

## Research Item 5: Stateless Request Handling

### Decision
Reconstruct conversation context from database on each request.

### Rationale
- Constitution v2.0.0 requires stateless backend
- Enables horizontal scaling
- Ensures data consistency

### Implementation Pattern
```python
async def handle_chat(user_id: str, message: str, conversation_id: str = None):
    # 1. Get or create conversation
    conversation = await chat_service.get_or_create_conversation(user_id, conversation_id)

    # 2. Load recent messages (context)
    history = await chat_service.get_recent_messages(conversation.id, limit=20)

    # 3. Store user message
    await chat_service.add_message(conversation.id, "user", message)

    # 4. Run agent with context
    response = await agent_service.run(history + [message], user_id)

    # 5. Store assistant response
    await chat_service.add_message(conversation.id, "assistant", response.content, response.tool_calls)

    # 6. Return response
    return response
```

## Research Item 6: JWT Authentication for Chat

### Decision
Reuse existing JWT verification middleware from auth module.

### Rationale
- Consistent with existing authentication pattern
- No additional security implementation needed
- User isolation already enforced

### Implementation Notes
```python
from ..middleware.jwt_auth import verify_jwt

@router.post("/api/{user_id}/chat")
async def chat(
    user_id: str,
    request: ChatRequest,
    authenticated_user_id: str = Depends(verify_jwt)
):
    # Verify user_id matches authenticated user
    verify_user_match(user_id, authenticated_user_id)
    # Process chat...
```

## Dependency Verification

### Backend Dependencies
| Package | Version | Status |
|---------|---------|--------|
| openai-agents-sdk | Latest | To be added |
| mcp | Latest | To be added |
| fastapi | 0.109.0 | ✅ Installed |
| sqlmodel | 0.0.14 | ✅ Installed |
| PyJWT | 2.8.0 | ✅ Installed |

### Frontend Dependencies
| Package | Version | Status |
|---------|---------|--------|
| @openai/chatkit | Latest | To be verified/added |
| next | 15.x | ✅ Installed |
| tailwindcss | 3.x | ✅ Installed |

## Open Questions (Resolved)

1. **Q: How to handle agent timeouts?**
   A: Set 30-second timeout, return error message to user

2. **Q: How many messages in context window?**
   A: 20 messages (configurable via environment variable)

3. **Q: How to identify which conversation to continue?**
   A: Pass conversation_id in request, or create new if not provided

4. **Q: How to handle concurrent messages?**
   A: Process sequentially per conversation (optimistic locking)
