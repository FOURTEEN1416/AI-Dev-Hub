/**
 * 筛选状态管理 Hook
 * 提供筛选状态管理、更新、重置等功能
 */

'use client';

import { useState, useCallback, useEffect } from 'react';
import type { AdvancedFilter } from '@/lib/api';

/** 本地存储键名 */
const STORAGE_KEY = 'ai-dev-hub-advanced-filters';

/** 默认筛选条件 */
const DEFAULT_FILTERS: AdvancedFilter = {
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

/**
 * 从本地存储加载筛选条件
 */
function loadFiltersFromStorage(): AdvancedFilter | null {
  if (typeof window === 'undefined') return null;
  
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (error) {
    console.error('加载筛选条件失败:', error);
  }
  return null;
}

/**
 * 保存筛选条件到本地存储
 */
function saveFiltersToStorage(filters: AdvancedFilter): void {
  if (typeof window === 'undefined') return;
  
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filters));
  } catch (error) {
    console.error('保存筛选条件失败:', error);
  }
}

/**
 * 清除本地存储中的筛选条件
 */
function clearFiltersFromStorage(): void {
  if (typeof window === 'undefined') return;
  
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.error('清除筛选条件失败:', error);
  }
}

/**
 * 筛选状态管理 Hook
 */
export function useFilter(initialFilters?: AdvancedFilter) {
  const [filters, setFilters] = useState<AdvancedFilter>(() => {
    // 优先使用传入的初始筛选条件
    if (initialFilters) {
      return { ...DEFAULT_FILTERS, ...initialFilters };
    }
    
    // 尝试从本地存储加载
    const storedFilters = loadFiltersFromStorage();
    if (storedFilters) {
      return { ...DEFAULT_FILTERS, ...storedFilters };
    }
    
    return DEFAULT_FILTERS;
  });

  // 筛选条件变更时保存到本地存储
  useEffect(() => {
    saveFiltersToStorage(filters);
  }, [filters]);

  /**
   * 更新筛选条件
   */
  const updateFilters = useCallback((updates: Partial<AdvancedFilter>) => {
    setFilters((prev) => ({
      ...prev,
      ...updates,
    }));
  }, []);

  /**
   * 设置关键词
   */
  const setKeyword = useCallback((keyword: string) => {
    updateFilters({ keyword: keyword || undefined });
  }, [updateFilters]);

  /**
   * 设置类型
   */
  const setTypes = useCallback((types: string[]) => {
    updateFilters({ types: types.length > 0 ? types : undefined });
  }, [updateFilters]);

  /**
   * 设置来源
   */
  const setSources = useCallback((sources: string[]) => {
    updateFilters({ sources: sources.length > 0 ? sources : undefined });
  }, [updateFilters]);

  /**
   * 设置标签
   */
  const setTags = useCallback((tags: string[]) => {
    updateFilters({ tags: tags.length > 0 ? tags : undefined });
  }, [updateFilters]);

  /**
   * 设置状态
   */
  const setStatus = useCallback((status: string) => {
    updateFilters({ status: status || undefined });
  }, [updateFilters]);

  /**
   * 设置截止日期范围
   */
  const setDeadlineRange = useCallback((startDate?: string, endDate?: string) => {
    updateFilters({
      deadline_start: startDate,
      deadline_end: endDate,
    });
  }, [updateFilters]);

  /**
   * 设置创建时间范围
   */
  const setCreatedRange = useCallback((startDate?: string, endDate?: string) => {
    updateFilters({
      created_start: startDate,
      created_end: endDate,
    });
  }, [updateFilters]);

  /**
   * 设置排序
   */
  const setSort = useCallback((
    sortBy: 'created_at' | 'deadline' | 'title',
    sortOrder: 'asc' | 'desc'
  ) => {
    updateFilters({
      sort_by: sortBy,
      sort_order: sortOrder,
    });
  }, [updateFilters]);

  /**
   * 切换有截止日期筛选
   */
  const toggleHasDeadline = useCallback((hasDeadline?: boolean) => {
    updateFilters({ has_deadline: hasDeadline });
  }, [updateFilters]);

  /**
   * 移除单个筛选条件
   */
  const removeFilter = useCallback((key: keyof AdvancedFilter, value?: string) => {
    setFilters((prev) => {
      const newFilters = { ...prev };
      
      // 处理数组类型的筛选条件
      if (value && Array.isArray(prev[key])) {
        const array = prev[key] as string[];
        newFilters[key] = array.filter((item) => item !== value) as any;
        if ((newFilters[key] as string[]).length === 0) {
          newFilters[key] = undefined;
        }
      } else {
        // 单值类型的筛选条件直接置空
        newFilters[key] = undefined;
      }
      
      return newFilters;
    });
  }, []);

  /**
   * 重置所有筛选条件
   */
  const resetFilters = useCallback(() => {
    setFilters(DEFAULT_FILTERS);
    clearFiltersFromStorage();
  }, []);

  /**
   * 判断是否有活跃的筛选条件
   */
  const hasActiveFilters = useCallback(() => {
    return (
      (filters.keyword && filters.keyword.length > 0) ||
      (filters.types && filters.types.length > 0) ||
      (filters.sources && filters.sources.length > 0) ||
      (filters.tags && filters.tags.length > 0) ||
      !!filters.status ||
      filters.has_deadline !== undefined ||
      !!filters.deadline_start ||
      !!filters.deadline_end ||
      !!filters.created_start ||
      !!filters.created_end
    );
  }, [filters]);

  /**
   * 获取活跃筛选条件数量
   */
  const getActiveFilterCount = useCallback(() => {
    let count = 0;
    if (filters.keyword) count++;
    if (filters.types?.length) count += filters.types.length;
    if (filters.sources?.length) count += filters.sources.length;
    if (filters.tags?.length) count += filters.tags.length;
    if (filters.status) count++;
    if (filters.has_deadline !== undefined) count++;
    if (filters.deadline_start || filters.deadline_end) count++;
    if (filters.created_start || filters.created_end) count++;
    return count;
  }, [filters]);

  return {
    /** 当前筛选条件 */
    filters,
    /** 更新筛选条件 */
    updateFilters,
    /** 设置关键词 */
    setKeyword,
    /** 设置类型 */
    setTypes,
    /** 设置来源 */
    setSources,
    /** 设置标签 */
    setTags,
    /** 设置状态 */
    setStatus,
    /** 设置截止日期范围 */
    setDeadlineRange,
    /** 设置创建时间范围 */
    setCreatedRange,
    /** 设置排序 */
    setSort,
    /** 切换有截止日期筛选 */
    toggleHasDeadline,
    /** 移除单个筛选条件 */
    removeFilter,
    /** 重置所有筛选条件 */
    resetFilters,
    /** 判断是否有活跃的筛选条件 */
    hasActiveFilters,
    /** 获取活跃筛选条件数量 */
    getActiveFilterCount,
  };
}

export default useFilter;
