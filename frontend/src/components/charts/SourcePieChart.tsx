/**
 * 来源饼图组件
 * 使用 recharts 的 PieChart 展示各来源占比
 */

'use client';

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
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
  '#14b8a6', // 青绿色
  '#f97316', // 深橙色
];

interface SourcePieChartProps {
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
    name: string;
    value: number;
    payload: DistributionItem;
  }>;
}) {
  if (active && payload && payload.length) {
    const item = payload[0];
    return (
      <div className="glass-card p-3 rounded-lg border border-[var(--border-color)] shadow-lg">
        <p className="text-sm font-medium text-[var(--text-primary)]">
          {item.name}
        </p>
        <p className="text-sm text-[var(--text-secondary)]">
          数量: {item.value}
        </p>
        <p className="text-sm text-[var(--text-muted)]">
          占比: {item.payload.percentage.toFixed(1)}%
        </p>
      </div>
    );
  }
  return null;
}

/**
 * 自定义图例渲染
 */
function renderLegendText(value: string, entry: { color: string }) {
  return (
    <span style={{ color: entry.color }} className="text-sm">
      {value}
    </span>
  );
}

export default function SourcePieChart({ data, isLoading }: SourcePieChartProps) {
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

  // 准备图表数据
  const chartData = data.map((item) => ({
    name: item.name,
    value: item.count,
    percentage: item.percentage,
  }));

  return (
    <div className="chart-container h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            paddingAngle={2}
            dataKey="value"
            animationBegin={0}
            animationDuration={800}
          >
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[index % COLORS.length]}
                stroke="transparent"
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            layout="horizontal"
            align="center"
            verticalAlign="bottom"
            formatter={renderLegendText}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
