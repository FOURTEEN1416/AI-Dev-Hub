/**
 * 机会相关自定义 Hook
 * 使用 @tanstack/react-query 管理数据请求
 */

'use client';

import { useQuery } from '@tanstack/react-query';
import {
  getOpportunities,
  getOpportunity,
  searchOpportunities,
} from '@/lib/api';
import type { OpportunityFilters } from '@/types';

/** Query Key 常量 */
export const QUERY_KEYS = {
  opportunities: (filters: OpportunityFilters) =>
    ['opportunities', filters] as const,
  opportunity: (id: number) =>
    ['opportunity', id] as const,
  search: (keyword: string, page: number) =>
    ['search', keyword, page] as const,
};

/**
 * 获取机会列表
 */
export function useOpportunities(filters: OpportunityFilters = {}) {
  return useQuery({
    queryKey: QUERY_KEYS.opportunities(filters),
    queryFn: () => getOpportunities(filters),
    staleTime: 5 * 60 * 1000, // 5 分钟内不重新请求
    gcTime: 10 * 60 * 1000,   // 10 分钟缓存
  });
}

/**
 * 获取单个机会详情
 */
export function useOpportunity(id: number) {
  return useQuery({
    queryKey: QUERY_KEYS.opportunity(id),
    queryFn: () => getOpportunity(id),
    enabled: !!id, // id 存在时才请求
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * 搜索机会
 */
export function useSearch(keyword: string, page: number = 1) {
  return useQuery({
    queryKey: QUERY_KEYS.search(keyword, page),
    queryFn: () => searchOpportunities(keyword, page),
    enabled: keyword.trim().length > 0, // 关键词非空时才请求
    staleTime: 2 * 60 * 1000,
  });
}
