/**
 * 筛选组件
 * 包含类型按钮组、来源下拉选择、搜索输入框和排序选择
 */

'use client';

import { useState, useEffect } from 'react';
import { SlidersHorizontal, ChevronDown } from 'lucide-react';
import { cn, getTypeLabel } from '@/lib/utils';
import { useFilterStore } from '@/store';
import SearchBar from '@/components/common/SearchBar';
import type { OpportunityType, SortOption } from '@/types';

/** 类型选项 */
const typeOptions: { value: OpportunityType | ''; label: string }[] = [
  { value: '', label: '全部' },
  { value: 'developer_program', label: '开发者计划' },
  { value: 'competition', label: '比赛竞赛' },
  { value: 'free_credits', label: '免费额度' },
  { value: 'community', label: '社区动态' },
];

/** 排序选项 */
const sortOptions: { value: SortOption; label: string }[] = [
  { value: 'latest', label: '最新' },
  { value: 'popular', label: '热门' },
  { value: 'deadline', label: '截止日期' },
];

/** 来源选项（模拟数据，后续从 API 获取） */
const sourceOptions = [
  { value: '', label: '全部来源' },
  { value: 'OpenAI', label: 'OpenAI' },
  { value: 'Google', label: 'Google' },
  { value: 'Kaggle', label: 'Kaggle' },
  { value: 'GitHub', label: 'GitHub' },
  { value: 'Hugging Face', label: 'Hugging Face' },
  { value: 'Anthropic', label: 'Anthropic' },
  { value: 'Meta', label: 'Meta' },
  { value: 'Hacker News', label: 'Hacker News' },
];

export default function OpportunityFilter() {
  const {
    type,
    source,
    keyword,
    sort,
    setType,
    setSource,
    setKeyword,
    setSort,
    resetFilters,
  } = useFilterStore();

  const [showFilters, setShowFilters] = useState(false);

  return (
    <div className="space-y-4">
      {/* 主筛选栏 */}
      <div className="flex flex-col sm:flex-row gap-3">
        {/* 搜索框 */}
        <div className="flex-1">
          <SearchBar
            placeholder="搜索机会标题、描述..."
            value={keyword}
            onChange={setKeyword}
            onSearch={setKeyword}
          />
        </div>

        {/* 筛选按钮 */}
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={cn(
            'flex items-center gap-2 px-4 py-2.5 rounded-lg transition-all',
            'border border-[var(--border-color)] text-[var(--text-secondary)]',
            'hover:border-[var(--border-hover)] hover:text-[var(--text-primary)]',
            showFilters && 'border-primary-500/50 text-primary-400 bg-primary-500/5'
          )}
        >
          <SlidersHorizontal className="h-4 w-4" />
          <span className="text-sm font-medium">筛选</span>
        </button>

        {/* 排序选择 */}
        <div className="relative">
          <select
            value={sort}
            onChange={(e) => setSort(e.target.value as SortOption)}
            className="appearance-none input-base pr-8 text-sm cursor-pointer min-w-[100px]"
          >
            {sortOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--text-muted)] pointer-events-none" />
        </div>
      </div>

      {/* 展开筛选面板 */}
      {showFilters && (
        <div className="card-base p-4 space-y-4 animate-in">
          {/* 类型按钮组 */}
          <div>
            <label className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider mb-2 block">
              机会类型
            </label>
            <div className="flex flex-wrap gap-2">
              {typeOptions.map((option) => (
                <button
                  key={option.value}
                  onClick={() => setType(option.value)}
                  className={cn(
                    'px-3 py-1.5 rounded-lg text-sm font-medium transition-all border',
                    type === option.value
                      ? 'bg-primary-500/10 text-primary-400 border-primary-500/30'
                      : 'border-[var(--border-color)] text-[var(--text-secondary)] hover:border-[var(--border-hover)] hover:text-[var(--text-primary)]'
                  )}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          {/* 来源选择 */}
          <div>
            <label className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider mb-2 block">
              来源平台
            </label>
            <div className="relative max-w-xs">
              <select
                value={source}
                onChange={(e) => setSource(e.target.value)}
                className="appearance-none input-base pr-8 text-sm cursor-pointer"
              >
                {sourceOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--text-muted)] pointer-events-none" />
            </div>
          </div>

          {/* 重置按钮 */}
          {(type || source || keyword) && (
            <div className="pt-2">
              <button
                onClick={resetFilters}
                className="text-sm text-primary-400 hover:text-primary-300 transition-colors"
              >
                清除所有筛选条件
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
