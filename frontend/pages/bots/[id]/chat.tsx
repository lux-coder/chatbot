import React from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { AuthGuard } from '@/components/auth';
import { Layout } from '@/components/layout';
import { Loading } from '@/components/common';
import { useBots, useBotConversations } from '@/hooks/useBots';

const BotChatPage: React.FC = () => {
  const router = useRouter();
  const { id } = router.query;
  const { bots, isLoading: isBotsLoading } = useBots();
  const { conversations, isLoading: isConversationsLoading } = useBotConversations(id as string);

  const bot = bots?.find(b => b.id === id);

  if (isBotsLoading) {
    return (
      <>
        <Head>
          <title>Bot Conversations - Secure Chatbot</title>
        </Head>
        <Layout>
          <div className="flex items-center justify-center h-64">
            <Loading size="lg" text="Loading bot details..." />
          </div>
        </Layout>
      </>
    );
  }

  if (!bot) {
    return (
      <>
        <Head>
          <title>Bot Not Found - Secure Chatbot</title>
        </Head>
        <Layout>
          <div className="max-w-4xl mx-auto text-center py-12">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-error-100">
              <ExclamationIcon className="h-6 w-6 text-error-600" />
            </div>
            <h1 className="mt-4 text-2xl font-bold text-secondary-900">Bot Not Found</h1>
            <p className="mt-2 text-sm text-secondary-600">
              The bot you're looking for doesn't exist or you don't have permission to view it.
            </p>
            <div className="mt-6">
              <Link href="/bots" className="text-primary-600 hover:text-primary-700">
                ← Back to My Bots
              </Link>
            </div>
          </div>
        </Layout>
      </>
    );
  }

  return (
    <>
      <Head>
        <title>{bot.name} Conversations - Secure Chatbot</title>
        <meta name="description" content={`View conversations for ${bot.name}`} />
      </Head>

      <Layout>
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center space-x-2 text-sm text-secondary-600 mb-2">
              <Link href="/bots" className="hover:text-secondary-900">
                My Bots
              </Link>
              <ChevronRightIcon className="w-4 h-4" />
              <Link href={`/bots/${bot.id}/edit`} className="hover:text-secondary-900">
                {bot.name}
              </Link>
              <ChevronRightIcon className="w-4 h-4" />
              <span>Conversations</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                  <span className="text-lg font-medium text-primary-600">
                    {bot.icon || bot.name.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-secondary-900">
                    {bot.name} Conversations
                  </h1>
                  <p className="mt-1 text-sm text-secondary-600 capitalize">
                    {bot.style} • {bot.language} • {bot.is_published ? 'Published' : 'Draft'}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <Link href={`/chat/${bot.id}`}>
                  <button className="btn btn-primary">
                    <ChatIcon className="w-4 h-4 mr-2" />
                    New Chat
                  </button>
                </Link>
                <Link href={`/bots/${bot.id}/edit`}>
                  <button className="btn btn-secondary">
                    <EditIcon className="w-4 h-4 mr-2" />
                    Edit Bot
                  </button>
                </Link>
              </div>
            </div>
          </div>

          {/* Conversations List */}
          <div className="card">
            <div className="px-6 py-4 border-b border-secondary-200">
              <h2 className="text-lg font-medium text-secondary-900">
                Conversation History
              </h2>
              <p className="mt-1 text-sm text-secondary-600">
                All conversations with this bot
              </p>
            </div>

            <div className="p-6">
              {isConversationsLoading ? (
                <div className="flex items-center justify-center py-12">
                  <Loading size="lg" text="Loading conversations..." />
                </div>
              ) : conversations && conversations.conversations.length > 0 ? (
                <div className="space-y-4">
                  {conversations.conversations.map((conversation) => (
                    <div key={conversation.conversation_id} className="border border-secondary-200 rounded-lg p-4 hover:border-secondary-300 transition-colors">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <h3 className="text-sm font-medium text-secondary-900">
                            {conversation.title}
                          </h3>
                          <p className="text-xs text-secondary-500 mt-1">
                            Last active: {new Date(conversation.last_message_at).toLocaleString()}
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Link href={`/chat/${bot.id}/${conversation.conversation_id}`}>
                            <button className="btn btn-secondary btn-sm">
                              <ChatIcon className="w-3 h-3 mr-1" />
                              View
                            </button>
                          </Link>
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {/* Pagination info */}
                  <div className="mt-6 flex items-center justify-between text-sm text-secondary-600">
                    <span>
                      Showing {conversations.conversations.length} of {conversations.total} conversations
                    </span>
                    {conversations.total > conversations.conversations.length && (
                      <button className="text-primary-600 hover:text-primary-700">
                        Load more
                      </button>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-secondary-100">
                    <ChatIcon className="h-6 w-6 text-secondary-400" />
                  </div>
                  <h3 className="mt-4 text-lg font-medium text-secondary-900">No conversations yet</h3>
                  <p className="mt-2 text-sm text-secondary-600">
                    Start chatting with this bot to see conversations here.
                  </p>
                  <div className="mt-6">
                    <Link href={`/chat/${bot.id}`}>
                      <button className="btn btn-primary">
                        <ChatIcon className="w-4 h-4 mr-2" />
                        Start First Conversation
                      </button>
                    </Link>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Bot Stats */}
          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="card p-6 text-center">
              <div className="text-2xl font-bold text-primary-600">
                {conversations?.total || 0}
              </div>
              <div className="text-sm text-secondary-600">Total Conversations</div>
            </div>
            <div className="card p-6 text-center">
              <div className="text-2xl font-bold text-success-600">
                {bot.is_published ? 'Active' : 'Draft'}
              </div>
              <div className="text-sm text-secondary-600">Bot Status</div>
            </div>
            <div className="card p-6 text-center">
              <div className="text-2xl font-bold text-secondary-600">
                {new Date(bot.created_at).toLocaleDateString()}
              </div>
              <div className="text-sm text-secondary-600">Created</div>
            </div>
          </div>
        </div>
      </Layout>
    </>
  );
};

// Icon components
const ChevronRightIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
  </svg>
);

const ExclamationIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z" />
  </svg>
);

const ChatIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
  </svg>
);

const EditIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
  </svg>
);

export default function BotChat() {
  return (
    <AuthGuard>
      <BotChatPage />
    </AuthGuard>
  );
} 