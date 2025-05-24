import React from 'react';
import Head from 'next/head';
import { AuthGuard } from '@/components/auth';
import { FullPageLayout } from '@/components/layout';
import { ChatInterface } from '@/components/chat';

const ChatPage: React.FC = () => {
  return (
    <>
      <Head>
        <title>Chat - Secure Chatbot</title>
        <meta name="description" content="Chat with your AI assistants" />
      </Head>

      <FullPageLayout>
        <div className="h-screen flex flex-col">
          <ChatInterface className="flex-1" />
        </div>
      </FullPageLayout>
    </>
  );
};

export default function Chat() {
  return (
    <AuthGuard>
      <ChatPage />
    </AuthGuard>
  );
} 