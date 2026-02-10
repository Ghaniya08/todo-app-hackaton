/**
 * Chat types for AI Chat Agent feature.
 *
 * [Task]: T003
 * [From]: specs/004-ai-chat-agent/contracts/chat-api.yaml
 * [From]: specs/004-ai-chat-agent/data-model.md
 */

// Message roles
export type MessageRole = 'user' | 'assistant' | 'tool';

// Tool call structure
export interface ToolCall {
  tool: 'add_task' | 'list_tasks' | 'complete_task' | 'delete_task' | 'update_task';
  input: Record<string, unknown>;
  output?: Record<string, unknown>;
}

// Message entity
export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  tool_calls?: ToolCall[] | null;
  created_at: string;
}

// Conversation summary (for listing)
export interface ConversationSummary {
  id: string;
  title?: string | null;
  created_at: string;
  updated_at: string;
  message_count?: number;
}

// Chat request payload
export interface ChatRequest {
  conversation_id?: string;
  message: string;
}

// Chat response payload
export interface ChatResponse {
  conversation_id: string;
  message: Message;
  tool_calls?: ToolCall[] | null;
}

// Frontend state types
export interface ChatState {
  messages: Message[];
  conversationId: string | null;
  isLoading: boolean;
  error: string | null;
}
