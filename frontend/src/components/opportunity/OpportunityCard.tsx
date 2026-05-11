/**
 * 机会卡片组件
 * 展示机会的摘要信息，包含类型标签、标题、来源、描述、标签列表、截止日期和收藏按钮
 */

'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Calendar, ExternalLink, Clock, Heart, Loader2 } from 'lucide-react';
import { cn, getTypeLabel, getTypeColor, formatDate, isExpired, truncateText } from '@/lib/utils';
import { useUserStore } from '@/store';
import { useFavorites } from '@/hooks/useAuth';
import TagBadge from '@/components/common/TagBadge';
import type { Opportunity } from '@/types';

interface OpportunityCardProps {
  opportunity: Opportunity;
  className?: string;
}

export default function OpportunityCard({
  opportunity,
  className,
}: OpportunityCardProps) {
  const router = useRouter();
  const { isAuthenticated } = useUserStore();
  const { isFavorited, toggleFavorite, checkFavoriteStatus } = useFavorites();
  
  const [favorited, setFavorited] = useState(false);
  const [loading, setLoading] = useState(false);

  const typeColor = getTypeColor(opportunity.type);
  const expired = isExpired(opportunity.deadline);

  // 检查收藏状态
  useEffect(() => {
    if (isAuthenticated) {
      // 先使用本地缓存判断
      if (isFavorited(opportunity.id)) {
        setFavorited(true);
      } else {
        // 从服务器获取状态
        checkFavoriteStatus(opportunity.id).then((status) => {
          setFavorited(status);
        });
      }
    }
  }, [isAuthenticated, opportunity.id, isFavorited, checkFavoriteStatus]);

  /**
   * 处理收藏点击
   */
  const handleFavoriteClick = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    setLoading(true);
    const result = await toggleFavorite(opportunity.id);
    if (result.success) {
      setFavorited(!favorited);
    }
    setLoading(false);
  };

  return (
    <Link href={`/opportunities/${opportunity.id}`} className="block">
      <article
        className={cn(
          'card-glow p-5 h-full flex flex-col cursor-pointer relative group',
          className
        )}
      >
        {/* 收藏按钮 */}
        <button
          onClick={handleFavoriteClick}
          disabled={loading}
          className={cn(
            'absolute top-4 right-4 p-2 rounded-full',
            'bg-[var(--bg-secondary)]/80 backdrop-blur-sm',
            'opacity-0 group-hover:opacity-100 transition-opacity',
            'hover:bg-[var(--bg-tertiary)] hover:scale-110',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            'z-10'
          )}
          aria-label={favorited ? '取消收藏' : '添加收藏'}
        >
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin text-[var(--text-muted)]" />
          ) : (
            <Heart
              className={cn(
                'h-4 w-4 transition-colors',
                favorited
                  ? 'fill-red-400 text-red-400'
                  : 'text-[var(--text-muted)] hover:text-red-400'
              )}
            />
          )}
        </button>

        {/* 已收藏指示器（始终显示） */}
        {favorited && (
          <div className="absolute top-4 right-4 group-hover:opacity-0 transition-opacity">
            <Heart className="h-4 w-4 fill-red-400 text-red-400" />
          </div>
        )}

        {/* 顶部：类型标签 + 来源 */}
        <div className="flex items-center gap-2 mb-3">
          <span
            className={cn(
              'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border',
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
        <h3 className="text-base font-semibold text-[var(--text-primary)] mb-2 line-clamp-2 group-hover:text-primary-400 transition-colors">
          {opportunity.title}
        </h3>

        {/* 描述 */}
        {opportunity.description && (
          <p className="text-sm text-[var(--text-secondary)] mb-3 line-clamp-2 leading-relaxed">
            {truncateText(opportunity.description, 120)}
          </p>
        )}

        {/* 标签列表 */}
        {opportunity.tags && opportunity.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-3">
            {opportunity.tags.slice(0, 4).map((tag) => (
              <TagBadge key={tag} size="sm">
                {tag}
              </TagBadge>
            ))}
            {opportunity.tags.length > 4 && (
              <TagBadge size="sm">
                +{opportunity.tags.length - 4}
              </TagBadge>
            )}
          </div>
        )}

        {/* 底部：截止日期 + 链接 */}
        <div className="mt-auto pt-3 border-t border-[var(--border-color)] flex items-center justify-between">
          {opportunity.deadline ? (
            <div
              className={cn(
                'flex items-center gap-1.5 text-xs',
                expired ? 'text-red-400' : 'text-[var(--text-muted)]'
              )}
            >
              {expired ? (
                <Clock className="h-3.5 w-3.5" />
              ) : (
                <Calendar className="h-3.5 w-3.5" />
              )}
              <span>
                {expired ? '已截止' : formatDate(opportunity.deadline)}
              </span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 text-xs text-[var(--text-muted)]">
              <Clock className="h-3.5 w-3.5" />
              <span>长期有效</span>
            </div>
          )}

          {opportunity.official_link && (
            <span className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1">
              查看
              <ExternalLink className="h-3 w-3" />
            </span>
          )}
        </div>
      </article>
    </Link>
  );
}
