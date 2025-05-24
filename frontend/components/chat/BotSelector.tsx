'use client';

import React, { useState } from 'react';
import { clsx } from 'clsx';
import type { ComponentProps } from '@/utils/types';

interface Bot {
  id: string;
  name: string;
  style: string;
  language: string;
  icon?: string;
  is_published: boolean;
}

interface BotSelectorProps extends ComponentProps {
  bots: Bot[];
  selectedBotId?: string | null;
  onBotSelect: (botId: string) => void;
}

export const BotSelector: React.FC<BotSelectorProps> = ({
  bots,
  selectedBotId,
  onBotSelect,
  className,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const selectedBot = bots.find(bot => bot.id === selectedBotId);
  const publishedBots = bots.filter(bot => bot.is_published);

  const handleBotSelect = (bot: Bot) => {
    onBotSelect(bot.id);
    setIsOpen(false);
  };

  return (
    <div className={clsx('relative', className)}>
      {/* Dropdown Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={clsx(
          'w-full flex items-center justify-between px-3 py-2 text-left bg-white border border-secondary-300 rounded-lg shadow-sm',
          'hover:bg-secondary-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
          'transition-colors duration-200'
        )}
      >
        <div className="flex items-center space-x-2 min-w-0 flex-1">
          {selectedBot ? (
            <>
              {/* Bot Icon */}
              <div className="flex-shrink-0 w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center">
                <span className="text-xs font-medium text-primary-600">
                  {selectedBot.icon || selectedBot.name.charAt(0).toUpperCase()}
                </span>
              </div>
              
              {/* Bot Info */}
              <div className="min-w-0 flex-1">
                <div className="text-sm font-medium text-secondary-900 truncate">
                  {selectedBot.name}
                </div>
                <div className="text-xs text-secondary-600 truncate capitalize">
                  {selectedBot.style} • {selectedBot.language}
                </div>
              </div>
            </>
          ) : (
            <div className="flex items-center space-x-2">
              <div className="w-6 h-6 bg-secondary-100 rounded-full flex items-center justify-center">
                <BotIcon className="w-3 h-3 text-secondary-400" />
              </div>
              <span className="text-sm text-secondary-600">Select a chatbot</span>
            </div>
          )}
        </div>

        {/* Dropdown Arrow */}
        <ChevronDownIcon 
          className={clsx(
            'w-4 h-4 text-secondary-400 transition-transform duration-200',
            isOpen && 'transform rotate-180'
          )}
        />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />

          {/* Dropdown Content */}
          <div className="absolute z-20 w-full mt-1 bg-white border border-secondary-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
            {publishedBots.length === 0 ? (
              <div className="p-4 text-center">
                <div className="mx-auto flex items-center justify-center h-8 w-8 rounded-full bg-secondary-100">
                  <BotIcon className="h-4 w-4 text-secondary-400" />
                </div>
                <p className="mt-2 text-sm text-secondary-600">
                  No published bots available
                </p>
                <p className="text-xs text-secondary-500">
                  Create and publish a bot to start chatting
                </p>
              </div>
            ) : (
              <div className="py-1">
                {publishedBots.map((bot) => {
                  const isSelected = bot.id === selectedBotId;
                  
                  return (
                    <button
                      key={bot.id}
                      onClick={() => handleBotSelect(bot)}
                      className={clsx(
                        'w-full flex items-center px-3 py-2 text-left hover:bg-secondary-50 transition-colors duration-200',
                        isSelected && 'bg-primary-50 text-primary-900'
                      )}
                    >
                      <div className="flex items-center space-x-2 w-full">
                        {/* Bot Icon */}
                        <div className={clsx(
                          'flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center',
                          isSelected 
                            ? 'bg-primary-100 text-primary-600' 
                            : 'bg-secondary-100 text-secondary-600'
                        )}>
                          <span className="text-xs font-medium">
                            {bot.icon || bot.name.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        
                        {/* Bot Info */}
                        <div className="min-w-0 flex-1">
                          <div className={clsx(
                            'text-sm font-medium truncate',
                            isSelected ? 'text-primary-900' : 'text-secondary-900'
                          )}>
                            {bot.name}
                          </div>
                          <div className={clsx(
                            'text-xs truncate capitalize',
                            isSelected ? 'text-primary-700' : 'text-secondary-600'
                          )}>
                            {bot.style} • {bot.language}
                          </div>
                        </div>

                        {/* Selected Indicator */}
                        {isSelected && (
                          <CheckIcon className="w-4 h-4 text-primary-600 flex-shrink-0" />
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

// Icon components
const BotIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2z" />
  </svg>
);

const ChevronDownIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
  </svg>
);

const CheckIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  </svg>
); 