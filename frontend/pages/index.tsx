import React from 'react';
import Head from 'next/head';
import { AuthGuard } from '@/components/auth/AuthGuard';
import { LoginButton } from '@/components/auth/LoginButton';
import { UserProfile } from '@/components/auth/UserProfile';
import { useAuth } from '@/hooks/useAuth';

const TestDashboard: React.FC = () => {
  const { 
    isAuthenticated, 
    getUserDisplayName, 
    getUserRoles,
    tenant,
    isAdmin,
    isModerator 
  } = useAuth();

  return (
    <div className="min-h-screen bg-secondary-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-secondary-900 mb-2">
            🚀 Phase 1 Authentication Test
          </h1>
          <p className="text-secondary-600">
            Testing Keycloak integration, authentication context, and components
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
                  
                  {tenant && (
                    <div className="flex justify-between">
                      <span className="text-secondary-600">Tenant:</span>
                      <span className="font-medium text-secondary-900">
                        {tenant.name || tenant.tenant_id}
                      </span>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>

          {/* Login/Logout Controls */}
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-secondary-900 mb-4">
              Authentication Controls
            </h2>
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-medium text-secondary-700 mb-2">
                  Login Button Component:
                </h3>
                <LoginButton variant="primary" />
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-secondary-700 mb-2">
                  Compact Login Button:
                </h3>
                <LoginButton variant="secondary" size="sm" />
              </div>
            </div>
          </div>
        </div>

        {/* User Profile Component (only when authenticated) */}
        {isAuthenticated && (
          <div className="mt-6">
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-secondary-900 mb-4">
                User Profile Component
              </h2>
              <UserProfile 
                showTenantInfo={true} 
                showRoles={true} 
                showAccountLink={true}
              />
            </div>
          </div>
        )}

        {/* Phase 1 Feature Checklist */}
        <div className="mt-6">
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-secondary-900 mb-4">
              ✅ Phase 1 Features Implemented
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex items-center text-success-600">
                  <span className="mr-2">✅</span>
                  <span>Keycloak Integration</span>
                </div>
                <div className="flex items-center text-success-600">
                  <span className="mr-2">✅</span>
                  <span>Authentication Context</span>
                </div>
                <div className="flex items-center text-success-600">
                  <span className="mr-2">✅</span>
                  <span>JWT Token Management</span>
                </div>
                <div className="flex items-center text-success-600">
                  <span className="mr-2">✅</span>
                  <span>Role-based Access Control</span>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center text-success-600">
                  <span className="mr-2">✅</span>
                  <span>AuthGuard Component</span>
                </div>
                <div className="flex items-center text-success-600">
                  <span className="mr-2">✅</span>
                  <span>LoginButton Component</span>
                </div>
                <div className="flex items-center text-success-600">
                  <span className="mr-2">✅</span>
                  <span>UserProfile Component</span>
                </div>
                <div className="flex items-center text-success-600">
                  <span className="mr-2">✅</span>
                  <span>Multi-tenant Support</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Next Steps */}
        <div className="mt-6">
          <div className="card p-6 bg-primary-50 border-primary-200">
            <h2 className="text-xl font-semibold text-primary-900 mb-4">
              🚀 Ready for Phase 2: API Integration
            </h2>
            <p className="text-primary-800 mb-4">
              Phase 1 authentication system is complete! Next steps include:
            </p>
            <ul className="space-y-2 text-primary-700">
              <li>• HTTP Client with authentication interceptors</li>
              <li>• API service modules for chat, bots, and tenant management</li>
              <li>• React Query hooks for data fetching</li>
              <li>• Error handling and retry logic</li>
            </ul>
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
        <title>Secure Chatbot - Phase 1 Test</title>
        <meta name="description" content="Testing Phase 1 Authentication System" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <AuthGuard>
        <TestDashboard />
      </AuthGuard>
    </>
  );
};

export default HomePage; 