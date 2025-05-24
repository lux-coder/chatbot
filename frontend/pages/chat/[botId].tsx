import React from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { AuthGuard } from '@/components/auth';
import { FullPageLayout } from '@/components/layout';
import { ChatInterface } from '@/components/chat';
import { Loading } from '@/components/common';
import { useBots } from '@/hooks/useBots';

const BotChatPage: React.FC = () => {
  const router = useRouter();
  const { botId } = router.query;
  const { bots, isLoading } = useBots();

  const bot = bots?.find(b => b.id === botId);

  const handleBotChange = (newBotId: string) => {
    router.push(`/chat/${newBotId}`);
  };

  if (isLoading) {
    return (
      <>
        <Head>
          <title>Chat - Secure Chatbot</title>
        </Head>
        <FullPageLayout>
          <div className="h-screen flex items-center justify-center">
            <Loading size="lg" text="Loading bot..." />
          </div>
        </FullPageLayout>
      </>
    );
  }

  if (botId && !bot) {
    return (
      <>
        <Head>
          <title>Bot Not Found - Secure Chatbot</title>
        </Head>
        <FullPageLayout>
          <div className="h-screen flex items-center justify-center">
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-error-100">
                <ExclamationIcon className="h-6 w-6 text-error-600" />
              </div>
              <h1 className="mt-4 text-2xl font-bold text-secondary-900">Bot Not Found</h1>
              <p className="mt-2 text-sm text-secondary-600">
                The bot you're trying to chat with doesn't exist or isn't available.
              </p>
              <div className="mt-6">
                <button
                  onClick={() => router.push('/chat')}
                  className="btn btn-primary"
                >
                  Choose Different Bot
                </button>
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
        <title>{bot ? `Chat with ${bot.name}` : 'Chat'} - Secure Chatbot</title>
        <meta name="description" content={bot ? `Chat with ${bot.name}` : 'Chat with your AI assistants'} />
      </Head>

      <FullPageLayout>
        <div className="h-screen flex flex-col">
          <ChatInterface 
            className="flex-1"
            botId={botId as string}
            onBotChange={handleBotChange}
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

export default function BotChat() {
  return (
    <AuthGuard>
      <BotChatPage />
    </AuthGuard>
  );
} 