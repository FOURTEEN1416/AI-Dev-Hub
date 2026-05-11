/**
 * 加载状态组件
 */

import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
  className?: string;
  fullScreen?: boolean;
}

const sizeMap = {
  sm: 'h-5 w-5',
  md: 'h-8 w-8',
  lg: 'h-12 w-12',
};

export default function Loading({
  size = 'md',
  text = '加载中...',
  className,
  fullScreen = false,
}: LoadingProps) {
  const content = (
    <div
      className={cn(
        'flex flex-col items-center justify-center gap-3',
        fullScreen && 'fixed inset-0 z-50 bg-[var(--bg-primary)]/80 backdrop-blur-sm',
        className
      )}
    >
      <Loader2
        className={cn(
          'animate-spin text-primary-400',
          sizeMap[size]
        )}
      />
      {text && (
        <p className="text-sm text-[var(--text-muted)] animate-pulse">
          {text}
        </p>
      )}
    </div>
  );

  if (fullScreen) return content;
  return <div className="py-12">{content}</div>;
}

/**
 * 骨架屏加载组件
 */
export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        'animate-pulse rounded-lg bg-[var(--bg-secondary)]',
        className
      )}
    />
  );
}

/**
 * 卡片骨架屏
 */
export function CardSkeleton() {
  return (
    <div className="card-base p-5 space-y-4">
      <div className="flex items-center gap-2">
        <Skeleton className="h-5 w-20 rounded-full" />
        <Skeleton className="h-5 w-16 rounded-full" />
      </div>
      <Skeleton className="h-6 w-3/4" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-2/3" />
      <div className="flex gap-2 pt-2">
        <Skeleton className="h-6 w-14 rounded-full" />
        <Skeleton className="h-6 w-14 rounded-full" />
        <Skeleton className="h-6 w-14 rounded-full" />
      </div>
    </div>
  );
}
