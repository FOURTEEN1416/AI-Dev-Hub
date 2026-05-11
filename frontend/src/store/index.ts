/**
 * Zustand 状态管理
 * 包含筛选条件和主题切换，支持 localStorage 持久化
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { OpportunityType, SortOption, User } from '@/types';
import type { AdvancedFilter } from '@/lib/api';

/** 筛选条件 Store */
interface FilterState {
  type: OpportunityType | '';
  source: string;
  keyword: string;
  sort: SortOption;
  page: number;
  limit: number;

  // 操作方法
  setType: (type: OpportunityType | '') => void;
  setSource: (source: string) => void;
  setKeyword: (keyword: string) => void;
  setSort: (sort: SortOption) => void;
  setPage: (page: number) => void;
  setLimit: (limit: number) => void;
  resetFilters: () => void;
}

/** 主题 Store */
interface ThemeState {
  isDark: boolean;
  toggleTheme: () => void;
  setTheme: (isDark: boolean) => void;
}

/** 高级筛选条件 Store */
interface AdvancedFilterState {
  filters: AdvancedFilter;
  setFilters: (filters: AdvancedFilter) => void;
  updateFilters: (updates: Partial<AdvancedFilter>) => void;
  resetFilters: () => void;
}

/** 用户状态 Store */
interface UserState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
  updateUser: (user: User) => void;
}

/** 初始筛选状态 */
const initialFilterState = {
  type: '' as OpportunityType | '',
  source: '',
  keyword: '',
  sort: 'latest' as SortOption,
  page: 1,
  limit: 12,
};

/** 初始高级筛选状态 */
const initialAdvancedFilterState: AdvancedFilter = {
  keyword: undefined,
  types: undefined,
  sources: undefined,
  tags: undefined,
  status: undefined,
  has_deadline: undefined,
  deadline_start: undefined,
  deadline_end: undefined,
  created_start: undefined,
  created_end: undefined,
  sort_by: 'created_at',
  sort_order: 'desc',
};

/** 筛选条件 Store（带持久化） */
export const useFilterStore = create<FilterState>()(
  persist(
    (set) => ({
      ...initialFilterState,

      setType: (type) => set({ type, page: 1 }),
      setSource: (source) => set({ source, page: 1 }),
      setKeyword: (keyword) => set({ keyword, page: 1 }),
      setSort: (sort) => set({ sort, page: 1 }),
      setPage: (page) => set({ page }),
      setLimit: (limit) => set({ limit, page: 1 }),
      resetFilters: () => set(initialFilterState),
    }),
    {
      name: 'ai-dev-hub-filter-storage',
      partialize: (state) => ({
        type: state.type,
        source: state.source,
        keyword: state.keyword,
        sort: state.sort,
        limit: state.limit,
      }),
    }
  )
);

/** 主题 Store（带持久化） */
export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      isDark: true, // 默认暗色主题

      toggleTheme: () =>
        set((state) => {
          const newIsDark = !state.isDark;
          // 同步更新 HTML 的 class
          if (typeof document !== 'undefined') {
            document.documentElement.classList.toggle('dark', newIsDark);
          }
          return { isDark: newIsDark };
        }),

      setTheme: (isDark) =>
        set(() => {
          if (typeof document !== 'undefined') {
            document.documentElement.classList.toggle('dark', isDark);
          }
          return { isDark };
        }),
    }),
    {
      name: 'ai-dev-hub-theme-storage',
    }
  )
);

/** 高级筛选条件 Store（带持久化） */
export const useAdvancedFilterStore = create<AdvancedFilterState>()(
  persist(
    (set) => ({
      filters: initialAdvancedFilterState,

      setFilters: (filters) => set({ filters }),

      updateFilters: (updates) =>
        set((state) => ({
          filters: {
            ...state.filters,
            ...updates,
          },
        })),

      resetFilters: () => set({ filters: initialAdvancedFilterState }),
    }),
    {
      name: 'ai-dev-hub-advanced-filter-storage',
      partialize: (state) => ({
        filters: state.filters,
      }),
    }
  )
);

/** 用户状态 Store（带持久化） */
export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: (user, token) =>
        set({
          user,
          token,
          isAuthenticated: true,
        }),

      logout: () =>
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        }),

      updateUser: (user) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...user } : user,
        })),
    }),
    {
      name: 'ai-dev-hub-user-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
