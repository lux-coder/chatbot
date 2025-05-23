'use client';

import React, { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import type { ComponentProps } from '@/utils/types';

interface UserProfileProps extends ComponentProps {
  showTenantInfo?: boolean;
  showRoles?: boolean;
  showAccountLink?: boolean;
  compact?: boolean;
}

export const UserProfile: React.FC<UserProfileProps> = ({
  showTenantInfo = true,
  showRoles = false,
  showAccountLink = true,
  compact = false,
  className,
}) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  
  const {
    isAuthenticated,
    user,
    tenant,
    getUserDisplayName,
    getUserInitials,
    getUserRoles,
    getTenantDisplayName,
    isTenantActive,
    getAccountUrl,
    logout,
    isAdmin,
    isModerator,
  } = useAuth();

  if (!isAuthenticated || !user) {
    return null;
  }

  const handleAccountClick = () => {
    const accountUrl = getAccountUrl();
    if (accountUrl) {
      window.open(accountUrl, '_blank');
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  if (compact) {
    return (
      <div className={`relative ${className || ''}`}>
        <button
          onClick={() => setIsDropdownOpen(!isDropdownOpen)}
          className="flex items-center space-x-2 p-2 rounded-lg hover:bg-secondary-100 transition-colors"
          aria-label="User menu"
        >
          <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
            {getUserInitials()}
          </div>
          <span className="text-sm font-medium text-secondary-700 hidden sm:inline">
            {getUserDisplayName()}
          </span>
          <svg className="w-4 h-4 text-secondary-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </button>

        {isDropdownOpen && (
          <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-large border border-secondary-200 z-50">
            <div className="p-4 border-b border-secondary-200">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-600 text-white rounded-full flex items-center justify-center font-medium">
                  {getUserInitials()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-secondary-900 truncate">
                    {getUserDisplayName()}
                  </p>
                  <p className="text-xs text-secondary-500 truncate">
                    {user.email}
                  </p>
                </div>
              </div>
            </div>

            <div className="p-2">
              {showTenantInfo && tenant && (
                <div className="px-3 py-2 text-xs text-secondary-600">
                  <div className="flex items-center justify-between">
                    <span>Tenant:</span>
                    <span className="font-medium">{getTenantDisplayName()}</span>
                  </div>
                  <div className="flex items-center justify-between mt-1">
                    <span>Status:</span>
                    <span className={`font-medium ${isTenantActive() ? 'text-success-600' : 'text-error-600'}`}>
                      {isTenantActive() ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
              )}

              {showRoles && getUserRoles().length > 0 && (
                <div className="px-3 py-2 border-t border-secondary-100">
                  <p className="text-xs text-secondary-500 mb-1">Roles:</p>
                  <div className="flex flex-wrap gap-1">
                    {getUserRoles().map((role) => (
                      <span
                        key={role}
                        className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-primary-100 text-primary-800"
                      >
                        {role}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="border-t border-secondary-100 mt-2 pt-2">
                {showAccountLink && (
                  <button
                    onClick={handleAccountClick}
                    className="w-full text-left px-3 py-2 text-sm text-secondary-700 hover:bg-secondary-50 rounded transition-colors"
                  >
                    Manage Account
                  </button>
                )}
                <button
                  onClick={handleLogout}
                  className="w-full text-left px-3 py-2 text-sm text-error-700 hover:bg-error-50 rounded transition-colors"
                >
                  Sign Out
                </button>
              </div>
            </div>
          </div>
        )}

        {isDropdownOpen && (
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsDropdownOpen(false)}
          />
        )}
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-soft border border-secondary-200 p-6 ${className || ''}`}>
      <div className="flex items-start space-x-4">
        <div className="w-16 h-16 bg-primary-600 text-white rounded-full flex items-center justify-center text-xl font-bold">
          {getUserInitials()}
        </div>
        
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-secondary-900 truncate">
            {getUserDisplayName()}
          </h3>
          <p className="text-sm text-secondary-600 truncate mb-2">
            {user.email}
          </p>
          
          {(isAdmin() || isModerator()) && (
            <div className="flex items-center space-x-2 mb-2">
              {isAdmin() && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-error-100 text-error-800">
                  Admin
                </span>
              )}
              {isModerator() && !isAdmin() && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-warning-100 text-warning-800">
                  Moderator
                </span>
              )}
            </div>
          )}

          {showTenantInfo && tenant && (
            <div className="bg-secondary-50 rounded-lg p-3 mb-4">
              <h4 className="text-sm font-medium text-secondary-900 mb-2">
                Tenant Information
              </h4>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-secondary-600">Name:</span>
                  <span className="text-secondary-900 font-medium">
                    {getTenantDisplayName()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-secondary-600">Status:</span>
                  <span className={`font-medium ${isTenantActive() ? 'text-success-600' : 'text-error-600'}`}>
                    {isTenantActive() ? 'Active' : 'Inactive'}
                  </span>
                </div>
                {tenant.tenant_id && (
                  <div className="flex justify-between">
                    <span className="text-secondary-600">ID:</span>
                    <span className="text-secondary-900 font-mono text-xs">
                      {tenant.tenant_id}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {showRoles && getUserRoles().length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-medium text-secondary-900 mb-2">
                Roles & Permissions
              </h4>
              <div className="flex flex-wrap gap-2">
                {getUserRoles().map((role) => (
                  <span
                    key={role}
                    className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
                  >
                    {role}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="flex space-x-3">
            {showAccountLink && (
              <button
                onClick={handleAccountClick}
                className="btn btn-secondary btn-sm"
              >
                Manage Account
              </button>
            )}
            <button
              onClick={handleLogout}
              className="btn btn-ghost btn-sm text-error-600 hover:bg-error-50"
            >
              Sign Out
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}; 