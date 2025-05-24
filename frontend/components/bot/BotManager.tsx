'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { clsx } from 'clsx';
import { Button, Input, Loading } from '@/components/common';
import { BotCard } from './BotCard';
import { useBots } from '@/hooks/useBots';
import { useAuth } from '@/hooks/useAuth';
import type { ComponentProps } from '@/utils/types';

interface Bot {
  id: string;
  name: string;
  style: string;
  language: string;
  icon?: string;
  is_published: boolean;
  published_at?: string;
  created_at: string;
}

interface BotManagerProps extends ComponentProps {
  onEditBot?: (bot: Bot) => void;
}

export const BotManager: React.FC<BotManagerProps> = ({
  onEditBot,
  className,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterPublished, setFilterPublished] = useState<'all' | 'published' | 'draft'>('all');
  const [sortBy, setSortBy] = useState<'name' | 'created' | 'updated'>('created');
  
  const { isAuthenticated } = useAuth();
  const { bots, isLoading, error, refetch } = useBots();

  // Filter and sort bots
  const filteredBots = React.useMemo(() => {
    if (!bots) return [];

    let filtered = bots.filter((bot) => {
      const matchesSearch = bot.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           bot.style.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           bot.language.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesFilter = filterPublished === 'all' ||
                           (filterPublished === 'published' && bot.is_published) ||
                           (filterPublished === 'draft' && !bot.is_published);
      
      return matchesSearch && matchesFilter;
    });

    // Sort the filtered results
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'created':
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        case 'updated':
          const aUpdated = a.published_at || a.created_at;
          const bUpdated = b.published_at || b.created_at;
          return new Date(bUpdated).getTime() - new Date(aUpdated).getTime();
        default:
          return 0;
      }
    });

    return filtered;
  }, [bots, searchTerm, filterPublished, sortBy]);

  const handleDeleteBot = () => {
    // The BotCard handles the actual deletion, we just need to refresh
    refetch();
  };

  const handleChatBot = () => {
    // Navigation is handled by the BotCard component
  };

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <p className="text-secondary-600">Please log in to manage your chatbots.</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loading size="lg" text="Loading your chatbots..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="mb-4">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-error-100">
              <ExclamationIcon className="h-6 w-6 text-error-600" />
            </div>
          </div>
          <h3 className="text-lg font-medium text-secondary-900 mb-2">
            Failed to load chatbots
          </h3>
          <p className="text-secondary-600 mb-4">
            There was an error loading your chatbots. Please try again.
          </p>
          <Button onClick={() => refetch()} variant="primary">
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className={clsx('space-y-6', className)}>
      {/* Header Section */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900">My Chatbots</h1>
          <p className="mt-1 text-sm text-secondary-600">
            Create and manage your AI chatbot instances
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <Link href="/bots/create">
            <Button variant="primary" size="lg">
              <PlusIcon className="w-5 h-5 mr-2" />
              Create New Bot
            </Button>
          </Link>
        </div>
      </div>

      {/* Search and Filter Section */}
      <div className="bg-white rounded-lg border border-secondary-200 p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div>
            <Input
              placeholder="Search chatbots..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              startIcon={<SearchIcon className="w-4 h-4" />}
            />
          </div>

          {/* Filter by Status */}
          <div>
            <select
              value={filterPublished}
              onChange={(e) => setFilterPublished(e.target.value as typeof filterPublished)}
              className="w-full p-2 border border-secondary-300 rounded-lg bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="all">All Status</option>
              <option value="published">Published</option>
              <option value="draft">Draft</option>
            </select>
          </div>

          {/* Sort By */}
          <div>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
              className="w-full p-2 border border-secondary-300 rounded-lg bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="created">Sort by Created</option>
              <option value="name">Sort by Name</option>
              <option value="updated">Sort by Updated</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results Summary */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-secondary-600">
          {filteredBots.length === 0 ? (
            'No chatbots found'
          ) : (
            `Showing ${filteredBots.length} of ${bots?.length || 0} chatbots`
          )}
        </p>
        
        {filteredBots.length > 0 && (
          <div className="flex items-center space-x-2 text-sm text-secondary-600">
            <span>View:</span>
            <button className="text-primary-600 hover:text-primary-700">Grid</button>
            <span>|</span>
            <button className="text-secondary-500 hover:text-secondary-700">List</button>
          </div>
        )}
      </div>

      {/* Bots Grid */}
      {filteredBots.length === 0 ? (
        <div className="text-center py-12">
          {searchTerm || filterPublished !== 'all' ? (
            // No results for search/filter
            <div>
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-secondary-100">
                <SearchIcon className="h-6 w-6 text-secondary-400" />
              </div>
              <h3 className="mt-4 text-lg font-medium text-secondary-900">No chatbots found</h3>
              <p className="mt-2 text-sm text-secondary-600">
                Try adjusting your search or filter criteria.
              </p>
              <div className="mt-4">
                <Button
                  variant="secondary"
                  onClick={() => {
                    setSearchTerm('');
                    setFilterPublished('all');
                  }}
                >
                  Clear Filters
                </Button>
              </div>
            </div>
          ) : (
            // No bots at all
            <div>
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-primary-100">
                <RobotIcon className="h-6 w-6 text-primary-600" />
              </div>
              <h3 className="mt-4 text-lg font-medium text-secondary-900">No chatbots yet</h3>
              <p className="mt-2 text-sm text-secondary-600">
                Get started by creating your first chatbot instance.
              </p>
              <div className="mt-4">
                <Link href="/bots/create">
                  <Button variant="primary">
                    <PlusIcon className="w-4 h-4 mr-2" />
                    Create Your First Bot
                  </Button>
                </Link>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredBots.map((bot) => (
            <BotCard
              key={bot.id}
              bot={bot}
              {...(onEditBot && { onEdit: onEditBot })}
              onDelete={handleDeleteBot}
              onChat={handleChatBot}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// Icon components
const PlusIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
  </svg>
);

const SearchIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
  </svg>
);

const ExclamationIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z" />
  </svg>
);

const RobotIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2z" />
  </svg>
); 