'use client';

import React from 'react';
import { clsx } from 'clsx';
import { Loading } from '@/components/common';
import type { ComponentProps } from '@/utils/types';

interface Message {
  message_id: string;
  role: string;
  content: string;
  timestamp: string;
  metadata?: {
    error?: boolean;
    processing?: boolean;
  };
}

interface MessageListProps extends ComponentProps {
  messages: Message[];
  isLoading?: boolean;
}

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  isLoading,
  className,
}) => {
  const formatTimestamp = (timestamp: string): string => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    // Less than 1 minute
    if (diff < 60000) {
      return 'Just now';
    }
    
    // Less than 1 hour
    if (diff < 3600000) {
      const minutes = Math.floor(diff / 60000);
      return `${minutes}m ago`;
    }
    
    // Less than 1 day
    if (diff < 86400000) {
      const hours = Math.floor(diff / 3600000);
      return `${hours}h ago`;
    }
    
    // More than 1 day
    return date.toLocaleDateString();
  };

  const renderMessage = (message: Message) => {
    const isUser = message.role === 'user';
    const isError = message.metadata?.error;
    const isProcessing = message.metadata?.processing;

    return (
      <div
        key={message.message_id}
        className={clsx(
          'flex w-full',
          isUser ? 'justify-end' : 'justify-start'
        )}
      >
        <div
          className={clsx(
            'flex max-w-[70%] md:max-w-[60%]',
            isUser ? 'flex-row-reverse' : 'flex-row'
          )}
        >
          {/* Avatar */}
          <div
            className={clsx(
              'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
              isUser
                ? 'bg-primary-100 text-primary-600 ml-2'
                : 'bg-secondary-100 text-secondary-600 mr-2'
            )}
          >
            {isUser ? (
              <UserIcon className="w-4 h-4" />
            ) : (
              <BotIcon className="w-4 h-4" />
            )}
          </div>

          {/* Message bubble */}
          <div className="flex flex-col">
            <div
              className={clsx(
                'rounded-lg px-4 py-2 max-w-full break-words',
                isUser
                  ? 'bg-primary-600 text-white'
                  : isError
                  ? 'bg-error-50 border border-error-200 text-error-700'
                  : 'bg-white border border-secondary-200 text-secondary-900'
              )}
            >
              {isProcessing ? (
                <div className="flex items-center space-x-2">
                  <Loading variant="dots" size="sm" />
                  <span className="text-sm text-secondary-600">Thinking...</span>
                </div>
              ) : (
                <div className="whitespace-pre-wrap">{message.content}</div>
              )}
              
              {isError && (
                <div className="mt-2 text-xs text-error-600">
                  Failed to send message. Please try again.
                </div>
              )}
            </div>

            {/* Timestamp */}
            <div
              className={clsx(
                'text-xs text-secondary-500 mt-1',
                isUser ? 'text-right' : 'text-left'
              )}
            >
              {formatTimestamp(message.timestamp)}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className={clsx('flex flex-col space-y-4 p-4', className)}>
      {messages.length === 0 ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-secondary-100">
              <ChatIcon className="h-6 w-6 text-secondary-400" />
            </div>
            <h3 className="mt-4 text-lg font-medium text-secondary-900">
              No messages yet
            </h3>
            <p className="mt-2 text-sm text-secondary-600">
              Start the conversation by sending a message below.
            </p>
          </div>
        </div>
      ) : (
        <>
          {messages.map((message) => renderMessage(message))}
          
          {/* Loading indicator for new message */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="flex max-w-[70%] md:max-w-[60%]">
                {/* Bot Avatar */}
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary-100 text-secondary-600 mr-2 flex items-center justify-center">
                  <BotIcon className="w-4 h-4" />
                </div>

                {/* Typing indicator */}
                <div className="bg-white border border-secondary-200 rounded-lg px-4 py-2">
                  <div className="flex items-center space-x-1">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-secondary-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-secondary-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-secondary-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                    <span className="text-sm text-secondary-500 ml-2">AI is typing...</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

// Icon components
const UserIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
  </svg>
);

const BotIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2z" />
  </svg>
);

const ChatIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
  </svg>
); 