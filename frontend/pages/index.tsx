import React from 'react';
import Head from 'next/head';
import { AuthGuard } from '@/components/auth/AuthGuard';
import { LoginButton } from '@/components/auth/LoginButton';
import { UserProfile } from '@/components/auth/UserProfile';
import { useAuth } from '@/hooks/useAuth';
import { useTenant } from '@/hooks/useTenant';
import { useBots } from '@/hooks/useBots';

const ApiTestDashboard: React.FC = () => {
  const { 
    isAuthenticated, 
    getUserDisplayName, 
    getUserRoles,
    isAdmin,
    isModerator 
  } = useAuth();

  // Phase 2: API Integration Tests
  const { tenantInfo, isLoading: isTenantLoading, error: tenantError } = useTenant();
  const { bots, isLoading: isBotsLoading, error: botsError } = useBots();

  return (
    <div className="min-h-screen bg-secondary-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-secondary-900 mb-2">
            🚀 Phase 2: API Integration Test
          </h1>
          <p className="text-secondary-600">
            Testing API client, tenant discovery, and bot management hooks
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Authentication Status Card */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-secondary-900 mb-4">
              Authentication Status
            </h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-secondary-600">Status:</span>
                <span className={`font-medium ${isAuthenticated ? 'text-success-600' : 'text-error-600'}`}>
                  {isAuthenticated ? '✅ Authenticated' : '❌ Not Authenticated'}
                </span>
              </div>
              
              {isAuthenticated && (
                <>
                  <div className="flex justify-between">
                    <span className="text-secondary-600">User:</span>
                    <span className="font-medium text-secondary-900">
                      {getUserDisplayName()}
                    </span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-secondary-600">Roles:</span>
                    <div className="flex flex-wrap gap-1">
                      {getUserRoles().map((role) => (
                        <span 
                          key={role}
                          className="px-2 py-0.5 bg-primary-100 text-primary-800 text-xs rounded"
                        >
                          {role}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-secondary-600">Admin:</span>
                    <span className={`font-medium ${isAdmin() ? 'text-success-600' : 'text-secondary-500'}`}>
                      {isAdmin() ? 'Yes' : 'No'}
                    </span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-secondary-600">Moderator:</span>
                    <span className={`font-medium ${isModerator() ? 'text-success-600' : 'text-secondary-500'}`}>
                      {isModerator() ? 'Yes' : 'No'}
                    </span>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* API Integration Status */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-secondary-900 mb-4">
              API Integration Status
            </h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-secondary-600">Tenant Discovery:</span>
                <span className={`font-medium ${!isTenantLoading && tenantInfo ? 'text-success-600' : 'text-warning-600'}`}>
                  {isTenantLoading ? '⏳ Loading...' : tenantInfo ? '✅ Connected' : '❌ Failed'}
                </span>
              </div>
              
              {tenantError && (
                <div className="text-error-600 text-sm">
                  Error: {tenantError.message}
                </div>
              )}
              
              {tenantInfo && (
                <>
                  <div className="flex justify-between">
                    <span className="text-secondary-600">Tenant ID:</span>
                    <span className="font-mono text-xs text-secondary-900">
                      {tenantInfo.tenant_id}
                    </span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-secondary-600">Tenant Name:</span>
                    <span className="font-medium text-secondary-900">
                      {tenantInfo.name || 'Default Tenant'}
                    </span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-secondary-600">Bot API:</span>
                    <span className={`font-medium ${!isBotsLoading && !botsError ? 'text-success-600' : 'text-warning-600'}`}>
                      {isBotsLoading ? '⏳ Loading...' : !botsError ? '✅ Connected' : '❌ Failed'}
                    </span>
                  </div>
                  
                  {botsError && (
                    <div className="text-error-600 text-sm">
                      Bot API Error: {botsError.message}
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>

        {/* Bot Management Section */}
        {isAuthenticated && tenantInfo && (
          <div className="mt-6">
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-secondary-900 mb-4">
                Bot Management API Test
              </h2>
              
              {isBotsLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="spinner mr-2"></div>
                  <span className="text-secondary-600">Loading bots...</span>
                </div>
              ) : botsError ? (
                <div className="bg-error-50 border border-error-200 rounded-lg p-4">
                  <p className="text-error-800">
                    Failed to load bots: {botsError.message}
                  </p>
                  <p className="text-error-600 text-sm mt-2">
                    This is expected if the backend is not running.
                  </p>
                </div>
              ) : (
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-secondary-600">Your Bots:</span>
                    <span className="font-medium text-secondary-900">
                      {bots?.length || 0} bots found
                    </span>
                  </div>
                  
                  {bots && bots.length > 0 ? (
                    <div className="space-y-2">
                      {bots.map((bot) => (
                        <div key={bot.id} className="bg-secondary-50 rounded-lg p-3">
                          <div className="flex justify-between items-center">
                            <div>
                              <h3 className="font-medium text-secondary-900">{bot.name}</h3>
                              <p className="text-sm text-secondary-600">
                                Style: {bot.style} | Language: {bot.language}
                              </p>
                            </div>
                            <div className="text-right">
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                bot.is_published 
                                  ? 'bg-success-100 text-success-800' 
                                  : 'bg-warning-100 text-warning-800'
                              }`}>
                                {bot.is_published ? 'Published' : 'Draft'}
                              </span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-secondary-600">
                      No bots found. Create your first bot to test the API!
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Phase 2 Features Checklist */}
        <div className="mt-6">
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-secondary-900 mb-4">
              ✅ Phase 2 Features Implemented
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex items-center text-success-600">
                  <span className="mr-2">✅</span>
                  <span>HTTP Client with Interceptors</span>
                </div>
                <div className="flex items-center text-success-600">
                  <span className="mr-2">✅</span>
                  <span>Tenant API Service</span>
                </div>
                <div className="flex items-center text-success-600">
                  <span className="mr-2">✅</span>
                  <span>Bot API Service</span>
                </div>
                <div className="flex items-center text-success-600">
                  <span className="mr-2">✅</span>
                  <span>Chat API Service</span>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center text-success-600">
                  <span className="mr-2">✅</span>
                  <span>React Query Integration</span>
                </div>
                <div className="flex items-center text-success-600">
                  <span className="mr-2">✅</span>
                  <span>Tenant Discovery Hook</span>
                </div>
                <div className="flex items-center text-success-600">
                  <span className="mr-2">✅</span>
                  <span>Bot Management Hooks</span>
                </div>
                <div className="flex items-center text-success-600">
                  <span className="mr-2">✅</span>
                  <span>Chat Hooks</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Next Steps */}
        <div className="mt-6">
          <div className="card p-6 bg-primary-50 border-primary-200">
            <h2 className="text-xl font-semibold text-primary-900 mb-4">
              🚀 Ready for Phase 3: Core UI Components
            </h2>
            <p className="text-primary-800 mb-4">
              Phase 2 API integration is complete! The frontend can now communicate with the backend.
            </p>
            <ul className="space-y-2 text-primary-700">
              <li>• HTTP client with authentication and tenant headers</li>
              <li>• Tenant discovery and management working</li>
              <li>• Bot CRUD operations available</li>
              <li>• Chat messaging infrastructure ready</li>
              <li>• React Query for efficient data management</li>
              <li>• Error handling and loading states</li>
            </ul>
          </div>
        </div>

        {/* Login/User Controls */}
        <div className="mt-6 flex justify-center">
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-secondary-900 mb-4 text-center">
              Authentication Controls
            </h2>
            <div className="flex flex-col items-center space-y-4">
              <LoginButton variant="primary" />
              {isAuthenticated && (
                <UserProfile 
                  showTenantInfo={true} 
                  showRoles={true} 
                  showAccountLink={true}
                  compact={true}
                />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const HomePage: React.FC = () => {
  return (
    <>
      <Head>
        <title>Secure Chatbot - Phase 2 API Integration</title>
        <meta name="description" content="Testing Phase 2 API Integration System" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <AuthGuard>
        <ApiTestDashboard />
      </AuthGuard>
    </>
  );
};

export default HomePage; 