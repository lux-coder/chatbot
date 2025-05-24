import React, { useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { LoginButton } from '@/components/auth';
import { useAuth } from '@/hooks/useAuth';

const HomePage: React.FC = () => {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      // Redirect authenticated users to dashboard
      router.replace('/dashboard');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <>
        <Head>
          <title>Secure Chatbot</title>
          <meta name="description" content="Your AI-powered chatbot platform" />
        </Head>
        <div className="min-h-screen flex items-center justify-center bg-secondary-50">
          <div className="text-center">
            <div className="spinner mb-4"></div>
            <p className="text-secondary-600">Loading...</p>
          </div>
        </div>
      </>
    );
  }

  if (isAuthenticated) {
    // This should not be reached due to the redirect above, but just in case
    return (
      <>
        <Head>
          <title>Secure Chatbot</title>
        </Head>
        <div className="min-h-screen flex items-center justify-center bg-secondary-50">
          <div className="text-center">
            <div className="spinner mb-4"></div>
            <p className="text-secondary-600">Redirecting to dashboard...</p>
          </div>
        </div>
      </>
    );
  }

  // Landing page for unauthenticated users
  return (
    <>
      <Head>
        <title>Secure Chatbot - AI-Powered Conversations</title>
        <meta name="description" content="Create and manage intelligent chatbots with our secure, multi-tenant platform" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50">
        {/* Header */}
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">SC</span>
                </div>
                <span className="text-xl font-bold text-secondary-900">Secure Chatbot</span>
              </div>
              <div className="flex items-center space-x-4">
                <button className="text-secondary-600 hover:text-secondary-900 font-medium">
                  Features
                </button>
                <button className="text-secondary-600 hover:text-secondary-900 font-medium">
                  About
                </button>
                <LoginButton />
              </div>
            </div>
          </div>
        </header>

        {/* Hero Section */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <h1 className="text-4xl sm:text-6xl font-bold text-secondary-900 mb-6">
              Build Intelligent
              <span className="text-primary-600 block">Chatbots</span>
            </h1>
            <p className="text-xl text-secondary-600 max-w-3xl mx-auto mb-8">
              Create, customize, and deploy AI-powered chatbots with our secure, 
              enterprise-grade platform. Choose from multiple AI models and 
              personalize your bot's personality and responses.
            </p>
            
            <div className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-4">
              <LoginButton 
                variant="primary" 
                size="lg"
                loginText="Get Started"
              />
              <button className="btn btn-secondary btn-lg">
                Learn More
              </button>
            </div>
          </div>

          {/* Features */}
          <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="card p-8 text-center hover:shadow-medium transition-shadow">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <RobotIcon className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-secondary-900 mb-2">
                Custom Personalities
              </h3>
              <p className="text-secondary-600">
                Create chatbots with unique personalities, conversation styles, 
                and language preferences to match your brand.
              </p>
            </div>

            <div className="card p-8 text-center hover:shadow-medium transition-shadow">
              <div className="w-12 h-12 bg-success-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <SecurityIcon className="w-6 h-6 text-success-600" />
              </div>
              <h3 className="text-xl font-semibold text-secondary-900 mb-2">
                Enterprise Security
              </h3>
              <p className="text-secondary-600">
                Multi-tenant architecture with advanced security features, 
                authentication, and data isolation.
              </p>
            </div>

            <div className="card p-8 text-center hover:shadow-medium transition-shadow">
              <div className="w-12 h-12 bg-warning-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <AIIcon className="w-6 h-6 text-warning-600" />
              </div>
              <h3 className="text-xl font-semibold text-secondary-900 mb-2">
                Multiple AI Models
              </h3>
              <p className="text-secondary-600">
                Choose between OpenAI GPT and local Llama models for 
                optimal performance and privacy.
              </p>
            </div>
          </div>

          {/* Stats */}
          <div className="mt-20 bg-white rounded-2xl shadow-large p-8">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
              <div>
                <div className="text-3xl font-bold text-primary-600">99.9%</div>
                <div className="text-secondary-600">Uptime</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-success-600">5+</div>
                <div className="text-secondary-600">AI Models</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-warning-600">8</div>
                <div className="text-secondary-600">Languages</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-error-600">24/7</div>
                <div className="text-secondary-600">Support</div>
              </div>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="bg-secondary-900 text-white py-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              <div>
                <div className="flex items-center space-x-2 mb-4">
                  <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold text-sm">SC</span>
                  </div>
                  <span className="text-xl font-bold">Secure Chatbot</span>
                </div>
                <p className="text-secondary-300 text-sm">
                  Building the future of conversational AI with security and 
                  customization at the forefront.
                </p>
              </div>
              
              <div>
                <h4 className="font-semibold mb-4">Product</h4>
                <div className="space-y-2 text-sm text-secondary-300">
                  <div>Features</div>
                  <div>Pricing</div>
                  <div>Documentation</div>
                  <div>API Reference</div>
                </div>
              </div>
              
              <div>
                <h4 className="font-semibold mb-4">Company</h4>
                <div className="space-y-2 text-sm text-secondary-300">
                  <div>About</div>
                  <div>Blog</div>
                  <div>Careers</div>
                  <div>Contact</div>
                </div>
              </div>
              
              <div>
                <h4 className="font-semibold mb-4">Support</h4>
                <div className="space-y-2 text-sm text-secondary-300">
                  <div>Help Center</div>
                  <div>Community</div>
                  <div>Status</div>
                  <div>Security</div>
                </div>
              </div>
            </div>
            
            <div className="border-t border-secondary-700 mt-8 pt-8 text-center text-sm text-secondary-300">
              © 2024 Secure Chatbot. All rights reserved.
            </div>
          </div>
        </footer>
      </div>
    </>
  );
};

// Icon components
const RobotIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2z" />
  </svg>
);

const SecurityIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
  </svg>
);

const AIIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
  </svg>
);

export default HomePage; 