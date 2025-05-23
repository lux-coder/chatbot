'use client';

import React from 'react';
import { useAuth } from '@/hooks/useAuth';
import type { ComponentProps } from '@/utils/types';

interface AuthGuardProps extends ComponentProps {
  children: React.ReactNode;
  roles?: string[];
  fallback?: React.ReactNode;
  loginComponent?: React.ReactNode;
  unauthorizedComponent?: React.ReactNode;
}

export const AuthGuard: React.FC<AuthGuardProps> = ({
  children,
  roles = [],
  fallback,
  loginComponent,
  unauthorizedComponent,
  className,
}) => {
  const {
    isAuthenticated,
    isLoading,
    hasRoles,
    login,
    error,
    getUserDisplayName,
  } = useAuth();

  // Show loading state
  if (isLoading) {
    return (
      <div className={`flex items-center justify-center min-h-screen ${className || ''}`}>
        <div className="text-center">
          <div className="spinner mb-4"></div>
          <p className="text-secondary-600">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // Show login if not authenticated
  if (!isAuthenticated) {
    if (loginComponent) {
      return <>{loginComponent}</>;
    }

    if (fallback) {
      return <>{fallback}</>;
    }

    return (
      <div className={`flex items-center justify-center min-h-screen ${className || ''}`}>
        <div className="text-center max-w-md">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-secondary-900 mb-2">
              Authentication Required
            </h1>
            <p className="text-secondary-600">
              Please log in to access this application.
            </p>
          </div>
          
          {error && (
            <div className="mb-4 p-3 bg-error-50 border border-error-200 rounded-lg">
              <p className="text-error-800 text-sm">{error}</p>
            </div>
          )}
          
          <button
            onClick={login}
            className="btn btn-primary"
            disabled={isLoading}
          >
            {isLoading ? 'Logging in...' : 'Log In'}
          </button>
        </div>
      </div>
    );
  }

  // Check roles if specified
  if (roles.length > 0 && !hasRoles(roles)) {
    if (unauthorizedComponent) {
      return <>{unauthorizedComponent}</>;
    }

    if (fallback) {
      return <>{fallback}</>;
    }

    return (
      <div className={`flex items-center justify-center min-h-screen ${className || ''}`}>
        <div className="text-center max-w-md">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-error-700 mb-2">
              Access Denied
            </h1>
            <p className="text-secondary-600 mb-4">
              You don't have permission to access this page.
            </p>
            <p className="text-sm text-secondary-500">
              Logged in as: {getUserDisplayName()}
            </p>
          </div>
          
          <div className="space-y-2">
            <p className="text-sm text-secondary-600">
              Required roles: {roles.join(', ')}
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Render children if authenticated and authorized
  return <>{children}</>;
};

// Higher-order component version
export const withAuthGuard = <P extends object>(
  Component: React.ComponentType<P>,
  options: {
    roles?: string[];
    fallback?: React.ReactNode;
    loginComponent?: React.ReactNode;
    unauthorizedComponent?: React.ReactNode;
  } = {}
) => {
  const AuthGuardedComponent = (props: P) => (
    <AuthGuard {...options}>
      <Component {...props} />
    </AuthGuard>
  );

  AuthGuardedComponent.displayName = `withAuthGuard(${Component.displayName || Component.name})`;
  
  return AuthGuardedComponent;
}; 