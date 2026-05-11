/**
 * 推荐区域组件
 * 
 * 显示个性化推荐的机会列表，包含推荐理由
 */

'use client';

import { Sparkles } from 'lucide-react';
import OpportunityCard from '@/components/opportunity/OpportunityCard';
import Loading from '@/components/common/Loading';
import EmptyState from '@/components/common/EmptyState';
import type { RecommendedOpportunity } from '@/types';

interface RecommendationSectionProps {
  /** 区域标题 */
  title: string;
  /** 推荐机会列表 */
  opportunities: RecommendedOpportunity[];
  /** 加载状态 */
  loading?: boolean;
}

export default function RecommendationSection({
  title,
  opportunities,
  loading = false,
}: RecommendationSectionProps) {
  // 加载状态
  if (loading) {
    return (
      <section className="py-8">
        <div className="flex items-center gap-2 mb-6">
          <Sparkles className="h-5 w-5 text-primary-400" />
          <h2 className="text-xl font-bold text-[var(--text-primary)]">
            {title}
          </h2>
        </div>
        <Loading />
      </section>
    );
  }

  // 空状态
  if (!opportunities || opportunities.length === 0) {
    return null;
  }

  return (
    <section className="py-8">
      {/* 标题栏 */}
      <div className="flex items-center gap-2 mb-6">
        <Sparkles className="h-5 w-5 text-primary-400" />
        <h2 className="text-xl font-bold text-[var(--text-primary)]">
          {title}
        </h2>
      </div>

      {/* 推荐卡片网格 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {opportunities.map((item) => (
          <div key={item.opportunity.id} className="relative">
            <OpportunityCard opportunity={item.opportunity} />
            {/* 推荐理由标签 */}
            {item.reason && (
              <div className="absolute top-3 left-3 z-10">
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-primary-500/90 text-white backdrop-blur-sm">
                  <Sparkles className="h-3 w-3 mr-1" />
                  {item.reason}
                </span>
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
