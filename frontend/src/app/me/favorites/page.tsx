/**
 * 收藏列表页面
 * 展示用户收藏的所有机会
 */

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Heart, Loader2, Trash2, Calendar, Clock, ExternalLink, ChevronLeft } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useFavorites } from '@/hooks/useAuth';
import { cn, formatDate, getTypeLabel, getTypeColor, isExpired, truncateText } from '@/lib/utils';
import Pagination from '@/components/common/Pagination';
import EmptyState from '@/components/common/EmptyState';
import TagBadge from '@/components/common/TagBadge';
import type { UserFavorite } from '@/types';

export default function FavoritesPage() {
  const router = useRouter();
  const { isAuthenticated, initialized } = useAuth();
  const { favorites, total, loading, fetchFavorites, removeFavorite } = useFavorites();

  // 分页状态
  const [page, setPage] = useState(1);
  const limit = 12;

  // 未登录重定向
  useEffect(() => {
    if (initialized && !isAuthenticated) {
      router.push('/login');
    }
  }, [initialized, isAuthenticated, router]);

  // 获取收藏列表
  useEffect(() => {
    if (isAuthenticated) {
      fetchFavorites(page, limit);
    }
  }, [isAuthenticated, page, fetchFavorites]);

  /**
   * 取消收藏
   */
  const handleRemove = async (opportunityId: number) => {
    await removeFavorite(opportunityId);
  };

  // 加载中状态
  if (!initialized || loading) {
    return (
      <div className="min-h-[calc(100vh-200px)] flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary-500" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* 返回链接 */}
      <Link
        href="/me"
        className="inline-flex items-center gap-1 text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] mb-4 transition-colors"
      >
        <ChevronLeft className="h-4 w-4" />
        返回个人中心
      </Link>

      {/* 页面标题 */}
      <div className="flex items-center gap-3 mb-6">
        <Heart className="h-6 w-6 text-primary-400" />
        <h1 className="text-2xl font-bold text-[var(--text-primary)]">
          我的收藏
        </h1>
        {total > 0 && (
          <span className="px-2.5 py-0.5 rounded-full bg-primary-500/20 text-primary-400 text-sm">
            {total} 个
          </span>
        )}
      </div>

      {/* 收藏列表 */}
      {favorites.length > 0 ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {favorites.map((favorite) => (
              <FavoriteCard
                key={favorite.id}
                favorite={favorite}
                onRemove={handleRemove}
              />
            ))}
          </div>

          {/* 分页 */}
          {total > limit && (
            <div className="mt-8">
              <Pagination
                currentPage={page}
                total={total}
                limit={limit}
                onPageChange={setPage}
              />
            </div>
          )}
        </>
      ) : (
        <EmptyState
          type="no-data"
          title="还没有收藏"
          description="浏览机会列表，收藏感兴趣的内容"
          action={
            <Link
              href="/opportunities"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-primary-500 to-accent-500 text-white font-medium hover:shadow-lg hover:shadow-primary-500/30 transition-all"
            >
              去发现机会
            </Link>
          }
        />
      )}
    </div>
  );
}

/**
 * 收藏卡片组件
 */
interface FavoriteCardProps {
  favorite: UserFavorite;
  onRemove: (opportunityId: number) => void;
}

function FavoriteCard({ favorite, onRemove }: FavoriteCardProps) {
  const { opportunity } = favorite;
  const typeColor = getTypeColor(opportunity.type);
  const expired = isExpired(opportunity.deadline);
  const [removing, setRemoving] = useState(false);

  const handleRemove = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setRemoving(true);
    await onRemove(opportunity.id);
    setRemoving(false);
  };

  return (
    <Link
      href={`/opportunities/${opportunity.id}`}
      className="block group"
    >
      <article className="card-glow p-4 h-full flex flex-col relative">
        {/* 取消收藏按钮 */}
        <button
          onClick={handleRemove}
          disabled={removing}
          className={cn(
            'absolute top-3 right-3 p-1.5 rounded-full',
            'bg-[var(--bg-secondary)]/80 backdrop-blur-sm',
            'opacity-0 group-hover:opacity-100 transition-opacity',
            'hover:bg-red-500/20 hover:text-red-400',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            'z-10'
          )}
          aria-label="取消收藏"
        >
          {removing ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Trash2 className="h-4 w-4" />
          )}
        </button>

        {/* 收藏指示器 */}
        <div className="absolute top-3 right-3 group-hover:opacity-0 transition-opacity">
          <Heart className="h-4 w-4 fill-red-400 text-red-400" />
        </div>

        {/* 顶部：类型标签 + 来源 */}
        <div className="flex items-center gap-2 mb-2">
          <span
            className={cn(
              'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border',
              typeColor.bg,
              typeColor.text,
              typeColor.border
            )}
          >
            {getTypeLabel(opportunity.type)}
          </span>
          <span className="text-xs text-[var(--text-muted)]">
            {opportunity.source}
          </span>
        </div>

        {/* 标题 */}
        <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-2 line-clamp-2 group-hover:text-primary-400 transition-colors">
          {opportunity.title}
        </h3>

        {/* 描述 */}
        {opportunity.description && (
          <p className="text-xs text-[var(--text-secondary)] mb-2 line-clamp-2 leading-relaxed flex-1">
            {truncateText(opportunity.description, 80)}
          </p>
        )}

        {/* 标签列表 */}
        {opportunity.tags && opportunity.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-2">
            {opportunity.tags.slice(0, 3).map((tag) => (
              <TagBadge key={tag} size="sm">
                {tag}
              </TagBadge>
            ))}
            {opportunity.tags.length > 3 && (
              <TagBadge size="sm">
                +{opportunity.tags.length - 3}
              </TagBadge>
            )}
          </div>
        )}

        {/* 底部：截止日期 + 收藏时间 */}
        <div className="mt-auto pt-2 border-t border-[var(--border-color)] flex items-center justify-between text-xs">
          {opportunity.deadline ? (
            <div
              className={cn(
                'flex items-center gap-1',
                expired ? 'text-red-400' : 'text-[var(--text-muted)]'
              )}
            >
              {expired ? (
                <Clock className="h-3 w-3" />
              ) : (
                <Calendar className="h-3 w-3" />
              )}
              <span>{expired ? '已截止' : formatDate(opportunity.deadline)}</span>
            </div>
          ) : (
            <div className="flex items-center gap-1 text-[var(--text-muted)]">
              <Clock className="h-3 w-3" />
              <span>长期有效</span>
            </div>
          )}

          <span className="text-[var(--text-muted)]">
            {formatDate(favorite.created_at)} 收藏
          </span>
        </div>
      </article>
    </Link>
  );
}
