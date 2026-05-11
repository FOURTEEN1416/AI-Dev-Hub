/**
 * 工具函数
 */

import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { format, formatDistanceToNow, isPast, parseISO } from 'date-fns';
import { zhCN } from 'date-fns/locale';
import type { OpportunityType } from '@/types';

/**
 * 合并 className
 * 使用 clsx 处理条件类名，tailwind-merge 处理 Tailwind 类名冲突
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * 格式化日期为可读字符串
 */
export function formatDate(dateStr: string | null): string {
  if (!dateStr) return '无截止日期';
  try {
    const date = parseISO(dateStr);
    return format(date, 'yyyy年MM月dd日', { locale: zhCN });
  } catch {
    return dateStr;
  }
}

/**
 * 格式化日期为相对时间
 */
export function formatRelativeDate(dateStr: string | null): string {
  if (!dateStr) return '';
  try {
    const date = parseISO(dateStr);
    return formatDistanceToNow(date, { addSuffix: true, locale: zhCN });
  } catch {
    return dateStr;
  }
}

/**
 * 判断日期是否已过期
 */
export function isExpired(dateStr: string | null): boolean {
  if (!dateStr) return false;
  try {
    return isPast(parseISO(dateStr));
  } catch {
    return false;
  }
}

/**
 * 获取机会类型的中文名称
 */
export function getTypeLabel(type: OpportunityType | string): string {
  const labels: Record<string, string> = {
    developer_program: '开发者计划',
    competition: '比赛竞赛',
    free_credits: '免费额度',
    community: '社区动态',
  };
  return labels[type] || type;
}

/**
 * 获取机会类型的颜色样式
 */
export function getTypeColor(type: OpportunityType | string): {
  bg: string;
  text: string;
  border: string;
} {
  const colors: Record<string, { bg: string; text: string; border: string }> = {
    developer_program: {
      bg: 'bg-blue-500/10',
      text: 'text-blue-400',
      border: 'border-blue-500/30',
    },
    competition: {
      bg: 'bg-amber-500/10',
      text: 'text-amber-400',
      border: 'border-amber-500/30',
    },
    free_credits: {
      bg: 'bg-emerald-500/10',
      text: 'text-emerald-400',
      border: 'border-emerald-500/30',
    },
    community: {
      bg: 'bg-purple-500/10',
      text: 'text-purple-400',
      border: 'border-purple-500/30',
    },
  };
  return colors[type] || {
    bg: 'bg-gray-500/10',
    text: 'text-gray-400',
    border: 'border-gray-500/30',
  };
}

/**
 * 截断文本
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

/**
 * 计算总页数
 */
export function getTotalPages(total: number, limit: number): number {
  return Math.ceil(total / limit);
}
