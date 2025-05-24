import React from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { AuthGuard } from '@/components/auth';
import { Layout } from '@/components/layout';
import { BotForm } from '@/components/bot';
import { Loading } from '@/components/common';
import { useBots } from '@/hooks/useBots';

const EditBotPage: React.FC = () => {
  const router = useRouter();
  const { id } = router.query;
  const { bots, isLoading } = useBots();

  const bot = bots?.find(b => b.id === id);

  const handleCancel = () => {
    router.back();
  };

  if (isLoading) {
    return (
      <>
        <Head>
          <title>Edit Bot - Secure Chatbot</title>
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
              The bot you're looking for doesn't exist or you don't have permission to edit it.
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
        <title>Edit {bot.name} - Secure Chatbot</title>
        <meta name="description" content={`Edit your chatbot: ${bot.name}`} />
      </Head>

      <Layout>
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center space-x-2 text-sm text-secondary-600 mb-2">
              <Link href="/bots" className="hover:text-secondary-900">
                My Bots
              </Link>
              <ChevronRightIcon className="w-4 h-4" />
              <span>{bot.name}</span>
              <ChevronRightIcon className="w-4 h-4" />
              <span>Edit</span>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-secondary-900">
                  Edit {bot.name}
                </h1>
                <p className="mt-1 text-sm text-secondary-600">
                  Update your chatbot's configuration and personality settings.
                </p>
              </div>
              <div className="flex items-center space-x-3">
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  bot.is_published 
                    ? 'bg-success-100 text-success-800' 
                    : 'bg-warning-100 text-warning-800'
                }`}>
                  {bot.is_published ? 'Published' : 'Draft'}
                </span>
                <Link href={`/chat/${bot.id}`}>
                  <button className="btn btn-secondary">
                    <ChatIcon className="w-4 h-4 mr-2" />
                    Test Chat
                  </button>
                </Link>
              </div>
            </div>
          </div>

          {/* Form Card */}
          <div className="card p-8">
            <BotForm
              bot={bot}
              onCancel={handleCancel}
              submitLabel="Update Bot"
            />
          </div>

          {/* Bot Info */}
          <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Bot Statistics */}
            <div className="card p-6">
              <h3 className="text-lg font-medium text-secondary-900 mb-4">
                Bot Statistics
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-secondary-600">Created:</span>
                  <span className="text-secondary-900">
                    {new Date(bot.created_at).toLocaleDateString()}
                  </span>
                </div>
                {bot.published_at && (
                  <div className="flex justify-between">
                    <span className="text-secondary-600">Published:</span>
                    <span className="text-secondary-900">
                      {new Date(bot.published_at).toLocaleDateString()}
                    </span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-secondary-600">Status:</span>
                  <span className={`font-medium ${
                    bot.is_published ? 'text-success-600' : 'text-warning-600'
                  }`}>
                    {bot.is_published ? 'Published' : 'Draft'}
                  </span>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="card p-6">
              <h3 className="text-lg font-medium text-secondary-900 mb-4">
                Quick Actions
              </h3>
              <div className="space-y-3">
                <Link href={`/chat/${bot.id}`} className="block">
                  <div className="flex items-center p-3 rounded-lg hover:bg-secondary-50 transition-colors">
                    <ChatIcon className="w-5 h-5 text-primary-600 mr-3" />
                    <div>
                      <p className="text-sm font-medium text-secondary-900">Start Chat</p>
                      <p className="text-xs text-secondary-500">Test your bot in action</p>
                    </div>
                  </div>
                </Link>
                <Link href={`/bots/${bot.id}/chat`} className="block">
                  <div className="flex items-center p-3 rounded-lg hover:bg-secondary-50 transition-colors">
                    <HistoryIcon className="w-5 h-5 text-success-600 mr-3" />
                    <div>
                      <p className="text-sm font-medium text-secondary-900">View Conversations</p>
                      <p className="text-xs text-secondary-500">See past chat history</p>
                    </div>
                  </div>
                </Link>
              </div>
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

const HistoryIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

export default function EditBot() {
  return (
    <AuthGuard>
      <EditBotPage />
    </AuthGuard>
  );
} 