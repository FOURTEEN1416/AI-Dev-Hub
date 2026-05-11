/**
 * 热门推荐组件
 * 
 * 显示近期热门的机会列表
 */

'use client';

import { useState, useEffect } from 'react';
import { Flame, ArrowRight } from 'lucide-react';
import Link from 'next/link';
import OpportunityCard from '@/components/opportunity/OpportunityCard';
import Loading from '@/components/common/Loading';
import { useTrending } from '@/hooks/useRecommendation';
import { mockOpportunities } from '@/lib/mock-data';

/**
 * 热门推荐区域组件
 * 显示近期热门的机会列表
 */
export default function TrendingSection() {
  const { data: trendingData, isLoading, error } = useTrending(7, 6);

  // 使用模拟数据作为后备
  const opportunities = trendingData || mockOpportunities.slice(0, 6);

  // 加载状态
  if (isLoading) {
    return (
      <section className="py-12 bg-[var(--bg-secondary)]">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-2">
              <Flame className="h-5 w-5 text-orange-400" />
              <h2 className="text-xl sm:text-2xl font-bold text-[var(--text-primary)]">
                热门推荐
              </h2>
            </div>
          </div>
          <Loading />
        </div>
      </section>
    );
  }

  // 无数据时不显示
  if (!opportunities || opportunities.length === 0) {
    return null;
  }

  return (
    <section className="py-12 bg-[var(--bg-secondary)]">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* 标题栏 */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Flame className="h-5 w-5 text-orange-400" />
              <h2 className="text-xl sm:text-2xl font-bold text-[var(--text-primary)]">
                热门推荐
              </h2>
            </div>
            <p className="text-sm text-[var(--text-muted)]">
              近 7 天最受关注的机会
            </p>
          </div>
          <Link
            href="/opportunities?sort=popular"
            className="btn-secondary text-sm inline-flex items-center gap-1.5"
          >
            查看更多
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>

        {/* 卡片网格 */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {opportunities.map((opportunity, index) => (
            <div key={opportunity.id} className="relative">
              <OpportunityCard opportunity={opportunity} />
              {/* 排名标识 */}
              {index < 3 && (
                <div className="absolute top-3 left-3 z-10">
                  <span
                    className={`
                      inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold
                      ${index === 0 ? 'bg-orange-500 text-white' : ''}
                      ${index === 1 ? 'bg-gray-400 text-white' : ''}
                      ${index === 2 ? 'bg-amber-600 text-white' : ''}
                    `}
                  >
                    {index + 1}
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
