/**
 * API 请求封装
 * 基于 axios，统一管理接口请求
 */

import axios from 'axios';
import type {
  Opportunity,
  OpportunityListResponse,
  OpportunityFilters,
  User,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  UserFavorite,
  RecommendedOpportunity,
  UserSubscription,
  UserBehavior,
} from '@/types';

/**
 * 高级筛选条件接口
 */
export interface AdvancedFilter {
  keyword?: string;
  types?: string[];
  sources?: string[];
  tags?: string[];
  status?: string;
  has_deadline?: boolean;
  deadline_start?: string;
  deadline_end?: string;
  created_start?: string;
  created_end?: string;
  sort_by?: 'created_at' | 'deadline' | 'title';
  sort_order?: 'asc' | 'desc';
}

// 创建 axios 实例
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 从 localStorage 获取 token
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败';
    console.error('API 请求错误:', message);
    return Promise.reject(error);
  }
);

/**
 * 获取机会列表
 */
export async function getOpportunities(
  filters: OpportunityFilters = {}
): Promise<OpportunityListResponse> {
  const params: Record<string, string | number | undefined> = {
    page: filters.page || 1,
    limit: filters.limit || 20,
  };

  if (filters.type) params.type = filters.type;
  if (filters.source) params.source = filters.source;
  if (filters.status) params.status = filters.status;
  if (filters.keyword) params.keyword = filters.keyword;
  if (filters.tags && filters.tags.length > 0) {
    params.tags = filters.tags.join(',');
  }

  return api.get('/opportunities', { params });
}

/**
 * 获取机会详情
 */
export async function getOpportunity(id: number): Promise<Opportunity> {
  return api.get(`/opportunities/${id}`);
}

/**
 * 搜索机会
 */
export async function searchOpportunities(
  keyword: string,
  page: number = 1,
  limit: number = 20
): Promise<OpportunityListResponse> {
  return api.get('/opportunities/search', {
    params: { keyword, page, limit },
  });
}

/**
 * 获取所有机会类型
 */
export async function getTypes(): Promise<string[]> {
  return api.get('/opportunities/types');
}

/**
 * 获取所有来源平台
 */
export async function getSources(): Promise<string[]> {
  return api.get('/opportunities/sources');
}

// ==================== 认证相关 API ====================

/**
 * 用户登录
 */
export async function login(data: LoginRequest): Promise<AuthResponse> {
  const response = await api.post('/auth/login', data) as AuthResponse;
  // 保存 token 到 localStorage
  if (typeof window !== 'undefined') {
    localStorage.setItem('token', response.access_token);
  }
  return response;
}

/**
 * 用户注册
 */
export async function register(data: RegisterRequest): Promise<AuthResponse> {
  const response = await api.post('/auth/register', data) as AuthResponse;
  // 保存 token 到 localStorage
  if (typeof window !== 'undefined') {
    localStorage.setItem('token', response.access_token);
  }
  return response;
}

/**
 * 用户登出
 */
export async function logout(): Promise<void> {
  try {
    await api.post('/auth/logout');
  } finally {
    // 无论请求成功与否，都清除本地 token
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
    }
  }
}

/**
 * 获取当前用户信息
 */
export async function getCurrentUser(): Promise<User> {
  return api.get('/auth/me');
}

/**
 * 更新用户资料
 */
export async function updateProfile(data: Partial<User>): Promise<User> {
  return api.patch('/auth/profile', data);
}

// ==================== 收藏相关 API ====================

/**
 * 获取用户收藏列表
 */
export async function getFavorites(
  page: number = 1,
  limit: number = 20
): Promise<{ items: UserFavorite[]; total: number }> {
  return api.get('/favorites', { params: { page, limit } });
}

/**
 * 添加收藏
 */
export async function addFavorite(opportunityId: number): Promise<void> {
  await api.post('/favorites', { opportunity_id: opportunityId });
}

/**
 * 取消收藏
 */
export async function removeFavorite(opportunityId: number): Promise<void> {
  await api.delete(`/favorites/${opportunityId}`);
}

/**
 * 检查是否已收藏
 */
export async function checkFavorite(opportunityId: number): Promise<boolean> {
  try {
    const response = await api.get(`/favorites/check/${opportunityId}`) as { is_favorited: boolean };
    return response.is_favorited;
  } catch {
    return false;
  }
}

/**
 * 高级搜索机会
 */
export async function advancedSearch(
  filters: AdvancedFilter,
  page: number = 1,
  limit: number = 20
): Promise<OpportunityListResponse> {
  const params: Record<string, string | number | boolean | undefined> = {
    page,
    limit,
  };

  if (filters.keyword) params.keyword = filters.keyword;
  if (filters.types && filters.types.length > 0) {
    params.types = filters.types.join(',');
  }
  if (filters.sources && filters.sources.length > 0) {
    params.sources = filters.sources.join(',');
  }
  if (filters.tags && filters.tags.length > 0) {
    params.tags = filters.tags.join(',');
  }
  if (filters.status) params.status = filters.status;
  if (filters.has_deadline !== undefined) {
    params.has_deadline = filters.has_deadline;
  }
  if (filters.deadline_start) params.deadline_start = filters.deadline_start;
  if (filters.deadline_end) params.deadline_end = filters.deadline_end;
  if (filters.created_start) params.created_start = filters.created_start;
  if (filters.created_end) params.created_end = filters.created_end;
  if (filters.sort_by) params.sort_by = filters.sort_by;
  if (filters.sort_order) params.sort_order = filters.sort_order;

  return api.get('/opportunities/advanced-search', { params });
}

/**
 * 获取热门标签
 */
export async function getPopularTags(limit: number = 20): Promise<string[]> {
  return api.get('/opportunities/tags/popular', { params: { limit } });
}

/**
 * 获取筛选选项
 */
export async function getFilterOptions(): Promise<{
  types: string[];
  sources: string[];
  tags: string[];
}> {
  return api.get('/opportunities/filter-options');
}

// ==================== 统计相关 API ====================

/**
 * 概览统计数据接口
 */
export interface OverviewStats {
  total_opportunities: number;
  by_type: Record<string, number>;
  by_source: Record<string, number>;
  active_count: number;
  expiring_soon: number;
}

/**
 * 趋势数据点接口
 */
export interface TrendDataPoint {
  date: string;
  count: number;
  by_type: Record<string, number>;
}

/**
 * 分布项接口
 */
export interface DistributionItem {
  name: string;
  count: number;
  percentage: number;
}

/**
 * 标签云项接口
 */
export interface TagCloudItem {
  tag: string;
  count: number;
  size: number;
}

/**
 * 获取概览统计数据
 */
export async function getOverviewStats(): Promise<OverviewStats> {
  return api.get('/stats/overview');
}

/**
 * 获取趋势数据
 * @param days 天数，默认 30 天
 * @param groupBy 分组方式，可选 'day' | 'week' | 'month'
 */
export async function getTrendData(
  days: number = 30,
  groupBy: string = 'day'
): Promise<TrendDataPoint[]> {
  return api.get('/stats/trend', { params: { days, group_by: groupBy } });
}

/**
 * 获取来源分布数据
 */
export async function getSourceDistribution(): Promise<DistributionItem[]> {
  return api.get('/stats/distribution/source');
}

/**
 * 获取类型分布数据
 */
export async function getTypeDistribution(): Promise<DistributionItem[]> {
  return api.get('/stats/distribution/type');
}

/**
 * 获取标签云数据
 * @param limit 限制数量，默认 50
 */
export async function getTagCloud(limit: number = 50): Promise<TagCloudItem[]> {
  return api.get('/stats/tags/cloud', { params: { limit } });
}

// ==================== 推荐相关 API ====================

/**
 * 获取个性化推荐机会
 * @param limit 限制数量，默认 10
 */
export async function getRecommendations(
  limit: number = 10
): Promise<RecommendedOpportunity[]> {
  return api.get('/recommendations', { params: { limit } });
}

/**
 * 获取热门机会
 * @param days 统计天数，默认 7 天
 * @param limit 限制数量，默认 10
 */
export async function getTrending(
  days: number = 7,
  limit: number = 10
): Promise<Opportunity[]> {
  return api.get('/recommendations/trending', { params: { days, limit } });
}

/**
 * 获取相似机会
 * @param id 机会 ID
 * @param limit 限制数量，默认 5
 */
export async function getSimilarOpportunities(
  id: number,
  limit: number = 5
): Promise<Opportunity[]> {
  return api.get(`/recommendations/similar/${id}`, { params: { limit } });
}

/**
 * 记录用户行为
 * @param behavior 用户行为数据
 */
export async function recordBehavior(behavior: UserBehavior): Promise<void> {
  await api.post('/recommendations/behavior', behavior);
}

// ==================== 订阅相关 API ====================

/**
 * 获取用户订阅设置
 */
export async function getSubscription(): Promise<UserSubscription> {
  return api.get('/subscriptions');
}

/**
 * 更新用户订阅设置
 * @param data 订阅设置数据
 */
export async function updateSubscription(
  data: Partial<UserSubscription>
): Promise<UserSubscription> {
  return api.patch('/subscriptions', data);
}

export default api;
