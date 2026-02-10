---
id: 003
title: Amend Constitution to v2.0.0 for Phase 3 AI Chatbot
stage: constitution
date: 2026-02-10
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: Khan Tech
command: /sp.constitution
labels: ["constitution", "phase-3", "ai-chatbot", "mcp", "architecture"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (constitutional document, no code tests)
---

## Prompt

(Phase 3)

Project: AI-Powered Todo Chatbot

Core principles:
- Agent-driven reasoning, tool-driven execution
- Stateless backend (no in-memory state)
- MCP tools as the only way to mutate data
- Strict user isolation and security

Key standards:
- All task actions must go through MCP tools
- Agents must not access the database directly
- Conversation state reconstructed from database per request
- JWT authentication required for all chat requests
Technology constraints:
- OpenAI Agents SDK
- Official MCP SDK
- FastAPI backend
- ChatKit frontend
- SQLModel + Neon PostgreSQL
- Better Auth (JWT)

Success criteria:
- Users manage tasks via natural language
- Conversations persist across requests
- Server remains stateless
- No cross-user data access

## Response snapshot

Updated constitution from v1.1.0 to v2.0.0 (MAJOR version bump) for Phase 3 AI-Powered Todo Chatbot. Added 4 new NON-NEGOTIABLE principles:

1. **Agent-Driven Architecture** - Agent reasons, MCP tools execute
2. **MCP Tool Protocol** - MCP tools are the ONLY way to mutate data
3. **Stateless Backend Design** - No in-memory state, database is source of truth
4. **Conversation Persistence** - State reconstructed from database per request

Modified existing principles to incorporate Phase 3 requirements (Security-First, Deterministic Behavior, Separation of Concerns, Auditability, Test-First Development). Added MCP tool specifications, conversation/message database schema, and updated technology stack to include OpenAI Agents SDK, Official MCP SDK, and ChatKit.

## Outcome

- ✅ Impact: Constitution fully updated for Phase 3 architectural requirements
- 🧪 Tests: N/A (constitutional document)
- 📁 Files: `.specify/memory/constitution.md` updated
- 🔁 Next prompts: `/sp.specify` for chatbot feature specification
- 🧠 Reflection: MAJOR version bump appropriate due to fundamental architectural changes (MCP-only mutations, agent-driven architecture)

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Verify constitution principles align with OpenAI Agents SDK patterns during spec creation
