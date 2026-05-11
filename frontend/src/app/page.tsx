/**
 * 首页
 * 包含 Hero 区域、最新机会卡片列表、热门推荐、热门标签云和统计数据展示
 */

'use client';

import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import HeroSection from '@/components/home/HeroSection';
import StatsSection from '@/components/home/StatsSection';
import TagCloud from '@/components/home/TagCloud';
import TrendingSection from '@/components/recommendation/TrendingSection';
import OpportunityCard from '@/components/opportunity/OpportunityCard';
import { mockOpportunities } from '@/lib/mock-data';

export default function HomePage() {
  // 取最新的 6 条机会作为展示
  const latestOpportunities = mockOpportunities.slice(0, 6);

  return (
    <div className="min-h-screen">
      {/* Hero 区域 */}
      <HeroSection />

      {/* 统计数据 */}
      <StatsSection />

      {/* 最新机会 */}
      <section className="py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          {/* 标题栏 */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-xl sm:text-2xl font-bold text-[var(--text-primary)]">
                最新机会
              </h2>
              <p className="text-sm text-[var(--text-muted)] mt-1">
                发现最新的 AI 开发者机会
              </p>
            </div>
            <Link
              href="/opportunities"
              className="btn-secondary text-sm inline-flex items-center gap-1.5"
            >
              查看全部
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>

          {/* 卡片网格 */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {latestOpportunities.map((opportunity) => (
              <OpportunityCard
                key={opportunity.id}
                opportunity={opportunity}
              />
            ))}
          </div>
        </div>
      </section>

      {/* 热门推荐 */}
      <TrendingSection />

      {/* 热门标签云 */}
      <TagCloud />

      {/* CTA 区域 */}
      <section className="py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="card-base p-8 sm:p-12 text-center bg-card-gradient">
            <h2 className="text-2xl sm:text-3xl font-bold text-[var(--text-primary)] mb-4">
              不要错过任何机会
            </h2>
            <p className="text-[var(--text-secondary)] mb-8 max-w-lg mx-auto">
              浏览所有 AI 开发者机会，找到适合你的计划、竞赛和免费资源
            </p>
            <Link href="/opportunities" className="btn-primary text-base px-8 py-3 inline-flex items-center gap-2">
              探索全部机会
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
