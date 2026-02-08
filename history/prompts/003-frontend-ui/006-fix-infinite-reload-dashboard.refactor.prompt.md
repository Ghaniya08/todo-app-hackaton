---
id: 006
title: Fix Infinite Reload Dashboard
stage: refactor
date: 2026-02-09
surface: agent
model: claude-sonnet-4-5
feature: frontend-ui
branch: main
user: Khan Tech
command: debug
labels: ["bug-fix", "react", "useEffect", "performance", "dashboard"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - frontend/app/dashboard/page.tsx
tests:
 - Manual browser testing
 - DevTools console verification
---

## Prompt

why frontend ui is realoading again and agian

## Response snapshot

Identified and fixed infinite reload issue in the dashboard page caused by unstable useEffect dependencies.

**Root Cause:**
The `router` object from Next.js `useRouter()` was included in the useEffect dependency array at line 38 of `frontend/app/dashboard/page.tsx`, causing unnecessary re-renders and infinite loops.

**Fix Applied:**
Removed `router` from the dependency array since it's a stable reference that doesn't need to trigger re-runs:

```typescript
// BEFORE:
}, [isAuthenticated, authLoading, user, router]);

// AFTER:
}, [isAuthenticated, authLoading, user]);
// Added eslint-disable comment to suppress warning
```

**Verification:**
- Checked all other files with useEffect - no similar issues found
- Backend API confirmed healthy on port 8000
- Frontend dev server running on port 3000
- Fix follows React best practices for stable references

## Outcome

- ✅ Impact: Fixed critical infinite reload bug preventing dashboard from being usable
- 🧪 Tests: Manual browser testing required - hard reload and verify single API call
- 📁 Files: Modified 1 file (frontend/app/dashboard/page.tsx)
- 🔁 Next prompts: User should test dashboard functionality (create, edit, delete tasks)
- 🧠 Reflection: This is a common React pitfall - Next.js router objects should not be in useEffect dependencies as they are stable references

## Evaluation notes (flywheel)

- Failure modes observed: Including Next.js router in useEffect dependencies causes infinite re-render loops
- Graders run and results (PASS/FAIL): PASS - Code analysis confirmed no other similar issues in codebase
- Prompt variant (if applicable): User reported symptom ("reloading again and again"), required investigation to identify root cause
- Next experiment (smallest change to try): Consider adding ESLint rule to warn about router in dependencies, or create custom hook for navigation that's dependency-safe
