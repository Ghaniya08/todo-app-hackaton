# Quickstart: AI Chat Agent & Integration

**Feature**: 004-ai-chat-agent
**Date**: 2026-02-10

## Prerequisites

Before starting, ensure you have:

- [ ] Phase II backend running (FastAPI with task endpoints)
- [ ] Phase II frontend running (Next.js with authentication)
- [ ] Neon PostgreSQL database configured
<!-- - [ ] OpenAI API key (for agent) -->
- [ ] Python 3.13+ installed
- [ ] Node.js 20+ installed

## Environment Variables

### Backend (.env)

```bash
# Existing variables
DATABASE_URL=postgresql://user:pass@host/db
BETTER_AUTH_SECRET=your-jwt-secret

# New variables for Phase III
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4o-mini  # Cost-effective for hackathon
CHAT_CONTEXT_LIMIT=20     # Max messages in agent context
CHAT_TIMEOUT_SECONDS=30   # Agent response timeout
```

### Frontend (.env.local)

```bash
# Existing variable
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Installation Steps

### 1. Backend Dependencies

```bash
cd backend

# Add new dependencies
pip install openai-agents-sdk mcp

# Or update requirements.txt and install
pip install -r requirements.txt
```

### 2. Database Migration

The new tables will be created automatically on startup via SQLModel.

Alternatively, run manual migration:

```sql
-- Connect to your Neon database and run:
-- (See data-model.md for full migration script)

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(200),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    tool_calls JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
```

### 3. Frontend Dependencies (if using ChatKit)

```bash
cd frontend

# Add ChatKit (verify package name)
npm install @openai/chatkit

# Or use existing components for simpler implementation
```

## Running the Application

### Start Backend

```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend

```bash
cd frontend
npm run dev
```

## Testing the Chat Endpoint

### 1. Get JWT Token

First, sign in to get a JWT token:

```bash
curl -X POST http://localhost:8000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

Save the token from the response.

### 2. Send Chat Message (New Conversation)

```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {your-jwt-token}" \
  -d '{"message": "Hello, what can you help me with?"}'
```

Expected response:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": {
    "role": "assistant",
    "content": "Hello! I'm your todo assistant..."
  },
  "tool_calls": null
}
```

### 3. Create Task via Chat

```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {your-jwt-token}" \
  -d '{
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Add a task to buy groceries"
  }'
```

Expected response:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": {
    "role": "assistant",
    "content": "I've created a task 'buy groceries' for you."
  },
  "tool_calls": [
    {
      "tool": "add_task",
      "input": {"title": "buy groceries"},
      "output": {"task_id": 42, "title": "buy groceries"}
    }
  ]
}
```

### 4. List Tasks via Chat

```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {your-jwt-token}" \
  -d '{
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Show my tasks"
  }'
```

## Verification Checklist

After implementation, verify:

- [ ] Chat endpoint responds to messages
- [ ] Conversations are created and persisted
- [ ] Messages are stored in database
- [ ] Agent correctly identifies task intents
- [ ] MCP tools are called for task operations
- [ ] User isolation enforced (can't access other users' chats)
- [ ] JWT authentication working
- [ ] Frontend displays messages correctly
- [ ] Conversation history loads on page refresh

## Troubleshooting

### "Missing authentication token"

- Ensure JWT token is included in Authorization header
- Check token hasn't expired
- Verify BETTER_AUTH_SECRET matches frontend

### "Agent timeout"

- Check OPENAI_API_KEY is valid
- Increase CHAT_TIMEOUT_SECONDS if needed
- Check network connectivity to OpenAI

### "Conversation not found"

- Verify conversation_id is valid UUID
- Check conversation belongs to authenticated user
- Ensure database connection is working

### "Tool not found"

- Verify MCP tools are properly registered
- Check tool names match expected values
- Review agent configuration

## Next Steps

After basic chat is working:

1. Add conversation list to frontend sidebar
2. Implement conversation history loading
3. Add error handling and retry logic
4. Polish UI with loading states
5. Test edge cases (empty messages, long messages)
