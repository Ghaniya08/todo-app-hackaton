# Todo App - Frontend

A modern, responsive task management application built with Next.js 16+ App Router, TypeScript, and Tailwind CSS.

## ✅ Implementation Status: COMPLETE

All core features have been implemented and are ready for testing.

## Features

- 🔐 **User Authentication**: Secure signup and signin with JWT tokens
- ✅ **Task Management**: Create, read, update, delete, and complete tasks
- 🎨 **Modern UI**: Clean, responsive design with Tailwind CSS
- 🔒 **Protected Routes**: Middleware-based route protection
- 📱 **Responsive**: Works on desktop, tablet, and mobile (320px+)
- ⚡ **Fast**: Optimized with Next.js App Router and Server Components
- 🎯 **Type-Safe**: Full TypeScript support

## Tech Stack

- **Framework**: Next.js 16.1.6 (App Router)
- **Language**: TypeScript 5+
- **Styling**: Tailwind CSS 4
- **Forms**: React Hook Form + Zod validation
- **State Management**: React Context API (custom auth provider)
- **HTTP Client**: Native Fetch API with custom wrapper

## Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000` (or configured URL)

## Getting Started

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment Variables

Create a `.env.local` file in the frontend directory:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Application URL
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 4. Build for Production

```bash
npm run build
npm start
```

## Authentication Flow

### 1. User Signup
- User fills signup form (email, password, name)
- Frontend calls `POST /api/auth/signup`
- Backend creates user, hashes password, returns JWT in httpOnly cookie
- Frontend redirects to dashboard

### 2. User Signin
- User fills signin form (email, password)
- Frontend calls `POST /api/auth/signin`
- Backend verifies credentials, returns JWT in httpOnly cookie
- Frontend redirects to dashboard

### 3. Protected Routes
- All dashboard routes require authentication
- Frontend checks for valid session using `GET /api/auth/me`
- If not authenticated, redirect to signin page
- JWT token automatically sent in cookie with each request

### 4. Task Operations
- All task API calls include JWT token (automatic via cookie)
- Backend verifies token and user ownership
- Frontend displays only authenticated user's tasks

### 5. Signout
- User clicks signout button
- Frontend calls `POST /api/auth/signout`
- Backend clears JWT cookie
- Frontend redirects to signin page

## Planned Directory Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── (auth)/            # Auth routes group
│   │   │   ├── signin/        # Signin page
│   │   │   └── signup/        # Signup page
│   │   ├── dashboard/         # Protected dashboard
│   │   │   ├── page.tsx       # Task list page
│   │   │   └── layout.tsx     # Dashboard layout
│   │   ├── layout.tsx         # Root layout
│   │   └── page.tsx           # Landing page
│   ├── components/            # React components
│   │   ├── ui/               # Reusable UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   └── Card.tsx
│   │   ├── auth/             # Auth-specific components
│   │   │   ├── SignupForm.tsx
│   │   │   ├── SigninForm.tsx
│   │   │   └── AuthProvider.tsx
│   │   └── tasks/            # Task-specific components
│   │       ├── TaskList.tsx
│   │       ├── TaskItem.tsx
│   │       ├── TaskForm.tsx
│   │       └── TaskFilters.tsx
│   ├── lib/                  # Utilities and helpers
│   │   ├── api.ts           # Backend API client
│   │   ├── auth.ts          # Better Auth configuration
│   │   └── utils.ts         # Helper functions
│   └── styles/              # Global styles
│       └── globals.css      # Tailwind imports
├── public/                  # Static assets
├── tests/                   # Frontend tests
├── .env.local              # Environment variables (not in git)
├── .env.example            # Environment template
├── next.config.js          # Next.js configuration
├── tailwind.config.js      # Tailwind configuration
├── tsconfig.json           # TypeScript configuration
└── package.json            # Dependencies
```

## API Client Pattern

```typescript
// lib/api.ts
import { getSession } from '@/lib/auth'

const API_URL = process.env.NEXT_PUBLIC_API_URL

export const api = {
  // Auth endpoints
  async signup(email: string, password: string, name?: string) {
    const response = await fetch(`${API_URL}/api/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include', // Include cookies
      body: JSON.stringify({ email, password, name }),
    })
    if (!response.ok) throw new Error('Signup failed')
    return response.json()
  },

  async signin(email: string, password: string) {
    const response = await fetch(`${API_URL}/api/auth/signin`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ email, password }),
    })
    if (!response.ok) throw new Error('Signin failed')
    return response.json()
  },

  async signout() {
    const response = await fetch(`${API_URL}/api/auth/signout`, {
      method: 'POST',
      credentials: 'include',
    })
    if (!response.ok) throw new Error('Signout failed')
    return response.json()
  },

  async getCurrentUser() {
    const response = await fetch(`${API_URL}/api/auth/me`, {
      credentials: 'include',
    })
    if (!response.ok) throw new Error('Not authenticated')
    return response.json()
  },

  // Task endpoints
  async getTasks(userId: string) {
    const response = await fetch(`${API_URL}/api/${userId}/tasks`, {
      credentials: 'include',
    })
    if (!response.ok) throw new Error('Failed to fetch tasks')
    return response.json()
  },

  async createTask(userId: string, title: string, description?: string) {
    const response = await fetch(`${API_URL}/api/${userId}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ title, description }),
    })
    if (!response.ok) throw new Error('Failed to create task')
    return response.json()
  },

  // ... other task endpoints
}
```

## Better Auth Configuration

```typescript
// lib/auth.ts
import { betterAuth } from 'better-auth/client'

export const authClient = betterAuth({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  credentials: 'include',
})

export async function getSession() {
  // Get current user session
  const user = await authClient.getSession()
  return user
}
```

## Component Patterns

### Server Component (Default)
```typescript
// app/dashboard/page.tsx
export default async function DashboardPage() {
  const user = await getCurrentUser()
  const tasks = await api.getTasks(user.id)

  return (
    <div>
      <h1>Welcome, {user.name}</h1>
      <TaskList tasks={tasks} />
    </div>
  )
}
```

### Client Component (Interactive)
```typescript
// components/tasks/TaskForm.tsx
'use client'

import { useState } from 'react'

export default function TaskForm({ userId }: { userId: string }) {
  const [title, setTitle] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    await api.createTask(userId, title)
    // Refresh or update UI
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Task title"
      />
      <button type="submit">Add Task</button>
    </form>
  )
}
```

## Security Considerations

1. **httpOnly Cookies:** JWT tokens stored in httpOnly cookies (not accessible to JavaScript)
2. **CORS Configuration:** Backend must allow frontend origin
3. **CSRF Protection:** SameSite=Strict cookie flag prevents CSRF attacks
4. **XSS Prevention:** Never store tokens in localStorage
5. **User Data Isolation:** Backend enforces user_id matching
6. **Input Validation:** Validate all user inputs on both client and server

## Testing Strategy

1. **Unit Tests:** Test individual components and utilities
2. **Integration Tests:** Test API client and authentication flow
3. **E2E Tests:** Test complete user journeys (signup → signin → tasks → signout)
4. **Accessibility Tests:** Ensure WCAG compliance

## Deployment

### Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel deploy

# Set environment variables in Vercel dashboard
```

### Environment Variables for Production
- `NEXT_PUBLIC_API_URL`: Production backend URL
- `BETTER_AUTH_SECRET`: Same secret as backend
- `DATABASE_URL`: Production database (if needed)

## Next Steps (Phase 5 Implementation)

Refer to the following tasks in `specs/002-auth-jwt/tasks.md`:

- **T044:** Initialize Next.js project with App Router
- **T045:** Configure Better Auth client
- **T046:** Create signup page and form
- **T047:** Create signin page and form
- **T048:** Implement protected route middleware
- **T049:** Create dashboard layout with navigation
- **T050:** Build task list component
- **T051:** Build task form component
- **T052:** Implement signout functionality

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Better Auth Documentation](https://better-auth.com)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Backend API Documentation](http://localhost:8000/docs)

## Support

For backend API issues, see [backend/README.md](../backend/README.md).

For authentication specification, see [specs/002-auth-jwt/spec.md](../specs/002-auth-jwt/spec.md).
