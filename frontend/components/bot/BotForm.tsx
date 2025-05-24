'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { Button, Input } from '@/components/common';
import { useCreateBot, useUpdateBot } from '@/hooks/useBots';
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

interface BotFormData {
  name: string;
  style: string;
  language: string;
  icon: string;
}

interface BotFormProps extends ComponentProps {
  bot?: Bot;
  onSubmit?: (data: BotFormData) => void;
  onCancel?: () => void;
  submitLabel?: string;
  showCancelButton?: boolean;
}

const BOT_STYLES = [
  { value: 'professional', label: 'Professional', description: 'Formal and business-oriented responses' },
  { value: 'casual', label: 'Casual', description: 'Friendly and conversational tone' },
  { value: 'technical', label: 'Technical', description: 'Detailed and precise explanations' },
  { value: 'creative', label: 'Creative', description: 'Imaginative and artistic responses' },
  { value: 'supportive', label: 'Supportive', description: 'Empathetic and encouraging tone' },
];

const BOT_LANGUAGES = [
  { value: 'english', label: 'English', flag: '🇺🇸' },
  { value: 'spanish', label: 'Spanish', flag: '🇪🇸' },
  { value: 'french', label: 'French', flag: '🇫🇷' },
  { value: 'german', label: 'German', flag: '🇩🇪' },
  { value: 'italian', label: 'Italian', flag: '🇮🇹' },
  { value: 'portuguese', label: 'Portuguese', flag: '🇵🇹' },
  { value: 'chinese', label: 'Chinese', flag: '🇨🇳' },
  { value: 'japanese', label: 'Japanese', flag: '🇯🇵' },
];

const BOT_ICONS = [
  '🤖', '👨‍💼', '👩‍💼', '🎓', '💡', '🎯', '🚀', '⭐', '🔥', '💎',
  '🌟', '🎭', '🎨', '📚', '🔬', '⚡', '🌈', '🦄', '🎪', '🎨'
];

export const BotForm: React.FC<BotFormProps> = ({
  bot,
  onSubmit,
  onCancel,
  submitLabel,
  showCancelButton = true,
  className,
}) => {
  const router = useRouter();
  const createBot = useCreateBot();
  const updateBot = useUpdateBot();
  
  const [formData, setFormData] = useState<BotFormData>({
    name: bot?.name || '',
    style: bot?.style || 'professional',
    language: bot?.language || 'english',
    icon: bot?.icon || '🤖',
  });

  const [errors, setErrors] = useState<Partial<BotFormData>>({});
  const [touched, setTouched] = useState<Partial<Record<keyof BotFormData, boolean>>>({});

  const isEditing = Boolean(bot);
  const isLoading = createBot.isLoading || updateBot.isLoading;

  // Update form data when bot prop changes
  useEffect(() => {
    if (bot) {
      setFormData({
        name: bot.name,
        style: bot.style,
        language: bot.language,
        icon: bot.icon || '🤖',
      });
    }
  }, [bot]);

  const validateField = (name: keyof BotFormData, value: string): string | undefined => {
    switch (name) {
      case 'name':
        if (!value.trim()) return 'Bot name is required';
        if (value.length < 2) return 'Bot name must be at least 2 characters';
        if (value.length > 100) return 'Bot name must be less than 100 characters';
        break;
      case 'style':
        if (!BOT_STYLES.find(s => s.value === value)) return 'Please select a valid style';
        break;
      case 'language':
        if (!BOT_LANGUAGES.find(l => l.value === value)) return 'Please select a valid language';
        break;
      case 'icon':
        if (!value) return 'Please select an icon';
        break;
    }
    return undefined;
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<BotFormData> = {};
    
    Object.keys(formData).forEach(key => {
      const fieldName = key as keyof BotFormData;
      const error = validateField(fieldName, formData[fieldName]);
      if (error) {
        newErrors[fieldName] = error;
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (name: keyof BotFormData, value: string) => {
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const handleBlur = (name: keyof BotFormData) => {
    setTouched(prev => ({ ...prev, [name]: true }));
    
    const error = validateField(name, formData[name]);
    if (error) {
      setErrors(prev => ({ ...prev, [name]: error }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      // Mark all fields as touched to show errors
      setTouched({
        name: true,
        style: true,
        language: true,
        icon: true,
      });
      return;
    }

    try {
      if (onSubmit) {
        onSubmit(formData);
      } else if (isEditing && bot) {
        await updateBot.mutateAsync({
          id: bot.id,
          ...formData,
        });
        router.push('/bots');
      } else {
        await createBot.mutateAsync(formData);
        router.push('/bots');
      }
    } catch (error) {
      console.error('Failed to save bot:', error);
    }
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    } else {
      router.back();
    }
  };

  return (
    <div className={className}>
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Bot Name */}
        <div>
          <Input
            label="Bot Name"
            placeholder="Enter a name for your chatbot"
            value={formData.name}
            onChange={(e) => handleInputChange('name', e.target.value)}
            onBlur={() => handleBlur('name')}
            error={touched.name ? errors.name : undefined}
            required
            maxLength={100}
          />
        </div>

        {/* Bot Style */}
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-3">
            Conversation Style
            <span className="text-error-500 ml-1">*</span>
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {BOT_STYLES.map((style) => (
              <label
                key={style.value}
                className={`relative flex cursor-pointer rounded-lg border p-4 focus:outline-none transition-colors ${
                  formData.style === style.value
                    ? 'border-primary-600 ring-2 ring-primary-600 bg-primary-50'
                    : 'border-secondary-300 hover:border-secondary-400'
                }`}
              >
                <input
                  type="radio"
                  name="style"
                  value={style.value}
                  checked={formData.style === style.value}
                  onChange={(e) => handleInputChange('style', e.target.value)}
                  className="sr-only"
                />
                <div className="flex flex-1">
                  <div className="flex flex-col">
                    <span className="block text-sm font-medium text-secondary-900">
                      {style.label}
                    </span>
                    <span className="block text-sm text-secondary-500">
                      {style.description}
                    </span>
                  </div>
                </div>
                {formData.style === style.value && (
                  <CheckIcon className="h-5 w-5 text-primary-600" />
                )}
              </label>
            ))}
          </div>
          {touched.style && errors.style && (
            <p className="mt-2 text-sm text-error-600">{errors.style}</p>
          )}
        </div>

        {/* Bot Language */}
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-3">
            Language
            <span className="text-error-500 ml-1">*</span>
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {BOT_LANGUAGES.map((language) => (
              <label
                key={language.value}
                className={`relative flex items-center cursor-pointer rounded-lg border p-3 focus:outline-none transition-colors ${
                  formData.language === language.value
                    ? 'border-primary-600 ring-2 ring-primary-600 bg-primary-50'
                    : 'border-secondary-300 hover:border-secondary-400'
                }`}
              >
                <input
                  type="radio"
                  name="language"
                  value={language.value}
                  checked={formData.language === language.value}
                  onChange={(e) => handleInputChange('language', e.target.value)}
                  className="sr-only"
                />
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{language.flag}</span>
                  <span className="text-sm font-medium text-secondary-900">
                    {language.label}
                  </span>
                </div>
                {formData.language === language.value && (
                  <CheckIcon className="h-4 w-4 text-primary-600 ml-auto" />
                )}
              </label>
            ))}
          </div>
          {touched.language && errors.language && (
            <p className="mt-2 text-sm text-error-600">{errors.language}</p>
          )}
        </div>

        {/* Bot Icon */}
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-3">
            Bot Icon
            <span className="text-error-500 ml-1">*</span>
          </label>
          <div className="grid grid-cols-10 gap-2">
            {BOT_ICONS.map((icon) => (
              <button
                key={icon}
                type="button"
                onClick={() => handleInputChange('icon', icon)}
                className={`w-10 h-10 flex items-center justify-center text-xl rounded-lg border transition-colors ${
                  formData.icon === icon
                    ? 'border-primary-600 ring-2 ring-primary-600 bg-primary-50'
                    : 'border-secondary-300 hover:border-secondary-400 hover:bg-secondary-50'
                }`}
              >
                {icon}
              </button>
            ))}
          </div>
          {touched.icon && errors.icon && (
            <p className="mt-2 text-sm text-error-600">{errors.icon}</p>
          )}
        </div>

        {/* Form Actions */}
        <div className="flex flex-col sm:flex-row sm:justify-end sm:space-x-3 space-y-3 sm:space-y-0">
          {showCancelButton && (
            <Button
              type="button"
              variant="secondary"
              onClick={handleCancel}
              disabled={isLoading}
            >
              Cancel
            </Button>
          )}
          <Button
            type="submit"
            variant="primary"
            loading={isLoading}
            disabled={isLoading}
          >
            {submitLabel || (isEditing ? 'Update Bot' : 'Create Bot')}
          </Button>
        </div>
      </form>
    </div>
  );
};

// Icon component
const CheckIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  </svg>
); 