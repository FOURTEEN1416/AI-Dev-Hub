/**
 * 数据看板页面
 * 展示完整的数据统计信息，包括概览卡片、趋势图、分布图等
 */

'use client';

import { useState } from 'react';
import { BarChart3, PieChart, TrendingUp, Tags } from 'lucide-react';
import OverviewStats from '@/components/dashboard/OverviewStats';
import TrendChart from '@/components/charts/TrendChart';
import SourcePieChart from '@/components/charts/SourcePieChart';
import TypeBarChart from '@/components/charts/TypeBarChart';
import TagCloudChart from '@/components/charts/TagCloudChart';
import {
  useTrendData,
  useSourceDistribution,
  useTypeDistribution,
  useTagCloud,
} from '@/hooks/useStatistics';
import { cn } from '@/lib/utils';

/** 时间范围选项 */
const timeRangeOptions = [
  { value: 7, label: '7 天' },
  { value: 30, label: '30 天' },
  { value: 90, label: '90 天' },
];

/** 图表卡片组件 */
function ChartCard({
  title,
  icon,
  children,
  className,
}: {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn('card-base p-4', className)}>
      <div className="flex items-center gap-2 mb-4">
        <span className="text-primary-400">{icon}</span>
        <h3 className="text-lg font-semibold text-[var(--text-primary)]">{title}</h3>
      </div>
      {children}
    </div>
  );
}

export default function StatsPage() {
  // 时间范围状态
  const [days, setDays] = useState(30);

  // 获取各类数据
  const { data: trendData, isLoading: trendLoading } = useTrendData(days);
  const { data: sourceData, isLoading: sourceLoading } = useSourceDistribution();
  const { data: typeData, isLoading: typeLoading } = useTypeDistribution();
  const { data: tagData, isLoading: tagLoading } = useTagCloud(50);

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] py-8">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* 页面标题 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gradient">数据看板</h1>
          <p className="mt-2 text-[var(--text-secondary)]">
            全面了解机会数据统计和趋势分析
          </p>
        </div>

        {/* 概览统计卡片 */}
        <section className="mb-8">
          <OverviewStats />
        </section>

        {/* 时间范围选择器 */}
        <div className="flex justify-end mb-6">
          <div className="flex items-center gap-2 p-1 rounded-lg bg-[var(--bg-secondary)] border border-[var(--border-color)]">
            {timeRangeOptions.map((option) => (
              <button
                key={option.value}
                onClick={() => setDays(option.value)}
                className={cn(
                  'px-3 py-1.5 rounded-md text-sm font-medium transition-all',
                  days === option.value
                    ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/30'
                    : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                )}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {/* 图表区域 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 趋势折线图 */}
          <ChartCard
            title="机会趋势"
            icon={<TrendingUp className="w-5 h-5" />}
            className="lg:col-span-2"
          >
            <TrendChart data={trendData || []} isLoading={trendLoading} />
          </ChartCard>

          {/* 类型柱状图 */}
          <ChartCard
            title="类型分布"
            icon={<BarChart3 className="w-5 h-5" />}
          >
            <TypeBarChart data={typeData || []} isLoading={typeLoading} />
          </ChartCard>

          {/* 来源饼图 */}
          <ChartCard
            title="来源分布"
            icon={<PieChart className="w-5 h-5" />}
          >
            <SourcePieChart data={sourceData || []} isLoading={sourceLoading} />
          </ChartCard>

          {/* 标签云 */}
          <ChartCard
            title="热门标签"
            icon={<Tags className="w-5 h-5" />}
            className="lg:col-span-2"
          >
            <TagCloudChart data={tagData || []} isLoading={tagLoading} />
          </ChartCard>
        </div>

        {/* 底部说明 */}
        <div className="mt-8 text-center text-sm text-[var(--text-muted)]">
          <p>数据每小时自动更新一次，最后更新时间：{new Date().toLocaleString('zh-CN')}</p>
        </div>
      </div>
    </div>
  );
}
