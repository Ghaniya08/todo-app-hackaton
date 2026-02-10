/**
 * Chat page - AI assistant interface under dashboard.
 *
 * [Task]: UI-REFACTOR
 * [From]: User request for /dashboard/chat route
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/lib/auth';
import { api } from '@/lib/api';
import { Message, ChatResponse } from '@/types/chat';
import { MessageList } from '@/components/chat/MessageList';
import { ChatInput } from '@/components/chat/ChatInput';
import { Spinner } from '@/components/ui/Spinner';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { toast } from 'sonner';

export default function ChatPage() {
  const { user } = useAuth();

  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user && conversationId) {
      loadConversationHistory();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user, conversationId]);

  const loadConversationHistory = useCallback(async () => {
    if (!user || !conversationId) return;

    setIsLoadingHistory(true);
    setError(null);

    try {
      const history = await api.chat.getMessages(user.id, conversationId);
      setMessages(history);
    } catch (err) {
      console.error('Failed to load conversation history:', err);
    } finally {
      setIsLoadingHistory(false);
    }
  }, [user, conversationId]);

  const handleSendMessage = async (content: string) => {
    if (!user) return;

    const tempUserMessage: Message = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response: ChatResponse = await api.chat.sendMessage(user.id, {
        conversation_id: conversationId || undefined,
        message: content,
      });

      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      setMessages((prev) => {
        const filtered = prev.filter((m) => m.id !== tempUserMessage.id);
        return [
          ...filtered,
          {
            id: `user-${Date.now()}`,
            role: 'user',
            content,
            created_at: new Date().toISOString(),
          },
          response.message,
        ];
      });

      if (response.tool_calls && response.tool_calls.length > 0) {
        const toolNames = response.tool_calls.map((tc) => tc.tool).join(', ');
        toast.success(`Action completed: ${toolNames}`);
      }
    } catch (err) {
      console.error('Chat error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      toast.error(errorMessage);
      setMessages((prev) => prev.filter((m) => m.id !== tempUserMessage.id));
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* Chat Container Card */}
      <div className="bg-surface rounded-2xl shadow-lg border border-border overflow-hidden h-[calc(100vh-140px)] flex flex-col">
        {/* Chat Header */}
        <div className="flex-shrink-0 bg-gradient-to-r from-primary/5 to-transparent border-b border-border px-4 sm:px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-12 h-12 bg-gradient-to-br from-violet-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg shadow-violet-500/20">
                  <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
                  </svg>
                </div>
                <div className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 bg-emerald-400 rounded-full border-2 border-surface"></div>
              </div>
              <div>
                <h2 className="font-semibold text-foreground text-lg">AI Task Assistant</h2>
                <p className="text-xs text-muted flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse"></span>
                  Online and ready to help
                </p>
              </div>
            </div>
            <button
              onClick={handleNewChat}
              className="flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-muted bg-accent hover:bg-accent/80 hover:text-foreground rounded-xl transition-all duration-200"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
              </svg>
              New Chat
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="flex-shrink-0 px-4 sm:px-6 pt-4">
            <ErrorMessage message={error} onRetry={() => setError(null)} />
          </div>
        )}

        {/* Main Content */}
        {isLoadingHistory ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <Spinner size="lg" />
              <p className="mt-3 text-sm text-muted">Loading conversation...</p>
            </div>
          </div>
        ) : (
          <>
            <MessageList messages={messages} isLoading={isLoading} />
            <ChatInput
              onSend={handleSendMessage}
              isLoading={isLoading}
              disabled={isLoadingHistory}
            />
          </>
        )}
      </div>
    </div>
  );
}
