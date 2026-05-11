/**
 * 机会详情展示组件
 * 集成行为追踪功能
 */

'use client';

import {
  Calendar,
  Clock,
  ExternalLink,
  Gift,
  UserCheck,
  Tag,
  Globe,
  ChevronRight,
  Share2,
} from 'lucide-react';
import { cn, getTypeLabel, getTypeColor, formatDate, isExpired } from '@/lib/utils';
import TagBadge from '@/components/common/TagBadge';
import BehaviorTracker, { useBehaviorTracker } from '@/components/common/BehaviorTracker';
import type { Opportunity } from '@/types';

interface OpportunityDetailProps {
  opportunity: Opportunity;
}

export default function OpportunityDetail({ opportunity }: OpportunityDetailProps) {
  const typeColor = getTypeColor(opportunity.type);
  const expired = isExpired(opportunity.deadline);
  const { trackShare } = useBehaviorTracker();

  /**
   * 处理分享操作
   */
  const handleShare = async () => {
    const shareData = {
      title: opportunity.title,
      text: opportunity.description || opportunity.title,
      url: window.location.href,
    };

    // 尝试使用原生分享 API
    if (navigator.share) {
      try {
        await navigator.share(shareData);
        trackShare(opportunity.id);
      } catch (err) {
        // 用户取消分享，不做处理
      }
    } else {
      // 回退到复制链接
      try {
        await navigator.clipboard.writeText(window.location.href);
        alert('链接已复制到剪贴板');
        trackShare(opportunity.id);
      } catch (err) {
        console.error('复制失败:', err);
      }
    }
  };

  /** 信息项组件 */
  const InfoItem = ({
    icon: Icon,
    label,
    value,
    variant = 'default',
  }: {
    icon: React.ElementType;
    label: string;
    value: string | null | undefined;
    variant?: 'default' | 'warning' | 'success';
  }) => {
    if (!value) return null;
    return (
      <div className="flex items-start gap-3 p-3 rounded-lg bg-[var(--bg-secondary)]">
        <div
          className={cn(
            'flex items-center justify-center w-9 h-9 rounded-lg shrink-0',
            variant === 'warning' && 'bg-amber-500/10',
            variant === 'success' && 'bg-emerald-500/10',
            variant === 'default' && 'bg-primary-500/10'
          )}
        >
          <Icon
            className={cn(
              'h-4.5 w-4.5',
              variant === 'warning' && 'text-amber-400',
              variant === 'success' && 'text-emerald-400',
              variant === 'default' && 'text-primary-400'
            )}
          />
        </div>
        <div>
          <p className="text-xs text-[var(--text-muted)] mb-0.5">{label}</p>
          <p className="text-sm text-[var(--text-primary)] font-medium">{value}</p>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6 animate-in">
      {/* 行为追踪组件 */}
      <BehaviorTracker opportunityId={opportunity.id} />

      {/* 标题区域 */}
      <div>
        {/* 类型 + 来源标签 */}
        <div className="flex flex-wrap items-center gap-2 mb-4">
          <span
            className={cn(
              'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border',
              typeColor.bg,
              typeColor.text,
              typeColor.border
            )}
          >
            {getTypeLabel(opportunity.type)}
          </span>
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm border border-[var(--border-color)] text-[var(--text-secondary)]">
            <Globe className="h-3.5 w-3.5" />
            {opportunity.source}
          </span>
          {opportunity.status === 'closed' && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-500/10 text-red-400 border border-red-500/30">
              已关闭
            </span>
          )}
          {opportunity.status === 'expired' && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-500/10 text-gray-400 border border-gray-500/30">
              已过期
            </span>
          )}
        </div>

        {/* 标题 */}
        <h1 className="text-2xl sm:text-3xl font-bold text-[var(--text-primary)] mb-2">
          {opportunity.title}
        </h1>

        {/* 发布时间 */}
        <p className="text-sm text-[var(--text-muted)]">
          发布于 {formatDate(opportunity.created_at)}
        </p>
      </div>

      {/* 详细描述 */}
      {opportunity.description && (
        <div className="card-base p-6">
          <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4">
            详细描述
          </h2>
          <div className="prose prose-sm max-w-none text-[var(--text-secondary)] leading-relaxed whitespace-pre-wrap">
            {opportunity.description}
          </div>
        </div>
      )}

      {/* 关键信息卡片 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <InfoItem
          icon={Calendar}
          label="截止日期"
          value={
            opportunity.deadline
              ? `${formatDate(opportunity.deadline)}${expired ? '（已截止）' : ''}`
              : null
          }
          variant={expired ? 'warning' : 'default'}
        />
        <InfoItem
          icon={Gift}
          label="奖励说明"
          value={opportunity.reward}
          variant="success"
        />
        <InfoItem
          icon={UserCheck}
          label="参与条件"
          value={opportunity.requirements}
        />
        <InfoItem
          icon={Clock}
          label="最后更新"
          value={opportunity.updated_at ? formatDate(opportunity.updated_at) : null}
        />
      </div>

      {/* 标签列表 */}
      {opportunity.tags && opportunity.tags.length > 0 && (
        <div className="card-base p-5">
          <div className="flex items-center gap-2 mb-3">
            <Tag className="h-4 w-4 text-[var(--text-muted)]" />
            <h3 className="text-sm font-medium text-[var(--text-primary)]">
              相关标签
            </h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {opportunity.tags.map((tag) => (
              <TagBadge key={tag} size="md">
                {tag}
              </TagBadge>
            ))}
          </div>
        </div>
      )}

      {/* 操作按钮区域 */}
      <div className="flex flex-wrap items-center gap-3">
        {/* 官方链接 */}
        {opportunity.official_link && (
          <a
            href={opportunity.official_link}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary inline-flex items-center gap-2 text-base px-6 py-3"
          >
            访问官方页面
            <ExternalLink className="h-4 w-4" />
          </a>
        )}

        {/* 分享按钮 */}
        <button
          onClick={handleShare}
          className="btn-secondary inline-flex items-center gap-2 text-sm px-4 py-3"
        >
          分享
          <Share2 className="h-4 w-4" />
        </button>

        {/* 来源链接 */}
        {opportunity.source_url && (
          <a
            href={opportunity.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary inline-flex items-center gap-2 text-sm"
          >
            查看来源
            <ChevronRight className="h-4 w-4" />
          </a>
        )}
      </div>
    </div>
  );
}
