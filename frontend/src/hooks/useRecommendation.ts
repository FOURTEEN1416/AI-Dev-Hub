/**
 * 推荐相关 Hooks
 * 提供个性化推荐、热门推荐、相似机会等数据获取功能
 */

import { useQuery } from '@tanstack/react-query';
import { getRecommendations, getTrending, getSimilarOpportunities } from '@/lib/api';
import type { RecommendedOpportunity, Opportunity } from '@/types';

/**
 * 获取个性化推荐机会
 * @param limit 限制数量，默认 10
 */
export function useRecommendations(limit: number = 10) {
  return useQuery<RecommendedOpportunity[]>({
    queryKey: ['recommendations', limit],
    queryFn: () => getRecommendations(limit),
    staleTime: 5 * 60 * 1000, // 5 分钟内数据视为新鲜
    gcTime: 30 * 60 * 1000, // 缓存保留 30 分钟
  });
}

/**
 * 获取热门机会
 * @param days 统计天数，默认 7 天
 * @param limit 限制数量，默认 10
 */
export function useTrending(days: number = 7, limit: number = 10) {
  return useQuery<Opportunity[]>({
    queryKey: ['trending', days, limit],
    queryFn: () => getTrending(days, limit),
    staleTime: 10 * 60 * 1000, // 10 分钟内数据视为新鲜
    gcTime: 30 * 60 * 1000, // 缓存保留 30 分钟
  });
}

/**
 * 获取相似机会
 * @param id 机会 ID
 * @param limit 限制数量，默认 5
 */
export function useSimilarOpportunities(id: number, limit: number = 5) {
  return useQuery<Opportunity[]>({
    queryKey: ['similar-opportunities', id, limit],
    queryFn: () => getSimilarOpportunities(id, limit),
    enabled: id > 0, // 只有 ID 有效时才发起请求
    staleTime: 10 * 60 * 1000, // 10 分钟内数据视为新鲜
    gcTime: 30 * 60 * 1000, // 缓存保留 30 分钟
  });
}
