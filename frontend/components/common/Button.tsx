'use client';

import React, { forwardRef } from 'react';
import { clsx } from 'clsx';
import type { ComponentProps } from '@/utils/types';

interface ButtonProps extends ComponentProps {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
  type?: 'button' | 'submit' | 'reset';
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  children: React.ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      disabled = false,
      loading = false,
      fullWidth = false,
      type = 'button',
      onClick,
      children,
      className,
      ...props
    },
    ref
  ) => {
    const baseClasses = [
      'inline-flex',
      'items-center',
      'justify-center',
      'font-medium',
      'rounded-lg',
      'transition-all',
      'duration-200',
      'focus:outline-none',
      'focus:ring-2',
      'focus:ring-offset-2',
      'disabled:opacity-50',
      'disabled:cursor-not-allowed',
    ];

    const variantClasses = {
      primary: [
        'bg-primary-600',
        'text-white',
        'hover:bg-primary-700',
        'focus:ring-primary-500',
        'disabled:hover:bg-primary-600',
      ],
      secondary: [
        'bg-secondary-100',
        'text-secondary-700',
        'hover:bg-secondary-200',
        'focus:ring-secondary-500',
        'disabled:hover:bg-secondary-100',
      ],
      danger: [
        'bg-error-600',
        'text-white',
        'hover:bg-error-700',
        'focus:ring-error-500',
        'disabled:hover:bg-error-600',
      ],
      ghost: [
        'text-secondary-600',
        'hover:bg-secondary-100',
        'focus:ring-secondary-500',
        'disabled:hover:bg-transparent',
      ],
      outline: [
        'border',
        'border-secondary-300',
        'text-secondary-700',
        'bg-white',
        'hover:bg-secondary-50',
        'focus:ring-secondary-500',
        'disabled:hover:bg-white',
      ],
    };

    const sizeClasses = {
      sm: ['px-3', 'py-1.5', 'text-sm'],
      md: ['px-4', 'py-2', 'text-sm'],
      lg: ['px-6', 'py-3', 'text-base'],
    };

    const widthClasses = fullWidth ? ['w-full'] : [];

    const buttonClasses = clsx(
      baseClasses,
      variantClasses[variant],
      sizeClasses[size],
      widthClasses,
      className
    );

    const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
      if (!disabled && !loading && onClick) {
        onClick(event);
      }
    };

    return (
      <button
        ref={ref}
        type={type}
        disabled={disabled || loading}
        onClick={handleClick}
        className={buttonClasses}
        {...props}
      >
        {loading && (
          <div className="spinner mr-2" aria-hidden="true" />
        )}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button'; 