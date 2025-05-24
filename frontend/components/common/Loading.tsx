'use client';

import React from 'react';
import { clsx } from 'clsx';
import type { ComponentProps } from '@/utils/types';

interface LoadingProps extends ComponentProps {
  variant?: 'spinner' | 'dots' | 'pulse' | 'skeleton';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  text?: string;
  fullScreen?: boolean;
  overlay?: boolean;
}

export const Loading: React.FC<LoadingProps> = ({
  variant = 'spinner',
  size = 'md',
  text,
  fullScreen = false,
  overlay = false,
  className,
}) => {
  const sizeClasses = {
    xs: 'w-3 h-3',
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12',
  };

  const textSizeClasses = {
    xs: 'text-xs',
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg',
    xl: 'text-xl',
  };

  const renderSpinner = () => (
    <div
      className={clsx(
        'animate-spin rounded-full border-2 border-current border-t-transparent',
        sizeClasses[size]
      )}
      role="status"
      aria-label="Loading"
    />
  );

  const renderDots = () => (
    <div className="flex space-x-1" role="status" aria-label="Loading">
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className={clsx(
            'rounded-full bg-current animate-pulse',
            size === 'xs' ? 'w-1 h-1' : 
            size === 'sm' ? 'w-1.5 h-1.5' : 
            size === 'md' ? 'w-2 h-2' : 
            size === 'lg' ? 'w-3 h-3' : 'w-4 h-4'
          )}
          style={{
            animationDelay: `${i * 0.2}s`,
            animationDuration: '1.4s',
          }}
        />
      ))}
    </div>
  );

  const renderPulse = () => (
    <div
      className={clsx(
        'rounded-full bg-current animate-pulse',
        sizeClasses[size]
      )}
      role="status"
      aria-label="Loading"
    />
  );

  const renderSkeleton = () => (
    <div className="animate-pulse space-y-2" role="status" aria-label="Loading">
      <div className="bg-secondary-200 rounded h-4 w-3/4"></div>
      <div className="bg-secondary-200 rounded h-4 w-1/2"></div>
      <div className="bg-secondary-200 rounded h-4 w-5/6"></div>
    </div>
  );

  const renderLoadingElement = () => {
    switch (variant) {
      case 'dots':
        return renderDots();
      case 'pulse':
        return renderPulse();
      case 'skeleton':
        return renderSkeleton();
      default:
        return renderSpinner();
    }
  };

  const containerClasses = clsx(
    'flex items-center justify-center text-primary-600',
    fullScreen && 'min-h-screen',
    overlay && 'absolute inset-0 bg-white bg-opacity-75 z-50',
    className
  );

  const contentClasses = clsx(
    'flex flex-col items-center justify-center',
    text && 'space-y-2'
  );

  return (
    <div className={containerClasses}>
      <div className={contentClasses}>
        {renderLoadingElement()}
        {text && (
          <div className={clsx('text-secondary-600 font-medium', textSizeClasses[size])}>
            {text}
          </div>
        )}
      </div>
    </div>
  );
};

// Specialized loading components
export const ButtonLoading: React.FC<{ size?: 'xs' | 'sm' | 'md' }> = ({ 
  size = 'sm' 
}) => (
  <Loading variant="spinner" size={size} className="inline-flex" />
);

export const PageLoading: React.FC<{ text?: string }> = ({ 
  text = "Loading..." 
}) => (
  <Loading 
    variant="spinner" 
    size="lg" 
    text={text} 
    fullScreen 
    className="bg-white"
  />
);

export const OverlayLoading: React.FC<{ text?: string }> = ({ 
  text = "Loading..." 
}) => (
  <Loading 
    variant="spinner" 
    size="lg" 
    text={text} 
    overlay 
  />
);

export const SkeletonLoading: React.FC<{ className?: string }> = ({ 
  className = ""
}) => (
  <Loading 
    variant="skeleton" 
    className={className}
  />
); 