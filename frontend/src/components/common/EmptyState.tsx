/**
 * 空状态组件
 */

import { cn } from '@/lib/utils';
import { SearchX, Inbox, AlertCircle } from 'lucide-react';

interface EmptyStateProps {
  type?: 'no-results' | 'no-data' | 'error';
  title?: string;
  description?: string;
  className?: string;
  action?: React.ReactNode;
}

const defaultConfig = {
  'no-results': {
    icon: SearchX,
    title: '没有找到匹配的结果',
    description: '试试调整搜索关键词或筛选条件',
  },
  'no-data': {
    icon: Inbox,
    title: '暂无数据',
    description: '目前还没有相关内容，请稍后再来看看',
  },
  error: {
    icon: AlertCircle,
    title: '加载失败',
    description: '请检查网络连接后重试',
  },
};

export default function EmptyState({
  type = 'no-data',
  title,
  description,
  className,
  action,
}: EmptyStateProps) {
  const config = defaultConfig[type];
  const Icon = config.icon;

  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center py-16 px-4 text-center',
        className
      )}
    >
      <div className="mb-4 rounded-full bg-[var(--bg-secondary)] p-4">
        <Icon className="h-10 w-10 text-[var(--text-muted)]" />
      </div>
      <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">
        {title || config.title}
      </h3>
      <p className="text-sm text-[var(--text-muted)] max-w-md mb-6">
        {description || config.description}
      </p>
      {action && <div>{action}</div>}
    </div>
  );
}
