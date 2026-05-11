/**
 * 统计卡片组件
 * 用于展示单个统计数据，支持图标和趋势显示
 */

'use client';

import { TrendingUp, TrendingDown } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StatsCardProps {
  /** 标题 */
  title: string;
  /** 数值 */
  value: number | string;
  /** 图标 */
  icon?: React.ReactNode;
  /** 趋势数据 */
  trend?: { value: number; isUp: boolean };
  /** 主题颜色 */
  color?: 'blue' | 'purple' | 'cyan' | 'green' | 'orange' | 'red';
  /** 是否正在加载 */
  isLoading?: boolean;
}

/** 颜色配置 */
const colorConfig = {
  blue: {
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/30',
    icon: 'text-blue-400',
    glow: 'shadow-blue-500/20',
  },
  purple: {
    bg: 'bg-purple-500/10',
    border: 'border-purple-500/30',
    icon: 'text-purple-400',
    glow: 'shadow-purple-500/20',
  },
  cyan: {
    bg: 'bg-cyan-500/10',
    border: 'border-cyan-500/30',
    icon: 'text-cyan-400',
    glow: 'shadow-cyan-500/20',
  },
  green: {
    bg: 'bg-green-500/10',
    border: 'border-green-500/30',
    icon: 'text-green-400',
    glow: 'shadow-green-500/20',
  },
  orange: {
    bg: 'bg-orange-500/10',
    border: 'border-orange-500/30',
    icon: 'text-orange-400',
    glow: 'shadow-orange-500/20',
  },
  red: {
    bg: 'bg-red-500/10',
    border: 'border-red-500/30',
    icon: 'text-red-400',
    glow: 'shadow-red-500/20',
  },
};

export default function StatsCard({
  title,
  value,
  icon,
  trend,
  color = 'blue',
  isLoading,
}: StatsCardProps) {
  const config = colorConfig[color];

  // 加载状态
  if (isLoading) {
    return (
      <div className="card-base p-4 animate-pulse">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-[var(--bg-secondary)]" />
          <div className="flex-1">
            <div className="h-4 w-20 bg-[var(--bg-secondary)] rounded mb-2" />
            <div className="h-6 w-16 bg-[var(--bg-secondary)] rounded" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        'card-hover p-4',
        'border',
        config.bg,
        config.border
      )}
    >
      <div className="flex items-center gap-3">
        {/* 图标 */}
        {icon && (
          <div
            className={cn(
              'flex items-center justify-center w-10 h-10 rounded-lg',
              config.bg,
              config.icon
            )}
          >
            {icon}
          </div>
        )}

        {/* 内容 */}
        <div className="flex-1 min-w-0">
          <p className="text-sm text-[var(--text-muted)] truncate">{title}</p>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-[var(--text-primary)]">
              {value}
            </span>
            {/* 趋势指示 */}
            {trend && (
              <span
                className={cn(
                  'flex items-center text-xs font-medium',
                  trend.isUp ? 'text-green-400' : 'text-red-400'
                )}
              >
                {trend.isUp ? (
                  <TrendingUp className="w-3 h-3 mr-0.5" />
                ) : (
                  <TrendingDown className="w-3 h-3 mr-0.5" />
                )}
                {Math.abs(trend.value)}%
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
