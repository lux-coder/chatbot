import React from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { AuthGuard } from '@/components/auth';
import { Layout } from '@/components/layout';
import { Button, Loading } from '@/components/common';
import { useAuth } from '@/hooks/useAuth';
import { useBots } from '@/hooks/useBots';
import { useTenant } from '@/hooks/useTenant';

const DashboardPage: React.FC = () => {
  const { getUserDisplayName, isAdmin, isModerator } = useAuth();
  const { bots, isLoading: isBotsLoading } = useBots();
  const { tenantInfo } = useTenant();

  // Calculate dashboard stats
  const totalBots = bots?.length || 0;
  const publishedBots = bots?.filter(bot => bot.is_published).length || 0;
  const draftBots = totalBots - publishedBots;
  const recentBots = bots?.slice(0, 3) || [];

  return (
    <>
      <Head>
        <title>Dashboard - Secure Chatbot</title>
        <meta name="description" content="Your chatbot dashboard overview" />
      </Head>

      <Layout>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-secondary-900">
                Welcome back, {getUserDisplayName()}!
              </h1>
              <p className="mt-1 text-sm text-secondary-600">
                Here's what's happening with your chatbots today.
              </p>
            </div>
            <div className="mt-4 sm:mt-0 flex space-x-3">
              <Link href="/bots/create">
                <Button variant="primary">
                  <PlusIcon className="w-4 h-4 mr-2" />
                  Create Bot
                </Button>
              </Link>
              <Link href="/chat">
                <Button variant="secondary">
                  <ChatIcon className="w-4 h-4 mr-2" />
                  Start Chat
                </Button>
              </Link>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                    <RobotIcon className="w-4 h-4 text-primary-600" />
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-secondary-500 truncate">
                      Total Bots
                    </dt>
                    <dd className="text-lg font-medium text-secondary-900">
                      {isBotsLoading ? <Loading size="sm" /> : totalBots}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-success-100 rounded-lg flex items-center justify-center">
                    <CheckIcon className="w-4 h-4 text-success-600" />
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-secondary-500 truncate">
                      Published
                    </dt>
                    <dd className="text-lg font-medium text-secondary-900">
                      {isBotsLoading ? <Loading size="sm" /> : publishedBots}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-warning-100 rounded-lg flex items-center justify-center">
                    <EditIcon className="w-4 h-4 text-warning-600" />
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-secondary-500 truncate">
                      Drafts
                    </dt>
                    <dd className="text-lg font-medium text-secondary-900">
                      {isBotsLoading ? <Loading size="sm" /> : draftBots}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-secondary-100 rounded-lg flex items-center justify-center">
                    <TenantIcon className="w-4 h-4 text-secondary-600" />
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-secondary-500 truncate">
                      Tenant
                    </dt>
                    <dd className="text-lg font-medium text-secondary-900">
                      {tenantInfo?.name || 'Default'}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions & Recent Activity */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Quick Actions */}
            <div className="card p-6">
              <h3 className="text-lg font-medium text-secondary-900 mb-4">
                Quick Actions
              </h3>
              <div className="space-y-3">
                <Link href="/bots/create" className="block">
                  <div className="flex items-center p-3 rounded-lg hover:bg-secondary-50 transition-colors">
                    <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center mr-3">
                      <PlusIcon className="w-4 h-4 text-primary-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-secondary-900">Create New Bot</p>
                      <p className="text-xs text-secondary-500">Set up a new chatbot instance</p>
                    </div>
                  </div>
                </Link>

                <Link href="/chat" className="block">
                  <div className="flex items-center p-3 rounded-lg hover:bg-secondary-50 transition-colors">
                    <div className="w-8 h-8 bg-success-100 rounded-lg flex items-center justify-center mr-3">
                      <ChatIcon className="w-4 h-4 text-success-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-secondary-900">Start Chatting</p>
                      <p className="text-xs text-secondary-500">Begin a conversation with your bots</p>
                    </div>
                  </div>
                </Link>

                <Link href="/bots" className="block">
                  <div className="flex items-center p-3 rounded-lg hover:bg-secondary-50 transition-colors">
                    <div className="w-8 h-8 bg-warning-100 rounded-lg flex items-center justify-center mr-3">
                      <SettingsIcon className="w-4 h-4 text-warning-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-secondary-900">Manage Bots</p>
                      <p className="text-xs text-secondary-500">Edit and configure your bots</p>
                    </div>
                  </div>
                </Link>

                {(isAdmin() || isModerator()) && (
                  <Link href="/settings" className="block">
                    <div className="flex items-center p-3 rounded-lg hover:bg-secondary-50 transition-colors">
                      <div className="w-8 h-8 bg-error-100 rounded-lg flex items-center justify-center mr-3">
                        <AdminIcon className="w-4 h-4 text-error-600" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-secondary-900">Admin Settings</p>
                        <p className="text-xs text-secondary-500">Configure application settings</p>
                      </div>
                    </div>
                  </Link>
                )}
              </div>
            </div>

            {/* Recent Bots */}
            <div className="card p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-secondary-900">
                  Recent Bots
                </h3>
                <Link href="/bots" className="text-sm text-primary-600 hover:text-primary-700">
                  View all
                </Link>
              </div>

              {isBotsLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loading size="md" text="Loading bots..." />
                </div>
              ) : recentBots.length > 0 ? (
                <div className="space-y-3">
                  {recentBots.map((bot) => (
                    <div key={bot.id} className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center mr-3">
                          <span className="text-xs font-medium text-primary-600">
                            {bot.icon || bot.name.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div>
                          <p className="text-sm font-medium text-secondary-900">{bot.name}</p>
                          <p className="text-xs text-secondary-500 capitalize">
                            {bot.style} • {bot.language}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          bot.is_published 
                            ? 'bg-success-100 text-success-800' 
                            : 'bg-warning-100 text-warning-800'
                        }`}>
                          {bot.is_published ? 'Published' : 'Draft'}
                        </span>
                        <Link href={`/chat/${bot.id}`}>
                          <Button variant="ghost" size="sm">
                            <ChatIcon className="w-3 h-3" />
                          </Button>
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-secondary-100">
                    <RobotIcon className="h-6 w-6 text-secondary-400" />
                  </div>
                  <h3 className="mt-4 text-sm font-medium text-secondary-900">No bots yet</h3>
                  <p className="mt-2 text-xs text-secondary-500">
                    Create your first bot to get started.
                  </p>
                  <div className="mt-4">
                    <Link href="/bots/create">
                      <Button variant="primary" size="sm">
                        Create Bot
                      </Button>
                    </Link>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* System Status */}
          <div className="card p-6">
            <h3 className="text-lg font-medium text-secondary-900 mb-4">
              System Status
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-success-400 rounded-full mr-2"></div>
                <span className="text-sm text-secondary-600">API Services</span>
              </div>
              <div className="flex items-center">
                <div className="w-2 h-2 bg-success-400 rounded-full mr-2"></div>
                <span className="text-sm text-secondary-600">Authentication</span>
              </div>
              <div className="flex items-center">
                <div className="w-2 h-2 bg-success-400 rounded-full mr-2"></div>
                <span className="text-sm text-secondary-600">AI Services</span>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    </>
  );
};

// Icon components
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

const CheckIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  </svg>
);

const EditIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
  </svg>
);

const SettingsIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
  </svg>
);

const AdminIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
  </svg>
);

const TenantIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
  </svg>
);

export default function Dashboard() {
  return (
    <AuthGuard>
      <DashboardPage />
    </AuthGuard>
  );
} 