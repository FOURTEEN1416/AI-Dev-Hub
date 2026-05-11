/**
 * 分页组件
 */

'use client';

import { ChevronLeft, ChevronRight } from 'lucide-react';
import { cn, getTotalPages } from '@/lib/utils';

interface PaginationProps {
  currentPage: number;
  total: number;
  limit: number;
  onPageChange: (page: number) => void;
  className?: string;
}

export default function Pagination({
  currentPage,
  total,
  limit,
  onPageChange,
  className,
}: PaginationProps) {
  const totalPages = getTotalPages(total, limit);

  // 不显示分页
  if (totalPages <= 1) return null;

  // 生成页码列表
  const getPageNumbers = (): (number | string)[] => {
    const pages: (number | string)[] = [];

    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      pages.push(1);
      if (currentPage > 3) pages.push('...');

      const start = Math.max(2, currentPage - 1);
      const end = Math.min(totalPages - 1, currentPage + 1);

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }

      if (currentPage < totalPages - 2) pages.push('...');
      pages.push(totalPages);
    }

    return pages;
  };

  return (
    <nav
      className={cn('flex items-center justify-center gap-1', className)}
      aria-label="分页导航"
    >
      {/* 上一页 */}
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage <= 1}
        className={cn(
          'flex items-center justify-center w-9 h-9 rounded-lg transition-all',
          'border border-[var(--border-color)]',
          'text-[var(--text-secondary)]',
          'hover:border-[var(--border-hover)] hover:text-[var(--text-primary)]',
          'disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:border-[var(--border-color)]'
        )}
        aria-label="上一页"
      >
        <ChevronLeft className="h-4 w-4" />
      </button>

      {/* 页码 */}
      {getPageNumbers().map((page, index) =>
        typeof page === 'string' ? (
          <span
            key={`ellipsis-${index}`}
            className="flex items-center justify-center w-9 h-9 text-[var(--text-muted)]"
          >
            ...
          </span>
        ) : (
          <button
            key={page}
            onClick={() => onPageChange(page)}
            className={cn(
              'flex items-center justify-center w-9 h-9 rounded-lg transition-all text-sm font-medium',
              page === currentPage
                ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/25'
                : 'border border-[var(--border-color)] text-[var(--text-secondary)] hover:border-[var(--border-hover)] hover:text-[var(--text-primary)]'
            )}
            aria-label={`第 ${page} 页`}
            aria-current={page === currentPage ? 'page' : undefined}
          >
            {page}
          </button>
        )
      )}

      {/* 下一页 */}
      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage >= totalPages}
        className={cn(
          'flex items-center justify-center w-9 h-9 rounded-lg transition-all',
          'border border-[var(--border-color)]',
          'text-[var(--text-secondary)]',
          'hover:border-[var(--border-hover)] hover:text-[var(--text-primary)]',
          'disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:border-[var(--border-color)]'
        )}
        aria-label="下一页"
      >
        <ChevronRight className="h-4 w-4" />
      </button>
    </nav>
  );
}
