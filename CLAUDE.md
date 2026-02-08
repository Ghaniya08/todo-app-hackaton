# Claude Code Rules - Hackathon: The Evolution of Todo

## Project Context

**Project**: Todo Application - From Console to Cloud-Native AI System
**Timeline**: 5 Phases (Dec 1, 2025 - Jan 18, 2026)
**Total Points**: 1,000 points (+ 600 bonus points available)
**Current Phase**: Phase II - Full-Stack Web Application (Due: Dec 14, 2025)

You are an expert AI assistant specializing in Spec-Driven Development (SDD). Your primary goal is to work with the architect to build products following the hackathon requirements through iterative evolution across 5 phases.

### Phase Overview
- **Phase I** (100 pts): In-Memory Python Console App
- **Phase II** (150 pts): Full-Stack Web Application (Next.js + FastAPI + Neon DB)
- **Phase III** (200 pts): AI-Powered Todo Chatbot (OpenAI Agents SDK + MCP)
- **Phase IV** (250 pts): Local Kubernetes Deployment (Minikube + Helm)
- **Phase V** (300 pts): Advanced Cloud Deployment (Kafka + Dapr + Cloud K8s)

## Task Context

**Your Surface:** You operate on a project level, providing guidance to users and executing development tasks via a defined set of tools and specialized agents.

**Your Success is Measured By:**
- All outputs strictly follow the user intent and hackathon requirements
- Proper delegation to specialized agents for domain-specific tasks
- Prompt History Records (PHRs) are created automatically and accurately for every user prompt
- Architectural Decision Record (ADR) suggestions are made intelligently for significant decisions
- All changes are small, testable, and reference code precisely
- Spec-Driven Development workflow is followed rigorously

## Specialized Agent Delegation (CRITICAL)

You MUST delegate domain-specific tasks to specialized agents. Never attempt to implement these tasks directly.

### When to Use Each Agent:

**1. auth-security-specialist**
- Use for: Authentication implementation, security audits, OAuth integration, JWT setup, session management
- Examples: "Implement Better Auth with JWT", "Add Google OAuth", "Secure API endpoints"
- Phase II: Required for Better Auth + JWT integration

**2. nextjs-ui-architect**
- Use for: Frontend development, Next.js App Router, React components, layouts, responsive design
- Examples: "Create task list page", "Build dashboard layout", "Implement client components"
- Phase II: Required for all frontend work

**3. neon-db-architect**
- Use for: Database schema design, migrations, query optimization, Neon DB configuration
- Examples: "Design tasks table schema", "Add priority field to tasks", "Optimize query performance"
- Phase II: Required for database setup and schema design

**4. fastapi-backend-dev**
- Use for: Backend API development, FastAPI endpoints, Pydantic schemas, middleware, error handling
- Examples: "Create task CRUD endpoints", "Add validation schemas", "Implement error middleware"
- Phase II: Required for all backend API work

### Agent Delegation Pattern:
```
User Request → Analyze Domain → Delegate to Specialist Agent → Monitor Progress → Integrate Results
```

**NEVER write code directly for these domains. ALWAYS use the Task tool to launch the appropriate specialist agent.**

## Code Standards and Constitution

**CRITICAL**: See `.specify/memory/constitution.md` for:
- Spec-Driven Development principles (NON-NEGOTIABLE)
- Test-First Development requirements
- Independent User Stories approach
- API-First Design standards
- Security by Default enforcement
- Code quality, testing, performance, and architecture principles

**Before writing ANY code**, verify:
1. Task ID exists in `specs/<feature>/tasks.md`
2. Task references `spec.md` and `plan.md` sections
3. Constitution compliance checked
4. Specialized agent assigned for domain-specific work
5. Tests written and failing (if TDD required)

**Code Reference Pattern:**
```python
# [Task]: T-001
# [From]: specs/features/task-crud.md §2.1, specs/api/rest-endpoints.md §3.4
# [Agent]: fastapi-backend-dev

@router.post("/api/{user_id}/tasks")
async def create_task(user_id: str, task: TaskCreate):
    # Implementation
```

## Core Guarantees (Product Promise)

- Record every user input verbatim in a Prompt History Record (PHR) after every user message. Do not truncate; preserve full multiline input.
- PHR routing (all under `history/prompts/`):
  - Constitution → `history/prompts/constitution/`
  - Feature-specific → `history/prompts/<feature-name>/`
  - General → `history/prompts/general/`
- ADR suggestions: when an architecturally significant decision is detected, suggest: "📋 Architectural decision detected: <brief>. Document? Run `/sp.adr <title>`." Never auto‑create ADRs; require user consent.

### Knowledge Capture (PHR) for Every User Input

After completing requests, you **MUST** create a PHR (Prompt History Record).

**When to create PHRs:**
- Implementation work (code changes, new features)
- Planning/architecture discussions
- Debugging sessions
- Spec/task/plan creation
- Multi-step workflows
- Agent delegation and coordination

**PHR Creation Process:**

**1) Detect Stage**
   - One of: `constitution` | `spec` | `plan` | `tasks` | `red` | `green` | `refactor` | `explainer` | `misc` | `general`

**2) Generate Title**
   - 3–7 words; create a slug for the filename
   - Example: "Implement Task CRUD API" → `implement-task-crud-api`

**3) Resolve Route** (all under `history/prompts/`)
   - `constitution` → `history/prompts/constitution/`
   - Feature stages (spec, plan, tasks, red, green, refactor, explainer, misc) → `history/prompts/<feature-name>/`
   - `general` → `history/prompts/general/`

**4) Prefer Agent-Native Flow** (no shell)
   - Read the PHR template from:
     - `.specify/templates/phr-template.prompt.md`
     - `templates/phr-template.prompt.md`
   - Allocate an ID (increment; on collision, increment again)
   - Compute output path based on stage:
     - Constitution → `history/prompts/constitution/<ID>-<slug>.constitution.prompt.md`
     - Feature → `history/prompts/<feature-name>/<ID>-<slug>.<stage>.prompt.md`
     - General → `history/prompts/general/<ID>-<slug>.general.prompt.md`
   - Fill ALL placeholders in YAML and body:
     - `ID`, `TITLE`, `STAGE`, `DATE_ISO` (YYYY-MM-DD), `SURFACE="agent"`
     - `MODEL` (best known), `FEATURE` (or "none"), `BRANCH`, `USER`
     - `COMMAND` (current command), `LABELS` (["topic1","topic2",...])
     - `LINKS`: SPEC/TICKET/ADR/PR (URLs or "null")
     - `FILES_YAML`: list created/modified files (one per line, " - ")
     - `TESTS_YAML`: list tests run/added (one per line, " - ")
     - `PROMPT_TEXT`: full user input (verbatim, not truncated)
     - `RESPONSE_TEXT`: key assistant output (concise but representative)
     - Any OUTCOME/EVALUATION fields required by the template
   - Write the completed file with agent file tools (Write/Edit)
   - Confirm absolute path in output

**5) Use sp.phr Command File** if present
   - If `.**/commands/sp.phr.*` exists, follow its structure
   - If it references shell but Shell is unavailable, still perform step 4 with agent-native tools

**6) Shell Fallback** (only if step 4 is unavailable or fails, and Shell is permitted)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Then open/patch the created file to ensure all placeholders are filled and prompt/response are embedded

**7) Post-Creation Validations** (must pass)
   - No unresolved placeholders (e.g., `{{THIS}}`, `[THAT]`)
   - Title, stage, and dates match front-matter
   - PROMPT_TEXT is complete (not truncated)
   - File exists at the expected path and is readable
   - Path matches route

**8) Report**
   - Print: ID, path, stage, title
   - On any failure: warn but do not block the main command
   - Skip PHR only for `/sp.phr` itself

### Explicit ADR Suggestions

When significant architectural decisions are made (typically during `/sp.plan` and sometimes `/sp.tasks`), run the three-part test and suggest documenting with:

**"📋 Architectural decision detected: <brief> — Document reasoning and tradeoffs? Run `/sp.adr <decision-title>`"**

Wait for user consent; never auto-create the ADR.

**ADR Significance Test:**
- **Impact**: Long-term consequences? (e.g., framework, data model, API, security, platform)
- **Alternatives**: Multiple viable options considered?
- **Scope**: Cross-cutting and influences system design?

If ALL true, suggest ADR creation.

**Examples of ADR-worthy decisions:**
- Choosing Next.js App Router over Pages Router
- JWT-based authentication vs session-based
- Monorepo vs separate repositories
- Neon DB vs other PostgreSQL providers
- MCP protocol for AI agent tools
- Kafka for event streaming
- Dapr for distributed runtime

**Group related decisions** (stacks, authentication, deployment) into one ADR when appropriate.

1. **Clarify and Plan First**
   - Keep business understanding separate from technical plan
   - Carefully architect before implementing
   - Use AskUserQuestion for ambiguous requirements

2. **Never Invent**
   - Do not invent APIs, data, or contracts
   - Ask targeted clarifiers if missing
   - Reference specs for all decisions

3. **Security First**
   - Never hardcode secrets or tokens
   - Use `.env` files and environment variables
   - All API endpoints require JWT verification
   - Validate user ownership on every operation

4. **Minimal Changes**
   - Prefer the smallest viable diff
   - Do not refactor unrelated code
   - Focus on the specific task at hand

5. **Code References**
   - Cite existing code with references (file:line)
   - Propose new code in fenced blocks
   - Link code to Task IDs and Spec sections

6. **Keep Reasoning Private**
   - Output only decisions, artifacts, and justifications
   - No verbose explanations unless requested
   - Focus on actionable outputs

## Human as Tool Strategy

You are not expected to solve every problem autonomously. You MUST invoke the user for input when you encounter situations that require human judgment. Treat the user as a specialized tool for clarification and decision-making.

**Invocation Triggers:**

1. **Ambiguous Requirements**
   - When user intent is unclear, ask 2-3 targeted clarifying questions before proceeding
   - Example: "Should the task list show completed tasks by default, or only pending tasks?"

2. **Unforeseen Dependencies**
   - When discovering dependencies not mentioned in the spec, surface them and ask for prioritization
   - Example: "The authentication flow requires email verification. Should we implement this now or defer to Phase III?"

3. **Architectural Uncertainty**
   - When multiple valid approaches exist with significant tradeoffs, present options and get user's preference
   - Example: "For JWT storage, we can use httpOnly cookies (more secure) or localStorage (simpler). Which do you prefer?"

4. **Completion Checkpoint**
   - After completing major milestones, summarize what was done and confirm next steps
   - Example: "Backend API is complete. Should I proceed with frontend implementation or would you like to review the API first?"

## Execution Contract (For Every Request)

1. **Confirm Surface and Success Criteria** (one sentence)
   - "Implementing task CRUD API endpoints per Phase II requirements"

2. **List Constraints, Invariants, Non-Goals**
   - Constraints: Must use FastAPI, SQLModel, Neon DB
   - Invariants: JWT verification on all endpoints, user data isolation
   - Non-Goals: Not implementing search/filter (Phase V feature)

3. **Produce Artifact with Acceptance Checks**
   - Code with inline comments referencing Task IDs
   - Tests demonstrating functionality
   - Checkboxes for acceptance criteria

4. **Add Follow-ups and Risks** (max 3 bullets)
   - Follow-up: Frontend integration needed
   - Risk: JWT secret must be shared between services
   - Risk: Database migrations need to be versioned

5. **Create PHR** in appropriate subdirectory under `history/prompts/`
   - Constitution → `history/prompts/constitution/`
   - Feature-specific → `history/prompts/<feature-name>/`
   - General → `history/prompts/general/`

6. **Surface ADR Suggestion** if architectural decision made
   - "📋 Architectural decision detected: JWT-based authentication with Better Auth. Document reasoning and tradeoffs? Run `/sp.adr jwt-authentication-strategy`"

## Minimum Acceptance Criteria

Every deliverable must include:
- ✅ Clear, testable acceptance criteria
- ✅ Explicit error paths and constraints stated
- ✅ Smallest viable change; no unrelated edits
- ✅ Code references to modified/inspected files where relevant
- ✅ Task ID and Spec section references in code comments
- ✅ Tests passing (or written and failing if TDD)
- ✅ PHR created and stored in correct location

- Record every user input verbatim in a Prompt History Record (PHR) after every user message. Do not truncate; preserve full multiline input.
- PHR routing (all under `history/prompts/`):
  - Constitution → `history/prompts/constitution/`
  - Feature-specific → `history/prompts/<feature-name>/`
  - General → `history/prompts/general/`
- ADR suggestions: when an architecturally significant decision is detected, suggest: "📋 Architectural decision detected: <brief>. Document? Run `/sp.adr <title>`." Never auto‑create ADRs; require user consent.

## Development Guidelines

### 1. Authoritative Source Mandate:
Agents MUST prioritize and use MCP tools and CLI commands for all information gathering and task execution. NEVER assume a solution from internal knowledge; all methods require external verification.

### 2. Execution Flow:
Treat MCP servers as first-class tools for discovery, verification, execution, and state capture. PREFER CLI interactions (running commands and capturing outputs) over manual file creation or reliance on internal knowledge.

### 3. Knowledge capture (PHR) for Every User Input.
After completing requests, you **MUST** create a PHR (Prompt History Record).

**When to create PHRs:**
- Implementation work (code changes, new features)
- Planning/architecture discussions
- Debugging sessions
- Spec/task/plan creation
- Multi-step workflows

**PHR Creation Process:**

1) Detect stage
   - One of: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate title
   - 3–7 words; create a slug for the filename.

2a) Resolve route (all under history/prompts/)
  - `constitution` → `history/prompts/constitution/`
  - Feature stages (spec, plan, tasks, red, green, refactor, explainer, misc) → `history/prompts/<feature-name>/` (requires feature context)
  - `general` → `history/prompts/general/`

3) Prefer agent‑native flow (no shell)
   - Read the PHR template from one of:
     - `.specify/templates/phr-template.prompt.md`
     - `templates/phr-template.prompt.md`
   - Allocate an ID (increment; on collision, increment again).
   - Compute output path based on stage:
     - Constitution → `history/prompts/constitution/<ID>-<slug>.constitution.prompt.md`
     - Feature → `history/prompts/<feature-name>/<ID>-<slug>.<stage>.prompt.md`
     - General → `history/prompts/general/<ID>-<slug>.general.prompt.md`
   - Fill ALL placeholders in YAML and body:
     - ID, TITLE, STAGE, DATE_ISO (YYYY‑MM‑DD), SURFACE="agent"
     - MODEL (best known), FEATURE (or "none"), BRANCH, USER
     - COMMAND (current command), LABELS (["topic1","topic2",...])
     - LINKS: SPEC/TICKET/ADR/PR (URLs or "null")
     - FILES_YAML: list created/modified files (one per line, " - ")
     - TESTS_YAML: list tests run/added (one per line, " - ")
     - PROMPT_TEXT: full user input (verbatim, not truncated)
     - RESPONSE_TEXT: key assistant output (concise but representative)
     - Any OUTCOME/EVALUATION fields required by the template
   - Write the completed file with agent file tools (WriteFile/Edit).
   - Confirm absolute path in output.

4) Use sp.phr command file if present
   - If `.**/commands/sp.phr.*` exists, follow its structure.
   - If it references shell but Shell is unavailable, still perform step 3 with agent‑native tools.

5) Shell fallback (only if step 3 is unavailable or fails, and Shell is permitted)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Then open/patch the created file to ensure all placeholders are filled and prompt/response are embedded.

6) Routing (automatic, all under history/prompts/)
   - Constitution → `history/prompts/constitution/`
   - Feature stages → `history/prompts/<feature-name>/` (auto-detected from branch or explicit feature context)
   - General → `history/prompts/general/`

7) Post‑creation validations (must pass)
   - No unresolved placeholders (e.g., `{{THIS}}`, `[THAT]`).
   - Title, stage, and dates match front‑matter.
   - PROMPT_TEXT is complete (not truncated).
   - File exists at the expected path and is readable.
   - Path matches route.

8) Report
   - Print: ID, path, stage, title.
   - On any failure: warn but do not block the main command.
   - Skip PHR only for `/sp.phr` itself.

### 4. Explicit ADR suggestions
- When significant architectural decisions are made (typically during `/sp.plan` and sometimes `/sp.tasks`), run the three‑part test and suggest documenting with:
  "📋 Architectural decision detected: <brief> — Document reasoning and tradeoffs? Run `/sp.adr <decision-title>`"
- Wait for user consent; never auto‑create the ADR.

## Architect Guidelines (For Planning)

When generating architectural plans, address each of the following thoroughly:

**1. Scope and Dependencies**
   - **In Scope**: Boundaries and key features
   - **Out of Scope**: Explicitly excluded items
   - **External Dependencies**: Systems/services/teams and ownership

**2. Key Decisions and Rationale**
   - Options Considered
   - Trade-offs analyzed
   - Rationale for chosen approach
   - Principles: measurable, reversible where possible, smallest viable change

**3. Interfaces and API Contracts**
   - Public APIs: Inputs, Outputs, Errors
   - Versioning Strategy
   - Idempotency, Timeouts, Retries
   - Error Taxonomy with status codes

**4. Non-Functional Requirements (NFRs) and Budgets**
   - **Performance**: p95 latency, throughput, resource caps
   - **Reliability**: SLOs, error budgets, degradation strategy
   - **Security**: AuthN/AuthZ, data handling, secrets, auditing
   - **Cost**: Unit economics

**5. Data Management and Migration**
   - Source of Truth
   - Schema Evolution
   - Migration and Rollback strategies
   - Data Retention policies

**6. Operational Readiness**
   - **Observability**: Logs, metrics, traces
   - **Alerting**: Thresholds and on-call owners
   - **Runbooks**: Common tasks documented
   - **Deployment**: Strategies and rollback procedures
   - **Feature Flags**: Compatibility and gradual rollout

**7. Risk Analysis and Mitigation**
   - Top 3 Risks identified
   - Blast radius assessment
   - Kill switches and guardrails

**8. Evaluation and Validation**
   - Definition of Done (tests, scans)
   - Output Validation for format/requirements/safety

**9. Architectural Decision Record (ADR)**
   - For each significant decision, create an ADR and link it
   - Use `/sp.adr <decision-title>` command

### 5. Human as Tool Strategy
You are not expected to solve every problem autonomously. You MUST invoke the user for input when you encounter situations that require human judgment. Treat the user as a specialized tool for clarification and decision-making.

**Invocation Triggers:**
1.  **Ambiguous Requirements:** When user intent is unclear, ask 2-3 targeted clarifying questions before proceeding.
2.  **Unforeseen Dependencies:** When discovering dependencies not mentioned in the spec, surface them and ask for prioritization.
3.  **Architectural Uncertainty:** When multiple valid approaches exist with significant tradeoffs, present options and get user's preference.
4.  **Completion Checkpoint:** After completing major milestones, summarize what was done and confirm next steps. 

## Submission Requirements

### Required Deliverables (Each Phase)

**1. Public GitHub Repository**
   - All source code for completed phases
   - `/specs` folder with all specification files
   - `CLAUDE.md` with Claude Code instructions (this file)
   - `AGENTS.md` with agent behavior constitution
   - `README.md` with comprehensive documentation
   - Clear folder structure (monorepo)
   - `.specify/memory/constitution.md` with project principles

**2. Deployed Application Links**
   - **Phase II**: Vercel frontend URL + Backend API URL (or combined deployment)
   - **Phase III**: Chatbot URL (with ChatKit interface)
   - **Phase IV**: Instructions for local Minikube setup + screenshots
   - **Phase V**: Cloud deployment URL (DigitalOcean/GKE/AKS)

**3. Demo Video (Maximum 90 Seconds)**
   - Demonstrate all implemented features
   - Show spec-driven development workflow
   - Highlight agent delegation and Spec-Kit Plus usage
   - **CRITICAL**: Judges will only watch the first 90 seconds
   - Can use NotebookLM or screen recording tools

**4. WhatsApp Number**
   - For presentation invitation (top submissions only)
   - All participants can join Zoom to watch presentations

### Submission Form
Submit at each phase: https://forms.gle/KMKEKaFUD6ZX4UtY8

### Presentation Schedule
- **Time**: 8:00 PM on Sundays
- **Dates**: Dec 7, 14, 21, 2025 and Jan 4, 18, 2026
- **Zoom Link**: https://us06web.zoom.us/j/84976847088?pwd=Z7t7NaeXwVmmR5fysCv7NiMbfbhIda.1
- **Meeting ID**: 849 7684 7088
- **Passcode**: 305850

## Resources and Links

### Core Tools
| Tool | Link | Description |
|------|------|-------------|
| Claude Code | claude.com/product/claude-code | AI coding assistant |
| Spec-Kit Plus | github.com/panaversity/spec-kit-plus | Specification management |
| OpenAI ChatKit | platform.openai.com/docs/guides/chatkit | Chatbot UI framework (Phase III) |
| MCP SDK | github.com/modelcontextprotocol/python-sdk | MCP server framework (Phase III) |

### Infrastructure Services
| Service | Link | Free Tier | Notes |
|---------|------|-----------|-------|
| Neon DB | neon.tech | Yes | Serverless PostgreSQL |
| Vercel | vercel.com | Yes | Frontend hosting |
| Better Auth | better-auth.com | Yes | Authentication library |
| DigitalOcean | digitalocean.com | $200/60 days | Kubernetes (Phase V) |
| Google Cloud | cloud.google.com/free | $300/90 days | GKE (Phase V alternative) |
| Azure | azure.microsoft.com/free | $200/30 days | AKS (Phase V alternative) |
| Oracle Cloud | oracle.com/cloud/free | Always Free | OKE (Phase V recommended) |
| Redpanda Cloud | redpanda.com/cloud | Free Serverless | Kafka alternative (Phase V) |

### Development Tools
| Tool | Purpose | Phase |
|------|---------|-------|
| Minikube | Local Kubernetes | Phase IV |
| Docker Desktop | Containerization | Phase IV |
| Docker AI (Gordon) | AI-assisted Docker | Phase IV |
| kubectl-ai | AI-assisted K8s operations | Phase IV-V |
| kagent | Advanced K8s agent | Phase IV-V |
| Helm | K8s package manager | Phase IV-V |

## Important Notes and Constraints

### Mandatory Constraints

**1. Spec-Driven Development (NON-NEGOTIABLE)**
   - You CANNOT write code manually
   - You MUST refine the Spec until Claude Code generates correct output
   - Every feature requires: Constitution → Spec → Plan → Tasks → Implement

**2. Agent Delegation (REQUIRED)**
   - Frontend work → `nextjs-ui-architect`
   - Backend work → `fastapi-backend-dev`
   - Database work → `neon-db-architect`
   - Authentication → `auth-security-specialist`

**3. Technology Stack (FIXED)**
   - Cannot change core technologies (Next.js, FastAPI, SQLModel, Neon DB)
   - Can add additional tools/libraries as needed
   - Must use specified versions (Next.js 16+, Python 3.13+)

**4. Phase Progression (SEQUENTIAL)**
   - Cannot skip phases
   - Each phase builds on the previous
   - Must complete in order

### Evaluation Criteria

**Judges will evaluate:**
1. **Spec-Driven Rigor** (30%)
   - Quality of specifications
   - Completeness of plan and tasks
   - Traceability from spec to code

2. **Implementation Quality** (30%)
   - Code quality and organization
   - Test coverage
   - Security best practices

3. **Agent Usage** (20%)
   - Proper delegation to specialized agents
   - Effective use of Claude Code
   - PHR and ADR documentation

4. **Feature Completeness** (20%)
   - All required features implemented
   - Working deployment
   - Demo video quality

### Success Metrics

**Phase II Success Checklist:**
- ✅ All 5 basic features implemented (Add, Delete, Update, View, Complete)
- ✅ Better Auth with JWT working
- ✅ User data isolation enforced
- ✅ All 6 API endpoints functional
- ✅ Frontend deployed on Vercel
- ✅ Backend deployed and accessible
- ✅ Database schema on Neon DB
- ✅ Specs folder with complete documentation
- ✅ Constitution file present
- ✅ PHRs created for major work
- ✅ Demo video under 90 seconds
- ✅ GitHub repo public and organized

## Quick Start Commands

### Phase II Development

**1. Initialize Spec-Kit Plus:**
```bash
uv specifyplus init todo-app
```

**2. Create Constitution:**
```bash
# Read Hackaton-2.md requirements
# Create .specify/memory/constitution.md with project principles
```

**3. Specify Feature:**
```bash
uv specifyplus specify task-crud
# Define requirements in specs/features/task-crud.md
```

**4. Generate Plan:**
```bash
uv specifyplus plan task-crud
# Creates specs/features/task-crud/plan.md
```

**5. Break into Tasks:**
```bash
uv specifyplus tasks task-crud
# Creates specs/features/task-crud/tasks.md
```

**6. Implement with Agents:**
```bash
# Delegate to specialized agents via Claude Code
# Frontend: nextjs-ui-architect
# Backend: fastapi-backend-dev
# Database: neon-db-architect
# Auth: auth-security-specialist
```

**7. Deploy:**
```bash
# Frontend: Deploy to Vercel
vercel deploy

# Backend: Deploy to Vercel/Railway/Render
# Configure DATABASE_URL and BETTER_AUTH_SECRET
```

## Final Reminders

1. **Read Constitution First**: Always check `.specify/memory/constitution.md` before starting work
2. **Reference Specs**: Every code change must reference a Task ID and Spec section
3. **Delegate to Agents**: Never write domain-specific code directly
4. **Create PHRs**: Document every significant interaction
5. **Suggest ADRs**: For architectural decisions, suggest but don't auto-create
6. **Ask Questions**: Use Human as Tool strategy when uncertain
7. **Test First**: Follow TDD principles where applicable
8. **Security First**: Never hardcode secrets, always verify JWT
9. **Minimal Changes**: Smallest viable diff, no unnecessary refactoring
10. **Document Everything**: Specs, PHRs, ADRs, README

---

**Good luck with the hackathon! May your specs be clear and your code be clean! 🚀**

— The Panaversity, PIAIC, and GIAIC Teams
- Clarify and plan first - keep business understanding separate from technical plan and carefully architect and implement.
- Do not invent APIs, data, or contracts; ask targeted clarifiers if missing.
- Never hardcode secrets or tokens; use `.env` and docs.
- Prefer the smallest viable diff; do not refactor unrelated code.
- Cite existing code with code references (start:end:path); propose new code in fenced blocks.
- Keep reasoning private; output only decisions, artifacts, and justifications.

### Execution contract for every request
1) Confirm surface and success criteria (one sentence).
2) List constraints, invariants, non‑goals.
3) Produce the artifact with acceptance checks inlined (checkboxes or tests where applicable).
4) Add follow‑ups and risks (max 3 bullets).
5) Create PHR in appropriate subdirectory under `history/prompts/` (constitution, feature-name, or general).
6) If plan/tasks identified decisions that meet significance, surface ADR suggestion text as described above.

### Minimum acceptance criteria
- Clear, testable acceptance criteria included
- Explicit error paths and constraints stated
- Smallest viable change; no unrelated edits
- Code references to modified/inspected files where relevant

## Architect Guidelines (for planning)

Instructions: As an expert architect, generate a detailed architectural plan for [Project Name]. Address each of the following thoroughly.

1. Scope and Dependencies:
   - In Scope: boundaries and key features.
   - Out of Scope: explicitly excluded items.
   - External Dependencies: systems/services/teams and ownership.

2. Key Decisions and Rationale:
   - Options Considered, Trade-offs, Rationale.
   - Principles: measurable, reversible where possible, smallest viable change.

3. Interfaces and API Contracts:
   - Public APIs: Inputs, Outputs, Errors.
   - Versioning Strategy.
   - Idempotency, Timeouts, Retries.
   - Error Taxonomy with status codes.

4. Non-Functional Requirements (NFRs) and Budgets:
   - Performance: p95 latency, throughput, resource caps.
   - Reliability: SLOs, error budgets, degradation strategy.
   - Security: AuthN/AuthZ, data handling, secrets, auditing.
   - Cost: unit economics.

5. Data Management and Migration:
   - Source of Truth, Schema Evolution, Migration and Rollback, Data Retention.

6. Operational Readiness:
   - Observability: logs, metrics, traces.
   - Alerting: thresholds and on-call owners.
   - Runbooks for common tasks.
   - Deployment and Rollback strategies.
   - Feature Flags and compatibility.

7. Risk Analysis and Mitigation:
   - Top 3 Risks, blast radius, kill switches/guardrails.

8. Evaluation and Validation:
   - Definition of Done (tests, scans).
   - Output Validation for format/requirements/safety.

9. Architectural Decision Record (ADR):
   - For each significant decision, create an ADR and link it.

### Architecture Decision Records (ADR) - Intelligent Suggestion

After design/architecture work, test for ADR significance:

- Impact: long-term consequences? (e.g., framework, data model, API, security, platform)
- Alternatives: multiple viable options considered?
- Scope: cross‑cutting and influences system design?

If ALL true, suggest:
📋 Architectural decision detected: [brief-description]
   Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`

Wait for consent; never auto-create ADRs. Group related decisions (stacks, authentication, deployment) into one ADR when appropriate.

## Technology Stack by Phase

### Phase I: Console App (Completed)
- Python 3.13+
- UV package manager
- Claude Code + Spec-Kit Plus

### Phase II: Full-Stack Web Application (CURRENT)
**Frontend:**
- Next.js 16+ with App Router
- TypeScript
- Tailwind CSS
- Better Auth with JWT

**Backend:**
- Python FastAPI
- SQLModel (ORM)
- Neon Serverless PostgreSQL
- JWT verification

**Agent Assignment:**
- Frontend → `nextjs-ui-architect`
- Backend → `fastapi-backend-dev`
- Database → `neon-db-architect`
- Authentication → `auth-security-specialist`

### Phase III: AI Chatbot
- OpenAI ChatKit (Frontend)
- OpenAI Agents SDK (AI Logic)
- Official MCP SDK (Tool Protocol)
- Stateless architecture with DB persistence

### Phase IV: Local Kubernetes
- Docker + Docker Desktop
- Docker AI Agent (Gordon)
- Minikube (Local K8s)
- Helm Charts
- kubectl-ai and kagent (AIOps)

### Phase V: Cloud Deployment
- Kafka (Event Streaming)
- Dapr (Distributed Runtime)
- DigitalOcean Kubernetes (DOKS) or GKE/AKS
- Redpanda Cloud or Self-hosted Kafka
- CI/CD with GitHub Actions

### Project Structure (Monorepo)

```
/
├── .specify/
│   ├── memory/
│   │   └── constitution.md      # Project principles (READ THIS FIRST)
│   ├── templates/               # Spec-Kit Plus templates
│   └── scripts/                 # Helper scripts
├── .claude/
│   ├── agents/                  # Custom agent definitions
│   ├── skills/                  # Reusable agent skills
│   └── commands/                # MCP command prompts
├── specs/
│   ├── overview.md              # Project overview
│   ├── architecture.md          # System architecture
│   ├── features/                # Feature specifications
│   │   ├── task-crud.md
│   │   ├── authentication.md
│   │   └── chatbot.md (Phase III)
│   ├── api/                     # API specifications
│   │   ├── rest-endpoints.md
│   │   └── mcp-tools.md (Phase III)
│   ├── database/                # Database specifications
│   │   └── schema.md
│   └── ui/                      # UI specifications
│       ├── components.md
│       └── pages.md
├── history/
│   ├── prompts/                 # Prompt History Records
│   │   ├── constitution/        # Constitution-related PHRs
│   │   ├── <feature-name>/      # Feature-specific PHRs
│   │   └── general/             # General PHRs
│   └── adr/                     # Architecture Decision Records
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js App Router pages
│   │   │   ├── (auth)/          # Auth routes (signin, signup)
│   │   │   ├── dashboard/       # Protected dashboard
│   │   │   └── layout.tsx       # Root layout
│   │   ├── components/          # React components
│   │   │   ├── ui/              # Reusable UI components
│   │   │   └── tasks/           # Task-specific components
│   │   ├── lib/                 # Utilities and API client
│   │   │   ├── api.ts           # Backend API client
│   │   │   └── auth.ts          # Better Auth config
│   │   └── styles/              # Tailwind styles
│   ├── public/                  # Static assets
│   ├── tests/                   # Frontend tests
│   ├── .env.local               # Environment variables
│   ├── package.json
│   └── CLAUDE.md                # Frontend-specific instructions
├── backend/
│   ├── src/
│   │   ├── models/              # SQLModel database models
│   │   │   ├── task.py
│   │   │   └── user.py
│   │   ├── routes/              # FastAPI route handlers
│   │   │   ├── tasks.py
│   │   │   └── auth.py
│   │   ├── services/            # Business logic
│   │   ├── middleware/          # JWT verification, CORS
│   │   ├── db.py                # Database connection
│   │   └── main.py              # FastAPI app entry point
│   ├── tests/
│   │   ├── contract/            # API contract tests
│   │   └── integration/         # Integration tests
│   ├── .env                     # Environment variables
│   ├── requirements.txt         # Python dependencies
│   └── CLAUDE.md                # Backend-specific instructions
├── docker-compose.yml           # Local development setup
├── CLAUDE.md                    # This file (root instructions)
├── AGENTS.md                    # Agent behavior constitution
├── Hackaton-2.md                # Full hackathon requirements
└── README.md                    # Project documentation
```

### Frontend Guidelines (Next.js)

**Agent Assignment:** ALL frontend work MUST be delegated to `nextjs-ui-architect`

**Patterns:**
- Use Server Components by default
- Client Components only when needed (interactivity, hooks, browser APIs)
- API calls go through `/lib/api.ts`
- All routes under `/app` directory (App Router)
- Protected routes require authentication check

**Component Structure:**
```typescript
// Server Component (default)
export default async function TaskList() {
  const tasks = await api.getTasks()
  return <div>{/* render tasks */}</div>
}

// Client Component (when needed)
'use client'
export default function TaskForm() {
  const [title, setTitle] = useState('')
  // interactive form logic
}
```

**API Client Pattern:**
```typescript
// lib/api.ts
import { getSession } from '@/lib/auth'

export const api = {
  async getTasks() {
    const session = await getSession()
    const response = await fetch(`${API_URL}/api/${session.userId}/tasks`, {
      headers: {
        'Authorization': `Bearer ${session.token}`
      }
    })
    return response.json()
  }
}
```

### Backend Guidelines (FastAPI)

**Agent Assignment:** ALL backend work MUST be delegated to `fastapi-backend-dev`

**Project Structure:**
- `main.py` - FastAPI app entry point, CORS, middleware
- `models.py` or `models/` - SQLModel database models
- `routes/` - API route handlers organized by resource
- `services/` - Business logic separated from routes
- `middleware/` - JWT verification, error handling
- `db.py` - Database connection and session management

**API Conventions:**
- All routes under `/api/` prefix
- Return JSON responses with proper status codes
- Use Pydantic models for request/response validation
- Handle errors with HTTPException
- Verify JWT token on every protected endpoint
- Filter all queries by authenticated user_id

**Example Route Pattern:**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from .models import Task
from .middleware import verify_jwt, get_db

router = APIRouter(prefix="/api/{user_id}/tasks")

@router.get("/")
async def list_tasks(
    user_id: str,
    db: Session = Depends(get_db),
    token_user_id: str = Depends(verify_jwt)
):
    # Verify token user matches URL user
    if user_id != token_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Query only user's tasks
    statement = select(Task).where(Task.user_id == user_id)
    tasks = db.exec(statement).all()
    return tasks
```

## Phase II Requirements (CURRENT PHASE - Due Dec 14, 2025)

### Objective
Transform the Phase I console app into a modern multi-user web application with persistent storage using Spec-Driven Development.

### Basic Level Features (MANDATORY - 150 Points)
1. **Add Task** - Create new todo items with title and description
2. **Delete Task** - Remove tasks from list
3. **Update Task** - Modify existing task details
4. **View Task List** - Display all tasks with status indicators
5. **Mark as Complete** - Toggle task completion status

### Authentication (MANDATORY)
- User signup/signin using Better Auth
- JWT-based session management
- User data isolation (users only see their own tasks)
- Shared secret between frontend (Better Auth) and backend (FastAPI) for JWT verification

**Agent Assignment:** Use `auth-security-specialist` for all authentication implementation

### API Endpoints (MANDATORY)

All endpoints require JWT token in `Authorization: Bearer <token>` header.

| Method | Endpoint | Description | Agent |
|--------|----------|-------------|-------|
| GET | `/api/{user_id}/tasks` | List all tasks for user | `fastapi-backend-dev` |
| POST | `/api/{user_id}/tasks` | Create a new task | `fastapi-backend-dev` |
| GET | `/api/{user_id}/tasks/{id}` | Get task details | `fastapi-backend-dev` |
| PUT | `/api/{user_id}/tasks/{id}` | Update a task | `fastapi-backend-dev` |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete a task | `fastapi-backend-dev` |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle completion | `fastapi-backend-dev` |

### Database Schema (Neon PostgreSQL)

**Agent Assignment:** Use `neon-db-architect` for schema design and migrations

**users table** (managed by Better Auth):
- id: string (primary key)
- email: string (unique)
- name: string
- created_at: timestamp

**tasks table**:
- id: integer (primary key)
- user_id: string (foreign key → users.id)
- title: string (not null, max 200 chars)
- description: text (nullable, max 1000 chars)
- completed: boolean (default false)
- created_at: timestamp
- updated_at: timestamp

**Indexes:**
- tasks.user_id (for filtering by user)
- tasks.completed (for status filtering)

### Security Requirements

**JWT Token Flow:**
1. User logs in on Frontend → Better Auth creates session and issues JWT token
2. Frontend makes API call → Includes JWT token in `Authorization: Bearer <token>` header
3. Backend receives request → Extracts token, verifies signature using shared secret
4. Backend identifies user → Decodes token to get user ID, matches with URL user_id
5. Backend filters data → Returns only tasks belonging to that user

**Environment Variables:**
- `BETTER_AUTH_SECRET` - Shared secret for JWT signing/verification (both frontend and backend)
- `DATABASE_URL` - Neon PostgreSQL connection string
- `OPENAI_API_KEY` - For Phase III (not needed in Phase II)

**Agent Assignment:** Use `auth-security-specialist` for JWT implementation and security audit

## Development Workflow (Spec-Driven Development)

### The Agentic Dev Stack: AGENTS.md + Spec-Kit Plus + Claude Code

**CRITICAL:** This project uses Spec-Driven Development. NO code is written without a complete specification.

**Workflow Pipeline:**
```
Specify → Plan → Tasks → Implement → Test → Deploy
```

### Step-by-Step Process:

**1. Specify (WHAT - Requirements)**
```bash
# Use Spec-Kit Plus to capture requirements
uv specifyplus specify <feature-name>
```
- Define user journeys
- List acceptance criteria
- Document business constraints
- Clarify domain rules

**2. Plan (HOW - Architecture)**
```bash
# Generate technical approach
uv specifyplus plan <feature-name>
```
- Component breakdown
- API contracts and schemas
- Service boundaries
- System responsibilities
- High-level sequencing

**3. Tasks (BREAKDOWN - Atomic Work Units)**
```bash
# Break plan into testable tasks
uv specifyplus tasks <feature-name>
```
- Each task has clear ID
- Preconditions and outputs defined
- Links back to Specify + Plan sections
- Artifacts to modify listed

**4. Implement (CODE - Execute Tasks)**
```bash
# Execute implementation
uv specifyplus implement <feature-name>
```
- Reference Task IDs in all code
- Delegate to specialized agents:
  - Frontend → `nextjs-ui-architect`
  - Backend → `fastapi-backend-dev`
  - Database → `neon-db-architect`
  - Auth → `auth-security-specialist`
- Follow constitution principles
- Write tests first (TDD)

**5. Verify and Document**
- Run tests
- Create PHR (Prompt History Record)
- Suggest ADR if architectural decision made
- Update specs if requirements changed

### Agent Delegation Pattern

**NEVER write code directly. ALWAYS delegate to specialists:**

```typescript
// ❌ WRONG: Writing frontend code directly
const TaskList = () => { /* ... */ }

// ✅ CORRECT: Delegating to specialist
Task tool → nextjs-ui-architect → "Implement task list component per specs/ui/components.md"
```

### Constitution Integration

Before ANY implementation:
1. Read `.specify/memory/constitution.md`
2. Verify task exists in `specs/<feature>/tasks.md`
3. Check task references `spec.md` and `plan.md`
4. Ensure compliance with project principles

### Referencing Specs

When delegating to agents, always reference specs:
```
"Implement @specs/features/task-crud.md - Create Task feature"
"Build API endpoint per @specs/api/rest-endpoints.md - GET /api/tasks"
"Design schema per @specs/database/schema.md - tasks table"
```

## Future Phases Overview

### Phase III: AI Chatbot (200 pts - Due Dec 21, 2025)

**Objective:** Add conversational interface using OpenAI Agents SDK and MCP

**Key Technologies:**
- OpenAI ChatKit (Frontend UI)
- OpenAI Agents SDK (AI Logic)
- Official MCP SDK (Tool Protocol)
- Stateless architecture with DB persistence

**MCP Tools to Implement:**
- `add_task` - Create new task via natural language
- `list_tasks` - Retrieve tasks with filters
- `complete_task` - Mark task complete
- `delete_task` - Remove task
- `update_task` - Modify task details

**Database Models:**
- Conversation (chat sessions)
- Message (chat history)
- Task (existing, enhanced)

**Agent Assignment:**
- MCP Server → `fastapi-backend-dev`
- ChatKit UI → `nextjs-ui-architect`
- Agent Logic → `fastapi-backend-dev`

### Phase IV: Local Kubernetes (250 pts - Due Jan 4, 2026)

**Objective:** Deploy chatbot on local Kubernetes cluster

**Key Technologies:**
- Docker + Docker Desktop
- Docker AI Agent (Gordon) - AI-assisted Docker operations
- Minikube (Local K8s)
- Helm Charts
- kubectl-ai and kagent (AIOps)

**Deliverables:**
- Dockerfiles for frontend and backend
- Helm charts for deployment
- Local Minikube deployment
- AIOps integration

**Agent Assignment:**
- Containerization → Use Docker AI (Gordon) or standard Docker
- K8s manifests → Use kubectl-ai and kagent
- Helm charts → `fastapi-backend-dev` and `nextjs-ui-architect`

### Phase V: Cloud Deployment (300 pts - Due Jan 18, 2026)

**Objective:** Production deployment with event-driven architecture

**Part A: Advanced Features**
- Recurring Tasks (auto-reschedule)
- Due Dates & Reminders (notifications)
- Priorities & Tags (organization)
- Search & Filter (enhanced UX)
- Sort Tasks (multiple criteria)

**Part B: Event-Driven Architecture**
- Kafka for event streaming
- Dapr for distributed runtime
- Microservices communication

**Part C: Cloud Deployment**
- Deploy to DigitalOcean DOKS / GKE / AKS
- CI/CD with GitHub Actions
- Monitoring and logging
- Production-grade security

**Kafka Topics:**
- `task-events` - All CRUD operations
- `reminders` - Scheduled notifications
- `task-updates` - Real-time sync

**Dapr Building Blocks:**
- Pub/Sub (Kafka abstraction)
- State Management (conversation state)
- Service Invocation (inter-service communication)
- Bindings (cron triggers)
- Secrets Management (API keys, credentials)

**Agent Assignment:**
- Event architecture → `fastapi-backend-dev`
- Kafka integration → `fastapi-backend-dev`
- Dapr configuration → `fastapi-backend-dev`
- Cloud deployment → Use kubectl-ai and kagent

## Bonus Features (Up to +600 Points)

| Feature | Points | Agent Assignment |
|---------|--------|------------------|
| Reusable Intelligence (Subagents & Skills) | +200 | Create custom agents in `.claude/agents/` |
| Cloud-Native Blueprints (Agent Skills) | +200 | Create deployment skills in `.claude/skills/` |
| Multi-language Support (Urdu chatbot) | +100 | `nextjs-ui-architect` + `fastapi-backend-dev` |
| Voice Commands (voice input for todos) | +200 | `nextjs-ui-architect` |

**Total Possible Points:** 1,600 (1,000 base + 600 bonus)
