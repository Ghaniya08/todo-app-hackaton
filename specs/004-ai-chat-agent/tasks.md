# Tasks: AI Chat Agent & Integration

**Input**: Design documents from `/specs/004-ai-chat-agent/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/chat-api.yaml, research.md, quickstart.md

**Tests**: Tests are OPTIONAL - manual testing for hackathon timeline (per constitution waiver).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, etc.)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`
- **Frontend**: `frontend/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add Phase III dependencies and environment configuration

- [x] T001 Add OpenAI Agents SDK and MCP SDK to backend/requirements.txt
- [x] T002 [P] Add OPENAI_API_KEY and chat config to backend/src/config.py
- [x] T003 [P] Create chat types in frontend/types/chat.ts
- [x] T004 [P] Add chat API methods to frontend/lib/api.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 [P] Create Conversation model in backend/src/models/conversation.py
- [x] T006 [P] Create Message model in backend/src/models/message.py
- [x] T007 Export models in backend/src/models/__init__.py (depends on T005, T006)
- [x] T008 Create ChatService in backend/src/services/chat_service.py
- [x] T009 Create chat request/response schemas in backend/src/schemas/chat_schemas.py
- [x] T010 Create AgentService in backend/src/services/agent_service.py
- [x] T011 [P] Create MCP tools wrapper in backend/src/mcp/__init__.py
- [x] T012 [P] Define MCP tool functions in backend/src/mcp/tools.py
- [x] T013 Create chat route in backend/src/routes/chat.py
- [x] T014 Register chat router in backend/src/main.py

**Checkpoint**: Foundation ready - backend can process chat messages

---

## Phase 3: User Story 1 - Send Chat Message and Receive Response (Priority: P1) 🎯 MVP

**Goal**: Users can type messages and receive AI responses (basic chat pipeline)

**Independent Test**: Type "Hello" in chat, verify response appears within 10 seconds

### Implementation for User Story 1

- [x] T015 [US1] Create ChatContainer component in frontend/components/chat/ChatContainer.tsx
- [x] T016 [US1] Create MessageList component in frontend/components/chat/MessageList.tsx
- [x] T017 [US1] Create ChatInput component in frontend/components/chat/ChatInput.tsx
- [x] T018 [US1] Create chat page in frontend/app/chat/page.tsx
- [x] T019 [US1] Add loading state and error handling to ChatContainer
- [x] T020 [US1] Add navigation link to chat page in frontend (header or dashboard)

**Checkpoint**: User Story 1 complete - basic chat flow works end-to-end

---

## Phase 4: User Story 2 - Create Task via Natural Language (Priority: P1)

**Goal**: Users can say "Add a task..." and have it created via MCP tool

**Independent Test**: Say "Add a task to buy groceries", verify task appears in task list

### Implementation for User Story 2

- [x] T021 [US2] Implement add_task MCP tool function in backend/src/mcp/tools.py
- [x] T022 [US2] Register add_task tool with agent in backend/src/services/agent_service.py
- [x] T023 [US2] Add task creation system prompt instructions to agent configuration
- [x] T024 [US2] Handle add_task tool response formatting in chat response

**Checkpoint**: User Story 2 complete - users can create tasks via chat

---

## Phase 5: User Story 3 - List Tasks via Natural Language (Priority: P1)

**Goal**: Users can say "Show my tasks" and see their task list

**Independent Test**: Say "Show my tasks", verify task list appears in chat response

### Implementation for User Story 3

- [x] T025 [US3] Implement list_tasks MCP tool function in backend/src/mcp/tools.py
- [x] T026 [US3] Register list_tasks tool with agent in backend/src/services/agent_service.py
- [x] T027 [US3] Add list formatting to agent response for task display
- [x] T028 [US3] Support filter parameter (all, pending, completed) in list_tasks tool

**Checkpoint**: User Story 3 complete - users can view tasks via chat

---

## Phase 6: User Story 4 - Complete Task via Natural Language (Priority: P2)

**Goal**: Users can say "Complete the groceries task" and have it marked done

**Independent Test**: Create task, say "Complete it", verify task is marked complete

### Implementation for User Story 4

- [x] T029 [US4] Implement complete_task MCP tool function in backend/src/mcp/tools.py
- [x] T030 [US4] Register complete_task tool with agent in backend/src/services/agent_service.py
- [x] T031 [US4] Add task matching logic (fuzzy match task by title) to complete_task tool
- [x] T032 [US4] Handle "task not found" scenario in agent response

**Checkpoint**: User Story 4 complete - users can complete tasks via chat

---

## Phase 7: User Story 5 - Delete Task via Natural Language (Priority: P2)

**Goal**: Users can say "Delete the groceries task" and have it removed

**Independent Test**: Create task, say "Delete it", verify task is removed

### Implementation for User Story 5

- [x] T033 [US5] Implement delete_task MCP tool function in backend/src/mcp/tools.py
- [x] T034 [US5] Register delete_task tool with agent in backend/src/services/agent_service.py
- [x] T035 [US5] Add task matching logic to delete_task tool
- [x] T036 [US5] Handle "task not found" scenario in agent response

**Checkpoint**: User Story 5 complete - users can delete tasks via chat

---

## Phase 8: User Story 6 - Conversation Persistence (Priority: P2)

**Goal**: Chat history persists across page refreshes and sessions

**Independent Test**: Send messages, refresh page, verify messages still visible

### Implementation for User Story 6

- [x] T037 [US6] Add conversation history loading to ChatService.get_or_create_conversation
- [x] T038 [US6] Load existing messages when chat page mounts in frontend
- [x] T039 [US6] Add GET /api/{user_id}/conversations endpoint for conversation list
- [x] T040 [US6] Add GET /api/{user_id}/conversations/{id}/messages endpoint for history
- [x] T041 [US6] Display conversation history in MessageList on page load
- [x] T042 [US6] Verify user isolation (cannot access other users' conversations)

**Checkpoint**: User Story 6 complete - conversations persist and resume

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T043 [P] Add structured logging for chat operations in backend
- [x] T044 [P] Add error boundaries and user-friendly error messages in frontend chat
- [x] T045 [P] Handle edge cases (empty messages, very long messages, timeouts)
- [x] T046 [P] Add agent timeout handling (30s) with retry suggestion
- [ ] T047 Validate against quickstart.md scenarios
- [ ] T048 Update README.md with Phase III chat feature documentation

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup (no dependencies)
    ↓
Phase 2: Foundational (depends on Phase 1)
    ↓
Phases 3-8: User Stories (all depend on Phase 2)
    ↓
Phase 9: Polish (depends on at least US1-US3)
```

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US1 (Chat) | Phase 2 | Foundational complete |
| US2 (Create Task) | US1 | Phase 3 checkpoint |
| US3 (List Tasks) | US1 | Phase 3 checkpoint |
| US4 (Complete) | US2, US3 | Phase 4 or 5 checkpoint |
| US5 (Delete) | US2, US3 | Phase 4 or 5 checkpoint |
| US6 (Persistence) | US1 | Phase 3 checkpoint |

### Within Each User Story

- Models before services
- Services before routes
- Backend before frontend integration
- Core implementation before edge cases

### Parallel Opportunities

**Phase 1 (Setup)**:
```
T002 [config.py] || T003 [chat.ts] || T004 [api.ts]
```

**Phase 2 (Foundational)**:
```
T005 [conversation.py] || T006 [message.py]
T011 [mcp/__init__.py] || T012 [mcp/tools.py]
```

**User Stories (After Phase 2)**:
```
US2, US3, US6 can run in parallel (all depend only on US1)
US4, US5 can run in parallel (both depend on US2 + US3)
```

---

## Parallel Example: Foundational Phase

```bash
# Launch model creation in parallel:
Task: T005 "Create Conversation model in backend/src/models/conversation.py"
Task: T006 "Create Message model in backend/src/models/message.py"

# Then (after T005, T006 complete):
Task: T007 "Export models in backend/src/models/__init__.py"
```

## Parallel Example: After Phase 3 (US1 complete)

```bash
# These can run in parallel:
Task: T021-T024 "User Story 2 - Create Task"
Task: T025-T028 "User Story 3 - List Tasks"
Task: T037-T042 "User Story 6 - Conversation Persistence"
```

---

## Implementation Strategy

### MVP First (Recommended for Hackathon)

1. ✅ Complete Phase 1: Setup
2. ✅ Complete Phase 2: Foundational
3. ✅ Complete Phase 3: User Story 1 (Basic Chat)
4. **STOP and DEMO**: Prove chat pipeline works
5. Continue to Phase 4-5: Add task creation and listing (core value)
6. Add Phase 6-7: Complete and delete (full CRUD)
7. Add Phase 8: Persistence (nice-to-have)
8. Phase 9: Polish as time permits

### Suggested MVP Scope

**Minimum Demo (US1 + US2 + US3)**:
- User can chat with AI
- User can create tasks via chat
- User can list tasks via chat
- **Total Tasks**: T001-T028 (28 tasks)

### Full Feature Scope

**Complete Feature (US1-US6)**:
- All above plus complete, delete, persistence
- **Total Tasks**: T001-T048 (48 tasks)

---

## Task Summary

| Phase | Story | Task Count | Priority |
|-------|-------|------------|----------|
| 1 | Setup | 4 | Required |
| 2 | Foundational | 10 | Required |
| 3 | US1 (Chat) | 6 | P1 - MVP |
| 4 | US2 (Create) | 4 | P1 - MVP |
| 5 | US3 (List) | 4 | P1 - MVP |
| 6 | US4 (Complete) | 4 | P2 |
| 7 | US5 (Delete) | 4 | P2 |
| 8 | US6 (Persistence) | 6 | P2 |
| 9 | Polish | 6 | Nice-to-have |
| **Total** | | **48** | |

---

## Notes

- [P] tasks can run in parallel (different files, no dependencies)
- [Story] label maps task to specific user story
- Constitution v2.0.0 waives TDD for hackathon timeline
- MCP tools wrap existing TaskService methods (assumes Phase II complete)
- Agent uses OpenAI Agents SDK with gpt-4o-mini for cost efficiency
- Commit after each task or logical group
- Stop at any checkpoint to validate and demo
