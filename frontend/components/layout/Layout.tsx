'use client';

import React, { useState } from 'react';
import { clsx } from 'clsx';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { ErrorBoundary } from '@/components/common';
import { useAuth } from '@/hooks/useAuth';
import type { ComponentProps } from '@/utils/types';

interface LayoutProps extends ComponentProps {
  children: React.ReactNode;
  showSidebar?: boolean;
}

export const Layout: React.FC<LayoutProps> = ({
  children,
  showSidebar = true,
  className,
}) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const { isAuthenticated } = useAuth();

  const handleSidebarToggle = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const handleSidebarClose = () => {
    setIsSidebarOpen(false);
  };

  return (
    <div className={clsx('h-screen flex overflow-hidden bg-secondary-50', className)}>
      {/* Sidebar */}
      {showSidebar && isAuthenticated && (
        <Sidebar
          isOpen={isSidebarOpen}
          onClose={handleSidebarClose}
        />
      )}

      {/* Main content area */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Header */}
        <Header
          onMenuToggle={handleSidebarToggle}
          showMenuButton={showSidebar && isAuthenticated}
        />

        {/* Page content */}
        <main className="flex-1 relative overflow-y-auto focus:outline-none">
          <ErrorBoundary>
            <div className="py-6">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
                {children}
              </div>
            </div>
          </ErrorBoundary>
        </main>
      </div>
    </div>
  );
};

// Specialized layout variations
export const AuthenticatedLayout: React.FC<{ children: React.ReactNode }> = ({ 
  children 
}) => {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-secondary-50 flex items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-lg shadow-soft p-6 text-center">
          <h2 className="text-xl font-semibold text-secondary-900 mb-4">
            Authentication Required
          </h2>
          <p className="text-secondary-600 mb-4">
            Please log in to access this page.
          </p>
        </div>
      </div>
    );
  }

  return (
    <Layout>
      {children}
    </Layout>
  );
};

export const FullPageLayout: React.FC<{ children: React.ReactNode }> = ({ 
  children 
}) => (
  <Layout showSidebar={false}>
    {children}
  </Layout>
);

export const MinimalLayout: React.FC<{ children: React.ReactNode }> = ({ 
  children 
}) => (
  <div className="min-h-screen bg-white">
    <Header showMenuButton={false} />
    <main className="pt-16">
      {children}
    </main>
  </div>
); 