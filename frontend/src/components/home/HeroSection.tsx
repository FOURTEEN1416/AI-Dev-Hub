/**
 * 首页 Hero 区域
 * 包含大标题、副标题描述和搜索框
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Search, ArrowRight, Sparkles } from 'lucide-react';
import SearchBar from '@/components/common/SearchBar';

export default function HeroSection() {
  const router = useRouter();
  const [searchValue, setSearchValue] = useState('');

  const handleSearch = (value: string) => {
    if (value.trim()) {
      router.push(`/opportunities?keyword=${encodeURIComponent(value.trim())}`);
    }
  };

  return (
    <section className="relative overflow-hidden py-20 sm:py-28 lg:py-36">
      {/* 背景装饰 */}
      <div className="absolute inset-0 bg-hero-gradient opacity-60" />
      <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-primary-500/10 rounded-full blur-3xl animate-float" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '1.5s' }} />

      <div className="relative mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 text-center">
        {/* 标签 */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary-500/10 border border-primary-500/20 text-primary-400 text-sm font-medium mb-8 animate-fade-in">
          <Sparkles className="h-4 w-4" />
          <span>发现全球 AI 开发者机会</span>
        </div>

        {/* 大标题 */}
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-6 animate-slide-up">
          <span className="text-[var(--text-primary)]">发现</span>
          <span className="text-gradient">AI开发者</span>
          <br />
          <span className="text-[var(--text-primary)]">机会</span>
        </h1>

        {/* 副标题 */}
        <p className="text-lg sm:text-xl text-[var(--text-secondary)] max-w-2xl mx-auto mb-10 leading-relaxed animate-slide-up" style={{ animationDelay: '0.1s' }}>
          聚合全球 AI 开发者计划、竞赛、免费额度和社区动态，
          帮助你不错过每一个成长机会
        </p>

        {/* 搜索框 */}
        <div className="max-w-xl mx-auto mb-8 animate-slide-up" style={{ animationDelay: '0.2s' }}>
          <SearchBar
            placeholder="搜索开发者计划、竞赛、免费额度..."
            value={searchValue}
            onChange={setSearchValue}
            onSearch={handleSearch}
            size="lg"
          />
        </div>

        {/* 快捷操作 */}
        <div className="flex flex-wrap items-center justify-center gap-3 animate-slide-up" style={{ animationDelay: '0.3s' }}>
          <button
            onClick={() => router.push('/opportunities?type=developer_program')}
            className="btn-secondary text-sm inline-flex items-center gap-1.5"
          >
            开发者计划
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={() => router.push('/opportunities?type=competition')}
            className="btn-secondary text-sm inline-flex items-center gap-1.5"
          >
            比赛竞赛
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={() => router.push('/opportunities?type=free_credits')}
            className="btn-secondary text-sm inline-flex items-center gap-1.5"
          >
            免费额度
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={() => router.push('/opportunities?type=community')}
            className="btn-secondary text-sm inline-flex items-center gap-1.5"
          >
            社区动态
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>
    </section>
  );
}
