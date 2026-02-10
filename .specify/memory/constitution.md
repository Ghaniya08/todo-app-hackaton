<!--
Sync Impact Report:
Version: 1.1.0 → 2.0.0 (MAJOR - Architectural Evolution to AI-Powered Chatbot)
Modified Principles:
  - Spec-Driven Development: Unchanged (still NON-NEGOTIABLE)
  - Security-First Design: Expanded with "MCP tool-level user isolation"
  - Deterministic Behavior: Enhanced with "agent reasoning reproducibility"
  - Separation of Concerns: Restructured to include Agent/MCP/Backend layers
  - Auditability: Added "conversation history persistence"
  - Test-First Development: Added "MCP tool contract tests"
  - API-First Design: Evolved to "MCP-First Design"
Added Sections:
  - Principle XI: Agent-Driven Architecture (NEW - Core Phase 3 principle)
  - Principle XII: MCP Tool Protocol (NEW - Data mutation constraint)
  - Principle XIII: Stateless Backend Design (NEW - No in-memory state)
  - Principle XIV: Conversation Persistence (NEW - State reconstruction)
  - Technology Stack: OpenAI Agents SDK, Official MCP SDK, ChatKit frontend
Removed Sections: None (all Phase II principles preserved and extended)
Templates Status:
  ✅ spec-template.md - Already aligned with user story prioritization
  ✅ tasks-template.md - Already aligned with independent testable tasks
  ✅ plan-template.md - Already aligned with constitution checks
Follow-up TODOs: None
Rationale: Phase 3 introduces AI chatbot capabilities requiring fundamental architectural principles around agent-driven reasoning, MCP tool protocol, and stateless conversation management. This is a MAJOR version bump as it introduces non-backward-compatible constraints (MCP-only mutations, agent-only DB access).
-->

# AI-Powered Todo Chatbot Constitution

**Project Phase**: Phase 3 - AI-Powered Todo Chatbot
**Evolution**: Phase II Full-Stack → Phase III AI Chatbot

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

**No code without specification. All implementation MUST be derived strictly from specs.**

Every feature MUST follow the SDD lifecycle:

- **Specify** → Define WHAT (requirements, user stories, acceptance criteria)
- **Plan** → Define HOW (architecture, components, interfaces)
- **Tasks** → Define BREAKDOWN (atomic, testable work units)
- **Implement** → Write code ONLY for approved tasks via Claude Code

**Rationale**: Prevents "vibe coding" and ensures alignment between requirements and implementation. All AI agents must verify task authorization before writing code. Eliminates manual coding drift and ensures all code is traceable to specifications.

**Enforcement**:
- **No manual coding**: All code MUST be generated via Claude Code using approved specs and plans
- Every code file MUST contain comments linking to Task ID and Spec sections
- No architectural changes without updating plan.md
- No feature additions without updating spec.md
- Constitution supersedes all other practices
- Specs must be independently reviewable before implementation begins

### II. Agent-Driven Architecture (NON-NEGOTIABLE)

**Agent-driven reasoning, tool-driven execution. The AI agent reasons; MCP tools execute.**

The chatbot architecture MUST follow strict separation:

- **Agent Layer**: OpenAI Agents SDK handles natural language understanding, intent detection, and reasoning
- **Tool Layer**: MCP tools are the ONLY interface for data operations
- **Backend Layer**: FastAPI provides MCP tool implementations and database access

**Rationale**: Ensures clean separation between AI reasoning and data mutation. Agents focus on understanding user intent; tools focus on executing actions safely. This prevents accidental data corruption and enables auditability.

**Enforcement**:
- Agents MUST NOT access the database directly
- Agents MUST NOT call HTTP endpoints directly (only MCP tools)
- All user-facing actions MUST route through agent reasoning first
- Tool selection and parameters MUST be determined by agent logic
- Agent responses MUST be generated based on tool results

### III. MCP Tool Protocol (NON-NEGOTIABLE)

**MCP tools are the ONLY way to mutate data. No exceptions.**

All task operations MUST go through MCP tools:

| Tool | Purpose | Parameters |
|------|---------|------------|
| `add_task` | Create new task | title, description (optional) |
| `list_tasks` | Retrieve tasks | filter (optional: all, pending, completed) |
| `complete_task` | Mark task complete | task_id |
| `delete_task` | Remove task | task_id |
| `update_task` | Modify task | task_id, title (optional), description (optional) |

**Rationale**: Centralizes all data mutations through a controlled interface. Enables consistent validation, logging, and authorization. Prevents direct database manipulation that could bypass security.

**Enforcement**:
- Backend MUST NOT expose REST endpoints for task CRUD (Phase III)
- All data changes MUST be logged through MCP tool execution
- Tool implementations MUST verify JWT and user ownership
- Tool responses MUST be structured for agent consumption
- Failed tool calls MUST return actionable error messages

### IV. Stateless Backend Design (NON-NEGOTIABLE)

**No in-memory state. Server MUST be stateless.**

The backend MUST NOT maintain:
- Conversation history in memory
- User session state in memory
- Agent context between requests
- Any mutable state outside the database

**Rationale**: Enables horizontal scaling, simplifies deployment, and ensures reliability. State stored only in the database guarantees persistence and consistency across server restarts and multiple instances.

**Enforcement**:
- No global variables storing user/conversation state
- No caching of conversation history in memory
- Each request MUST reconstruct context from database
- Server restart MUST NOT lose any user data
- Load balancer compatibility required (any instance can handle any request)

### V. Conversation Persistence (NON-NEGOTIABLE)

**Conversation state reconstructed from database per request.**

Conversation management requirements:

- **Conversation Table**: Stores chat sessions with user_id and metadata
- **Message Table**: Stores individual messages with role, content, and timestamps
- **Context Reconstruction**: Each request loads recent messages from database
- **Message Limit**: Context window managed by limiting retrieved messages

**Rationale**: Ensures conversations persist across requests, server restarts, and even device switches. Users can continue conversations seamlessly. Enables conversation history features.

**Database Schema**:
```sql
conversations (
  id: UUID PRIMARY KEY,
  user_id: STRING NOT NULL,
  title: STRING,
  created_at: TIMESTAMP,
  updated_at: TIMESTAMP
)

messages (
  id: UUID PRIMARY KEY,
  conversation_id: UUID REFERENCES conversations(id),
  role: STRING NOT NULL (user|assistant|tool),
  content: TEXT NOT NULL,
  tool_calls: JSONB,
  created_at: TIMESTAMP
)
```

### VI. Security-First Design (MANDATORY)

**Authentication, authorization, and user isolation MUST be enforced at all layers.**

- Better Auth with JWT tokens for session management
- All MCP tool calls require valid JWT
- User data isolation: users only access their own resources
- Shared secret between frontend and backend for JWT verification
- No secrets in code: use environment variables
- **Stateless authentication**: JWT-based auth only, no server-side sessions
- **MCP tool-level isolation**: Every tool call MUST verify user ownership

**Rationale**: Protects user data and prevents unauthorized access. Security is not optional. Stateless design enables horizontal scaling and simplifies deployment.

**Implementation**:
- ChatKit: Attach JWT to every chat request header
- Backend: Verify JWT before processing any MCP tool call
- MCP Tools: Filter all queries by authenticated user_id
- Conversations: MUST be scoped to authenticated user
- **Error handling**: All authentication failures return clear HTTP status codes

### VII. Deterministic Behavior (MANDATORY)

**Same input MUST produce consistent, predictable output.**

- Tool execution must be reproducible given same parameters
- Error handling must be consistent
- Agent responses should follow predictable patterns
- No hidden side effects in tool execution

**Rationale**: Ensures reliability, simplifies debugging, and enables confident deployment. Deterministic systems are easier to test, reason about, and maintain.

**Enforcement**:
- MCP tools return consistent responses for identical inputs
- Database queries produce consistent results (proper ordering, filtering)
- Error messages are standardized and predictable
- Agent prompts should produce similar reasoning for similar inputs
- Configuration via environment variables only

### VIII. Separation of Concerns (MANDATORY)

**Agent, MCP Tools, Backend, and Frontend MUST be clearly isolated.**

Layer responsibilities:

| Layer | Responsibility | Technology |
|-------|----------------|------------|
| **Frontend** | Chat UI, user input, response display | ChatKit |
| **Agent** | Intent understanding, reasoning, tool selection | OpenAI Agents SDK |
| **MCP Tools** | Tool definitions, parameter schemas | Official MCP SDK |
| **Backend** | Tool implementation, database access, JWT verification | FastAPI + SQLModel |
| **Database** | Data persistence | Neon PostgreSQL |

**Rationale**: Enables independent development, testing, and deployment. Reduces coupling and improves maintainability. Each layer can evolve independently.

**Architectural Constraints**:
- Frontend communicates with Agent only
- Agent communicates with MCP Tools only
- MCP Tools communicate with Backend only
- Backend communicates with Database only
- No layer skipping allowed

### IX. Auditability (MANDATORY)

**Every decision and action MUST be traceable.**

- All code references Task IDs and Spec sections
- Architectural decisions documented in ADRs
- Prompt History Records (PHRs) for all significant work
- **Conversation history**: All messages persisted and retrievable
- **Tool call logging**: Every MCP tool invocation recorded
- Clear commit messages with task references

**Rationale**: Enables understanding of why decisions were made, facilitates debugging, and supports compliance. Critical for hackathon evaluation.

**Implementation**:
- Code comments: `# [Task]: T-001 | [From]: specs/features/chatbot.md §2.1`
- PHRs created for all implementation work
- ADRs suggested for architectural decisions
- Messages stored with conversation_id for history
- Tool calls logged with parameters and results

### X. Test-First Development (MANDATORY)

**TDD cycle strictly enforced** for all user-facing functionality:

1. Write tests that capture acceptance criteria
2. Verify tests FAIL (red)
3. Implement minimum code to pass (green)
4. Refactor while keeping tests green
5. Commit with test evidence

**Rationale**: Ensures code meets requirements and prevents regression.

**Scope for Phase 3**:
- Contract tests for MCP tools
- Integration tests for conversation flows
- Agent behavior tests (mocked tool responses)
- End-to-end tests for complete user journeys

### XI. Independent User Stories

**Every user story MUST be independently testable and deployable.**

- Prioritize stories (P1, P2, P3) by business value
- Each story delivers standalone value (viable MVP slice)
- Stories can be developed, tested, and deployed in isolation
- P1 stories are blocking; P2/P3 are incremental enhancements

**Rationale**: Enables iterative delivery, parallel development, and early validation.

### XII. MCP-First Design

**All chatbot functionality exposed via MCP tools with strict protocol adherence.**

- Clear tool contracts defined before implementation
- Input/output schemas documented in tool definitions
- Consistent error handling across all tools
- JWT-based authentication for all tool calls

**MCP Tools Specification**:

```python
# add_task
Input: {"title": str, "description": str | None}
Output: {"task_id": int, "title": str, "created_at": str}

# list_tasks
Input: {"filter": "all" | "pending" | "completed" | None}
Output: {"tasks": [{"id": int, "title": str, "completed": bool, ...}]}

# complete_task
Input: {"task_id": int}
Output: {"task_id": int, "completed": true, "completed_at": str}

# delete_task
Input: {"task_id": int}
Output: {"success": true, "deleted_task_id": int}

# update_task
Input: {"task_id": int, "title": str | None, "description": str | None}
Output: {"task_id": int, "title": str, "description": str, "updated_at": str}
```

### XIII. Monorepo Organization

**Single repository with clear separation of concerns.**

```
/
├── .specify/           # Spec-Kit Plus configuration and templates
├── specs/              # Feature specifications
├── frontend/           # Next.js + ChatKit application
├── backend/            # FastAPI + MCP Tools application
│   ├── src/
│   │   ├── models/     # SQLModel database models
│   │   ├── mcp/        # MCP tool implementations
│   │   ├── services/   # Business logic
│   │   └── main.py     # FastAPI entry point
│   └── tests/
├── CLAUDE.md           # AI agent instructions
└── README.md           # Project documentation
```

**Rationale**: Simplifies cross-cutting changes, maintains single context for AI agents.

### XIV. Observability and Debugging

**All operations MUST be traceable and debuggable.**

- Structured logging for all MCP tool calls
- Conversation flow logging
- Agent decision logging (reasoning steps)
- Clear error messages (no stack traces to users)
- Request/response logging in development

**Rationale**: Enables rapid debugging during development and hackathon evaluation.

## Technology Stack Constraints

### Frontend Requirements (ChatKit)

- **Framework**: Next.js 16+ with App Router (MANDATORY)
- **Chat UI**: OpenAI ChatKit (MANDATORY)
- **Language**: TypeScript (MANDATORY)
- **Styling**: Tailwind CSS (MANDATORY)
- **Authentication**: Better Auth with JWT (MANDATORY)
- **Patterns**:
  - Server components by default
  - Client components for chat interface
  - JWT attached to all chat requests

### Backend Requirements (FastAPI + MCP)

- **Framework**: Python FastAPI (MANDATORY)
- **AI Agent**: OpenAI Agents SDK (MANDATORY)
- **Tool Protocol**: Official MCP SDK (MANDATORY)
- **ORM**: SQLModel (MANDATORY)
- **Database**: Neon Serverless PostgreSQL (MANDATORY)
- **Authentication**: JWT verification (MANDATORY)
- **Patterns**:
  - MCP tools as primary interface
  - Stateless request handling
  - Conversation reconstruction per request
  - Async/await for all operations

### Development Tools

- **Spec Management**: Spec-Kit Plus (MANDATORY)
- **AI Assistant**: Claude Code (MANDATORY)
- **Version Control**: Git with meaningful commit messages
- **Environment**: WSL 2 for Windows users

## Development Workflow

### Feature Development Cycle

1. **Specify**: Create spec.md with user stories and acceptance criteria
2. **Plan**: Generate plan.md with architecture and technical approach
3. **Tasks**: Break down into tasks.md with clear dependencies
4. **Implement**: Execute tasks via Claude Code (delegate to specialist agents)
5. **Validate**: Test each user story independently
6. **Document**: Create PHR for learning

### Agent Delegation

- Frontend/ChatKit → `nextjs-ui-architect`
- Backend/MCP Tools → `fastapi-backend-dev`
- Database Schema → `neon-db-architect`
- Authentication → `auth-security-specialist`

### Code Review Requirements

- All code MUST reference Task ID in comments
- All MCP tools MUST have contract tests
- All conversations MUST be scoped to authenticated user
- No hardcoded secrets or credentials
- No direct database access from agent layer

### Commit Standards

- Atomic commits per task or logical group
- Commit messages reference Task ID
- Include co-authorship: `Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>`
- Never commit .env files or credentials

## Quality Gates

### Before Implementation

- [ ] Spec.md approved with clear acceptance criteria
- [ ] Plan.md reviewed with MCP tool definitions
- [ ] Tasks.md created with independent, testable tasks
- [ ] Constitution compliance verified

### Before Deployment

- [ ] All MCP tools tested with contract tests
- [ ] Conversation persistence verified
- [ ] User isolation tested (no cross-user data access)
- [ ] JWT authentication working end-to-end
- [ ] Stateless behavior verified (server restart test)
- [ ] Demo video prepared (max 90 seconds)

### Success Criteria (Phase 3)

- [ ] Users can manage tasks via natural language
- [ ] Conversations persist across requests
- [ ] Server remains stateless
- [ ] No cross-user data access possible
- [ ] All MCP tools functional
- [ ] ChatKit UI deployed and working

## Non-Functional Requirements

### Performance

- MCP tool response time: <500ms
- Conversation load time: <1s
- Agent reasoning time: Acceptable for chat UX

### Scalability

- Stateless backend (horizontal scaling ready)
- Connection pooling for database
- JWT-based auth (no server-side sessions)
- Conversation context limited to prevent memory issues

### Maintainability

- Clear separation: Agent / MCP / Backend / Database
- Consistent naming conventions
- Self-documenting tool definitions
- Comprehensive error handling

## Governance

### Amendment Process

1. Identify need for constitutional change
2. Document rationale and impact
3. Update constitution.md with version bump
4. Propagate changes to dependent templates
5. Create ADR for significant architectural decisions

### Version Semantics

- **MAJOR**: Backward incompatible changes (e.g., removing principles, new mandatory constraints)
- **MINOR**: New principles or expanded guidance
- **PATCH**: Clarifications, typos, non-semantic refinements

### Compliance

- All PRs/reviews MUST verify constitution compliance
- MCP tool changes MUST be justified in plan.md
- Use CLAUDE.md for runtime development guidance
- PHRs MUST be created for all significant work

### Conflict Resolution

When conflicts arise between artifacts, the hierarchy is:

1. **Constitution** (this file) - Highest authority
2. **Spec.md** - What to build
3. **Plan.md** - How to build
4. **Tasks.md** - Breakdown of work

**Version**: 2.0.0 | **Ratified**: 2026-02-07 | **Last Amended**: 2026-02-10
