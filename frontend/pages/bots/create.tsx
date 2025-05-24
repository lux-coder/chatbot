import React from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { AuthGuard } from '@/components/auth';
import { Layout } from '@/components/layout';
import { BotForm } from '@/components/bot';

const CreateBotPage: React.FC = () => {
  const router = useRouter();

  const handleCancel = () => {
    router.back();
  };

  return (
    <>
      <Head>
        <title>Create Bot - Secure Chatbot</title>
        <meta name="description" content="Create a new chatbot instance" />
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
              <span>Create New Bot</span>
            </div>
            <h1 className="text-3xl font-bold text-secondary-900">
              Create New Chatbot
            </h1>
            <p className="mt-1 text-sm text-secondary-600">
              Set up a new chatbot instance with custom personality and language preferences.
            </p>
          </div>

          {/* Form Card */}
          <div className="card p-8">
            <BotForm
              onCancel={handleCancel}
              submitLabel="Create Bot"
            />
          </div>

          {/* Help Section */}
          <div className="mt-8 bg-primary-50 border border-primary-200 rounded-lg p-6">
            <h3 className="text-lg font-medium text-primary-900 mb-4">
              💡 Bot Creation Tips
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-primary-800">
              <div>
                <h4 className="font-medium mb-2">Choosing a Style:</h4>
                <ul className="space-y-1 text-primary-700">
                  <li>• <strong>Professional:</strong> Formal business communication</li>
                  <li>• <strong>Casual:</strong> Friendly, conversational tone</li>
                  <li>• <strong>Technical:</strong> Detailed, precise explanations</li>
                  <li>• <strong>Creative:</strong> Imaginative and artistic responses</li>
                  <li>• <strong>Supportive:</strong> Empathetic and encouraging</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium mb-2">Language Support:</h4>
                <ul className="space-y-1 text-primary-700">
                  <li>• Choose the primary language for your bot</li>
                  <li>• Bot responses will be in the selected language</li>
                  <li>• You can create multiple bots for different languages</li>
                  <li>• Language affects conversation style and tone</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    </>
  );
};

// Icon component
const ChevronRightIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
  </svg>
);

export default function CreateBot() {
  return (
    <AuthGuard>
      <CreateBotPage />
    </AuthGuard>
  );
} 