'use client';

import React from 'react';
import { clsx } from 'clsx';
import { Loading } from '@/components/common';
import type { ComponentProps } from '@/utils/types';

interface Conversation {
  conversation_id: string;
  chatbot_instance_id: string;
  title: string;
  last_message_at: string;
}

interface ConversationListProps extends ComponentProps {
  conversations: Conversation[];
  selectedConversationId?: string | undefined;
  onConversationSelect: (conversationId: string) => void;
  isLoading?: boolean;
}

export const ConversationList: React.FC<ConversationListProps> = ({
  conversations,
  selectedConversationId,
  onConversationSelect,
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
      return `${minutes}m`;
    }
    
    // Less than 1 day
    if (diff < 86400000) {
      const hours = Math.floor(diff / 3600000);
      return `${hours}h`;
    }
    
    // Less than 1 week
    if (diff < 604800000) {
      const days = Math.floor(diff / 86400000);
      return `${days}d`;
    }
    
    // More than 1 week
    return date.toLocaleDateString();
  };

  const generateConversationTitle = (conversation: Conversation): string => {
    if (conversation.title) {
      return conversation.title;
    }
    
    // Fallback to date-based title since we don't have last_message in the API
    const date = new Date(conversation.last_message_at);
    return `Chat ${date.toLocaleDateString()}`;
  };

  if (isLoading) {
    return (
      <div className={clsx('flex items-center justify-center h-32', className)}>
        <Loading size="md" text="Loading conversations..." />
      </div>
    );
  }

  if (conversations.length === 0) {
    return (
      <div className={clsx('p-4 text-center', className)}>
        <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-secondary-100">
          <ChatIcon className="h-6 w-6 text-secondary-400" />
        </div>
        <h3 className="mt-4 text-sm font-medium text-secondary-900">
          No conversations yet
        </h3>
        <p className="mt-2 text-xs text-secondary-600">
          Start a new conversation to see it here.
        </p>
      </div>
    );
  }

  return (
    <div className={clsx('space-y-1', className)}>
      {conversations.map((conversation) => {
        const isSelected = selectedConversationId === conversation.conversation_id;
        const title = generateConversationTitle(conversation);
        
        return (
          <button
            key={conversation.conversation_id}
            onClick={() => onConversationSelect(conversation.conversation_id)}
            className={clsx(
              'w-full text-left px-3 py-3 border-l-2 transition-colors duration-200 hover:bg-secondary-50',
              isSelected
                ? 'bg-primary-50 border-primary-600 text-primary-900'
                : 'border-transparent text-secondary-900 hover:border-secondary-300'
            )}
          >
            <div className="flex items-start justify-between">
              {/* Conversation content */}
              <div className="flex-1 min-w-0">
                {/* Title */}
                <div className={clsx(
                  'text-sm font-medium truncate',
                  isSelected ? 'text-primary-900' : 'text-secondary-900'
                )}>
                  {title}
                </div>
                
                {/* Since we don't have last_message or message_count from API, show simplified info */}
                <div className={clsx(
                  'text-xs mt-1',
                  isSelected ? 'text-primary-600' : 'text-secondary-500'
                )}>
                  Conversation
                </div>
              </div>
              
              {/* Timestamp */}
              <div className={clsx(
                'text-xs ml-2 flex-shrink-0',
                isSelected ? 'text-primary-600' : 'text-secondary-500'
              )}>
                {formatTimestamp(conversation.last_message_at)}
              </div>
            </div>
          </button>
        );
      })}
    </div>
  );
};

// Icon component
const ChatIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
  </svg>
); 