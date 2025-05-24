import React from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { AuthGuard } from '@/components/auth';
import { Layout } from '@/components/layout';
import { Button } from '@/components/common';
import { useAuth } from '@/hooks/useAuth';
import { useTenant } from '@/hooks/useTenant';
import { useBots } from '@/hooks/useBots';

const ProfilePage: React.FC = () => {
  const { 
    user, 
    getUserDisplayName, 
    getUserInitials,
    getUserRoles,
    isAdmin,
    isModerator,
    getAccountUrl 
  } = useAuth();
  
  const { tenantInfo } = useTenant();
  const { bots } = useBots();

  const handleManageAccount = () => {
    const accountUrl = getAccountUrl();
    if (accountUrl) {
      window.open(accountUrl, '_blank');
    }
  };

  // Calculate user statistics
  const totalBots = bots?.length || 0;
  const publishedBots = bots?.filter(bot => bot.is_published).length || 0;
  const draftBots = totalBots - publishedBots;

  return (
    <>
      <Head>
        <title>Profile - Secure Chatbot</title>
        <meta name="description" content="Manage your profile and account settings" />
      </Head>

      <Layout>
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-secondary-900">Profile</h1>
              <p className="mt-1 text-sm text-secondary-600">
                Manage your account information and preferences
              </p>
            </div>
            <Button onClick={handleManageAccount} variant="secondary">
              <ExternalLinkIcon className="w-4 h-4 mr-2" />
              Manage Account
            </Button>
          </div>

          {/* Profile Information */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* User Profile Card */}
            <div className="lg:col-span-2">
              <div className="card p-6">
                <div className="flex items-start space-x-6">
                  {/* Avatar */}
                  <div className="w-20 h-20 bg-primary-600 text-white rounded-full flex items-center justify-center text-2xl font-bold">
                    {getUserInitials()}
                  </div>
                  
                  {/* User Info */}
                  <div className="flex-1">
                    <h2 className="text-2xl font-bold text-secondary-900">
                      {getUserDisplayName()}
                    </h2>
                    <p className="text-secondary-600">{user?.email}</p>
                    
                    {/* Roles */}
                    <div className="mt-4">
                      <h3 className="text-sm font-medium text-secondary-700 mb-2">Roles</h3>
                      <div className="flex flex-wrap gap-2">
                        {getUserRoles().map((role) => (
                          <span
                            key={role}
                            className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
                          >
                            {role}
                          </span>
                        ))}
                        {isAdmin() && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-error-100 text-error-800">
                            Administrator
                          </span>
                        )}
                        {isModerator() && !isAdmin() && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-warning-100 text-warning-800">
                            Moderator
                          </span>
                        )}
                      </div>
                    </div>

                    {/* User Details */}
                    <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-secondary-700">
                          Username
                        </label>
                        <p className="mt-1 text-sm text-secondary-900">
                          {user?.username || 'Not set'}
                        </p>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-secondary-700">
                          Name
                        </label>
                        <p className="mt-1 text-sm text-secondary-900">
                          {user?.firstName || user?.lastName 
                            ? `${user?.firstName || ''} ${user?.lastName || ''}`.trim()
                            : 'Not set'
                          }
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Statistics Card */}
            <div className="space-y-6">
              <div className="card p-6">
                <h3 className="text-lg font-medium text-secondary-900 mb-4">Statistics</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-secondary-600">Total Bots</span>
                    <span className="text-sm font-medium text-secondary-900">{totalBots}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-secondary-600">Published</span>
                    <span className="text-sm font-medium text-success-600">{publishedBots}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-secondary-600">Drafts</span>
                    <span className="text-sm font-medium text-warning-600">{draftBots}</span>
                  </div>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="card p-6">
                <h3 className="text-lg font-medium text-secondary-900 mb-4">Quick Actions</h3>
                <div className="space-y-3">
                  <Link href="/bots/create" className="block">
                    <div className="flex items-center p-3 rounded-lg hover:bg-secondary-50 transition-colors">
                      <PlusIcon className="w-5 h-5 text-primary-600 mr-3" />
                      <span className="text-sm font-medium text-secondary-900">Create Bot</span>
                    </div>
                  </Link>
                  <Link href="/bots" className="block">
                    <div className="flex items-center p-3 rounded-lg hover:bg-secondary-50 transition-colors">
                      <RobotIcon className="w-5 h-5 text-success-600 mr-3" />
                      <span className="text-sm font-medium text-secondary-900">Manage Bots</span>
                    </div>
                  </Link>
                  <Link href="/chat" className="block">
                    <div className="flex items-center p-3 rounded-lg hover:bg-secondary-50 transition-colors">
                      <ChatIcon className="w-5 h-5 text-warning-600 mr-3" />
                      <span className="text-sm font-medium text-secondary-900">Start Chat</span>
                    </div>
                  </Link>
                </div>
              </div>
            </div>
          </div>

          {/* Tenant Information */}
          {tenantInfo && (
            <div className="card p-6">
              <h3 className="text-lg font-medium text-secondary-900 mb-4">
                Organization Information
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700">
                    Organization Name
                  </label>
                  <p className="mt-1 text-sm text-secondary-900">
                    {tenantInfo.name || 'Default Organization'}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700">
                    Tenant ID
                  </label>
                  <p className="mt-1 text-sm text-secondary-900 font-mono">
                    {tenantInfo.tenant_id}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700">
                    Status
                  </label>
                  <p className="mt-1">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      tenantInfo.is_active 
                        ? 'bg-success-100 text-success-800' 
                        : 'bg-error-100 text-error-800'
                    }`}>
                      {tenantInfo.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Account Management */}
          <div className="card p-6">
            <h3 className="text-lg font-medium text-secondary-900 mb-4">
              Account Management
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium text-secondary-900">Keycloak Account</h4>
                  <p className="text-sm text-secondary-600">
                    Manage your password, security settings, and authentication methods
                  </p>
                </div>
                <Button onClick={handleManageAccount} variant="secondary">
                  Manage
                </Button>
              </div>
              
              <div className="border-t border-secondary-200 pt-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-secondary-900">Application Settings</h4>
                    <p className="text-sm text-secondary-600">
                      Configure application preferences and notifications
                    </p>
                  </div>
                  <Link href="/settings">
                    <Button variant="secondary">
                      Settings
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    </>
  );
};

// Icon components
const ExternalLinkIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
  </svg>
);

const PlusIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
  </svg>
);

const RobotIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2z" />
  </svg>
);

const ChatIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
  </svg>
);

export default function Profile() {
  return (
    <AuthGuard>
      <ProfilePage />
    </AuthGuard>
  );
} 