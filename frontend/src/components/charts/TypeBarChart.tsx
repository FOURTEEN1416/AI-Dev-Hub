/**
 * 类型柱状图组件
 * 使用 recharts 的 BarChart 展示各类型数量分布
 */

'use client';

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { DistributionItem } from '@/lib/api';

/** 图表颜色配置 - 暗色科技风格 */
const COLORS = [
  '#3b82f6', // 蓝色
  '#8b5cf6', // 紫色
  '#06b6d4', // 青色
  '#10b981', // 绿色
  '#f59e0b', // 橙色
  '#ef4444', // 红色
  '#ec4899', // 粉色
  '#6366f1', // 靛蓝色
];

interface TypeBarChartProps {
  /** 分布数据 */
  data: DistributionItem[];
  /** 是否正在加载 */
  isLoading?: boolean;
}

/**
 * 自定义 Tooltip 组件
 */
function CustomTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{
    value: number;
    payload: DistributionItem;
  }>;
}) {
  if (active && payload && payload.length) {
    const item = payload[0].payload;
    return (
      <div className="glass-card p-3 rounded-lg border border-[var(--border-color)] shadow-lg">
        <p className="text-sm font-medium text-[var(--text-primary)]">
          {item.name}
        </p>
        <p className="text-sm text-[var(--text-secondary)]">
          数量: {item.count}
        </p>
        <p className="text-sm text-[var(--text-muted)]">
          占比: {item.percentage.toFixed(1)}%
        </p>
      </div>
    );
  }
  return null;
}

export default function TypeBarChart({ data, isLoading }: TypeBarChartProps) {
  // 加载状态
  if (isLoading) {
    return (
      <div className="chart-container flex items-center justify-center h-[300px]">
        <div className="animate-pulse text-[var(--text-muted)]">加载中...</div>
      </div>
    );
  }

  // 无数据状态
  if (!data || data.length === 0) {
    return (
      <div className="chart-container flex items-center justify-center h-[300px]">
        <p className="text-[var(--text-muted)]">暂无数据</p>
      </div>
    );
  }

  // 准备图表数据，按数量排序
  const chartData = [...data]
    .sort((a, b) => b.count - a.count)
    .slice(0, 10) // 最多显示前 10 个
    .map((item) => ({
      name: item.name.length > 8 ? item.name.slice(0, 8) + '...' : item.name,
      fullName: item.name,
      value: item.count,
      percentage: item.percentage,
    }));

  return (
    <div className="chart-container h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="rgba(100, 116, 139, 0.2)"
            horizontal={true}
            vertical={false}
          />
          <XAxis
            type="number"
            stroke="#64748b"
            tick={{ fill: '#94a3b8', fontSize: 12 }}
            axisLine={{ stroke: 'rgba(100, 116, 139, 0.3)' }}
          />
          <YAxis
            type="category"
            dataKey="name"
            stroke="#64748b"
            tick={{ fill: '#94a3b8', fontSize: 12 }}
            axisLine={{ stroke: 'rgba(100, 116, 139, 0.3)' }}
            width={80}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(59, 130, 246, 0.1)' }} />
          <Bar
            dataKey="value"
            radius={[0, 4, 4, 0]}
            animationBegin={0}
            animationDuration={800}
          >
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[index % COLORS.length]}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
