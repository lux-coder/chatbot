import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { AuthGuard } from '@/components/auth';
import { Layout } from '@/components/layout';
import { Button } from '@/components/common';
import { useAuth } from '@/hooks/useAuth';
import { logger } from '@/utils/logger';

interface LogEvent {
  event: string;
  category: string;
  level: string;
  timestamp: string;
  userId?: string;
  tenantId?: string;
  sessionId?: string;
  data?: any;
  [key: string]: any;
}

const LogsDebugPage: React.FC = () => {
  const [events, setEvents] = useState<LogEvent[]>([]);
  const [filter, setFilter] = useState({
    category: 'all',
    level: 'all',
    search: '',
  });
  const [autoRefresh, setAutoRefresh] = useState(false);
  const { isAdmin } = useAuth();

  // Load events from logger
  const loadEvents = () => {
    const debugEvents = logger.getDebugEvents();
    setEvents(debugEvents.reverse()); // Show newest first
  };

  useEffect(() => {
    loadEvents();
  }, []);

  // Auto-refresh every 5 seconds if enabled
  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(loadEvents, 5000);
      return () => clearInterval(interval);
    }
    return undefined;
  }, [autoRefresh]);

  const clearLogs = () => {
    logger.clearDebugEvents();
    setEvents([]);
  };

  const exportLogs = () => {
    const dataStr = JSON.stringify(events, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `chat-logs-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  // Filter events
  const filteredEvents = events.filter((event) => {
    const matchesCategory = filter.category === 'all' || event.category === filter.category;
    const matchesLevel = filter.level === 'all' || event.level === filter.level;
    const matchesSearch = !filter.search || 
      event.event.toLowerCase().includes(filter.search.toLowerCase()) ||
      JSON.stringify(event.data || {}).toLowerCase().includes(filter.search.toLowerCase());
    
    return matchesCategory && matchesLevel && matchesSearch;
  });

  const categories = ['all', ...Array.from(new Set(events.map(e => e.category)))];
  const levels = ['all', 'debug', 'info', 'warn', 'error'];

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'error': return 'text-error-600 bg-error-50';
      case 'warn': return 'text-warning-600 bg-warning-50';
      case 'info': return 'text-primary-600 bg-primary-50';
      case 'debug': return 'text-secondary-600 bg-secondary-50';
      default: return 'text-secondary-600 bg-secondary-50';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'auth': return 'text-purple-600 bg-purple-50';
      case 'bot': return 'text-green-600 bg-green-50';
      case 'chat': return 'text-blue-600 bg-blue-50';
      case 'navigation': return 'text-indigo-600 bg-indigo-50';
      case 'error': return 'text-error-600 bg-error-50';
      case 'system': return 'text-secondary-600 bg-secondary-50';
      default: return 'text-secondary-600 bg-secondary-50';
    }
  };

  if (!isAdmin()) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-center">
            <h2 className="text-xl font-semibold text-secondary-900 mb-2">
              Access Denied
            </h2>
            <p className="text-secondary-600">
              You need administrator privileges to view debug logs.
            </p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <>
      <Head>
        <title>Debug Logs - Secure Chatbot</title>
        <meta name="description" content="Debug logs and monitoring dashboard" />
      </Head>

      <Layout>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-secondary-900">Debug Logs</h1>
              <p className="text-sm text-secondary-600">
                Real-time application events and debugging information
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm text-secondary-600">Auto-refresh</span>
              </label>
              <Button onClick={loadEvents} variant="secondary" size="sm">
                <RefreshIcon className="w-4 h-4 mr-2" />
                Refresh
              </Button>
              <Button onClick={exportLogs} variant="secondary" size="sm">
                <DownloadIcon className="w-4 h-4 mr-2" />
                Export
              </Button>
              <Button onClick={clearLogs} variant="danger" size="sm">
                <TrashIcon className="w-4 h-4 mr-2" />
                Clear
              </Button>
            </div>
          </div>

          {/* Filters */}
          <div className="card p-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Category
                </label>
                <select
                  value={filter.category}
                  onChange={(e) => setFilter(prev => ({ ...prev, category: e.target.value }))}
                  className="input w-full"
                >
                  {categories.map(category => (
                    <option key={category} value={category}>
                      {category.charAt(0).toUpperCase() + category.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Level
                </label>
                <select
                  value={filter.level}
                  onChange={(e) => setFilter(prev => ({ ...prev, level: e.target.value }))}
                  className="input w-full"
                >
                  {levels.map(level => (
                    <option key={level} value={level}>
                      {level.charAt(0).toUpperCase() + level.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Search
                </label>
                <input
                  type="text"
                  placeholder="Search events, data, or error messages..."
                  value={filter.search}
                  onChange={(e) => setFilter(prev => ({ ...prev, search: e.target.value }))}
                  className="input w-full"
                />
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="card p-4 text-center">
              <div className="text-2xl font-bold text-primary-600">{events.length}</div>
              <div className="text-sm text-secondary-600">Total Events</div>
            </div>
            <div className="card p-4 text-center">
              <div className="text-2xl font-bold text-error-600">
                {events.filter(e => e.level === 'error').length}
              </div>
              <div className="text-sm text-secondary-600">Errors</div>
            </div>
            <div className="card p-4 text-center">
              <div className="text-2xl font-bold text-warning-600">
                {events.filter(e => e.level === 'warn').length}
              </div>
              <div className="text-sm text-secondary-600">Warnings</div>
            </div>
            <div className="card p-4 text-center">
              <div className="text-2xl font-bold text-secondary-600">{filteredEvents.length}</div>
              <div className="text-sm text-secondary-600">Filtered</div>
            </div>
          </div>

          {/* Events List */}
          <div className="card">
            <div className="px-6 py-4 border-b border-secondary-200">
              <h2 className="text-lg font-medium text-secondary-900">
                Events ({filteredEvents.length})
              </h2>
            </div>
            <div className="divide-y divide-secondary-200 max-h-96 overflow-y-auto">
              {filteredEvents.length === 0 ? (
                <div className="p-8 text-center text-secondary-500">
                  No events match your current filters.
                </div>
              ) : (
                filteredEvents.map((event, index) => (
                  <div key={index} className="p-4 hover:bg-secondary-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getCategoryColor(event.category)}`}>
                            {event.category}
                          </span>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getLevelColor(event.level)}`}>
                            {event.level}
                          </span>
                          <span className="text-xs text-secondary-500">
                            {new Date(event.timestamp).toLocaleString()}
                          </span>
                        </div>
                        <div className="font-medium text-secondary-900 mb-1">
                          {event.event}
                        </div>
                        {event.data && Object.keys(event.data).length > 0 && (
                          <details className="mt-2">
                            <summary className="text-sm text-secondary-600 cursor-pointer hover:text-secondary-800">
                              View Details
                            </summary>
                            <pre className="mt-2 text-xs bg-secondary-50 p-2 rounded overflow-x-auto">
                              {JSON.stringify(event.data, null, 2)}
                            </pre>
                          </details>
                        )}
                      </div>
                      <div className="ml-4 text-right text-xs text-secondary-500">
                        {event.userId && (
                          <div>User: {event.userId.substring(0, 8)}...</div>
                        )}
                        {event.sessionId && (
                          <div>Session: {event.sessionId.substring(0, 8)}...</div>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </Layout>
    </>
  );
};

// Icon components
const RefreshIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
  </svg>
);

const DownloadIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
  </svg>
);

const TrashIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
  </svg>
);

export default function DebugLogs() {
  return (
    <AuthGuard>
      <LogsDebugPage />
    </AuthGuard>
  );
} 