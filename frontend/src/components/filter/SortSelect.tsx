/**
 * 排序选择器
 * 支持多种排序方式和升降序切换
 */

'use client';

import { useState, useRef, useEffect } from 'react';
import { ArrowUpDown, ArrowUp, ArrowDown, ChevronDown, Check } from 'lucide-react';
import { cn } from '@/lib/utils';

/** 排序字段选项 */
const SORT_BY_OPTIONS: { value: 'created_at' | 'deadline' | 'title'; label: string; icon: React.ReactNode }[] = [
  { value: 'created_at', label: '最新发布', icon: <ArrowUpDown className="h-3.5 w-3.5" /> },
  { value: 'deadline', label: '即将截止', icon: <ArrowDown className="h-3.5 w-3.5" /> },
  { value: 'title', label: '标题排序', icon: <ArrowUpDown className="h-3.5 w-3.5" /> },
];

interface SortSelectProps {
  /** 当前排序字段 */
  sortBy?: 'created_at' | 'deadline' | 'title';
  /** 当前排序方向 */
  sortOrder?: 'asc' | 'desc';
  /** 排序变更回调 */
  onChange: (sortBy: 'created_at' | 'deadline' | 'title', sortOrder: 'asc' | 'desc') => void;
  /** 是否显示升降序切换按钮 */
  showOrderToggle?: boolean;
}

export default function SortSelect({
  sortBy = 'created_at',
  sortOrder = 'desc',
  onChange,
  showOrderToggle = true,
}: SortSelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // 点击外部关闭下拉
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  /**
   * 获取当前排序选项的标签
   */
  const getCurrentLabel = () => {
    const option = SORT_BY_OPTIONS.find((o) => o.value === sortBy);
    return option?.label || '排序方式';
  };

  /**
   * 处理排序字段选择
   */
  const handleSortBySelect = (value: 'created_at' | 'deadline' | 'title') => {
    // 如果选择相同的字段，切换排序方向
    if (value === sortBy) {
      onChange(sortBy, sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      // 选择新字段时，使用默认排序方向
      const defaultOrder = value === 'title' ? 'asc' : 'desc';
      onChange(value, defaultOrder);
    }
    setIsOpen(false);
  };

  /**
   * 切换排序方向
   */
  const toggleSortOrder = () => {
    onChange(sortBy, sortOrder === 'asc' ? 'desc' : 'asc');
  };

  return (
    <div className="space-y-2">
      <label className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider">
        排序方式
      </label>
      <div className="flex items-center gap-2" ref={containerRef}>
        {/* 排序字段选择 */}
        <div className="relative flex-1">
          <button
            type="button"
            onClick={() => setIsOpen(!isOpen)}
            className={cn(
              'w-full flex items-center justify-between gap-2 px-3 py-2 rounded-lg transition-all',
              'border border-[var(--border-color)] text-left',
              'hover:border-[var(--border-hover)]',
              isOpen && 'border-primary-500/50 ring-1 ring-primary-500/20'
            )}
          >
            <span className="text-sm text-[var(--text-primary)]">{getCurrentLabel()}</span>
            <ChevronDown
              className={cn(
                'h-4 w-4 text-[var(--text-muted)] transition-transform',
                isOpen && 'rotate-180'
              )}
            />
          </button>

          {/* 下拉选项 */}
          {isOpen && (
            <div className="absolute z-50 mt-1 w-full bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg shadow-lg overflow-hidden">
              {SORT_BY_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => handleSortBySelect(option.value)}
                  className={cn(
                    'w-full flex items-center justify-between gap-2 px-3 py-2 text-sm text-left transition-colors',
                    'hover:bg-[var(--bg-tertiary)]',
                    sortBy === option.value && 'bg-primary-500/5 text-primary-400'
                  )}
                >
                  <span className="flex items-center gap-2">
                    {option.icon}
                    {option.label}
                  </span>
                  {sortBy === option.value && <Check className="h-4 w-4" />}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* 升降序切换按钮 */}
        {showOrderToggle && (
          <button
            type="button"
            onClick={toggleSortOrder}
            className={cn(
              'flex items-center justify-center w-10 h-10 rounded-lg transition-all border',
              'border-[var(--border-color)] hover:border-[var(--border-hover)]',
              'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
            )}
            title={sortOrder === 'asc' ? '升序' : '降序'}
          >
            {sortOrder === 'asc' ? (
              <ArrowUp className="h-4 w-4" />
            ) : (
              <ArrowDown className="h-4 w-4" />
            )}
          </button>
        )}
      </div>

      {/* 当前排序说明 */}
      <p className="text-xs text-[var(--text-muted)]">
        {sortBy === 'created_at' && (sortOrder === 'desc' ? '最新发布的在前' : '最早发布的在前')}
        {sortBy === 'deadline' && (sortOrder === 'asc' ? '截止日期最近的在前' : '截止日期最远的在前')}
        {sortBy === 'title' && (sortOrder === 'asc' ? '按标题 A-Z 排序' : '按标题 Z-A 排序')}
      </p>
    </div>
  );
}
