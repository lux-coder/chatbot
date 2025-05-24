'use client';

import React, { useState, useRef, useEffect } from 'react';
import { clsx } from 'clsx';
import { Button } from '@/components/common';
import type { ComponentProps } from '@/utils/types';

interface MessageInputProps extends ComponentProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
}

export const MessageInput: React.FC<MessageInputProps> = ({
  onSendMessage,
  disabled = false,
  placeholder = 'Type your message...',
  maxLength = 4000,
  className,
}) => {
  const [message, setMessage] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const scrollHeight = textarea.scrollHeight;
      const maxHeight = 200; // Max height in pixels
      textarea.style.height = `${Math.min(scrollHeight, maxHeight)}px`;
    }
  };

  useEffect(() => {
    adjustTextareaHeight();
  }, [message]);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    if (value.length <= maxLength) {
      setMessage(value);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Send message on Enter (but not Shift+Enter)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSendMessage = () => {
    const trimmedMessage = message.trim();
    if (trimmedMessage && !disabled) {
      onSendMessage(trimmedMessage);
      setMessage('');
    }
  };

  const canSend = message.trim().length > 0 && !disabled;

  return (
    <div className={clsx('bg-white border-t border-secondary-200', className)}>
      <div className="px-4 py-3">
        <div
          className={clsx(
            'flex items-end space-x-3 bg-secondary-50 rounded-lg border transition-colors',
            isFocused
              ? 'border-primary-300 ring-1 ring-primary-300'
              : 'border-secondary-200',
            disabled && 'opacity-50'
          )}
        >
          {/* Text input area */}
          <div className="flex-1 min-w-0">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder={placeholder}
              disabled={disabled}
              rows={1}
              className={clsx(
                'w-full resize-none border-none bg-transparent px-3 py-3 text-sm placeholder-secondary-500 focus:outline-none focus:ring-0',
                'min-h-[2.5rem] max-h-[12.5rem] overflow-y-auto',
                disabled && 'cursor-not-allowed'
              )}
              style={{ minHeight: '2.5rem' }}
            />
          </div>

          {/* Send button and character count */}
          <div className="flex flex-col items-end justify-end pb-1 pr-1">
            {/* Character count */}
            {message.length > maxLength * 0.8 && (
              <div className="text-xs text-secondary-500 mb-1">
                {message.length}/{maxLength}
              </div>
            )}

            {/* Send button */}
            <Button
              variant={canSend ? 'primary' : 'secondary'}
              size="sm"
              onClick={handleSendMessage}
              disabled={!canSend}
              className="h-8 w-8 rounded-full p-0 flex items-center justify-center"
            >
              <SendIcon className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Helper text */}
        <div className="flex items-center justify-between mt-2 text-xs text-secondary-500">
          <div className="flex items-center space-x-4">
            <span>Press <kbd className="px-1 py-0.5 bg-secondary-200 rounded text-xs">Enter</kbd> to send</span>
            <span><kbd className="px-1 py-0.5 bg-secondary-200 rounded text-xs">Shift + Enter</kbd> for new line</span>
          </div>
          
          {disabled && (
            <div className="flex items-center space-x-1 text-secondary-400">
              <LoadingIcon className="w-3 h-3 animate-spin" />
              <span>Sending...</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Icon components
const SendIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
  </svg>
);

const LoadingIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
  </svg>
); 