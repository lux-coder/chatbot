import type { AppProps } from 'next/app';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';
import { Toaster } from 'react-hot-toast';
import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import { AuthProvider } from '@/auth/authContext';
import { logger } from '@/utils/logger';
import '@/styles/globals.css';

export default function MyApp({ Component, pageProps }: AppProps) {
  const router = useRouter();
  
  // Create a stable query client instance
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 5 * 60 * 1000, // 5 minutes
            cacheTime: 10 * 60 * 1000, // 10 minutes
            refetchOnWindowFocus: false,
            refetchOnReconnect: true,
            retry: (failureCount, error: any) => {
              // Don't retry on 4xx errors except 408, 429
              if (error?.response?.status >= 400 && error?.response?.status < 500) {
                if (error?.response?.status === 408 || error?.response?.status === 429) {
                  return failureCount < 3;
                }
                return false;
              }
              // Retry on network errors and 5xx errors
              return failureCount < 3;
            },
            onError: (error: any) => {
              // Log API errors globally
              logger.apiError(
                'unknown_endpoint',
                'UNKNOWN',
                error?.response?.status || 0,
                String(error)
              );
            },
          },
          mutations: {
            retry: (failureCount, error: any) => {
              // Don't retry mutations on 4xx errors
              if (error?.response?.status >= 400 && error?.response?.status < 500) {
                return false;
              }
              // Retry on network errors and 5xx errors
              return failureCount < 2;
            },
            onError: (error: any) => {
              // Log mutation errors globally
              logger.apiError(
                'unknown_mutation',
                'POST',
                error?.response?.status || 0,
                String(error)
              );
            },
          },
        },
      })
  );

  // Track navigation events
  useEffect(() => {
    const handleRouteChangeStart = (url: string) => {
      logger.pageVisited(url, router.asPath);
    };

    const handleRouteChangeComplete = (url: string) => {
      // Update logger context with current page
      logger.setContext({ url });
    };

    const handleRouteChangeError = (err: any, url: string) => {
      logger.componentError('Router', `Navigation error to ${url}: ${String(err)}`);
    };

    // Log initial page visit
    logger.pageVisited(router.asPath);

    // Listen to route changes
    router.events.on('routeChangeStart', handleRouteChangeStart);
    router.events.on('routeChangeComplete', handleRouteChangeComplete);
    router.events.on('routeChangeError', handleRouteChangeError);

    // Cleanup
    return () => {
      router.events.off('routeChangeStart', handleRouteChangeStart);
      router.events.off('routeChangeComplete', handleRouteChangeComplete);
      router.events.off('routeChangeError', handleRouteChangeError);
    };
  }, [router]);

  // Global error boundary for components
  useEffect(() => {
    const handleGlobalError = (event: ErrorEvent) => {
      logger.componentError(
        'Global',
        event.message,
        event.error?.stack
      );
    };

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      logger.componentError(
        'Global',
        `Unhandled Promise Rejection: ${String(event.reason)}`
      );
    };

    window.addEventListener('error', handleGlobalError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    return () => {
      window.removeEventListener('error', handleGlobalError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Component {...pageProps} />
        
        {/* Toast notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              style: {
                background: '#10b981',
              },
            },
            error: {
              style: {
                background: '#ef4444',
              },
            },
          }}
        />
        
        {/* React Query Devtools - only in development */}
        {process.env.NODE_ENV === 'development' && (
          <ReactQueryDevtools initialIsOpen={false} />
        )}
      </AuthProvider>
    </QueryClientProvider>
  );
} 