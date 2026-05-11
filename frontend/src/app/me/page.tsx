/**
 * 个人中心页面
 * 展示用户信息和收藏列表
 */

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Mail, User, Calendar, Heart, LogOut, Loader2, ChevronRight, Clock } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useFavorites } from '@/hooks/useAuth';
import { cn, formatDate, getTypeLabel, getTypeColor, truncateText } from '@/lib/utils';
import type { UserFavorite } from '@/types';

export default function MePage() {
  const router = useRouter();
  const { user, isAuthenticated, loading: authLoading, logout, initialized } = useAuth();
  const { favorites, total: favoritesTotal, loading: favoritesLoading, fetchFavorites } = useFavorites();

  // 未登录重定向
  useEffect(() => {
    if (initialized && !isAuthenticated) {
      router.push('/login');
    }
  }, [initialized, isAuthenticated, router]);

  // 获取收藏列表
  useEffect(() => {
    if (isAuthenticated) {
      fetchFavorites(1, 5);
    }
  }, [isAuthenticated, fetchFavorites]);

  /**
   * 退出登录
   */
  const handleLogout = async () => {
    await logout();
  };

  // 加载中状态
  if (!initialized || authLoading) {
    return (
      <div className="min-h-[calc(100vh-200px)] flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary-500" />
      </div>
    );
  }

  // 未登录状态
  if (!user) {
    return null;
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* 页面标题 */}
      <h1 className="text-2xl font-bold text-[var(--text-primary)] mb-6">
        个人中心
      </h1>

      <div className="grid gap-6 md:grid-cols-3">
        {/* 用户信息卡片 */}
        <div className="md:col-span-1">
          <div className="card-glow p-6">
            {/* 头像 */}
            <div className="flex justify-center mb-4">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white text-2xl font-bold shadow-lg shadow-primary-500/20">
                {user.username?.charAt(0).toUpperCase() || user.email.charAt(0).toUpperCase()}
              </div>
            </div>

            {/* 用户名 */}
            <h2 className="text-lg font-semibold text-[var(--text-primary)] text-center mb-4">
              {user.username || '未设置用户名'}
            </h2>

            {/* 信息列表 */}
            <div className="space-y-3">
              {/* 邮箱 */}
              <div className="flex items-center gap-3 text-sm">
                <Mail className="h-4 w-4 text-[var(--text-muted)]" />
                <span className="text-[var(--text-secondary)] truncate">{user.email}</span>
              </div>

              {/* 用户名 */}
              <div className="flex items-center gap-3 text-sm">
                <User className="h-4 w-4 text-[var(--text-muted)]" />
                <span className="text-[var(--text-secondary)]">
                  {user.username || '未设置'}
                </span>
              </div>

              {/* 注册时间 */}
              <div className="flex items-center gap-3 text-sm">
                <Calendar className="h-4 w-4 text-[var(--text-muted)]" />
                <span className="text-[var(--text-secondary)]">
                  {formatDate(user.created_at)} 注册
                </span>
              </div>
            </div>

            {/* 退出登录按钮 */}
            <button
              onClick={handleLogout}
              className={cn(
                'w-full mt-6 py-2.5 rounded-lg font-medium',
                'border border-red-500/30 text-red-400',
                'hover:bg-red-500/10 hover:border-red-500/50',
                'transition-all flex items-center justify-center gap-2'
              )}
            >
              <LogOut className="h-4 w-4" />
              退出登录
            </button>
          </div>
        </div>

        {/* 右侧内容区 */}
        <div className="md:col-span-2 space-y-6">
          {/* 我的收藏 */}
          <div className="card-glow p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Heart className="h-5 w-5 text-primary-400" />
                <h3 className="text-lg font-semibold text-[var(--text-primary)]">
                  我的收藏
                </h3>
                {favoritesTotal > 0 && (
                  <span className="px-2 py-0.5 rounded-full bg-primary-500/20 text-primary-400 text-xs">
                    {favoritesTotal}
                  </span>
                )}
              </div>
              {favoritesTotal > 5 && (
                <Link
                  href="/me/favorites"
                  className="text-sm text-primary-400 hover:text-primary-300 flex items-center gap-1 transition-colors"
                >
                  查看全部
                  <ChevronRight className="h-4 w-4" />
                </Link>
              )}
            </div>

            {/* 收藏列表 */}
            {favoritesLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-primary-500" />
              </div>
            ) : favorites.length > 0 ? (
              <div className="space-y-3">
                {favorites.map((favorite) => (
                  <FavoriteItem key={favorite.id} favorite={favorite} />
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Heart className="h-12 w-12 text-[var(--text-muted)] mx-auto mb-3" />
                <p className="text-[var(--text-secondary)] mb-4">还没有收藏任何机会</p>
                <Link
                  href="/opportunities"
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary-500/20 text-primary-400 hover:bg-primary-500/30 transition-colors"
                >
                  去发现机会
                </Link>
              </div>
            )}
          </div>

          {/* 快捷操作 */}
          <div className="card-glow p-6">
            <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4">
              快捷操作
            </h3>
            <div className="grid grid-cols-2 gap-3">
              <Link
                href="/opportunities"
                className="flex items-center gap-3 p-3 rounded-lg bg-[var(--bg-secondary)] hover:bg-[var(--bg-tertiary)] transition-colors"
              >
                <div className="w-10 h-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
                  <Heart className="h-5 w-5 text-primary-400" />
                </div>
                <div>
                  <p className="text-sm font-medium text-[var(--text-primary)]">浏览机会</p>
                  <p className="text-xs text-[var(--text-muted)]">发现最新机会</p>
                </div>
              </Link>
              <Link
                href="/me/favorites"
                className="flex items-center gap-3 p-3 rounded-lg bg-[var(--bg-secondary)] hover:bg-[var(--bg-tertiary)] transition-colors"
              >
                <div className="w-10 h-10 rounded-lg bg-accent-500/20 flex items-center justify-center">
                  <Clock className="h-5 w-5 text-accent-400" />
                </div>
                <div>
                  <p className="text-sm font-medium text-[var(--text-primary)]">收藏记录</p>
                  <p className="text-xs text-[var(--text-muted)]">查看所有收藏</p>
                </div>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * 收藏项组件
 */
function FavoriteItem({ favorite }: { favorite: UserFavorite }) {
  const { opportunity } = favorite;
  const typeColor = getTypeColor(opportunity.type);

  return (
    <Link
      href={`/opportunities/${opportunity.id}`}
      className="flex items-start gap-3 p-3 rounded-lg bg-[var(--bg-secondary)] hover:bg-[var(--bg-tertiary)] transition-colors group"
    >
      {/* 类型标签 */}
      <span
        className={cn(
          'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border flex-shrink-0',
          typeColor.bg,
          typeColor.text,
          typeColor.border
        )}
      >
        {getTypeLabel(opportunity.type)}
      </span>

      {/* 内容 */}
      <div className="flex-1 min-w-0">
        <h4 className="text-sm font-medium text-[var(--text-primary)] line-clamp-1 group-hover:text-primary-400 transition-colors">
          {opportunity.title}
        </h4>
        <p className="text-xs text-[var(--text-muted)] mt-1">
          {opportunity.source} · {formatDate(favorite.created_at)} 收藏
        </p>
      </div>

      <ChevronRight className="h-4 w-4 text-[var(--text-muted)] group-hover:text-primary-400 transition-colors flex-shrink-0" />
    </Link>
  );
}
