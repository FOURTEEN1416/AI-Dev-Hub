/**
 * 标签云图组件
 * 自定义实现标签云，根据数量计算大小和颜色
 */

'use client';

import { useRouter } from 'next/navigation';
import { TagCloudItem } from '@/lib/api';
import { cn } from '@/lib/utils';

/** 颜色梯度配置 - 从冷色到暖色 */
const COLOR_GRADIENT = [
  '#3b82f6', // 蓝色 - 最小
  '#6366f1', // 靛蓝色
  '#8b5cf6', // 紫色
  '#a855f7', // 亮紫色
  '#d946ef', // 紫红色
  '#ec4899', // 粉色 - 最大
];

interface TagCloudChartProps {
  /** 标签云数据 */
  data: TagCloudItem[];
  /** 是否正在加载 */
  isLoading?: boolean;
  /** 最大显示数量 */
  maxTags?: number;
}

/**
 * 根据数量计算颜色
 */
function getColorByCount(count: number, minCount: number, maxCount: number): string {
  if (maxCount === minCount) return COLOR_GRADIENT[0];
  const ratio = (count - minCount) / (maxCount - minCount);
  const index = Math.min(
    Math.floor(ratio * (COLOR_GRADIENT.length - 1)),
    COLOR_GRADIENT.length - 1
  );
  return COLOR_GRADIENT[index];
}

/**
 * 根据大小计算字体尺寸
 */
function getFontSize(size: number): string {
  // size 范围通常是 1-10，映射到字体大小
  const minSize = 12;
  const maxSize = 24;
  const fontSize = minSize + (size / 10) * (maxSize - minSize);
  return `${fontSize}px`;
}

export default function TagCloudChart({
  data,
  isLoading,
  maxTags = 50,
}: TagCloudChartProps) {
  const router = useRouter();

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

  // 取前 maxTags 个标签
  const displayTags = data.slice(0, maxTags);

  // 计算数量范围
  const counts = displayTags.map((tag) => tag.count);
  const minCount = Math.min(...counts);
  const maxCount = Math.max(...counts);

  // 点击标签跳转搜索
  const handleTagClick = (tag: string) => {
    router.push(`/opportunities?keyword=${encodeURIComponent(tag)}`);
  };

  return (
    <div className="chart-container h-[300px] w-full overflow-hidden">
      <div className="flex flex-wrap gap-2 justify-center items-center h-full p-4">
        {displayTags.map((tag, index) => {
          const color = getColorByCount(tag.count, minCount, maxCount);
          const fontSize = getFontSize(tag.size);

          return (
            <button
              key={`${tag.tag}-${index}`}
              onClick={() => handleTagClick(tag.tag)}
              className={cn(
                'tag-cloud-item',
                'px-2 py-1 rounded-md transition-all duration-200',
                'hover:scale-110 hover:shadow-lg',
                'focus:outline-none focus:ring-2 focus:ring-primary-500/50'
              )}
              style={{
                color,
                fontSize,
                backgroundColor: `${color}15`, // 添加淡色背景
              }}
              title={`${tag.tag}: ${tag.count} 个机会`}
            >
              {tag.tag}
            </button>
          );
        })}
      </div>
    </div>
  );
}
