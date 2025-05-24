import React from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { AuthGuard } from '@/components/auth';
import { Layout } from '@/components/layout';
import { BotManager } from '@/components/bot';

const BotsPage: React.FC = () => {
  const router = useRouter();

  const handleEditBot = (bot: any) => {
    router.push(`/bots/${bot.id}/edit`);
  };

  return (
    <>
      <Head>
        <title>My Bots - Secure Chatbot</title>
        <meta name="description" content="Manage your chatbot instances" />
      </Head>

      <Layout>
        <BotManager onEditBot={handleEditBot} />
      </Layout>
    </>
  );
};

export default function Bots() {
  return (
    <AuthGuard>
      <BotsPage />
    </AuthGuard>
  );
} 