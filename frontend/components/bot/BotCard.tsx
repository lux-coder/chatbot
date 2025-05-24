'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { clsx } from 'clsx';
import { Button } from '@/components/common';
import { useDeleteBot, usePublishBot } from '@/hooks/useBots';
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

interface BotCardProps extends ComponentProps {
  bot: Bot;
  onEdit?: (bot: Bot) => void;
  onDelete?: (botId: string) => void;
  onChat?: (botId: string) => void;
}

export const BotCard: React.FC<BotCardProps> = ({
  bot,
  onEdit,
  onDelete,
  onChat,
  className,
}) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const deleteBot = useDeleteBot();
  const publishBot = usePublishBot();

  const handleDelete = async () => {
    try {
      await deleteBot.mutateAsync(bot.id);
      onDelete?.(bot.id);
      setShowDeleteConfirm(false);
    } catch (error) {
      console.error('Failed to delete bot:', error);
    }
  };

  const handlePublish = async () => {
    try {
      await publishBot.mutateAsync(bot.id);
    } catch (error) {
      console.error('Failed to publish bot:', error);
    }
  };

  const handleEdit = () => {
    onEdit?.(bot);
    setIsMenuOpen(false);
  };

  const handleChat = () => {
    onChat?.(bot.id);
    setIsMenuOpen(false);
  };

  const getStatusColor = (status: boolean) => {
    return status ? 'bg-success-100 text-success-800' : 'bg-warning-100 text-warning-800';
  };

  const getStatusText = (status: boolean) => {
    return status ? 'Published' : 'Draft';
  };

  const getBotInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .substring(0, 2)
      .toUpperCase();
  };

  return (
    <div className={clsx('bg-white rounded-lg border border-secondary-200 hover:border-secondary-300 transition-colors duration-200 shadow-sm hover:shadow-md', className)}>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            {/* Bot Avatar */}
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
              {bot.icon ? (
                <img src={bot.icon} alt={bot.name} className="w-8 h-8 rounded" />
              ) : (
                <span className="text-primary-600 font-semibold text-sm">
                  {getBotInitials(bot.name)}
                </span>
              )}
            </div>

            {/* Bot Info */}
            <div>
              <h3 className="text-lg font-semibold text-secondary-900 line-clamp-1">
                {bot.name}
              </h3>
              <div className="flex items-center space-x-2 mt-1">
                <span className={clsx('inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium', getStatusColor(bot.is_published))}>
                  {getStatusText(bot.is_published)}
                </span>
              </div>
            </div>
          </div>

          {/* Actions Menu */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="p-2 text-secondary-400 hover:text-secondary-600 rounded-lg hover:bg-secondary-100 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-colors duration-200"
              aria-label="Bot actions"
            >
              <DotsVerticalIcon className="w-5 h-5" />
            </button>

            {isMenuOpen && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setIsMenuOpen(false)}
                />
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-secondary-200 z-20">
                  <div className="py-1">
                    <button
                      onClick={handleChat}
                      className="w-full text-left px-4 py-2 text-sm text-secondary-700 hover:bg-secondary-50 transition-colors duration-200"
                    >
                      <ChatIcon className="w-4 h-4 inline mr-2" />
                      Start Chat
                    </button>
                    <button
                      onClick={handleEdit}
                      className="w-full text-left px-4 py-2 text-sm text-secondary-700 hover:bg-secondary-50 transition-colors duration-200"
                    >
                      <EditIcon className="w-4 h-4 inline mr-2" />
                      Edit Bot
                    </button>
                    {!bot.is_published && (
                      <button
                        onClick={handlePublish}
                        disabled={publishBot.isLoading}
                        className="w-full text-left px-4 py-2 text-sm text-secondary-700 hover:bg-secondary-50 transition-colors duration-200 disabled:opacity-50"
                      >
                        <PublishIcon className="w-4 h-4 inline mr-2" />
                        {publishBot.isLoading ? 'Publishing...' : 'Publish'}
                      </button>
                    )}
                    <hr className="my-1" />
                    <button
                      onClick={() => {
                        setShowDeleteConfirm(true);
                        setIsMenuOpen(false);
                      }}
                      className="w-full text-left px-4 py-2 text-sm text-error-700 hover:bg-error-50 transition-colors duration-200"
                    >
                      <TrashIcon className="w-4 h-4 inline mr-2" />
                      Delete
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Bot Details */}
        <div className="space-y-2 mb-4">
          <div className="flex items-center text-sm text-secondary-600">
            <span className="font-medium mr-2">Style:</span>
            <span className="capitalize">{bot.style}</span>
          </div>
          <div className="flex items-center text-sm text-secondary-600">
            <span className="font-medium mr-2">Language:</span>
            <span className="capitalize">{bot.language}</span>
          </div>
          <div className="flex items-center text-sm text-secondary-600">
            <span className="font-medium mr-2">Created:</span>
            <span>{new Date(bot.created_at).toLocaleDateString()}</span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex space-x-2">
          <Link href={`/chat/${bot.id}`} className="flex-1">
            <Button variant="primary" size="sm" fullWidth>
              <ChatIcon className="w-4 h-4 mr-2" />
              Chat
            </Button>
          </Link>
          <Button
            variant="secondary"
            size="sm"
            onClick={handleEdit}
          >
            <EditIcon className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-lg p-6 max-w-sm w-full mx-4">
            <h3 className="text-lg font-semibold text-secondary-900 mb-2">
              Delete Bot
            </h3>
            <p className="text-secondary-600 mb-6">
              Are you sure you want to delete "{bot.name}"? This action cannot be undone.
            </p>
            <div className="flex space-x-3">
              <Button
                variant="danger"
                onClick={handleDelete}
                loading={deleteBot.isLoading}
                disabled={deleteBot.isLoading}
                fullWidth
              >
                Delete
              </Button>
              <Button
                variant="secondary"
                onClick={() => setShowDeleteConfirm(false)}
                disabled={deleteBot.isLoading}
                fullWidth
              >
                Cancel
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Icon components
const DotsVerticalIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01" />
  </svg>
);

const ChatIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
  </svg>
);

const EditIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
  </svg>
);

const TrashIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
  </svg>
);

const PublishIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
  </svg>
); 