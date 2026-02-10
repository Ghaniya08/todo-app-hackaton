import type {
  User,
  SignupRequest,
  SigninRequest,
  AuthResponse,
} from '@/types/user';
import type {
  Task,
  TaskCreate,
  TaskUpdate,
  TaskListResponse,
} from '@/types/task';

// API Error Classes
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export class AuthenticationError extends ApiError {
  constructor(message: string = 'Your session has expired. Please sign in again.') {
    super(message, 401);
    this.name = 'AuthenticationError';
  }
}

export class AuthorizationError extends ApiError {
  constructor(message: string = "You don't have permission to perform this action.") {
    super(message, 403);
    this.name = 'AuthorizationError';
  }
}

export class ValidationError extends ApiError {
  constructor(message: string, public errors?: any[]) {
    super(message, 400);
    this.name = 'ValidationError';
  }
}

export class NotFoundError extends ApiError {
  constructor(message: string = 'The requested resource was not found.') {
    super(message, 404);
    this.name = 'NotFoundError';
  }
}

export class NetworkError extends ApiError {
  constructor(message: string = 'Network error. Please check your connection and try again.') {
    super(message);
    this.name = 'NetworkError';
  }
}

export class ServerError extends ApiError {
  constructor(message: string = 'Something went wrong. Please try again later.') {
    super(message, 500);
    this.name = 'ServerError';
  }
}

// API Client Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

class ApiClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    console.log(`[API] ${options.method || 'GET'} ${endpoint}`);

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        credentials: 'include', // Include cookies (JWT token)
      });

      console.log(`[API] Response status: ${response.status}`);

      // Handle error responses
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'An error occurred' }));
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
      // Network error or other fetch failure
      throw new NetworkError();
    }
  }

  private handleError(status: number, data: any): ApiError {
    const message = data.detail || 'An error occurred';

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

  // Authentication methods
  auth = {
    signup: (data: SignupRequest): Promise<AuthResponse> =>
      this.request('/api/auth/signup', {
        method: 'POST',
        body: JSON.stringify(data),
      }),

    signin: (data: SigninRequest): Promise<AuthResponse> =>
      this.request('/api/auth/signin', {
        method: 'POST',
        body: JSON.stringify(data),
      }),

    signout: (): Promise<{ message: string }> =>
      this.request('/api/auth/signout', {
        method: 'POST',
      }),

    me: (): Promise<User> =>
      this.request('/api/auth/me'),
  };

  // Task methods
  tasks = {
    list: (userId: string): Promise<TaskListResponse> =>
      this.request(`/api/${userId}/tasks`),

    get: (userId: string, taskId: number): Promise<Task> =>
      this.request(`/api/${userId}/tasks/${taskId}`),

    create: (userId: string, data: TaskCreate): Promise<Task> =>
      this.request(`/api/${userId}/tasks`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),

    update: (userId: string, taskId: number, data: TaskUpdate): Promise<Task> =>
      this.request(`/api/${userId}/tasks/${taskId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),

    toggleComplete: (userId: string, taskId: number): Promise<Task> =>
      this.request(`/api/${userId}/tasks/${taskId}/complete`, {
        method: 'PATCH',
      }),

    delete: (userId: string, taskId: number): Promise<void> =>
      this.request(`/api/${userId}/tasks/${taskId}`, {
        method: 'DELETE',
      }),
  };
}

export const api = new ApiClient();
