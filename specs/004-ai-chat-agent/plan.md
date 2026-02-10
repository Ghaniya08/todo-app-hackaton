# Implementation Plan: AI Chat Agent & Integration

**Branch**: `main` | **Date**: 2026-02-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-ai-chat-agent/spec.md`

## Summary

Implement an AI-powered chat system that enables users to manage their todo tasks through natural language conversation. The system integrates an OpenAI Agents SDK-powered backend with a ChatKit frontend, maintaining stateless operation while persisting conversation history in the database. The agent uses MCP tools for all task operations, ensuring clean separation between AI reasoning and data mutation.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, OpenAI Agents SDK, Official MCP SDK, SQLModel, ChatKit
**Storage**: Neon Serverless PostgreSQL (existing)
**Testing**: pytest (backend), manual integration testing
**Target Platform**: Web (Vercel frontend, Cloud backend)
**Project Type**: Web application (monorepo with backend/ and frontend/)
**Performance Goals**: <10s response time, 50 concurrent chat users
**Constraints**: Stateless backend, MCP-only data mutations, JWT authentication required
**Scale/Scope**: Phase III hackathon deliverable

## Constitution Check

*GATE: Must pass before implementation. Based on Constitution v2.0.0*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ PASS | Spec created at `specs/004-ai-chat-agent/spec.md` |
| II. Agent-Driven Architecture | ✅ PASS | Agent reasons, MCP tools execute |
| III. MCP Tool Protocol | ✅ PASS | All task ops through MCP tools (assumes tools exist) |
| IV. Stateless Backend Design | ✅ PASS | No in-memory state, DB reconstruction per request |
| V. Conversation Persistence | ✅ PASS | Conversation/Message tables defined |
| VI. Security-First Design | ✅ PASS | JWT verification on chat endpoint |
| VII. Deterministic Behavior | ✅ PASS | Consistent tool execution |
| VIII. Separation of Concerns | ✅ PASS | Frontend → Agent → MCP → Backend → DB |
| IX. Auditability | ✅ PASS | Messages and tool calls persisted |
| X. Test-First Development | ⚠️ WAIVED | Manual testing for hackathon timeline |

## Project Structure

### Documentation (this feature)

```text
specs/004-ai-chat-agent/
├── spec.md              # Feature specification (created)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── chat-api.yaml    # OpenAPI for chat endpoint
├── checklists/          # Quality checklists
│   └── requirements.md  # Spec validation checklist
└── tasks.md             # Phase 2 output (via /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── task.py          # Existing Task model
│   │   ├── user.py          # Existing User model
│   │   ├── conversation.py  # NEW: Conversation model
│   │   └── message.py       # NEW: Message model
│   ├── routes/
│   │   ├── tasks.py         # Existing task routes
│   │   ├── auth.py          # Existing auth routes
│   │   └── chat.py          # NEW: Chat endpoint
│   ├── services/
│   │   ├── task_service.py  # Existing task service
│   │   ├── chat_service.py  # NEW: Chat/conversation service
│   │   └── agent_service.py # NEW: Agent configuration and execution
│   ├── mcp/                  # NEW: MCP tool definitions
│   │   ├── __init__.py
│   │   └── tools.py         # MCP tool implementations (assumes exist)
│   ├── middleware/
│   │   └── jwt_auth.py      # Existing JWT verification
│   ├── db.py                # Existing database config
│   ├── config.py            # Existing app config
│   └── main.py              # App entry point
└── tests/

frontend/
├── app/
│   ├── dashboard/
│   │   └── page.tsx         # Existing dashboard
│   ├── chat/                # NEW: Chat page
│   │   └── page.tsx         # ChatKit interface
│   └── layout.tsx           # Root layout
├── components/
│   ├── tasks/               # Existing task components
│   ├── chat/                # NEW: Chat components
│   │   ├── ChatContainer.tsx
│   │   ├── MessageList.tsx
│   │   └── ChatInput.tsx
│   └── ui/                  # Existing UI components
├── lib/
│   ├── api.ts               # Existing API client (extend for chat)
│   └── auth.tsx             # Existing auth context
└── types/
    ├── task.ts              # Existing task types
    └── chat.ts              # NEW: Chat types
```

**Structure Decision**: Extends existing web application monorepo structure. New files added to existing directories following established patterns.

## Architecture Overview

### Request Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   ChatKit    │────▶│  Chat API    │────▶│ OpenAI Agent │────▶│  MCP Tools   │
│   Frontend   │     │  (FastAPI)   │     │    (SDK)     │     │  (Backend)   │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │                    │
       │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼
  User Input          JWT Verify           Intent Parse         Task CRUD
  + Display           + Load History       + Tool Select        + DB Access
```

### Key Components

1. **ChatKit Frontend** (`frontend/app/chat/`)
   - Chat UI with message display
   - Input field for user messages
   - Loading states and error handling
   - JWT token attached to requests

2. **Chat API Endpoint** (`backend/src/routes/chat.py`)
   - POST `/api/{user_id}/chat` - Send message, get response
   - JWT verification (reuse existing middleware)
   - Load conversation history from DB
   - Invoke agent, store response
   - Return formatted response

3. **Agent Service** (`backend/src/services/agent_service.py`)
   - Configure OpenAI Agent with MCP tools
   - Build conversation context from DB messages
   - Run agent with user message
   - Parse and return agent response

4. **Chat Service** (`backend/src/services/chat_service.py`)
   - Create/get conversations
   - Store messages (user, assistant, tool)
   - Load conversation history
   - Manage conversation context window

5. **Conversation/Message Models** (`backend/src/models/`)
   - Conversation: user_id, title, timestamps
   - Message: conversation_id, role, content, tool_calls, timestamp

## Dependencies

### Backend Dependencies (add to requirements.txt)

```
# AI Agent Dependencies (Phase III)
openai-agents-sdk>=0.1.0    # OpenAI Agents SDK
mcp>=0.1.0                  # Official MCP SDK
```

### Existing Dependencies (already installed)
- fastapi==0.109.0
- sqlmodel==0.0.14
- PyJWT==2.8.0
- psycopg[binary]==3.2.3

### Frontend Dependencies (add to package.json)

Note: ChatKit is the OpenAI chat UI framework. Check npm for exact package name.

## Implementation Phases

### Phase 1: Backend Foundation
1. Create Conversation and Message models
2. Add migrations for new tables
3. Create chat_service for conversation management
4. Create chat route with JWT auth

### Phase 2: Agent Integration
5. Configure OpenAI Agent with system prompt
6. Create agent_service for agent execution
7. Connect agent to MCP tools (assumes tools exist)
8. Implement conversation context loading

### Phase 3: Frontend Integration
9. Create chat page with ChatKit
10. Create API client methods for chat
11. Implement message display and input
12. Add loading states and error handling

### Phase 4: Polish
13. Test end-to-end flow
14. Handle edge cases (empty messages, timeouts)
15. Update documentation

## Exit Criteria

- [ ] Stateless chat endpoint works (POST `/api/{user_id}/chat`)
- [ ] Conversations persist and resume across requests
- [ ] Agent responses integrate with frontend UI
- [ ] User context enforced on every request (JWT + user_id match)
- [ ] No cross-user data access possible
- [ ] Server restart does not lose conversation data

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| OpenAI API latency | Set reasonable timeout (30s), show loading state |
| MCP tools not implemented | Spec assumes tools exist; verify or create separately |
| Token limits | Limit conversation context to 20 recent messages |
| JWT secret mismatch | Reuse existing JWT verification middleware |

## Out of Scope (Per Spec)

- MCP tool implementations (assumes exist)
- Advanced UI customization
- Streaming/real-time responses
- Voice input/output
- File attachments
