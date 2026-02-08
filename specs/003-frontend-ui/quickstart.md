# Quickstart Guide: Frontend UI & Integration

**Feature**: 003-frontend-ui | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)

## Overview

This guide provides step-by-step instructions for implementing the authenticated task management frontend. Follow these steps in order to build a production-ready Next.js application that integrates with the existing backend API.

**Prerequisites:**
- Backend API running and accessible (Phase II: 002-auth-jwt complete)
- Node.js 18+ and npm/yarn/pnpm installed
- Git repository initialized
- Environment variables configured

**Estimated Implementation Time:** 3-4 hours (with specialized agents)

---

## Phase 0: Project Setup

### Step 1: Initialize Next.js Project

```bash
# Navigate to repository root
cd todo-full-stack-web-application

# Create Next.js app with TypeScript and Tailwind CSS
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir --import-alias "@/*"

# Navigate to frontend directory
cd frontend
```

**Acceptance Criteria:**
- ✅ Next.js 16+ installed with App Router
- ✅ TypeScript configured
- ✅ Tailwind CSS configured
- ✅ Project structure created

**Agent Assignment:** Manual setup or `nextjs-ui-architect`

---

### Step 2: Install Dependencies

```bash
# Install Better Auth and dependencies
npm install better-auth @better-auth/react

# Install form handling and validation
npm install react-hook-form zod @hookform/resolvers

# Install development dependencies
npm install -D @types/node @types/react @types/react-dom
```

**Acceptance Criteria:**
- ✅ All dependencies installed
- ✅ package.json updated
- ✅ package-lock.json generated

**Agent Assignment:** Manual or `nextjs-ui-architect`

---

### Step 3: Configure Environment Variables

Create `.env.local` file in `frontend/` directory:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration
BETTER_AUTH_SECRET=your-shared-secret-here
BETTER_AUTH_URL=http://localhost:3000
```

Create `.env.example` template:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration (must match backend JWT secret)
BETTER_AUTH_SECRET=
BETTER_AUTH_URL=http://localhost:3000
```

**Acceptance Criteria:**
- ✅ `.env.local` created with actual values
- ✅ `.env.example` created as template
- ✅ `.env.local` added to `.gitignore`
- ✅ `BETTER_AUTH_SECRET` matches backend `JWT_SECRET`

**Security Note:** Never commit `.env.local` to version control.

**Agent Assignment:** Manual configuration

---

## Phase 1: Authentication Setup (User Story 1)

### Step 4: Configure Better Auth

Create `src/lib/auth.ts`:

```typescript
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET!,
  baseURL: process.env.BETTER_AUTH_URL!,
  database: {
    // Better Auth will use backend API for user management
    type: "custom",
    customAdapter: {
      // Delegate to backend API
    },
  },
  session: {
    expiresIn: 60 * 60 * 24, // 24 hours (matches backend JWT expiration)
    updateAge: 60 * 60, // Update session every hour
    cookieCache: {
      enabled: true,
      maxAge: 60 * 5, // 5 minutes
    },
  },
  cookies: {
    sessionToken: {
      name: "session",
      options: {
        httpOnly: true,
        sameSite: "strict",
        secure: process.env.NODE_ENV === "production",
        path: "/",
      },
    },
  },
});
```

**Acceptance Criteria:**
- ✅ Better Auth configured with JWT settings
- ✅ Session expiration matches backend (24 hours)
- ✅ httpOnly cookies enabled
- ✅ SameSite=Strict for CSRF protection

**Agent Assignment:** `auth-security-specialist`

**References:**
- [spec.md](./spec.md) - FR-010, FR-014
- [research.md](./research.md) - Section 1 (Better Auth decision)

---

### Step 5: Create API Client

Create `src/lib/api.ts`:

```typescript
import {
  ApiClient,
  ApiConfig,
  defaultApiConfig,
  AuthenticationError,
  AuthorizationError,
  ValidationError,
  NotFoundError,
  NetworkError,
  ServerError,
} from "@/contracts/api-client";

class ApiClientImpl implements ApiClient {
  private config: ApiConfig;

  constructor(config: Partial<ApiConfig> = {}) {
    this.config = { ...defaultApiConfig, ...config };
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.config.baseUrl}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
        credentials: "include", // Include cookies (JWT token)
      });

      // Handle error responses
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw this.handleError(response.status, errorData);
      }

      // Handle 204 No Content
      if (response.status === 204) {
        return undefined as T;
      }

      return await response.json();
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new NetworkError();
    }
  }

  private handleError(status: number, data: any): Error {
    const message = data.detail || "An error occurred";

    switch (status) {
      case 401:
        return new AuthenticationError(message);
      case 403:
        return new AuthorizationError(message);
      case 404:
        return new NotFoundError(message);
      case 400:
        return new ValidationError(message, data.errors);
      case 500:
        return new ServerError(message);
      default:
        return new ApiError(message, status);
    }
  }

  // Implement auth methods
  auth = {
    signup: (data) => this.request("/api/auth/signup", {
      method: "POST",
      body: JSON.stringify(data),
    }),
    signin: (data) => this.request("/api/auth/signin", {
      method: "POST",
      body: JSON.stringify(data),
    }),
    signout: () => this.request("/api/auth/signout", {
      method: "POST",
    }),
    me: () => this.request("/api/auth/me"),
  };

  // Implement task methods
  tasks = {
    list: (userId) => this.request(`/api/${userId}/tasks`),
    get: (userId, taskId) => this.request(`/api/${userId}/tasks/${taskId}`),
    create: (userId, data) => this.request(`/api/${userId}/tasks`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
    update: (userId, taskId, data) => this.request(`/api/${userId}/tasks/${taskId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
    toggleComplete: (userId, taskId) => this.request(`/api/${userId}/tasks/${taskId}/complete`, {
      method: "PATCH",
    }),
    delete: (userId, taskId) => this.request(`/api/${userId}/tasks/${taskId}`, {
      method: "DELETE",
    }),
  };
}

export const api = new ApiClientImpl();
```

**Acceptance Criteria:**
- ✅ API client implements all endpoints
- ✅ JWT token automatically included via cookies
- ✅ Typed error handling for all status codes
- ✅ Network error handling with retry capability

**Agent Assignment:** `nextjs-ui-architect`

**References:**
- [contracts/api-client.ts](./contracts/api-client.ts) - Full interface definition
- [research.md](./research.md) - Section 2 (API client architecture)

---

### Step 6: Create Authentication Pages

Create `src/app/(auth)/signin/page.tsx`:

```typescript
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { api } from "@/lib/api";

const signinSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

type SigninForm = z.infer<typeof signinSchema>;

export default function SigninPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SigninForm>({
    resolver: zodResolver(signinSchema),
  });

  const onSubmit = async (data: SigninForm) => {
    setIsLoading(true);
    setError(null);

    try {
      await api.auth.signin(data);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign in failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <h2 className="text-3xl font-bold text-center">Sign In</h2>

        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div>
            <label htmlFor="email" className="block text-sm font-medium">
              Email
            </label>
            <input
              {...register("email")}
              type="email"
              className="mt-1 block w-full rounded border-gray-300"
            />
            {errors.email && (
              <p className="text-red-600 text-sm mt-1">{errors.email.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium">
              Password
            </label>
            <input
              {...register("password")}
              type="password"
              className="mt-1 block w-full rounded border-gray-300"
            />
            {errors.password && (
              <p className="text-red-600 text-sm mt-1">{errors.password.message}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2 px-4 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <p className="text-center text-sm">
          Don't have an account?{" "}
          <a href="/signup" className="text-blue-600 hover:underline">
            Sign Up
          </a>
        </p>
      </div>
    </div>
  );
}
```

Create similar page for `src/app/(auth)/signup/page.tsx` with signup form.

**Acceptance Criteria:**
- ✅ Signin page with email/password form
- ✅ Signup page with email/password/name form
- ✅ Form validation with React Hook Form + Zod
- ✅ Loading states during submission
- ✅ Error message display
- ✅ Redirect to dashboard on success

**Agent Assignment:** `nextjs-ui-architect`

**References:**
- [spec.md](./spec.md) - FR-001, FR-002, FR-017
- [research.md](./research.md) - Section 5 (Form validation)

---

## Phase 2: Task Management UI (User Story 2)

### Step 7: Create Dashboard Page

Create `src/app/dashboard/page.tsx`:

```typescript
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Task } from "@/contracts/api-client";
import TaskList from "@/components/tasks/TaskList";
import TaskForm from "@/components/tasks/TaskForm";

export default function DashboardPage() {
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [user, setUser] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadUserAndTasks();
  }, []);

  const loadUserAndTasks = async () => {
    try {
      const { user } = await api.auth.me();
      setUser(user);

      const taskList = await api.tasks.list(user.id);
      setTasks(taskList);
    } catch (err) {
      if (err instanceof AuthenticationError) {
        router.push("/signin");
      } else {
        setError("Failed to load tasks");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateTask = async (data: TaskCreateRequest) => {
    const newTask = await api.tasks.create(user.id, data);
    setTasks([...tasks, newTask]);
  };

  const handleToggleComplete = async (taskId: number) => {
    const updatedTask = await api.tasks.toggleComplete(user.id, taskId);
    setTasks(tasks.map(t => t.id === taskId ? updatedTask : t));
  };

  const handleDeleteTask = async (taskId: number) => {
    await api.tasks.delete(user.id, taskId);
    setTasks(tasks.filter(t => t.id !== taskId));
  };

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold">My Tasks</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <TaskForm onSubmit={handleCreateTask} />
        <TaskList
          tasks={tasks}
          onToggleComplete={handleToggleComplete}
          onDelete={handleDeleteTask}
        />
      </main>
    </div>
  );
}
```

**Acceptance Criteria:**
- ✅ Dashboard fetches user and tasks on mount
- ✅ Redirects to signin if not authenticated
- ✅ Displays task list with CRUD operations
- ✅ Loading and error states handled

**Agent Assignment:** `nextjs-ui-architect`

**References:**
- [spec.md](./spec.md) - FR-005, FR-006, FR-007, FR-008, FR-009
- [data-model.md](./data-model.md) - Task entity, UI state

---

### Step 8: Create Task Components

Create reusable components in `src/components/tasks/`:

- **TaskList.tsx** - Displays list of tasks
- **TaskItem.tsx** - Individual task with checkbox and actions
- **TaskForm.tsx** - Create/edit task form
- **EmptyState.tsx** - Empty state when no tasks

**Acceptance Criteria:**
- ✅ TaskList renders all tasks
- ✅ TaskItem shows title, description, completion status
- ✅ TaskForm validates input with Zod
- ✅ EmptyState shows helpful message

**Agent Assignment:** `nextjs-ui-architect`

**References:**
- [spec.md](./spec.md) - FR-013 (empty state)
- [plan.md](./plan.md) - Component structure

---

## Phase 3: Session Persistence & Polish (User Story 3)

### Step 9: Add Route Protection Middleware

Create `src/middleware.ts`:

```typescript
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const sessionToken = request.cookies.get("session");
  const isAuthPage = request.nextUrl.pathname.startsWith("/signin") ||
                     request.nextUrl.pathname.startsWith("/signup");
  const isProtectedPage = request.nextUrl.pathname.startsWith("/dashboard");

  // Redirect authenticated users away from auth pages
  if (sessionToken && isAuthPage) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  // Redirect unauthenticated users to signin
  if (!sessionToken && isProtectedPage) {
    return NextResponse.redirect(new URL("/signin", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
```

**Acceptance Criteria:**
- ✅ Protected routes require authentication
- ✅ Authenticated users redirected from auth pages
- ✅ Unauthenticated users redirected to signin

**Agent Assignment:** `auth-security-specialist`

**References:**
- [spec.md](./spec.md) - FR-003, FR-004
- [research.md](./research.md) - Section 8 (Routing)

---

### Step 10: Add Loading States

Create `src/components/ui/Spinner.tsx` and skeleton screens:

```typescript
export function Spinner() {
  return (
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
  );
}

export function TaskSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-4 bg-gray-200 rounded w-3/4" />
      <div className="h-4 bg-gray-200 rounded w-1/2" />
    </div>
  );
}
```

**Acceptance Criteria:**
- ✅ Spinner for button actions
- ✅ Skeleton screens for initial load
- ✅ Loading states prevent duplicate submissions

**Agent Assignment:** `nextjs-ui-architect`

**References:**
- [spec.md](./spec.md) - FR-011, SC-003, SC-007
- [research.md](./research.md) - Section 7 (Loading states)

---

## Phase 4: Testing

### Step 11: Write Component Tests

Create tests in `tests/components/`:

```typescript
import { render, screen } from "@testing-library/react";
import TaskItem from "@/components/tasks/TaskItem";

describe("TaskItem", () => {
  it("renders task title and description", () => {
    const task = {
      id: 1,
      title: "Test Task",
      description: "Test Description",
      completed: false,
    };

    render(<TaskItem task={task} />);

    expect(screen.getByText("Test Task")).toBeInTheDocument();
    expect(screen.getByText("Test Description")).toBeInTheDocument();
  });
});
```

**Acceptance Criteria:**
- ✅ Component rendering tests
- ✅ Form validation tests
- ✅ API client error handling tests

**Agent Assignment:** `nextjs-ui-architect`

---

### Step 12: Write E2E Tests

Create E2E tests with Playwright in `tests/e2e/`:

```typescript
import { test, expect } from "@playwright/test";

test("user can create and complete a task", async ({ page }) => {
  // Sign in
  await page.goto("/signin");
  await page.fill('input[type="email"]', "test@example.com");
  await page.fill('input[type="password"]', "password123");
  await page.click('button[type="submit"]');

  // Create task
  await page.fill('input[name="title"]', "New Task");
  await page.click('button:has-text("Add Task")');

  // Verify task appears
  await expect(page.locator("text=New Task")).toBeVisible();

  // Complete task
  await page.click('input[type="checkbox"]');
  await expect(page.locator("text=New Task")).toHaveClass(/completed/);
});
```

**Acceptance Criteria:**
- ✅ Critical user flows tested
- ✅ Cross-browser testing
- ✅ Mobile responsive testing

**Agent Assignment:** `nextjs-ui-architect`

---

## Phase 5: Deployment

### Step 13: Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel deploy

# Set environment variables in Vercel dashboard
# - NEXT_PUBLIC_API_URL
# - BETTER_AUTH_SECRET
# - BETTER_AUTH_URL
```

**Acceptance Criteria:**
- ✅ Frontend deployed to Vercel
- ✅ Environment variables configured
- ✅ Custom domain configured (optional)
- ✅ HTTPS enabled

**Agent Assignment:** Manual deployment

---

## Verification Checklist

After completing all steps, verify:

- [ ] All 18 functional requirements (FR-001 to FR-018) implemented
- [ ] All 8 success criteria (SC-001 to SC-008) met
- [ ] User Story 1 (Authentication) complete and tested
- [ ] User Story 2 (Task Management) complete and tested
- [ ] User Story 3 (Session Persistence) complete and tested
- [ ] All tests passing (unit + integration + E2E)
- [ ] No console errors or warnings
- [ ] Responsive design works on mobile (320px+)
- [ ] JWT tokens in httpOnly cookies
- [ ] User data isolation enforced
- [ ] Loading states visible for operations >300ms
- [ ] Error messages user-friendly
- [ ] Application deployed and accessible

---

## Troubleshooting

### Issue: JWT token not included in requests

**Solution:** Ensure `credentials: "include"` is set in fetch options and CORS is configured on backend to allow credentials.

### Issue: Session expires immediately

**Solution:** Verify `BETTER_AUTH_SECRET` matches backend `JWT_SECRET` exactly.

### Issue: CORS errors

**Solution:** Configure backend CORS to allow frontend origin:

```python
# backend/src/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Tasks not loading

**Solution:** Check browser console for errors. Verify backend API is running and accessible at `NEXT_PUBLIC_API_URL`.

---

## Related Documents

- [spec.md](./spec.md) - Feature specification
- [plan.md](./plan.md) - Implementation plan
- [data-model.md](./data-model.md) - Data entities
- [research.md](./research.md) - Technical decisions
- [contracts/api-client.ts](./contracts/api-client.ts) - API interface

---

## Next Steps

After completing this quickstart:

1. Run `/sp.tasks` to generate detailed task breakdown
2. Execute tasks using specialized agents
3. Create PHR for implementation work
4. Deploy to production
5. Proceed to Phase III (AI Chatbot)

---

**Status**: ✅ Ready for implementation via `/sp.tasks` command
