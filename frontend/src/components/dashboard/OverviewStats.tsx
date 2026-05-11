/**
 * 概览统计组件
 * 展示多个统计卡片，包括总机会数、活跃机会、即将截止等
 */

'use client';

import { Briefcase, Activity, Clock, TrendingUp } from 'lucide-react';
import StatsCard from './StatsCard';
import { useOverviewStats } from '@/hooks/useStatistics';

export default function OverviewStats() {
  const { data, isLoading } = useOverviewStats();

  // 计算本周新增（模拟数据，实际应从后端获取）
  const weeklyNewCount = data?.by_type
    ? Object.values(data.by_type).reduce((sum, count) => sum + Math.floor(count * 0.1), 0)
    : 0;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* 总机会数 */}
      <StatsCard
        title="总机会数"
        value={data?.total_opportunities ?? 0}
        icon={<Briefcase className="w-5 h-5" />}
        color="blue"
        isLoading={isLoading}
      />

      {/* 活跃机会 */}
      <StatsCard
        title="活跃机会"
        value={data?.active_count ?? 0}
        icon={<Activity className="w-5 h-5" />}
        color="green"
        trend={{ value: 12, isUp: true }}
        isLoading={isLoading}
      />

      {/* 即将截止 */}
      <StatsCard
        title="即将截止"
        value={data?.expiring_soon ?? 0}
        icon={<Clock className="w-5 h-5" />}
        color="orange"
        isLoading={isLoading}
      />

      {/* 本周新增 */}
      <StatsCard
        title="本周新增"
        value={weeklyNewCount}
        icon={<TrendingUp className="w-5 h-5" />}
        color="purple"
        trend={{ value: 8, isUp: true }}
        isLoading={isLoading}
      />
    </div>
  );
}
