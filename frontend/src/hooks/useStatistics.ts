/**
 * 统计数据相关 Hooks
 * 封装统计 API 调用，提供响应式数据
 */

'use client';

import { useQuery } from '@tanstack/react-query';
import {
  getOverviewStats,
  getTrendData,
  getSourceDistribution,
  getTypeDistribution,
  getTagCloud,
  OverviewStats,
  TrendDataPoint,
  DistributionItem,
  TagCloudItem,
} from '@/lib/api';

/**
 * 概览统计数据 Hook
 */
export function useOverviewStats() {
  return useQuery<OverviewStats>({
    queryKey: ['stats', 'overview'],
    queryFn: getOverviewStats,
    staleTime: 5 * 60 * 1000, // 5 分钟内数据视为新鲜
    refetchOnWindowFocus: false,
  });
}

/**
 * 趋势数据 Hook
 * @param days 天数，默认 30 天
 */
export function useTrendData(days: number = 30) {
  return useQuery<TrendDataPoint[]>({
    queryKey: ['stats', 'trend', days],
    queryFn: () => getTrendData(days),
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}

/**
 * 来源分布数据 Hook
 */
export function useSourceDistribution() {
  return useQuery<DistributionItem[]>({
    queryKey: ['stats', 'distribution', 'source'],
    queryFn: getSourceDistribution,
    staleTime: 10 * 60 * 1000, // 10 分钟内数据视为新鲜
    refetchOnWindowFocus: false,
  });
}

/**
 * 类型分布数据 Hook
 */
export function useTypeDistribution() {
  return useQuery<DistributionItem[]>({
    queryKey: ['stats', 'distribution', 'type'],
    queryFn: getTypeDistribution,
    staleTime: 10 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}

/**
 * 标签云数据 Hook
 * @param limit 限制数量，默认 50
 */
export function useTagCloud(limit: number = 50) {
  return useQuery<TagCloudItem[]>({
    queryKey: ['stats', 'tags', 'cloud', limit],
    queryFn: () => getTagCloud(limit),
    staleTime: 10 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}
