/**
 * 机会详情页
 * 包含面包屑导航、详情展示、行为追踪和相似机会推荐
 */

'use client';

import { use } from 'react';
import Link from 'next/link';
import { ChevronRight, Home } from 'lucide-react';
import OpportunityDetail from '@/components/opportunity/OpportunityDetail';
import SimilarOpportunities from '@/components/recommendation/SimilarOpportunities';
import Loading from '@/components/common/Loading';
import EmptyState from '@/components/common/EmptyState';
import { mockOpportunities } from '@/lib/mock-data';
import { getTypeLabel } from '@/lib/utils';

export default function OpportunityDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const opportunityId = parseInt(id, 10);

  // 模拟数据查找
  const opportunity = mockOpportunities.find((item) => item.id === opportunityId);

  // 加载状态
  if (!opportunity) {
    return (
      <div className="min-h-screen py-8">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          <EmptyState
            type="no-data"
            title="机会不存在"
            description="该机会可能已被删除或 ID 无效"
            action={
              <Link href="/opportunities" className="btn-primary">
                返回机会列表
              </Link>
            }
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-8">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        {/* 面包屑导航 */}
        <nav className="flex items-center gap-2 text-sm text-[var(--text-muted)] mb-8">
          <Link
            href="/"
            className="hover:text-[var(--text-primary)] transition-colors flex items-center gap-1"
          >
            <Home className="h-3.5 w-3.5" />
            首页
          </Link>
          <ChevronRight className="h-3.5 w-3.5" />
          <Link
            href="/opportunities"
            className="hover:text-[var(--text-primary)] transition-colors"
          >
            机会列表
          </Link>
          <ChevronRight className="h-3.5 w-3.5" />
          <span className="text-[var(--text-primary)] truncate max-w-xs">
            {opportunity.title}
          </span>
        </nav>

        {/* 详情内容 */}
        <OpportunityDetail opportunity={opportunity} />

        {/* 相似机会推荐 */}
        <SimilarOpportunities 
          opportunityId={opportunityId} 
          currentOpportunity={opportunity}
        />
      </div>
    </div>
  );
}
