/**
 * ChatInput component for sending messages.
 *
 * [Task]: T017, T045
 * [From]: specs/004-ai-chat-agent/spec.md §User Story 1
 */

'use client';

import { useState, useRef, useEffect, KeyboardEvent } from 'react';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
  disabled?: boolean;
}

export function ChatInput({ onSend, isLoading, disabled }: ChatInputProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [message]);

  const handleSubmit = () => {
    const trimmedMessage = message.trim();
    if (trimmedMessage && !isLoading && !disabled) {
      onSend(trimmedMessage);
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const quickActions = [
    { label: 'Show tasks', icon: '📋' },
    { label: 'Add task', icon: '➕' },
    { label: 'Help', icon: '❓' },
  ];

  return (
    <div className="flex-shrink-0 bg-surface/80 backdrop-blur-lg border-t border-border">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-4">
        {/* Quick Actions */}
        <div className="flex flex-wrap gap-2 mb-3">
          {quickActions.map((action) => (
            <button
              key={action.label}
              onClick={() => {
                setMessage(action.label);
                textareaRef.current?.focus();
              }}
              disabled={isLoading || disabled}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm text-muted bg-accent hover:bg-accent/80 rounded-full transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span>{action.icon}</span>
              <span>{action.label}</span>
            </button>
          ))}
        </div>

        {/* Input Area */}
        <div className="relative flex items-end gap-3">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value.slice(0, 2000))}
              onKeyDown={handleKeyDown}
              placeholder="Type your message..."
              disabled={isLoading || disabled}
              rows={1}
              maxLength={2000}
              className="w-full resize-none rounded-2xl border border-border bg-accent px-4 py-3.5 pr-24 text-foreground placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
              style={{ minHeight: '52px', maxHeight: '150px' }}
            />

            {/* Character count & keyboard hint */}
            <div className="absolute right-3 bottom-3 flex items-center gap-2 text-xs text-muted">
              <span className={message.length > 1800 ? 'text-warning' : ''}>
                {message.length}/2000
              </span>
              <span className="hidden sm:inline text-border">|</span>
              <span className="hidden sm:inline">Enter ↵</span>
            </div>
          </div>

          {/* Send Button */}
          <button
            onClick={handleSubmit}
            disabled={!message.trim() || isLoading || disabled}
            className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700 text-white rounded-2xl flex items-center justify-center shadow-lg shadow-violet-500/25 hover:shadow-violet-500/40 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none transition-all duration-200 active:scale-95"
          >
            {isLoading ? (
              <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5"
                />
              </svg>
            )}
          </button>
        </div>

        {/* Helper text */}
        <p className="text-xs text-muted mt-2 text-center">
          Press <kbd className="px-1.5 py-0.5 bg-accent rounded text-muted">Shift + Enter</kbd> for new line
        </p>
      </div>
    </div>
  );
}
