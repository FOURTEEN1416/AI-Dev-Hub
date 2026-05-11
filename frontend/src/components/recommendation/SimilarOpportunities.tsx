/**
 * 相似机会组件
 * 
 * 在详情页显示相似的机会
 */

'use client';

import { Lightbulb } from 'lucide-react';
import OpportunityCard from '@/components/opportunity/OpportunityCard';
import Loading from '@/components/common/Loading';
import { useSimilarOpportunities } from '@/hooks/useRecommendation';
import { mockOpportunities } from '@/lib/mock-data';
import type { Opportunity } from '@/types';

interface SimilarOpportunitiesProps {
  /** 当前机会 ID */
  opportunityId: number;
  /** 当前机会（用于本地筛选相似项） */
  currentOpportunity?: Opportunity;
}

/**
 * 相似机会推荐组件
 * 显示与当前机会相似的其他机会
 */
export default function SimilarOpportunities({
  opportunityId,
  currentOpportunity,
}: SimilarOpportunitiesProps) {
  const { data: similarData, isLoading } = useSimilarOpportunities(opportunityId, 3);

  // 使用本地数据作为后备
  const getLocalSimilarOpportunities = (): Opportunity[] => {
    if (!currentOpportunity) return [];
    
    return mockOpportunities
      .filter(
        (item) =>
          item.id !== opportunityId &&
          (item.type === currentOpportunity.type ||
            item.tags?.some((tag) => currentOpportunity.tags?.includes(tag)))
      )
      .slice(0, 3);
  };

  const opportunities = similarData || getLocalSimilarOpportunities();

  // 加载状态
  if (isLoading) {
    return (
      <section className="mt-12 pt-8 border-t border-[var(--border-color)]">
        <div className="flex items-center gap-2 mb-6">
          <Lightbulb className="h-5 w-5 text-yellow-400" />
          <h2 className="text-xl font-bold text-[var(--text-primary)]">
            相似机会
          </h2>
        </div>
        <Loading />
      </section>
    );
  }

  // 无数据时不显示
  if (!opportunities || opportunities.length === 0) {
    return null;
  }

  return (
    <section className="mt-12 pt-8 border-t border-[var(--border-color)]">
      {/* 标题栏 */}
      <div className="flex items-center gap-2 mb-6">
        <Lightbulb className="h-5 w-5 text-yellow-400" />
        <h2 className="text-xl font-bold text-[var(--text-primary)]">
          相似机会
        </h2>
        <span className="text-sm text-[var(--text-muted)]">
          你可能还感兴趣
        </span>
      </div>

      {/* 卡片网格 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {opportunities.map((opportunity) => (
          <OpportunityCard key={opportunity.id} opportunity={opportunity} />
        ))}
      </div>
    </section>
  );
}
