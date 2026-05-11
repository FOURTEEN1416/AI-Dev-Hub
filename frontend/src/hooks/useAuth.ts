/**
 * 认证相关 Hooks
 * 提供用户登录、注册、登出和收藏功能
 */

'use client';

import { useState, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useUserStore } from '@/store';
import {
  login as apiLogin,
  register as apiRegister,
  logout as apiLogout,
  getCurrentUser,
  getFavorites as apiGetFavorites,
  addFavorite as apiAddFavorite,
  removeFavorite as apiRemoveFavorite,
  checkFavorite as apiCheckFavorite,
} from '@/lib/api';
import type { User, LoginRequest, RegisterRequest, UserFavorite } from '@/types';

/**
 * 认证 Hook
 * 提供用户登录、注册、登出功能
 */
export function useAuth() {
  const router = useRouter();
  const { user, token, isAuthenticated, login: setUser, logout: clearUser, updateUser } = useUserStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [initialized, setInitialized] = useState(false);

  // 初始化：检查本地存储的 token 并获取用户信息
  useEffect(() => {
    const initAuth = async () => {
      if (token && !user) {
        try {
          const userData = await getCurrentUser();
          updateUser(userData);
        } catch (err) {
          // Token 无效，清除状态
          clearUser();
        }
      }
      setInitialized(true);
    };

    initAuth();
  }, [token, user, updateUser, clearUser]);

  /**
   * 用户登录
   */
  const login = useCallback(async (data: LoginRequest) => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiLogin(data);
      setUser(response.user, response.access_token);
      return { success: true, user: response.user };
    } catch (err: unknown) {
      const errorMessage = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || '登录失败，请检查邮箱和密码';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, [setUser]);

  /**
   * 用户注册
   */
  const register = useCallback(async (data: RegisterRequest) => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiRegister(data);
      setUser(response.user, response.access_token);
      return { success: true, user: response.user };
    } catch (err: unknown) {
      const errorMessage = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || '注册失败，请稍后重试';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, [setUser]);

  /**
   * 用户登出
   */
  const logout = useCallback(async () => {
    setLoading(true);

    try {
      await apiLogout();
    } finally {
      clearUser();
      setLoading(false);
      router.push('/');
    }
  }, [clearUser, router]);

  /**
   * 获取当前用户信息
   */
  const fetchCurrentUser = useCallback(async () => {
    if (!token) return null;

    try {
      const userData = await getCurrentUser();
      updateUser(userData);
      return userData;
    } catch {
      clearUser();
      return null;
    }
  }, [token, updateUser, clearUser]);

  return {
    user,
    token,
    isAuthenticated,
    loading,
    error,
    initialized,
    login,
    register,
    logout,
    fetchCurrentUser,
    clearError: () => setError(null),
  };
}

/**
 * 收藏 Hook
 * 提供收藏列表、添加收藏、取消收藏功能
 */
export function useFavorites() {
  const { isAuthenticated } = useUserStore();
  const [favorites, setFavorites] = useState<UserFavorite[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 收藏状态缓存（用于快速判断是否已收藏）
  const [favoritedIds, setFavoritedIds] = useState<Set<number>>(new Set());

  /**
   * 获取收藏列表
   */
  const fetchFavorites = useCallback(async (page: number = 1, limit: number = 20) => {
    if (!isAuthenticated) {
      setFavorites([]);
      setTotal(0);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiGetFavorites(page, limit);
      setFavorites(response.items);
      setTotal(response.total);
      // 更新收藏状态缓存
      setFavoritedIds(new Set(response.items.map((f) => f.opportunity_id)));
    } catch (err: unknown) {
      const errorMessage = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || '获取收藏列表失败';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  /**
   * 添加收藏
   */
  const addFavorite = useCallback(async (opportunityId: number) => {
    if (!isAuthenticated) {
      return { success: false, error: '请先登录' };
    }

    try {
      await apiAddFavorite(opportunityId);
      // 更新本地状态
      setFavoritedIds((prev) => new Set(prev).add(opportunityId));
      return { success: true };
    } catch (err: unknown) {
      const errorMessage = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || '添加收藏失败';
      return { success: false, error: errorMessage };
    }
  }, [isAuthenticated]);

  /**
   * 取消收藏
   */
  const removeFavorite = useCallback(async (opportunityId: number) => {
    if (!isAuthenticated) {
      return { success: false, error: '请先登录' };
    }

    try {
      await apiRemoveFavorite(opportunityId);
      // 更新本地状态
      setFavoritedIds((prev) => {
        const newSet = new Set(prev);
        newSet.delete(opportunityId);
        return newSet;
      });
      // 从列表中移除
      setFavorites((prev) => prev.filter((f) => f.opportunity_id !== opportunityId));
      setTotal((prev) => Math.max(0, prev - 1));
      return { success: true };
    } catch (err: unknown) {
      const errorMessage = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || '取消收藏失败';
      return { success: false, error: errorMessage };
    }
  }, [isAuthenticated]);

  /**
   * 切换收藏状态
   */
  const toggleFavorite = useCallback(async (opportunityId: number) => {
    if (favoritedIds.has(opportunityId)) {
      return removeFavorite(opportunityId);
    } else {
      return addFavorite(opportunityId);
    }
  }, [favoritedIds, addFavorite, removeFavorite]);

  /**
   * 检查是否已收藏
   */
  const isFavorited = useCallback((opportunityId: number): boolean => {
    return favoritedIds.has(opportunityId);
  }, [favoritedIds]);

  /**
   * 检查单个机会的收藏状态（从服务器获取）
   */
  const checkFavoriteStatus = useCallback(async (opportunityId: number): Promise<boolean> => {
    if (!isAuthenticated) return false;

    try {
      const result = await apiCheckFavorite(opportunityId);
      // 更新本地缓存
      setFavoritedIds((prev) => {
        const newSet = new Set(prev);
        if (result) {
          newSet.add(opportunityId);
        } else {
          newSet.delete(opportunityId);
        }
        return newSet;
      });
      return result;
    } catch {
      return false;
    }
  }, [isAuthenticated]);

  return {
    favorites,
    total,
    loading,
    error,
    isFavorited,
    addFavorite,
    removeFavorite,
    toggleFavorite,
    fetchFavorites,
    checkFavoriteStatus,
    clearError: () => setError(null),
  };
}
