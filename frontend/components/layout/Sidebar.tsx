'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { clsx } from 'clsx';
import { useAuth } from '@/hooks/useAuth';
import { useBots } from '@/hooks/useBots';
import type { ComponentProps } from '@/utils/types';

interface SidebarProps extends ComponentProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen = true,
  onClose,
  className,
}) => {
  const { isAuthenticated } = useAuth();
  const { bots } = useBots();
  const router = useRouter();

  const isActivePath = (path: string) => {
    return router.pathname === path || router.pathname.startsWith(path);
  };

  const mainNavigation = [
    {
      name: 'Dashboard',
      href: '/',
      icon: DashboardIcon,
      description: 'Overview and analytics',
    },
    {
      name: 'My Bots',
      href: '/bots',
      icon: RobotIcon,
      description: 'Manage your chatbots',
    },
    {
      name: 'Chat',
      href: '/chat',
      icon: ChatIcon,
      description: 'Start conversations',
    },
  ];

  if (!isAuthenticated) {
    return null;
  }

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-secondary-600 bg-opacity-75 md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div
        className={clsx(
          'fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-secondary-200 transform transition-transform duration-300 ease-in-out md:translate-x-0 md:static md:inset-0',
          isOpen ? 'translate-x-0' : '-translate-x-full',
          className
        )}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between h-16 px-4 border-b border-secondary-200">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">SC</span>
              </div>
              <span className="text-lg font-semibold text-secondary-900">
                Secure Chatbot
              </span>
            </div>
            
            {/* Close button for mobile */}
            <button
              type="button"
              className="md:hidden p-2 rounded-md text-secondary-400 hover:text-secondary-500 hover:bg-secondary-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
              onClick={onClose}
              aria-label="Close sidebar"
            >
              <CloseIcon className="h-5 w-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
            {/* Main navigation */}
            <div className="space-y-1">
              {mainNavigation.map((item) => {
                const Icon = item.icon;
                const isActive = isActivePath(item.href);
                
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={clsx(
                      'group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-200',
                      isActive
                        ? 'bg-primary-100 text-primary-700 border-r-2 border-primary-600'
                        : 'text-secondary-600 hover:text-secondary-900 hover:bg-secondary-50'
                    )}
                  >
                    <div onClick={onClose} className="flex items-center w-full">
                      <Icon
                        className={clsx(
                          'mr-3 h-5 w-5 transition-colors duration-200',
                          isActive
                            ? 'text-primary-600'
                            : 'text-secondary-400 group-hover:text-secondary-600'
                        )}
                      />
                      <div className="flex-1">
                        <div className="text-sm font-medium">{item.name}</div>
                        <div className="text-xs text-secondary-500">{item.description}</div>
                      </div>
                    </div>
                  </Link>
                );
              })}
            </div>

            {/* Quick actions */}
            <div className="pt-6 border-t border-secondary-200">
              <div className="px-3 py-2">
                <h3 className="text-xs font-semibold text-secondary-500 uppercase tracking-wider">
                  Quick Actions
                </h3>
              </div>
              <div className="mt-2 space-y-1">
                <Link
                  href="/bots/create"
                  className="group flex items-center px-3 py-2 text-sm font-medium text-secondary-600 rounded-lg hover:text-secondary-900 hover:bg-secondary-50 transition-colors duration-200"
                >
                  <div onClick={onClose} className="flex items-center w-full">
                    <PlusIcon className="mr-3 h-4 w-4 text-secondary-400 group-hover:text-secondary-600" />
                    Create New Bot
                  </div>
                </Link>
              </div>
            </div>

            {/* Recent bots */}
            {bots && bots.length > 0 && (
              <div className="pt-6 border-t border-secondary-200">
                <div className="px-3 py-2">
                  <h3 className="text-xs font-semibold text-secondary-500 uppercase tracking-wider">
                    Recent Bots
                  </h3>
                </div>
                <div className="mt-2 space-y-1">
                  {bots.slice(0, 3).map((bot) => (
                    <Link
                      key={bot.id}
                      href={`/chat/${bot.id}`}
                      className="group flex items-center px-3 py-2 text-sm font-medium text-secondary-600 rounded-lg hover:text-secondary-900 hover:bg-secondary-50 transition-colors duration-200"
                    >
                      <div onClick={onClose} className="flex items-center w-full">
                        <div className="mr-3 h-6 w-6 bg-primary-100 rounded-full flex items-center justify-center">
                          <span className="text-xs font-medium text-primary-600">
                            {bot.name.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div className="flex-1 truncate">
                          <div className="text-sm font-medium truncate">{bot.name}</div>
                          <div className="text-xs text-secondary-500 capitalize">
                            {bot.style} • {bot.language}
                          </div>
                        </div>
                        {bot.is_published && (
                          <div className="h-2 w-2 bg-success-400 rounded-full"></div>
                        )}
                      </div>
                    </Link>
                  ))}
                  
                  {bots.length > 3 && (
                    <Link
                      href="/bots"
                      className="group flex items-center px-3 py-2 text-sm font-medium text-primary-600 rounded-lg hover:text-primary-700 hover:bg-primary-50 transition-colors duration-200"
                    >
                      <div onClick={onClose} className="w-full">
                        <span className="text-xs">View all {bots.length} bots →</span>
                      </div>
                    </Link>
                  )}
                </div>
              </div>
            )}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-secondary-200">
            <div className="text-xs text-secondary-500 text-center">
              Secure Chatbot v1.0.0
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

// Icon components
const DashboardIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2 2z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5a2 2 0 012-2h4a2 2 0 012 2v4H8V5z" />
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

const PlusIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
  </svg>
);

const CloseIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
); 