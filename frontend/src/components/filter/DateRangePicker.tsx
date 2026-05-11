/**
 * 日期范围选择器
 * 支持开始日期、结束日期、快捷选项
 */

'use client';

import { useState } from 'react';
import { Calendar, ChevronDown, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { format, subDays, startOfWeek, startOfMonth, endOfWeek, endOfMonth } from 'date-fns';

/** 快捷选项类型 */
type QuickOption = 'today' | 'this_week' | 'this_month' | 'last_30_days' | 'custom';

/** 快捷选项配置 */
const QUICK_OPTIONS: { value: QuickOption; label: string }[] = [
  { value: 'today', label: '今天' },
  { value: 'this_week', label: '本周' },
  { value: 'this_month', label: '本月' },
  { value: 'last_30_days', label: '最近30天' },
  { value: 'custom', label: '自定义' },
];

interface DateRangePickerProps {
  /** 开始日期 */
  startDate?: string;
  /** 结束日期 */
  endDate?: string;
  /** 日期变更回调 */
  onChange: (startDate?: string, endDate?: string) => void;
  /** 标签文本 */
  label?: string;
  /** 占位文本 */
  placeholder?: string;
}

export default function DateRangePicker({
  startDate,
  endDate,
  onChange,
  label = '日期范围',
  placeholder = '选择日期范围',
}: DateRangePickerProps) {
  const [quickOption, setQuickOption] = useState<QuickOption>('custom');
  const [showCustom, setShowCustom] = useState(false);

  /**
   * 获取快捷选项的日期范围
   */
  const getQuickOptionDates = (option: QuickOption): { start: string; end: string } | null => {
    const today = new Date();
    
    switch (option) {
      case 'today':
        return {
          start: format(today, 'yyyy-MM-dd'),
          end: format(today, 'yyyy-MM-dd'),
        };
      case 'this_week':
        return {
          start: format(startOfWeek(today, { weekStartsOn: 1 }), 'yyyy-MM-dd'),
          end: format(endOfWeek(today, { weekStartsOn: 1 }), 'yyyy-MM-dd'),
        };
      case 'this_month':
        return {
          start: format(startOfMonth(today), 'yyyy-MM-dd'),
          end: format(endOfMonth(today), 'yyyy-MM-dd'),
        };
      case 'last_30_days':
        return {
          start: format(subDays(today, 30), 'yyyy-MM-dd'),
          end: format(today, 'yyyy-MM-dd'),
        };
      default:
        return null;
    }
  };

  /**
   * 处理快捷选项点击
   */
  const handleQuickOption = (option: QuickOption) => {
    setQuickOption(option);
    
    if (option === 'custom') {
      setShowCustom(true);
      return;
    }
    
    setShowCustom(false);
    const dates = getQuickOptionDates(option);
    if (dates) {
      onChange(dates.start, dates.end);
    }
  };

  /**
   * 处理自定义日期变更
   */
  const handleDateChange = (type: 'start' | 'end', value: string) => {
    if (type === 'start') {
      onChange(value, endDate);
    } else {
      onChange(startDate, value);
    }
  };

  /**
   * 清空日期选择
   */
  const handleClear = () => {
    setQuickOption('custom');
    setShowCustom(false);
    onChange(undefined, undefined);
  };

  /**
   * 格式化显示日期
   */
  const formatDisplayDate = (dateStr?: string) => {
    if (!dateStr) return '';
    try {
      return format(new Date(dateStr), 'MM/dd');
    } catch {
      return dateStr;
    }
  };

  const hasValue = startDate || endDate;

  return (
    <div className="space-y-2">
      <label className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider">
        {label}
      </label>

      {/* 快捷选项 */}
      <div className="flex flex-wrap gap-1.5">
        {QUICK_OPTIONS.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => handleQuickOption(option.value)}
            className={cn(
              'px-2.5 py-1 text-xs rounded-md transition-all border',
              quickOption === option.value
                ? 'bg-primary-500/10 text-primary-400 border-primary-500/30'
                : 'border-[var(--border-color)] text-[var(--text-secondary)] hover:border-[var(--border-hover)] hover:text-[var(--text-primary)]'
            )}
          >
            {option.label}
          </button>
        ))}
      </div>

      {/* 自定义日期选择 */}
      {showCustom && (
        <div className="flex items-center gap-2 mt-2">
          <div className="relative flex-1">
            <Calendar className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--text-muted)]" />
            <input
              type="date"
              value={startDate || ''}
              onChange={(e) => handleDateChange('start', e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 text-sm bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-md focus:outline-none focus:ring-1 focus:ring-primary-500/50"
            />
          </div>
          <span className="text-[var(--text-muted)]">至</span>
          <div className="relative flex-1">
            <Calendar className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--text-muted)]" />
            <input
              type="date"
              value={endDate || ''}
              onChange={(e) => handleDateChange('end', e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 text-sm bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-md focus:outline-none focus:ring-1 focus:ring-primary-500/50"
            />
          </div>
        </div>
      )}

      {/* 已选日期显示 */}
      {hasValue && !showCustom && (
        <div className="flex items-center gap-2 mt-2">
          <span className="inline-flex items-center gap-1.5 px-2 py-1 text-xs rounded-md bg-primary-500/10 text-primary-400">
            <Calendar className="h-3 w-3" />
            {formatDisplayDate(startDate)} - {formatDisplayDate(endDate)}
          </span>
          <button
            type="button"
            onClick={handleClear}
            className="p-1 rounded hover:bg-[var(--bg-tertiary)] transition-colors"
          >
            <X className="h-3.5 w-3.5 text-[var(--text-muted)]" />
          </button>
        </div>
      )}
    </div>
  );
}
