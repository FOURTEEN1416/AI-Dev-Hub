/**
 * 高级筛选组件
 * 包含关键词搜索、类型多选、来源多选、标签多选、状态选择、日期范围选择、排序方式选择
 * 支持展开/收起功能和重置按钮
 */

'use client';

import { useState, useEffect } from 'react';
import { SlidersHorizontal, ChevronDown, ChevronUp, RotateCcw, Search } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { AdvancedFilter } from '@/lib/api';
import TypeFilter from './TypeFilter';
import SourceFilter from './SourceFilter';
import TagFilter from './TagFilter';
import DateRangePicker from './DateRangePicker';
import SortSelect from './SortSelect';

interface AdvancedFilterProps {
  /** 筛选条件变更回调 */
  onFilterChange: (filters: AdvancedFilter) => void;
  /** 初始筛选条件 */
  initialFilters?: AdvancedFilter;
  /** 是否默认展开 */
  defaultExpanded?: boolean;
}

/** 默认筛选条件 */
const DEFAULT_FILTERS: AdvancedFilter = {
  keyword: '',
  types: [],
  sources: [],
  tags: [],
  status: undefined,
  has_deadline: undefined,
  deadline_start: undefined,
  deadline_end: undefined,
  created_start: undefined,
  created_end: undefined,
  sort_by: 'created_at',
  sort_order: 'desc',
};

export default function AdvancedFilter({
  onFilterChange,
  initialFilters,
  defaultExpanded = false,
}: AdvancedFilterProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const [filters, setFilters] = useState<AdvancedFilter>({
    ...DEFAULT_FILTERS,
    ...initialFilters,
  });

  // 同步外部传入的初始筛选条件
  useEffect(() => {
    if (initialFilters) {
      setFilters((prev) => ({ ...DEFAULT_FILTERS, ...initialFilters }));
    }
  }, [initialFilters]);

  /**
   * 更新筛选条件并触发回调
   */
  const updateFilters = (updates: Partial<AdvancedFilter>) => {
    const newFilters = { ...filters, ...updates };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  /**
   * 重置所有筛选条件
   */
  const resetFilters = () => {
    const resetFilters = { ...DEFAULT_FILTERS };
    setFilters(resetFilters);
    onFilterChange(resetFilters);
  };

  /**
   * 处理关键词变更
   */
  const handleKeywordChange = (keyword: string) => {
    updateFilters({ keyword: keyword || undefined });
  };

  /**
   * 处理类型变更
   */
  const handleTypesChange = (types: string[]) => {
    updateFilters({ types: types.length > 0 ? types : undefined });
  };

  /**
   * 处理来源变更
   */
  const handleSourcesChange = (sources: string[]) => {
    updateFilters({ sources: sources.length > 0 ? sources : undefined });
  };

  /**
   * 处理标签变更
   */
  const handleTagsChange = (tags: string[]) => {
    updateFilters({ tags: tags.length > 0 ? tags : undefined });
  };

  /**
   * 处理状态变更
   */
  const handleStatusChange = (status: string) => {
    updateFilters({ status: status || undefined });
  };

  /**
   * 处理截止日期范围变更
   */
  const handleDeadlineChange = (startDate?: string, endDate?: string) => {
    updateFilters({
      deadline_start: startDate,
      deadline_end: endDate,
    });
  };

  /**
   * 处理创建时间范围变更
   */
  const handleCreatedChange = (startDate?: string, endDate?: string) => {
    updateFilters({
      created_start: startDate,
      created_end: endDate,
    });
  };

  /**
   * 处理排序变更
   */
  const handleSortChange = (sortBy: 'created_at' | 'deadline' | 'title', sortOrder: 'asc' | 'desc') => {
    updateFilters({
      sort_by: sortBy,
      sort_order: sortOrder,
    });
  };

  /**
   * 判断是否有筛选条件
   */
  const hasActiveFilters = () => {
    return (
      (filters.keyword && filters.keyword.length > 0) ||
      (filters.types && filters.types.length > 0) ||
      (filters.sources && filters.sources.length > 0) ||
      (filters.tags && filters.tags.length > 0) ||
      filters.status ||
      filters.has_deadline !== undefined ||
      filters.deadline_start ||
      filters.deadline_end ||
      filters.created_start ||
      filters.created_end
    );
  };

  /**
   * 获取活跃筛选条件数量
   */
  const getActiveFilterCount = () => {
    let count = 0;
    if (filters.keyword) count++;
    if (filters.types?.length) count += filters.types.length;
    if (filters.sources?.length) count += filters.sources.length;
    if (filters.tags?.length) count += filters.tags.length;
    if (filters.status) count++;
    if (filters.has_deadline !== undefined) count++;
    if (filters.deadline_start || filters.deadline_end) count++;
    if (filters.created_start || filters.created_end) count++;
    return count;
  };

  const activeFilterCount = getActiveFilterCount();

  return (
    <div className="space-y-4">
      {/* 主筛选栏 */}
      <div className="flex flex-col sm:flex-row gap-3">
        {/* 关键词搜索框 */}
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--text-muted)]" />
          <input
            type="text"
            value={filters.keyword || ''}
            onChange={(e) => handleKeywordChange(e.target.value)}
            placeholder="搜索机会标题、描述..."
            className={cn(
              'w-full pl-10 pr-4 py-2.5 rounded-lg transition-all',
              'bg-[var(--bg-secondary)] border border-[var(--border-color)]',
              'text-[var(--text-primary)] placeholder:text-[var(--text-muted)]',
              'focus:outline-none focus:ring-1 focus:ring-primary-500/50 focus:border-primary-500/50'
            )}
          />
        </div>

        {/* 展开/收起按钮 */}
        <button
          type="button"
          onClick={() => setIsExpanded(!isExpanded)}
          className={cn(
            'flex items-center gap-2 px-4 py-2.5 rounded-lg transition-all',
            'border border-[var(--border-color)] text-[var(--text-secondary)]',
            'hover:border-[var(--border-hover)] hover:text-[var(--text-primary)]',
            isExpanded && 'border-primary-500/50 text-primary-400 bg-primary-500/5'
          )}
        >
          <SlidersHorizontal className="h-4 w-4" />
          <span className="text-sm font-medium">高级筛选</span>
          {activeFilterCount > 0 && (
            <span className="px-1.5 py-0.5 text-xs rounded-full bg-primary-500/20 text-primary-400">
              {activeFilterCount}
            </span>
          )}
          {isExpanded ? (
            <ChevronUp className="h-4 w-4" />
          ) : (
            <ChevronDown className="h-4 w-4" />
          )}
        </button>

        {/* 重置按钮 */}
        {hasActiveFilters() && (
          <button
            type="button"
            onClick={resetFilters}
            className={cn(
              'flex items-center gap-2 px-4 py-2.5 rounded-lg transition-all',
              'border border-[var(--border-color)] text-[var(--text-secondary)]',
              'hover:border-[var(--border-hover)] hover:text-[var(--text-primary)]'
            )}
          >
            <RotateCcw className="h-4 w-4" />
            <span className="text-sm font-medium">重置</span>
          </button>
        )}
      </div>

      {/* 展开的筛选面板 */}
      {isExpanded && (
        <div className="card-base p-6 space-y-6 animate-in">
          {/* 第一行：类型和来源 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <TypeFilter
              selectedTypes={filters.types || []}
              onChange={handleTypesChange}
              multiple={true}
            />
            <SourceFilter
              selectedSources={filters.sources || []}
              onChange={handleSourcesChange}
            />
          </div>

          {/* 第二行：标签和状态 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <TagFilter
              selectedTags={filters.tags || []}
              onChange={handleTagsChange}
            />
            <div className="space-y-2">
              <label className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider">
                状态
              </label>
              <div className="flex flex-wrap gap-2">
                {[
                  { value: '', label: '全部' },
                  { value: 'active', label: '进行中' },
                  { value: 'closed', label: '已关闭' },
                  { value: 'expired', label: '已过期' },
                ].map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => handleStatusChange(option.value)}
                    className={cn(
                      'px-3 py-1.5 rounded-lg text-sm font-medium transition-all border',
                      (option.value === '' && !filters.status) || filters.status === option.value
                        ? 'bg-primary-500/10 text-primary-400 border-primary-500/30'
                        : 'border-[var(--border-color)] text-[var(--text-secondary)] hover:border-[var(--border-hover)] hover:text-[var(--text-primary)]'
                    )}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* 第三行：日期范围 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <DateRangePicker
              startDate={filters.deadline_start}
              endDate={filters.deadline_end}
              onChange={handleDeadlineChange}
              label="截止日期范围"
            />
            <DateRangePicker
              startDate={filters.created_start}
              endDate={filters.created_end}
              onChange={handleCreatedChange}
              label="创建时间范围"
            />
          </div>

          {/* 第四行：排序 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <SortSelect
              sortBy={filters.sort_by}
              sortOrder={filters.sort_order}
              onChange={handleSortChange}
            />
            {/* 有截止日期筛选 */}
            <div className="space-y-2">
              <label className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider">
                其他筛选
              </label>
              <div className="flex items-center gap-3">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={filters.has_deadline === true}
                    onChange={(e) => {
                      updateFilters({
                        has_deadline: e.target.checked ? true : undefined,
                      });
                    }}
                    className="w-4 h-4 rounded border-[var(--border-color)] bg-[var(--bg-tertiary)] text-primary-500 focus:ring-primary-500/50"
                  />
                  <span className="text-sm text-[var(--text-secondary)]">
                    仅显示有截止日期的机会
                  </span>
                </label>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
