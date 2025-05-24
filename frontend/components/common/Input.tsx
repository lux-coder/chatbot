'use client';

import React, { forwardRef } from 'react';
import { clsx } from 'clsx';
import type { ComponentProps } from '@/utils/types';

interface InputProps extends ComponentProps {
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search';
  placeholder?: string;
  value?: string;
  defaultValue?: string;
  disabled?: boolean;
  readOnly?: boolean;
  required?: boolean;
  error?: string | undefined;
  helperText?: string;
  label?: string;
  id?: string;
  name?: string;
  autoComplete?: string;
  autoFocus?: boolean;
  maxLength?: number;
  minLength?: number;
  pattern?: string;
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  startIcon?: React.ReactNode;
  endIcon?: React.ReactNode;
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onFocus?: (event: React.FocusEvent<HTMLInputElement>) => void;
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void;
  onKeyDown?: (event: React.KeyboardEvent<HTMLInputElement>) => void;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      type = 'text',
      placeholder,
      value,
      defaultValue,
      disabled = false,
      readOnly = false,
      required = false,
      error,
      helperText,
      label,
      id,
      name,
      autoComplete,
      autoFocus = false,
      maxLength,
      minLength,
      pattern,
      size = 'md',
      fullWidth = false,
      startIcon,
      endIcon,
      onChange,
      onFocus,
      onBlur,
      onKeyDown,
      className,
      ...props
    },
    ref
  ) => {
    const inputId = id || name || `input-${Math.random().toString(36).substr(2, 9)}`;
    const hasError = Boolean(error);

    const containerClasses = clsx(
      'relative',
      fullWidth ? 'w-full' : 'w-auto'
    );

    const inputBaseClasses = [
      'block',
      'border',
      'rounded-lg',
      'bg-white',
      'placeholder-secondary-400',
      'transition-colors',
      'duration-200',
      'focus:outline-none',
      'focus:ring-2',
      'focus:ring-offset-0',
      'disabled:bg-secondary-50',
      'disabled:cursor-not-allowed',
      'disabled:text-secondary-500',
    ];

    const sizeClasses = {
      sm: ['px-3', 'py-1.5', 'text-sm'],
      md: ['px-3', 'py-2', 'text-sm'],
      lg: ['px-4', 'py-3', 'text-base'],
    };

    const stateClasses = hasError
      ? [
          'border-error-300',
          'text-error-900',
          'placeholder-error-300',
          'focus:border-error-500',
          'focus:ring-error-500',
        ]
      : [
          'border-secondary-300',
          'text-secondary-900',
          'focus:border-primary-500',
          'focus:ring-primary-500',
        ];

    const widthClasses = fullWidth ? ['w-full'] : [];

    const iconPaddingClasses = {
      start: startIcon ? (size === 'sm' ? 'pl-8' : size === 'lg' ? 'pl-12' : 'pl-10') : '',
      end: endIcon ? (size === 'sm' ? 'pr-8' : size === 'lg' ? 'pr-12' : 'pr-10') : '',
    };

    const inputClasses = clsx(
      inputBaseClasses,
      sizeClasses[size],
      stateClasses,
      widthClasses,
      iconPaddingClasses.start,
      iconPaddingClasses.end,
      className
    );

    const iconSizeClasses = {
      sm: 'w-4 h-4',
      md: 'w-5 h-5',
      lg: 'w-6 h-6',
    };

    const iconPositionClasses = {
      start: {
        sm: 'left-2',
        md: 'left-3',
        lg: 'left-3',
      },
      end: {
        sm: 'right-2',
        md: 'right-3',
        lg: 'right-3',
      },
    };

    return (
      <div className={containerClasses}>
        {label && (
          <label
            htmlFor={inputId}
            className={clsx(
              'block text-sm font-medium mb-1',
              hasError ? 'text-error-700' : 'text-secondary-700',
              disabled && 'text-secondary-500'
            )}
          >
            {label}
            {required && <span className="text-error-500 ml-1">*</span>}
          </label>
        )}

        <div className="relative">
          {startIcon && (
            <div
              className={clsx(
                'absolute inset-y-0 flex items-center pointer-events-none text-secondary-400',
                iconPositionClasses.start[size]
              )}
            >
              <div className={iconSizeClasses[size]}>{startIcon}</div>
            </div>
          )}

          <input
            ref={ref}
            type={type}
            id={inputId}
            name={name}
            placeholder={placeholder}
            value={value}
            defaultValue={defaultValue}
            disabled={disabled}
            readOnly={readOnly}
            required={required}
            autoComplete={autoComplete}
            autoFocus={autoFocus}
            maxLength={maxLength}
            minLength={minLength}
            pattern={pattern}
            onChange={onChange}
            onFocus={onFocus}
            onBlur={onBlur}
            onKeyDown={onKeyDown}
            className={inputClasses}
            aria-invalid={hasError}
            aria-describedby={
              error ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined
            }
            {...props}
          />

          {endIcon && (
            <div
              className={clsx(
                'absolute inset-y-0 flex items-center pointer-events-none text-secondary-400',
                iconPositionClasses.end[size]
              )}
            >
              <div className={iconSizeClasses[size]}>{endIcon}</div>
            </div>
          )}
        </div>

        {(error || helperText) && (
          <div className="mt-1">
            {error && (
              <p
                id={`${inputId}-error`}
                className="text-sm text-error-600"
                role="alert"
              >
                {error}
              </p>
            )}
            {!error && helperText && (
              <p
                id={`${inputId}-helper`}
                className="text-sm text-secondary-500"
              >
                {helperText}
              </p>
            )}
          </div>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input'; 