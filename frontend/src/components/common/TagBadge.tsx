/**
 * 标签徽章组件
 */

import { cn } from '@/lib/utils';

interface TagBadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'primary' | 'accent' | 'success' | 'warning' | 'danger';
  size?: 'sm' | 'md';
  className?: string;
  onClick?: () => void;
}

const variantClasses = {
  default: 'bg-dark-700/50 text-dark-300 border-dark-600/50',
  primary: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
  accent: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
  success: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  warning: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  danger: 'bg-red-500/10 text-red-400 border-red-500/30',
};

const sizeClasses = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-3 py-1 text-sm',
};

export default function TagBadge({
  children,
  variant = 'default',
  size = 'sm',
  className,
  onClick,
}: TagBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border font-medium transition-colors',
        variantClasses[variant],
        sizeClasses[size],
        onClick && 'cursor-pointer hover:opacity-80',
        className
      )}
      onClick={onClick}
    >
      {children}
    </span>
  );
}
