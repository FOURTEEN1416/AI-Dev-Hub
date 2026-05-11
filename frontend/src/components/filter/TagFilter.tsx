/**
 * 标签筛选组件
 * 热门标签展示，点击选择/取消，已选标签高亮，支持搜索更多标签
 */

'use client';

import { useState, useEffect, useRef } from 'react';
import { ChevronDown, X, Search, Hash } from 'lucide-react';
import { cn } from '@/lib/utils';

/** 模拟热门标签数据 */
const DEFAULT_POPULAR_TAGS = [
  'AI',
  '机器学习',
  '深度学习',
  'GPT',
  'LLM',
  '计算机视觉',
  'NLP',
  '强化学习',
  '开源',
  '竞赛',
  '奖学金',
  '实习',
  '研究',
  '创业',
  'API',
];

/** 模拟所有标签数据 */
const DEFAULT_ALL_TAGS = [
  ...DEFAULT_POPULAR_TAGS,
  '数据科学',
  'TensorFlow',
  'PyTorch',
  'Kaggle',
  '数据分析',
  '自然语言处理',
  '图像识别',
  '语音识别',
  '推荐系统',
  '联邦学习',
  '模型优化',
  '边缘计算',
  '自动驾驶',
  '医疗AI',
  '金融科技',
];

interface TagFilterProps {
  /** 已选中的标签列表 */
  selectedTags: string[];
  /** 标签变更回调 */
  onChange: (tags: string[]) => void;
  /** 热门标签列表 */
  popularTags?: string[];
  /** 所有标签列表 */
  allTags?: string[];
  /** 显示的热门标签数量 */
  popularLimit?: number;
}

export default function TagFilter({
  selectedTags,
  onChange,
  popularTags = DEFAULT_POPULAR_TAGS,
  allTags = DEFAULT_ALL_TAGS,
  popularLimit = 10,
}: TagFilterProps) {
  const [showAll, setShowAll] = useState(false);
  const [searchKeyword, setSearchKeyword] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);

  // 过滤标签
  const filteredTags = showAll
    ? allTags.filter((tag) => tag.toLowerCase().includes(searchKeyword.toLowerCase()))
    : popularTags.slice(0, popularLimit);

  /**
   * 切换标签选择
   */
  const toggleTag = (tag: string) => {
    const newTags = selectedTags.includes(tag)
      ? selectedTags.filter((t) => t !== tag)
      : [...selectedTags, tag];
    onChange(newTags);
  };

  /**
   * 移除单个标签
   */
  const removeTag = (tag: string, e: React.MouseEvent) => {
    e.stopPropagation();
    onChange(selectedTags.filter((t) => t !== tag));
  };

  /**
   * 清空所有标签
   */
  const clearAll = () => {
    onChange([]);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider">
          标签筛选
        </label>
        {selectedTags.length > 0 && (
          <button
            type="button"
            onClick={clearAll}
            className="text-xs text-primary-400 hover:text-primary-300 transition-colors"
          >
            清空已选
          </button>
        )}
      </div>

      {/* 热门标签展示 */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-xs text-[var(--text-muted)]">热门标签:</span>
          <button
            type="button"
            onClick={() => setShowAll(!showAll)}
            className="text-xs text-primary-400 hover:text-primary-300 transition-colors flex items-center gap-0.5"
          >
            {showAll ? '收起' : '更多'}
            <ChevronDown
              className={cn('h-3 w-3 transition-transform', showAll && 'rotate-180')}
            />
          </button>
        </div>

        {/* 标签云 */}
        <div className="flex flex-wrap gap-1.5">
          {filteredTags.map((tag) => {
            const isSelected = selectedTags.includes(tag);
            return (
              <button
                key={tag}
                type="button"
                onClick={() => toggleTag(tag)}
                className={cn(
                  'inline-flex items-center gap-1 px-2 py-1 text-xs rounded-full transition-all border',
                  isSelected
                    ? 'bg-primary-500/10 text-primary-400 border-primary-500/30'
                    : 'bg-[var(--bg-tertiary)] text-[var(--text-secondary)] border-transparent hover:border-[var(--border-color)] hover:text-[var(--text-primary)]'
                )}
              >
                <Hash className="h-3 w-3" />
                {tag}
              </button>
            );
          })}
        </div>

        {/* 搜索更多标签（展开时显示） */}
        {showAll && (
          <div className="relative mt-2">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--text-muted)]" />
            <input
              type="text"
              value={searchKeyword}
              onChange={(e) => setSearchKeyword(e.target.value)}
              placeholder="搜索标签..."
              className="w-full pl-8 pr-3 py-1.5 text-sm bg-[var(--bg-tertiary)] border border-[var(--border-color)] rounded-md focus:outline-none focus:ring-1 focus:ring-primary-500/50"
            />
          </div>
        )}
      </div>

      {/* 已选标签展示 */}
      {selectedTags.length > 0 && (
        <div className="pt-2 border-t border-[var(--border-color)]">
          <p className="text-xs text-[var(--text-muted)] mb-2">
            已选择 {selectedTags.length} 个标签:
          </p>
          <div className="flex flex-wrap gap-1.5">
            {selectedTags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded-full bg-primary-500/10 text-primary-400 border border-primary-500/20"
              >
                <Hash className="h-3 w-3" />
                {tag}
                <button
                  type="button"
                  onClick={(e) => removeTag(tag, e)}
                  className="p-0.5 rounded hover:bg-primary-500/20 transition-colors"
                >
                  <X className="h-3 w-3" />
                </button>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
