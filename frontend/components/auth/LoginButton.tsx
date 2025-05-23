'use client';

import React from 'react';
import { useAuth } from '@/hooks/useAuth';
import type { ComponentProps } from '@/utils/types';

interface LoginButtonProps extends ComponentProps {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
  loginText?: string;
  logoutText?: string;
  loadingText?: string;
}

export const LoginButton: React.FC<LoginButtonProps> = ({
  variant = 'primary',
  size = 'md',
  showText = true,
  loginText = 'Log In',
  logoutText = 'Log Out',
  loadingText = 'Loading...',
  className,
}) => {
  const {
    isAuthenticated,
    isLoading,
    login,
    logout,
    error,
    getUserDisplayName,
    getUserInitials,
  } = useAuth();

  const handleClick = async () => {
    try {
      if (isAuthenticated) {
        await logout();
      } else {
        await login();
      }
    } catch (error) {
      console.error('Authentication action failed:', error);
    }
  };

  const buttonClasses = [
    'btn',
    `btn-${variant}`,
    size === 'sm' && 'px-3 py-1.5 text-sm',
    size === 'md' && 'px-4 py-2 text-sm',
    size === 'lg' && 'px-6 py-3 text-base',
    className,
  ].filter(Boolean).join(' ');

  if (isLoading) {
    return (
      <button
        className={buttonClasses}
        disabled
        aria-label="Loading authentication status"
      >
        <div className="spinner mr-2"></div>
        {showText && loadingText}
      </button>
    );
  }

  if (isAuthenticated) {
    return (
      <div className="flex items-center space-x-2">
        {showText && (
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
              {getUserInitials()}
            </div>
            <span className="text-sm text-secondary-700 hidden sm:inline">
              {getUserDisplayName()}
            </span>
          </div>
        )}
        
        <button
          onClick={handleClick}
          className={buttonClasses}
          aria-label={`Log out ${getUserDisplayName()}`}
        >
          {showText ? logoutText : (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          )}
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <button
        onClick={handleClick}
        className={buttonClasses}
        aria-label="Log in to your account"
      >
        {showText ? loginText : (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
          </svg>
        )}
      </button>
      
      {error && (
        <div className="text-xs text-error-600 max-w-xs">
          {error}
        </div>
      )}
    </div>
  );
}; 