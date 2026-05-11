/**
 * 类型筛选组件
 * 单选按钮组样式，支持多选
 */

'use client';

import { cn, getTypeLabel } from '@/lib/utils';
import type { OpportunityType } from '@/types';

/** 类型选项配置 */
const TYPE_OPTIONS: { value: OpportunityType | ''; label: string; color: string }[] = [
  { value: '', label: '全部', color: 'gray' },
  { value: 'developer_program', label: '开发者计划', color: 'blue' },
  { value: 'competition', label: '比赛竞赛', color: 'amber' },
  { value: 'free_credits', label: '免费额度', color: 'emerald' },
  { value: 'community', label: '社区动态', color: 'purple' },
];

interface TypeFilterProps {
  /** 已选中的类型列表 */
  selectedTypes: string[];
  /** 类型变更回调 */
  onChange: (types: string[]) => void;
  /** 是否多选模式 */
  multiple?: boolean;
}

export default function TypeFilter({
  selectedTypes,
  onChange,
  multiple = true,
}: TypeFilterProps) {
  /**
   * 处理类型点击
   */
  const handleTypeClick = (type: OpportunityType | '') => {
    if (!multiple) {
      // 单选模式
      onChange(type ? [type] : []);
      return;
    }

    // 多选模式
    if (type === '') {
      // 点击"全部"清空选择
      onChange([]);
      return;
    }

    const newTypes = selectedTypes.includes(type)
      ? selectedTypes.filter((t) => t !== type)
      : [...selectedTypes, type];
    
    onChange(newTypes);
  };

  /**
   * 判断类型是否选中
   */
  const isSelected = (type: OpportunityType | '') => {
    if (type === '') {
      return selectedTypes.length === 0;
    }
    return selectedTypes.includes(type);
  };

  /**
   * 获取按钮样式
   */
  const getButtonStyle = (type: OpportunityType | '', color: string) => {
    const selected = isSelected(type);
    
    const colorStyles: Record<string, { bg: string; text: string; border: string }> = {
      gray: {
        bg: 'bg-gray-500/10',
        text: 'text-gray-400',
        border: 'border-gray-500/30',
      },
      blue: {
        bg: 'bg-blue-500/10',
        text: 'text-blue-400',
        border: 'border-blue-500/30',
      },
      amber: {
        bg: 'bg-amber-500/10',
        text: 'text-amber-400',
        border: 'border-amber-500/30',
      },
      emerald: {
        bg: 'bg-emerald-500/10',
        text: 'text-emerald-400',
        border: 'border-emerald-500/30',
      },
      purple: {
        bg: 'bg-purple-500/10',
        text: 'text-purple-400',
        border: 'border-purple-500/30',
      },
    };

    const style = colorStyles[color] || colorStyles.gray;

    return cn(
      'px-3 py-1.5 rounded-lg text-sm font-medium transition-all border cursor-pointer',
      selected
        ? `${style.bg} ${style.text} ${style.border}`
        : 'border-[var(--border-color)] text-[var(--text-secondary)] hover:border-[var(--border-hover)] hover:text-[var(--text-primary)]'
    );
  };

  return (
    <div className="space-y-2">
      <label className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider">
        机会类型
      </label>
      <div className="flex flex-wrap gap-2">
        {TYPE_OPTIONS.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => handleTypeClick(option.value)}
            className={getButtonStyle(option.value, option.color)}
          >
            {option.label}
          </button>
        ))}
      </div>
      {multiple && selectedTypes.length > 0 && (
        <p className="text-xs text-[var(--text-muted)]">
          已选择 {selectedTypes.length} 种类型
        </p>
      )}
    </div>
  );
}
