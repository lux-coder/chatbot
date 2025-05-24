import React, { useState } from 'react';
import Head from 'next/head';
import { AuthGuard } from '@/components/auth';
import { Layout } from '@/components/layout';
import { Button } from '@/components/common';
import { useAuth } from '@/hooks/useAuth';
import { useTenant } from '@/hooks/useTenant';

const SettingsPage: React.FC = () => {
  const { isAdmin, isModerator } = useAuth();
  const { tenantInfo } = useTenant();

  // Settings state
  const [settings, setSettings] = useState({
    theme: 'light',
    notifications: {
      email: true,
      browser: true,
      mobile: false,
    },
    privacy: {
      analytics: true,
      errorReporting: true,
    },
    chat: {
      autoSave: true,
      messageHistory: 50,
      typingIndicator: true,
    },
    ai: {
      defaultModel: 'openai',
      temperature: 0.7,
      maxTokens: 1000,
    },
  });

  const [adminSettings, setAdminSettings] = useState({
    userRegistration: true,
    publicBots: false,
    rateLimit: 100,
    sessionTimeout: 30,
  });

  const handleSettingChange = (category: string, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...(prev[category as keyof typeof prev] as object) || {},
        [key]: value,
      },
    }));
  };

  const handleAdminSettingChange = (key: string, value: any) => {
    setAdminSettings(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleSaveSettings = () => {
    // TODO: Implement settings save to backend
    console.log('Saving settings:', settings);
    alert('Settings saved successfully!');
  };

  const handleSaveAdminSettings = () => {
    // TODO: Implement admin settings save to backend
    console.log('Saving admin settings:', adminSettings);
    alert('Admin settings saved successfully!');
  };

  return (
    <>
      <Head>
        <title>Settings - Secure Chatbot</title>
        <meta name="description" content="Configure your application settings and preferences" />
      </Head>

      <Layout>
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Header */}
          <div>
            <h1 className="text-3xl font-bold text-secondary-900">Settings</h1>
            <p className="mt-1 text-sm text-secondary-600">
              Configure your application preferences and system settings
            </p>
          </div>

          {/* User Settings */}
          <div className="space-y-6">
            {/* Appearance */}
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-secondary-900 mb-4">Appearance</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Theme
                  </label>
                  <select
                    value={settings.theme}
                    onChange={(e) => setSettings(prev => ({ ...prev, theme: e.target.value }))}
                    className="input w-full max-w-xs"
                  >
                    <option value="light">Light</option>
                    <option value="dark">Dark</option>
                    <option value="auto">Auto (System)</option>
                  </select>
                  <p className="text-xs text-secondary-500 mt-1">
                    Choose your preferred theme for the application
                  </p>
                </div>
              </div>
            </div>

            {/* Notifications */}
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-secondary-900 mb-4">Notifications</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-secondary-900">Email Notifications</h3>
                    <p className="text-xs text-secondary-500">Receive updates via email</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings.notifications.email}
                    onChange={(e) => handleSettingChange('notifications', 'email', e.target.checked)}
                    className="rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-secondary-900">Browser Notifications</h3>
                    <p className="text-xs text-secondary-500">Show notifications in your browser</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings.notifications.browser}
                    onChange={(e) => handleSettingChange('notifications', 'browser', e.target.checked)}
                    className="rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-secondary-900">Mobile Push</h3>
                    <p className="text-xs text-secondary-500">Receive push notifications on mobile</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings.notifications.mobile}
                    onChange={(e) => handleSettingChange('notifications', 'mobile', e.target.checked)}
                    className="rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
                  />
                </div>
              </div>
            </div>

            {/* Chat Settings */}
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-secondary-900 mb-4">Chat Preferences</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-secondary-900">Auto-save Conversations</h3>
                    <p className="text-xs text-secondary-500">Automatically save chat history</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings.chat.autoSave}
                    onChange={(e) => handleSettingChange('chat', 'autoSave', e.target.checked)}
                    className="rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-secondary-900">Show Typing Indicator</h3>
                    <p className="text-xs text-secondary-500">Display when AI is responding</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings.chat.typingIndicator}
                    onChange={(e) => handleSettingChange('chat', 'typingIndicator', e.target.checked)}
                    className="rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Message History Limit
                  </label>
                  <input
                    type="number"
                    min="10"
                    max="200"
                    value={settings.chat.messageHistory}
                    onChange={(e) => handleSettingChange('chat', 'messageHistory', parseInt(e.target.value))}
                    className="input w-32"
                  />
                  <p className="text-xs text-secondary-500 mt-1">
                    Number of messages to keep in conversation history
                  </p>
                </div>
              </div>
            </div>

            {/* AI Settings */}
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-secondary-900 mb-4">AI Preferences</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Default AI Model
                  </label>
                  <select
                    value={settings.ai.defaultModel}
                    onChange={(e) => handleSettingChange('ai', 'defaultModel', e.target.value)}
                    className="input w-full max-w-xs"
                  >
                    <option value="openai">OpenAI GPT</option>
                    <option value="llama">Llama (Local)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Response Creativity (Temperature: {settings.ai.temperature})
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={settings.ai.temperature}
                    onChange={(e) => handleSettingChange('ai', 'temperature', parseFloat(e.target.value))}
                    className="w-full max-w-xs"
                  />
                  <div className="flex justify-between text-xs text-secondary-500 max-w-xs">
                    <span>Conservative</span>
                    <span>Creative</span>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Max Response Length (Tokens)
                  </label>
                  <input
                    type="number"
                    min="100"
                    max="4000"
                    step="100"
                    value={settings.ai.maxTokens}
                    onChange={(e) => handleSettingChange('ai', 'maxTokens', parseInt(e.target.value))}
                    className="input w-32"
                  />
                </div>
              </div>
            </div>

            {/* Privacy */}
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-secondary-900 mb-4">Privacy & Analytics</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-secondary-900">Usage Analytics</h3>
                    <p className="text-xs text-secondary-500">Help improve the application with usage data</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings.privacy.analytics}
                    onChange={(e) => handleSettingChange('privacy', 'analytics', e.target.checked)}
                    className="rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-secondary-900">Error Reporting</h3>
                    <p className="text-xs text-secondary-500">Automatically report errors to help fix issues</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings.privacy.errorReporting}
                    onChange={(e) => handleSettingChange('privacy', 'errorReporting', e.target.checked)}
                    className="rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
                  />
                </div>
              </div>
            </div>

            {/* Save Button */}
            <div className="flex justify-end">
              <Button onClick={handleSaveSettings} variant="primary">
                Save Settings
              </Button>
            </div>
          </div>

          {/* Admin Settings */}
          {(isAdmin() || isModerator()) && (
            <div className="border-t border-secondary-200 pt-8 space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-secondary-900 flex items-center">
                  <AdminIcon className="w-6 h-6 mr-2 text-error-600" />
                  Administrative Settings
                </h2>
                <p className="mt-1 text-sm text-secondary-600">
                  System-wide configuration options (Admin/Moderator only)
                </p>
              </div>

              {/* System Configuration */}
              <div className="card p-6">
                <h3 className="text-xl font-semibold text-secondary-900 mb-4">System Configuration</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium text-secondary-900">Allow User Registration</h4>
                      <p className="text-xs text-secondary-500">Enable new users to register accounts</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={adminSettings.userRegistration}
                      onChange={(e) => handleAdminSettingChange('userRegistration', e.target.checked)}
                      className="rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium text-secondary-900">Public Bot Gallery</h4>
                      <p className="text-xs text-secondary-500">Allow users to share bots publicly</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={adminSettings.publicBots}
                      onChange={(e) => handleAdminSettingChange('publicBots', e.target.checked)}
                      className="rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-2">
                      Rate Limit (requests per minute)
                    </label>
                    <input
                      type="number"
                      min="10"
                      max="1000"
                      value={adminSettings.rateLimit}
                      onChange={(e) => handleAdminSettingChange('rateLimit', parseInt(e.target.value))}
                      className="input w-32"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-2">
                      Session Timeout (minutes)
                    </label>
                    <input
                      type="number"
                      min="5"
                      max="480"
                      value={adminSettings.sessionTimeout}
                      onChange={(e) => handleAdminSettingChange('sessionTimeout', parseInt(e.target.value))}
                      className="input w-32"
                    />
                  </div>
                </div>
              </div>

              {/* Tenant Information */}
              {tenantInfo && (
                <div className="card p-6">
                  <h3 className="text-xl font-semibold text-secondary-900 mb-4">Tenant Information</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-secondary-700">Tenant ID</label>
                      <p className="text-sm text-secondary-900 font-mono">{tenantInfo.tenant_id}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-secondary-700">Organization Name</label>
                      <p className="text-sm text-secondary-900">{tenantInfo.name || 'Not set'}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-secondary-700">Status</label>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        tenantInfo.is_active 
                          ? 'bg-success-100 text-success-800' 
                          : 'bg-error-100 text-error-800'
                      }`}>
                        {tenantInfo.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Save Admin Settings */}
              <div className="flex justify-end">
                <Button onClick={handleSaveAdminSettings} variant="danger">
                  Save Admin Settings
                </Button>
              </div>
            </div>
          )}
        </div>
      </Layout>
    </>
  );
};

// Icon component
const AdminIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
  </svg>
);

export default function Settings() {
  return (
    <AuthGuard>
      <SettingsPage />
    </AuthGuard>
  );
} 