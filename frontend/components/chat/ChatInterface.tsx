'use client';

import React, { useState, useEffect, useRef } from 'react';
import { clsx } from 'clsx';
import { MessageList } from '@/components/chat/MessageList';
import { MessageInput } from '@/components/chat/MessageInput';
import { ConversationList } from '@/components/chat/ConversationList';
import { BotSelector } from '@/components/chat/BotSelector';
import { Button, Loading } from '@/components/common';
import { useChatManager } from '@/hooks/useChat';
import { useBots } from '@/hooks/useBots';
import { useAuth } from '@/hooks/useAuth';
import { ChatMessageRequest } from '@/api/chat';
import type { ComponentProps } from '@/utils/types';

interface ChatInterfaceProps extends ComponentProps {
  botId?: string;
  onBotChange?: (botId: string) => void;
  onConversationChange?: (conversationId: string) => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  botId,
  onBotChange,
  onConversationChange,
  className,
}) => {
  const [selectedBotId, setSelectedBotId] = useState<string | null>(botId || null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  const { isAuthenticated } = useAuth();
  const { bots, isLoading: isBotsLoading } = useBots();
  
  const {
    selectedConversationId,
    selectConversation,
    startNewConversation,
    sendMessage,
    conversations,
    history,
    isLoadingHistory,
  } = useChatManager(selectedBotId || '');

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [history?.messages]);

  // Handle bot selection
  const handleBotSelect = (botId: string) => {
    setSelectedBotId(botId);
    onBotChange?.(botId);
  };

  // Handle conversation selection
  const handleConversationSelect = (conversationId: string) => {
    selectConversation(conversationId);
    onConversationChange?.(conversationId);
    setIsSidebarOpen(false); // Close sidebar on mobile
  };

  // Handle new conversation
  const handleNewConversation = async () => {
    if (!selectedBotId) return;
    
    setIsLoading(true);
    try {
      await startNewConversation();
      setIsSidebarOpen(false); // Close sidebar on mobile
    } finally {
      setIsLoading(false);
    }
  };

  // Handle message sending
  const handleSendMessage = async (message: string) => {
    if (!selectedBotId || !message.trim()) return;

    setIsLoading(true);
    try {
      const requestPayload: ChatMessageRequest = {
        message: message.trim(),
        chatbot_instance_id: selectedBotId,
        ...(selectedConversationId && { conversation_id: selectedConversationId }),
      };
      await sendMessage.mutateAsync(requestPayload);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <h3 className="text-lg font-medium text-secondary-900 mb-2">
            Authentication Required
          </h3>
          <p className="text-secondary-600">
            Please log in to start chatting with your bots.
          </p>
        </div>
      </div>
    );
  }

  if (isBotsLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loading size="lg" text="Loading your chatbots..." />
      </div>
    );
  }

  if (!bots || bots.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center max-w-md">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-primary-100">
            <RobotIcon className="h-6 w-6 text-primary-600" />
          </div>
          <h3 className="mt-4 text-lg font-medium text-secondary-900">No chatbots available</h3>
          <p className="mt-2 text-sm text-secondary-600">
            Create your first chatbot to start having conversations.
          </p>
          <div className="mt-4">
            <Button
              variant="primary"
              onClick={() => window.location.href = '/bots/create'}
            >
              Create Your First Bot
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={clsx('flex h-full bg-secondary-50', className)}>
      {/* Sidebar - Conversations */}
      <div className={clsx(
        'fixed inset-y-0 left-0 z-50 w-80 bg-white border-r border-secondary-200 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0',
        isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
      )}>
        <div className="flex flex-col h-full">
          {/* Sidebar Header */}
          <div className="flex items-center justify-between p-4 border-b border-secondary-200">
            <h2 className="text-lg font-semibold text-secondary-900">Conversations</h2>
            <button
              type="button"
              className="lg:hidden p-2 rounded-md text-secondary-400 hover:text-secondary-500 hover:bg-secondary-100"
              onClick={() => setIsSidebarOpen(false)}
            >
              <CloseIcon className="h-5 w-5" />
            </button>
          </div>

          {/* Bot Selector */}
          <div className="p-4 border-b border-secondary-200">
            <BotSelector
              bots={bots}
              selectedBotId={selectedBotId}
              onBotSelect={handleBotSelect}
            />
          </div>

          {/* New Conversation Button */}
          {selectedBotId && (
            <div className="p-4 border-b border-secondary-200">
              <Button
                variant="primary"
                fullWidth
                onClick={handleNewConversation}
                loading={isLoading}
                disabled={isLoading}
              >
                <PlusIcon className="w-4 h-4 mr-2" />
                New Conversation
              </Button>
            </div>
          )}

          {/* Conversation List */}
          <div className="flex-1 overflow-y-auto">
            {selectedBotId ? (
              <ConversationList
                conversations={conversations?.conversations || []}
                selectedConversationId={selectedConversationId || undefined}
                onConversationSelect={handleConversationSelect}
                isLoading={false}
              />
            ) : (
              <div className="p-4 text-center text-secondary-500">
                <p>Select a bot to view conversations</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Overlay for mobile */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-secondary-600 bg-opacity-75 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Chat Header */}
        <div className="bg-white border-b border-secondary-200 px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {/* Mobile menu button */}
              <button
                type="button"
                className="lg:hidden p-2 rounded-md text-secondary-400 hover:text-secondary-500 hover:bg-secondary-100"
                onClick={() => setIsSidebarOpen(true)}
              >
                <MenuIcon className="h-5 w-5" />
              </button>

              {/* Current bot info */}
              {selectedBotId && (
                <div className="flex items-center space-x-2">
                  {(() => {
                    const bot = bots.find(b => b.id === selectedBotId);
                    return bot ? (
                      <>
                        <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                          <span className="text-sm font-medium text-primary-600">
                            {bot.icon || bot.name.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div>
                          <h1 className="text-lg font-semibold text-secondary-900">{bot.name}</h1>
                          <p className="text-sm text-secondary-600 capitalize">
                            {bot.style} • {bot.language}
                          </p>
                        </div>
                      </>
                    ) : null;
                  })()}
                </div>
              )}
            </div>

            {/* Chat actions */}
            <div className="flex items-center space-x-2">
              {selectedConversationId && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleNewConversation}
                  disabled={isLoading}
                >
                  <PlusIcon className="w-4 h-4" />
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto">
          {selectedBotId ? (
            isLoadingHistory ? (
              <div className="flex items-center justify-center h-full">
                <Loading size="lg" text="Loading conversation..." />
              </div>
            ) : history && history.messages.length > 0 ? (
              <>
                <MessageList
                  messages={history.messages}
                  isLoading={sendMessage.isLoading}
                />
                <div ref={messagesEndRef} />
              </>
            ) : (
              <div className="flex items-center justify-center h-full">
                <div className="text-center max-w-md">
                  <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-primary-100">
                    <ChatIcon className="h-6 w-6 text-primary-600" />
                  </div>
                  <h3 className="mt-4 text-lg font-medium text-secondary-900">
                    Start a conversation
                  </h3>
                  <p className="mt-2 text-sm text-secondary-600">
                    Send a message to begin chatting with your bot.
                  </p>
                </div>
              </div>
            )
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center max-w-md">
                <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-secondary-100">
                  <RobotIcon className="h-6 w-6 text-secondary-400" />
                </div>
                <h3 className="mt-4 text-lg font-medium text-secondary-900">
                  Select a chatbot
                </h3>
                <p className="mt-2 text-sm text-secondary-600">
                  Choose a bot from the sidebar to start chatting.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Message Input */}
        {selectedBotId && (
          <div className="border-t border-secondary-200 bg-white">
            <MessageInput
              onSendMessage={handleSendMessage}
              disabled={isLoading || sendMessage.isLoading}
              placeholder={`Message ${bots.find(b => b.id === selectedBotId)?.name || 'bot'}...`}
            />
          </div>
        )}
      </div>
    </div>
  );
};

// Icon components
const MenuIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
  </svg>
);

const CloseIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
);

const PlusIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
  </svg>
);

const ChatIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
  </svg>
);

const RobotIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2z" />
  </svg>
); 