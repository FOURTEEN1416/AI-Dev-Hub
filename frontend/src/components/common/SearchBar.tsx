/**
 * 搜索框组件
 */

'use client';

import { useState, useCallback } from 'react';
import { Search, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SearchBarProps {
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  onSearch?: (value: string) => void;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export default function SearchBar({
  placeholder = '搜索机会...',
  value: controlledValue,
  onChange,
  onSearch,
  className,
  size = 'md',
}: SearchBarProps) {
  const [internalValue, setInternalValue] = useState('');
  const value = controlledValue !== undefined ? controlledValue : internalValue;

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = e.target.value;
      if (controlledValue === undefined) {
        setInternalValue(newValue);
      }
      onChange?.(newValue);
    },
    [controlledValue, onChange]
  );

  const handleClear = useCallback(() => {
    if (controlledValue === undefined) {
      setInternalValue('');
    }
    onChange?.('');
  }, [controlledValue, onChange]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter') {
        onSearch?.(value);
      }
    },
    [onSearch, value]
  );

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2.5 text-base',
    lg: 'px-5 py-3 text-lg',
  };

  const iconSizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6',
  };

  return (
    <div className={cn('relative group', className)}>
      <Search
        className={cn(
          'absolute left-3 text-[var(--text-muted)] transition-colors group-focus-within:text-primary-400',
          iconSizeClasses[size]
        )}
      />
      <input
        type="text"
        value={value}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        className={cn(
          'input-base pl-10 pr-10',
          sizeClasses[size]
        )}
      />
      {value && (
        <button
          onClick={handleClear}
          className="absolute right-3 text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
        >
          <X className={iconSizeClasses[size]} />
        </button>
      )}
    </div>
  );
}
