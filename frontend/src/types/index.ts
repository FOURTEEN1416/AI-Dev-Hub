/**
 * TypeScript 类型定义
 * 与后端 API 数据结构对应
 */

/** 机会类型枚举 */
export type OpportunityType =
  | 'developer_program'  // 开发者计划
  | 'competition'        // 比赛/竞赛
  | 'free_credits'       // 免费额度
  | 'community';         // 社区动态

/** 机会状态 */
export type OpportunityStatus = 'active' | 'closed' | 'expired';

/** 机会数据接口 */
export interface Opportunity {
  id: number;
  title: string;
  type: OpportunityType;
  source: string;
  source_url: string | null;
  description: string | null;
  tags: string[] | null;
  deadline: string | null;       // ISO 日期字符串
  reward: string | null;
  requirements: string | null;
  official_link: string | null;
  status: OpportunityStatus;
  created_at: string;            // ISO 日期字符串
  updated_at: string;            // ISO 日期字符串
}

/** 机会列表响应 */
export interface OpportunityListResponse {
  items: Opportunity[];
  total: number;
  page: number;
  limit: number;
}

/** 机会筛选条件 */
export interface OpportunityFilters {
  type?: OpportunityType | '';
  source?: string;
  status?: OpportunityStatus;
  tags?: string[];
  keyword?: string;
  page?: number;
  limit?: number;
}

/** 排序选项 */
export type SortOption = 'latest' | 'popular' | 'deadline';

/** 分页参数 */
export interface PaginationParams {
  page: number;
  limit: number;
  total: number;
}

// ==================== 用户相关类型 ====================

/** 用户信息 */
export interface User {
  id: number;
  email: string;
  username: string | null;
  is_active: boolean;
  created_at: string;
}

/** 登录请求 */
export interface LoginRequest {
  email: string;
  password: string;
}

/** 注册请求 */
export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

/** 认证响应 */
export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

/** 用户收藏 */
export interface UserFavorite {
  id: number;
  opportunity_id: number;
  opportunity: Opportunity;
  created_at: string;
}

// ==================== 推荐相关类型 ====================

/** 推荐机会 */
export interface RecommendedOpportunity {
  opportunity: Opportunity;
  score: number;
  reason: string;
}

/** 用户订阅设置 */
export interface UserSubscription {
  preferred_types: string[];
  preferred_sources: string[];
  preferred_tags: string[];
  email_notification: boolean;
  notification_frequency: 'daily' | 'weekly';
}

/** 用户行为 */
export interface UserBehavior {
  opportunity_id: number;
  behavior_type: 'view' | 'favorite' | 'click' | 'share';
  duration?: number;
}
