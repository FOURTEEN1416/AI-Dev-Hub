/**
 * 趋势折线图组件
 * 使用 recharts 的 LineChart 展示机会数量趋势
 */

'use client';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { TrendDataPoint } from '@/lib/api';

/** 图表颜色配置 - 暗色科技风格 */
const COLORS = [
  '#3b82f6', // 蓝色
  '#8b5cf6', // 紫色
  '#06b6d4', // 青色
  '#10b981', // 绿色
  '#f59e0b', // 橙色
  '#ef4444', // 红色
  '#ec4899', // 粉色
];

interface TrendChartProps {
  /** 趋势数据 */
  data: TrendDataPoint[];
  /** 是否正在加载 */
  isLoading?: boolean;
}

/**
 * 自定义 Tooltip 组件
 */
function CustomTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: Array<{ name: string; value: number; color: string }>;
  label?: string;
}) {
  if (active && payload && payload.length) {
    return (
      <div className="glass-card p-3 rounded-lg border border-[var(--border-color)] shadow-lg">
        <p className="text-sm font-medium text-[var(--text-primary)] mb-2">{label}</p>
        {payload.map((entry, index) => (
          <p
            key={index}
            className="text-sm"
            style={{ color: entry.color }}
          >
            {entry.name}: {entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
}

export default function TrendChart({ data, isLoading }: TrendChartProps) {
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

  // 获取所有类型
  const types = new Set<string>();
  data.forEach((item) => {
    Object.keys(item.by_type).forEach((type) => types.add(type));
  });
  const typeList = Array.from(types);

  // 格式化日期显示
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return `${date.getMonth() + 1}/${date.getDate()}`;
  };

  return (
    <div className="chart-container h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="rgba(100, 116, 139, 0.2)"
          />
          <XAxis
            dataKey="date"
            tickFormatter={formatDate}
            stroke="#64748b"
            tick={{ fill: '#94a3b8', fontSize: 12 }}
            axisLine={{ stroke: 'rgba(100, 116, 139, 0.3)' }}
          />
          <YAxis
            stroke="#64748b"
            tick={{ fill: '#94a3b8', fontSize: 12 }}
            axisLine={{ stroke: 'rgba(100, 116, 139, 0.3)' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ paddingTop: '10px' }}
            formatter={(value) => (
              <span className="text-[var(--text-secondary)] text-sm">{value}</span>
            )}
          />
          {/* 总数线 */}
          <Line
            type="monotone"
            dataKey="count"
            name="总数"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: '#3b82f6' }}
          />
          {/* 按类型分组的线 */}
          {typeList.map((type, index) => (
            <Line
              key={type}
              type="monotone"
              dataKey={`by_type.${type}`}
              name={type}
              stroke={COLORS[(index + 1) % COLORS.length]}
              strokeWidth={1.5}
              dot={false}
              activeDot={{ r: 3 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
