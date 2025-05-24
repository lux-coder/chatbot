import React from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { AuthGuard } from '@/components/auth';
import { FullPageLayout } from '@/components/layout';
import { ChatInterface } from '@/components/chat';
import { Loading } from '@/components/common';
import { useBots } from '@/hooks/useBots';
import { useChatHistory } from '@/hooks/useChat';

const ConversationChatPage: React.FC = () => {
  const router = useRouter();
  const { botId, conversationId } = router.query;
  const { bots, isLoading: isBotsLoading } = useBots();
  const { history, isLoading: isHistoryLoading } = useChatHistory(conversationId as string);

  const bot = bots?.find(b => b.id === botId);

  const handleBotChange = (newBotId: string) => {
    router.push(`/chat/${newBotId}`);
  };

  const handleConversationChange = (newConversationId: string) => {
    router.push(`/chat/${botId}/${newConversationId}`);
  };

  if (isBotsLoading || isHistoryLoading) {
    return (
      <>
        <Head>
          <title>Loading Conversation - Secure Chatbot</title>
        </Head>
        <FullPageLayout>
          <div className="h-screen flex items-center justify-center">
            <Loading size="lg" text="Loading conversation..." />
          </div>
        </FullPageLayout>
      </>
    );
  }

  if (!bot || !history) {
    return (
      <>
        <Head>
          <title>Conversation Not Found - Secure Chatbot</title>
        </Head>
        <FullPageLayout>
          <div className="h-screen flex items-center justify-center">
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-error-100">
                <ExclamationIcon className="h-6 w-6 text-error-600" />
              </div>
              <h1 className="mt-4 text-2xl font-bold text-secondary-900">
                {!bot ? 'Bot Not Found' : 'Conversation Not Found'}
              </h1>
              <p className="mt-2 text-sm text-secondary-600">
                {!bot 
                  ? "The bot you're trying to chat with doesn't exist or isn't available."
                  : "The conversation you're looking for doesn't exist or you don't have access to it."
                }
              </p>
              <div className="mt-6 space-x-3">
                <button
                  onClick={() => router.push('/chat')}
                  className="btn btn-primary"
                >
                  Go to Chat
                </button>
                {bot && (
                  <button
                    onClick={() => router.push(`/chat/${bot.id}`)}
                    className="btn btn-secondary"
                  >
                    Start New Chat with {bot.name}
                  </button>
                )}
              </div>
            </div>
          </div>
        </FullPageLayout>
      </>
    );
  }

  return (
    <>
      <Head>
        <title>{history.title} - {bot.name} - Secure Chatbot</title>
        <meta name="description" content={`Continue your conversation with ${bot.name}`} />
      </Head>

      <FullPageLayout>
        <div className="h-screen flex flex-col">
          <ChatInterface 
            className="flex-1"
            botId={botId as string}
            onBotChange={handleBotChange}
            onConversationChange={handleConversationChange}
          />
        </div>
      </FullPageLayout>
    </>
  );
};

// Icon component
const ExclamationIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z" />
  </svg>
);

export default function ConversationChat() {
  return (
    <AuthGuard>
      <ConversationChatPage />
    </AuthGuard>
  );
} 