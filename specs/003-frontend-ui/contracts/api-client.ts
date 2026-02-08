/**
 * API Client Interface: Frontend UI & Integration
 *
 * Feature: 003-frontend-ui
 * Date: 2026-02-08
 *
 * This file defines the TypeScript interfaces for all backend API interactions.
 * These contracts ensure type safety between frontend and backend.
 *
 * Backend API Base URL: process.env.NEXT_PUBLIC_API_URL (e.g., http://localhost:8000)
 * Authentication: JWT token in httpOnly cookie (automatically included)
 */

// ============================================================================
// Core Entities
// ============================================================================

/**
 * User entity from backend
 * Source: Backend /api/auth/me endpoint
 */
export interface User {
  id: string;              // UUID from backend
  email: string;           // User's email address
  name: string;            // User's display name
  created_at: string;      // ISO 8601 timestamp (UTC)
}

/**
 * Task entity from backend
 * Source: Backend /api/{user_id}/tasks endpoints
 */
export interface Task {
  id: number;              // Auto-increment ID from backend
  user_id: string;         // Owner's user ID (foreign key)
  title: string;           // Task title (max 200 chars)
  description: string | null;  // Task description (max 1000 chars, nullable)
  completed: boolean;      // Completion status
  created_at: string;      // ISO 8601 timestamp (UTC)
  updated_at: string;      // ISO 8601 timestamp (UTC)
}

// ============================================================================
// Request Payloads
// ============================================================================

/**
 * Signup request payload
 * Endpoint: POST /api/auth/signup
 */
export interface SignupRequest {
  email: string;           // Valid email format
  password: string;        // Min 8 chars, at least one letter and one number
  name: string;            // User's display name
}

/**
 * Signin request payload
 * Endpoint: POST /api/auth/signin
 */
export interface SigninRequest {
  email: string;           // Valid email format
  password: string;        // User's password
}

/**
 * Task creation request payload
 * Endpoint: POST /api/{user_id}/tasks
 */
export interface TaskCreateRequest {
  title: string;           // Required, 1-200 chars
  description?: string;    // Optional, max 1000 chars
}

/**
 * Task update request payload
 * Endpoint: PUT /api/{user_id}/tasks/{id}
 */
export interface TaskUpdateRequest {
  title?: string;          // Optional, 1-200 chars if provided
  description?: string;    // Optional, max 1000 chars if provided
  completed?: boolean;     // Optional, toggle completion
}

// ============================================================================
// Response Payloads
// ============================================================================

/**
 * Signup response
 * Endpoint: POST /api/auth/signup
 * Status: 201 Created
 */
export interface SignupResponse {
  user: User;              // Created user entity
  message: string;         // Success message
}

/**
 * Signin response
 * Endpoint: POST /api/auth/signin
 * Status: 200 OK
 * Note: JWT token set in httpOnly cookie (not in response body)
 */
export interface SigninResponse {
  user: User;              // Authenticated user entity
  message: string;         // Success message
}

/**
 * Current user response
 * Endpoint: GET /api/auth/me
 * Status: 200 OK
 */
export interface MeResponse {
  user: User;              // Current authenticated user
}

/**
 * Signout response
 * Endpoint: POST /api/auth/signout
 * Status: 200 OK
 */
export interface SignoutResponse {
  message: string;         // Success message
}

/**
 * Task list response
 * Endpoint: GET /api/{user_id}/tasks
 * Status: 200 OK
 */
export type TaskListResponse = Task[];

/**
 * Single task response
 * Endpoints:
 * - POST /api/{user_id}/tasks (201 Created)
 * - GET /api/{user_id}/tasks/{id} (200 OK)
 * - PUT /api/{user_id}/tasks/{id} (200 OK)
 * - PATCH /api/{user_id}/tasks/{id}/complete (200 OK)
 */
export type TaskResponse = Task;

/**
 * Task deletion response
 * Endpoint: DELETE /api/{user_id}/tasks/{id}
 * Status: 204 No Content
 */
export type TaskDeleteResponse = void;

// ============================================================================
// Error Responses
// ============================================================================

/**
 * Standard error response from backend
 * All error endpoints return this format
 */
export interface ErrorResponse {
  detail: string;          // User-friendly error message
}

/**
 * Validation error response (400 Bad Request)
 * Contains field-specific validation errors
 */
export interface ValidationErrorResponse {
  detail: string | ValidationError[];  // Error message or array of field errors
}

/**
 * Individual field validation error
 */
export interface ValidationError {
  loc: string[];           // Field location (e.g., ["body", "title"])
  msg: string;             // Error message
  type: string;            // Error type (e.g., "value_error")
}

// ============================================================================
// API Client Interface
// ============================================================================

/**
 * API Client for backend communication
 * Implementation: frontend/src/lib/api.ts
 *
 * All methods automatically include JWT token from httpOnly cookie.
 * All methods throw typed errors (see ApiError types below).
 */
export interface ApiClient {
  // Authentication endpoints
  auth: {
    /**
     * Create new user account
     * @throws AuthenticationError if email already exists
     * @throws ValidationError if input invalid
     * @throws NetworkError if request fails
     */
    signup(data: SignupRequest): Promise<SignupResponse>;

    /**
     * Sign in existing user
     * @throws AuthenticationError if credentials invalid
     * @throws ValidationError if input invalid
     * @throws NetworkError if request fails
     */
    signin(data: SigninRequest): Promise<SigninResponse>;

    /**
     * Sign out current user
     * @throws NetworkError if request fails
     */
    signout(): Promise<SignoutResponse>;

    /**
     * Get current authenticated user
     * @throws AuthenticationError if not authenticated
     * @throws NetworkError if request fails
     */
    me(): Promise<MeResponse>;
  };

  // Task endpoints
  tasks: {
    /**
     * List all tasks for authenticated user
     * @param userId - Authenticated user's ID
     * @throws AuthenticationError if not authenticated
     * @throws AuthorizationError if userId doesn't match token
     * @throws NetworkError if request fails
     */
    list(userId: string): Promise<TaskListResponse>;

    /**
     * Get single task by ID
     * @param userId - Authenticated user's ID
     * @param taskId - Task ID to retrieve
     * @throws AuthenticationError if not authenticated
     * @throws AuthorizationError if task doesn't belong to user
     * @throws NotFoundError if task doesn't exist
     * @throws NetworkError if request fails
     */
    get(userId: string, taskId: number): Promise<TaskResponse>;

    /**
     * Create new task
     * @param userId - Authenticated user's ID
     * @param data - Task creation payload
     * @throws AuthenticationError if not authenticated
     * @throws AuthorizationError if userId doesn't match token
     * @throws ValidationError if input invalid
     * @throws NetworkError if request fails
     */
    create(userId: string, data: TaskCreateRequest): Promise<TaskResponse>;

    /**
     * Update existing task
     * @param userId - Authenticated user's ID
     * @param taskId - Task ID to update
     * @param data - Task update payload
     * @throws AuthenticationError if not authenticated
     * @throws AuthorizationError if task doesn't belong to user
     * @throws NotFoundError if task doesn't exist
     * @throws ValidationError if input invalid
     * @throws NetworkError if request fails
     */
    update(userId: string, taskId: number, data: TaskUpdateRequest): Promise<TaskResponse>;

    /**
     * Toggle task completion status
     * @param userId - Authenticated user's ID
     * @param taskId - Task ID to toggle
     * @throws AuthenticationError if not authenticated
     * @throws AuthorizationError if task doesn't belong to user
     * @throws NotFoundError if task doesn't exist
     * @throws NetworkError if request fails
     */
    toggleComplete(userId: string, taskId: number): Promise<TaskResponse>;

    /**
     * Delete task
     * @param userId - Authenticated user's ID
     * @param taskId - Task ID to delete
     * @throws AuthenticationError if not authenticated
     * @throws AuthorizationError if task doesn't belong to user
     * @throws NotFoundError if task doesn't exist
     * @throws NetworkError if request fails
     */
    delete(userId: string, taskId: number): Promise<TaskDeleteResponse>;
  };
}

// ============================================================================
// Error Types
// ============================================================================

/**
 * Base API error class
 * All API errors extend this class
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: ErrorResponse
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Authentication error (401 Unauthorized)
 * User is not authenticated or session expired
 * Action: Redirect to signin page
 */
export class AuthenticationError extends ApiError {
  constructor(message: string = 'Your session has expired. Please sign in again.') {
    super(message, 401);
    this.name = 'AuthenticationError';
  }
}

/**
 * Authorization error (403 Forbidden)
 * User doesn't have permission for this action
 * Action: Show error message
 */
export class AuthorizationError extends ApiError {
  constructor(message: string = "You don't have permission to perform this action.") {
    super(message, 403);
    this.name = 'AuthorizationError';
  }
}

/**
 * Validation error (400 Bad Request)
 * Input validation failed
 * Action: Show field-specific errors
 */
export class ValidationError extends ApiError {
  constructor(
    message: string,
    public errors?: ValidationError[]
  ) {
    super(message, 400);
    this.name = 'ValidationError';
  }
}

/**
 * Not found error (404 Not Found)
 * Requested resource doesn't exist
 * Action: Show error message
 */
export class NotFoundError extends ApiError {
  constructor(message: string = 'The requested resource was not found.') {
    super(message, 404);
    this.name = 'NotFoundError';
  }
}

/**
 * Network error (no response)
 * Request failed due to network issues
 * Action: Show retry button
 */
export class NetworkError extends ApiError {
  constructor(message: string = 'Network error. Please check your connection and try again.') {
    super(message);
    this.name = 'NetworkError';
  }
}

/**
 * Server error (500 Internal Server Error)
 * Backend encountered an error
 * Action: Show retry button
 */
export class ServerError extends ApiError {
  constructor(message: string = 'Something went wrong. Please try again later.') {
    super(message, 500);
    this.name = 'ServerError';
  }
}

// ============================================================================
// HTTP Client Configuration
// ============================================================================

/**
 * API client configuration
 * Set via environment variables
 */
export interface ApiConfig {
  baseUrl: string;         // Backend API base URL (e.g., http://localhost:8000)
  timeout: number;         // Request timeout in milliseconds (default: 30000)
  retryAttempts: number;   // Number of retry attempts for network errors (default: 3)
  retryDelay: number;      // Delay between retries in milliseconds (default: 1000)
}

/**
 * Default API configuration
 */
export const defaultApiConfig: ApiConfig = {
  baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 30000,
  retryAttempts: 3,
  retryDelay: 1000,
};

// ============================================================================
// Request/Response Interceptors
// ============================================================================

/**
 * Request interceptor type
 * Allows modifying requests before they're sent
 */
export type RequestInterceptor = (
  url: string,
  options: RequestInit
) => Promise<{ url: string; options: RequestInit }>;

/**
 * Response interceptor type
 * Allows processing responses before they're returned
 */
export type ResponseInterceptor = (response: Response) => Promise<Response>;

/**
 * Error interceptor type
 * Allows handling errors globally
 */
export type ErrorInterceptor = (error: ApiError) => Promise<never>;

// ============================================================================
// Usage Examples
// ============================================================================

/**
 * Example: Creating the API client
 *
 * ```typescript
 * import { createApiClient } from '@/lib/api';
 *
 * const api = createApiClient({
 *   baseUrl: process.env.NEXT_PUBLIC_API_URL,
 *   timeout: 30000,
 * });
 * ```
 */

/**
 * Example: Signing up a new user
 *
 * ```typescript
 * try {
 *   const response = await api.auth.signup({
 *     email: 'user@example.com',
 *     password: 'SecurePass123',
 *     name: 'John Doe',
 *   });
 *   console.log('User created:', response.user);
 * } catch (error) {
 *   if (error instanceof ValidationError) {
 *     console.error('Validation failed:', error.errors);
 *   } else if (error instanceof AuthenticationError) {
 *     console.error('Email already exists');
 *   }
 * }
 * ```
 */

/**
 * Example: Fetching tasks
 *
 * ```typescript
 * try {
 *   const tasks = await api.tasks.list(userId);
 *   console.log('Tasks:', tasks);
 * } catch (error) {
 *   if (error instanceof AuthenticationError) {
 *     // Redirect to signin
 *     router.push('/signin');
 *   } else if (error instanceof NetworkError) {
 *     // Show retry button
 *     setError({ message: error.message, retry: () => fetchTasks() });
 *   }
 * }
 * ```
 */

/**
 * Example: Creating a task with optimistic update
 *
 * ```typescript
 * const optimisticTask = {
 *   id: Date.now(), // Temporary ID
 *   title: 'New Task',
 *   completed: false,
 *   // ... other fields
 * };
 *
 * // Add to UI immediately
 * setTasks([...tasks, optimisticTask]);
 *
 * try {
 *   const createdTask = await api.tasks.create(userId, {
 *     title: 'New Task',
 *     description: 'Task description',
 *   });
 *
 *   // Replace optimistic task with real task
 *   setTasks(tasks.map(t => t.id === optimisticTask.id ? createdTask : t));
 * } catch (error) {
 *   // Remove optimistic task on error
 *   setTasks(tasks.filter(t => t.id !== optimisticTask.id));
 *   handleError(error);
 * }
 * ```
 */

// ============================================================================
// Related Documents
// ============================================================================

/**
 * Related Specifications:
 * - specs/003-frontend-ui/spec.md - Feature specification
 * - specs/003-frontend-ui/plan.md - Implementation plan
 * - specs/003-frontend-ui/data-model.md - Data entities and state management
 * - specs/003-frontend-ui/research.md - Technical research and decisions
 *
 * Backend API Documentation:
 * - backend/src/routes/auth.py - Authentication endpoints
 * - backend/src/routes/tasks.py - Task endpoints
 * - backend/tests/contract/test_auth_api.py - Auth API contract tests
 * - backend/tests/contract/test_task_api.py - Task API contract tests
 */
