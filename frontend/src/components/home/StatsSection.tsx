/**
 * 统计数据区域
 * 展示总机会数、覆盖平台数、本周新增等统计信息
 */

'use client';

import { Zap, Globe, TrendingUp, Users } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StatItemProps {
  icon: React.ElementType;
  value: string;
  label: string;
  color: string;
  delay?: number;
}

/** 统计数据项 */
function StatItem({ icon: Icon, value, label, color, delay = 0 }: StatItemProps) {
  return (
    <div
      className="card-base p-5 text-center group hover:border-[var(--border-hover)] transition-all animate-slide-up"
      style={{ animationDelay: `${delay}s` }}
    >
      <div
        className={cn(
          'inline-flex items-center justify-center w-12 h-12 rounded-xl mb-3 transition-transform group-hover:scale-110',
          color
        )}
      >
        <Icon className="h-6 w-6" />
      </div>
      <p className="text-2xl sm:text-3xl font-bold text-[var(--text-primary)] mb-1">
        {value}
      </p>
      <p className="text-sm text-[var(--text-muted)]">{label}</p>
    </div>
  );
}

export default function StatsSection() {
  // 模拟统计数据
  const stats: StatItemProps[] = [
    {
      icon: Zap,
      value: '256+',
      label: '总机会数',
      color: 'bg-primary-500/10 text-primary-400',
      delay: 0,
    },
    {
      icon: Globe,
      value: '15+',
      label: '覆盖平台',
      color: 'bg-accent-500/10 text-accent-400',
      delay: 0.1,
    },
    {
      icon: TrendingUp,
      value: '38',
      label: '本周新增',
      color: 'bg-emerald-500/10 text-emerald-400',
      delay: 0.2,
    },
    {
      icon: Users,
      value: '1.2K+',
      label: '开发者关注',
      color: 'bg-amber-500/10 text-amber-400',
      delay: 0.3,
    },
  ];

  return (
    <section className="py-12">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.map((stat) => (
            <StatItem key={stat.label} {...stat} />
          ))}
        </div>
      </div>
    </section>
  );
}
