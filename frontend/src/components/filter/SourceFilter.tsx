/**
 * 来源筛选组件
 * 下拉多选，支持搜索，显示已选数量
 */

'use client';

import { useState, useRef, useEffect } from 'react';
import { ChevronDown, X, Search, Check } from 'lucide-react';
import { cn } from '@/lib/utils';

/** 来源选项（模拟数据，实际应从 API 获取） */
const DEFAULT_SOURCES = [
  { value: 'OpenAI', label: 'OpenAI' },
  { value: 'Google', label: 'Google' },
  { value: 'Kaggle', label: 'Kaggle' },
  { value: 'GitHub', label: 'GitHub' },
  { value: 'Hugging Face', label: 'Hugging Face' },
  { value: 'Anthropic', label: 'Anthropic' },
  { value: 'Meta', label: 'Meta' },
  { value: 'Hacker News', label: 'Hacker News' },
  { value: 'Microsoft', label: 'Microsoft' },
  { value: 'AWS', label: 'AWS' },
];

interface SourceFilterProps {
  /** 已选中的来源列表 */
  selectedSources: string[];
  /** 来源变更回调 */
  onChange: (sources: string[]) => void;
  /** 可选的来源列表 */
  options?: { value: string; label: string }[];
  /** 占位文本 */
  placeholder?: string;
}

export default function SourceFilter({
  selectedSources,
  onChange,
  options = DEFAULT_SOURCES,
  placeholder = '选择来源平台',
}: SourceFilterProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchKeyword, setSearchKeyword] = useState('');
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

  // 过滤选项
  const filteredOptions = options.filter((option) =>
    option.label.toLowerCase().includes(searchKeyword.toLowerCase())
  );

  /**
   * 切换来源选择
   */
  const toggleSource = (value: string) => {
    const newSources = selectedSources.includes(value)
      ? selectedSources.filter((s) => s !== value)
      : [...selectedSources, value];
    onChange(newSources);
  };

  /**
   * 移除单个来源
   */
  const removeSource = (value: string, e: React.MouseEvent) => {
    e.stopPropagation();
    onChange(selectedSources.filter((s) => s !== value));
  };

  /**
   * 清空所有选择
   */
  const clearAll = (e: React.MouseEvent) => {
    e.stopPropagation();
    onChange([]);
  };

  return (
    <div className="space-y-2">
      <label className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider">
        来源平台
      </label>
      <div ref={containerRef} className="relative">
        {/* 触发按钮 */}
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className={cn(
            'w-full flex items-center justify-between gap-2 px-3 py-2.5 rounded-lg transition-all',
            'border border-[var(--border-color)] text-left',
            'hover:border-[var(--border-hover)]',
            isOpen && 'border-primary-500/50 ring-1 ring-primary-500/20'
          )}
        >
          <div className="flex items-center gap-2 flex-1 min-w-0">
            {selectedSources.length > 0 ? (
              <>
                <span className="text-sm text-[var(--text-primary)] truncate">
                  {selectedSources.length === 1
                    ? options.find((o) => o.value === selectedSources[0])?.label
                    : `已选择 ${selectedSources.length} 个来源`}
                </span>
                <button
                  type="button"
                  onClick={clearAll}
                  className="p-0.5 rounded hover:bg-[var(--bg-tertiary)] transition-colors"
                >
                  <X className="h-3.5 w-3.5 text-[var(--text-muted)]" />
                </button>
              </>
            ) : (
              <span className="text-sm text-[var(--text-muted)]">{placeholder}</span>
            )}
          </div>
          <ChevronDown
            className={cn(
              'h-4 w-4 text-[var(--text-muted)] transition-transform',
              isOpen && 'rotate-180'
            )}
          />
        </button>

        {/* 下拉面板 */}
        {isOpen && (
          <div className="absolute z-50 mt-1 w-full bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg shadow-lg overflow-hidden">
            {/* 搜索框 */}
            <div className="p-2 border-b border-[var(--border-color)]">
              <div className="relative">
                <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--text-muted)]" />
                <input
                  type="text"
                  value={searchKeyword}
                  onChange={(e) => setSearchKeyword(e.target.value)}
                  placeholder="搜索来源..."
                  className="w-full pl-8 pr-3 py-1.5 text-sm bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-md focus:outline-none focus:ring-1 focus:ring-primary-500/50"
                />
              </div>
            </div>

            {/* 选项列表 */}
            <div className="max-h-48 overflow-y-auto">
              {filteredOptions.length === 0 ? (
                <div className="px-3 py-2 text-sm text-[var(--text-muted)] text-center">
                  没有匹配的来源
                </div>
              ) : (
                filteredOptions.map((option) => {
                  const isSelected = selectedSources.includes(option.value);
                  return (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => toggleSource(option.value)}
                      className={cn(
                        'w-full flex items-center gap-2 px-3 py-2 text-sm text-left transition-colors',
                        'hover:bg-[var(--bg-tertiary)]',
                        isSelected && 'bg-primary-500/5'
                      )}
                    >
                      <div
                        className={cn(
                          'w-4 h-4 rounded border flex items-center justify-center transition-colors',
                          isSelected
                            ? 'bg-primary-500 border-primary-500'
                            : 'border-[var(--border-color)]'
                        )}
                      >
                        {isSelected && <Check className="h-3 w-3 text-white" />}
                      </div>
                      <span className={isSelected ? 'text-[var(--text-primary)]' : 'text-[var(--text-secondary)]'}>
                        {option.label}
                      </span>
                    </button>
                  );
                })
              )}
            </div>

            {/* 底部操作 */}
            {selectedSources.length > 0 && (
              <div className="p-2 border-t border-[var(--border-color)] flex justify-between items-center">
                <span className="text-xs text-[var(--text-muted)]">
                  已选 {selectedSources.length} 项
                </span>
                <button
                  type="button"
                  onClick={() => onChange([])}
                  className="text-xs text-primary-400 hover:text-primary-300 transition-colors"
                >
                  清空
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* 已选标签展示 */}
      {selectedSources.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {selectedSources.map((source) => {
            const option = options.find((o) => o.value === source);
            return (
              <span
                key={source}
                className="inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded-full bg-primary-500/10 text-primary-400 border border-primary-500/20"
              >
                {option?.label || source}
                <button
                  type="button"
                  onClick={(e) => removeSource(source, e)}
                  className="p-0.5 rounded hover:bg-primary-500/20 transition-colors"
                >
                  <X className="h-3 w-3" />
                </button>
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
}
