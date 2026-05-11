/**
 * 筛选摘要组件
 * 显示当前已选的筛选条件，每个条件可单独移除，支持一键清除所有筛选
 */

'use client';

import { X, Filter, Hash, Calendar, Clock, Building, Tag, FileText } from 'lucide-react';
import { cn } from '@/lib/utils';
import { getTypeLabel } from '@/lib/utils';
import type { AdvancedFilter } from '@/lib/api';

interface FilterSummaryProps {
  /** 当前筛选条件 */
  filters: AdvancedFilter;
  /** 移除单个筛选条件 */
  onRemove: (key: keyof AdvancedFilter, value?: string) => void;
  /** 清除所有筛选条件 */
  onClearAll: () => void;
  /** 是否显示清除所有按钮 */
  showClearAll?: boolean;
}

interface FilterItem {
  key: keyof AdvancedFilter;
  label: string;
  value: string;
  icon: React.ReactNode;
  removableValue?: string; // 用于数组类型的单个移除
}

export default function FilterSummary({
  filters,
  onRemove,
  onClearAll,
  showClearAll = true,
}: FilterSummaryProps) {
  /**
   * 构建筛选条件列表
   */
  const buildFilterItems = (): FilterItem[] => {
    const items: FilterItem[] = [];

    // 关键词
    if (filters.keyword) {
      items.push({
        key: 'keyword',
        label: '关键词',
        value: filters.keyword,
        icon: <FileText className="h-3 w-3" />,
      });
    }

    // 类型（多选）
    if (filters.types && filters.types.length > 0) {
      filters.types.forEach((type) => {
        items.push({
          key: 'types',
          label: '类型',
          value: getTypeLabel(type),
          icon: <Tag className="h-3 w-3" />,
          removableValue: type,
        });
      });
    }

    // 来源（多选）
    if (filters.sources && filters.sources.length > 0) {
      filters.sources.forEach((source) => {
        items.push({
          key: 'sources',
          label: '来源',
          value: source,
          icon: <Building className="h-3 w-3" />,
          removableValue: source,
        });
      });
    }

    // 标签（多选）
    if (filters.tags && filters.tags.length > 0) {
      filters.tags.forEach((tag) => {
        items.push({
          key: 'tags',
          label: '标签',
          value: tag,
          icon: <Hash className="h-3 w-3" />,
          removableValue: tag,
        });
      });
    }

    // 状态
    if (filters.status) {
      const statusLabels: Record<string, string> = {
        active: '进行中',
        closed: '已关闭',
        expired: '已过期',
      };
      items.push({
        key: 'status',
        label: '状态',
        value: statusLabels[filters.status] || filters.status,
        icon: <Clock className="h-3 w-3" />,
      });
    }

    // 有截止日期
    if (filters.has_deadline !== undefined) {
      items.push({
        key: 'has_deadline',
        label: '截止日期',
        value: filters.has_deadline ? '有截止日期' : '无截止日期',
        icon: <Calendar className="h-3 w-3" />,
      });
    }

    // 截止日期范围
    if (filters.deadline_start || filters.deadline_end) {
      const start = filters.deadline_start || '不限';
      const end = filters.deadline_end || '不限';
      items.push({
        key: 'deadline_start', // 使用 start 作为主键
        label: '截止日期范围',
        value: `${start} 至 ${end}`,
        icon: <Calendar className="h-3 w-3" />,
      });
    }

    // 创建时间范围
    if (filters.created_start || filters.created_end) {
      const start = filters.created_start || '不限';
      const end = filters.created_end || '不限';
      items.push({
        key: 'created_start', // 使用 start 作为主键
        label: '创建时间范围',
        value: `${start} 至 ${end}`,
        icon: <Calendar className="h-3 w-3" />,
      });
    }

    return items;
  };

  const filterItems = buildFilterItems();
  const hasFilters = filterItems.length > 0;

  if (!hasFilters) {
    return null;
  }

  /**
   * 处理移除筛选条件
   */
  const handleRemove = (item: FilterItem) => {
    if (item.removableValue) {
      // 数组类型的单个移除
      onRemove(item.key, item.removableValue);
    } else {
      // 单值类型的移除
      onRemove(item.key);
    }
  };

  return (
    <div className="space-y-3">
      {/* 标题栏 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-[var(--text-muted)]" />
          <span className="text-sm font-medium text-[var(--text-primary)]">
            当前筛选条件
          </span>
          <span className="text-xs text-[var(--text-muted)]">
            ({filterItems.length} 项)
          </span>
        </div>
        {showClearAll && (
          <button
            type="button"
            onClick={onClearAll}
            className="text-xs text-primary-400 hover:text-primary-300 transition-colors"
          >
            清除全部
          </button>
        )}
      </div>

      {/* 筛选条件标签 */}
      <div className="flex flex-wrap gap-2">
        {filterItems.map((item, index) => (
          <div
            key={`${item.key}-${item.removableValue || index}`}
            className={cn(
              'inline-flex items-center gap-1.5 px-2.5 py-1 text-xs rounded-full',
              'bg-[var(--bg-tertiary)] border border-[var(--border-color)]',
              'text-[var(--text-secondary)]'
            )}
          >
            {item.icon}
            <span className="text-[var(--text-muted)]">{item.label}:</span>
            <span className="text-[var(--text-primary)]">{item.value}</span>
            <button
              type="button"
              onClick={() => handleRemove(item)}
              className="p-0.5 rounded hover:bg-[var(--bg-secondary)] transition-colors ml-1"
              title="移除此条件"
            >
              <X className="h-3 w-3 text-[var(--text-muted)] hover:text-[var(--text-primary)]" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
