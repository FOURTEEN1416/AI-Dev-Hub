/**
 * 机会列表页
 * 包含高级筛选栏、筛选摘要、卡片网格列表、分页和空状态展示
 */

'use client';

import { useState, useEffect, useCallback, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import OpportunityCard from '@/components/opportunity/OpportunityCard';
import Pagination from '@/components/common/Pagination';
import EmptyState from '@/components/common/EmptyState';
import { CardSkeleton } from '@/components/common/Loading';
import AdvancedFilterComponent from '@/components/filter/AdvancedFilter';
import FilterSummary from '@/components/filter/FilterSummary';
import { useAdvancedFilterStore } from '@/store';
import { getMockListResponse } from '@/lib/mock-data';
import type { Opportunity } from '@/types';
import type { AdvancedFilter } from '@/lib/api';

/**
 * 机会列表内容组件
 */
function OpportunitiesContent() {
  const searchParams = useSearchParams();
  const { filters, setFilters, updateFilters, resetFilters } = useAdvancedFilterStore();

  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [limit] = useState(12);

  // 从 URL 参数初始化筛选条件
  useEffect(() => {
    const urlKeyword = searchParams.get('keyword');
    const urlType = searchParams.get('type');
    const urlSource = searchParams.get('source');
    const urlTag = searchParams.get('tag');

    const urlFilters: Partial<AdvancedFilter> = {};
    
    if (urlKeyword) {
      urlFilters.keyword = urlKeyword;
    }
    if (urlType) {
      urlFilters.types = [urlType];
    }
    if (urlSource) {
      urlFilters.sources = [urlSource];
    }
    if (urlTag) {
      urlFilters.tags = [urlTag];
    }

    if (Object.keys(urlFilters).length > 0) {
      updateFilters(urlFilters);
    }
  }, [searchParams, updateFilters]);

  // 模拟数据加载（实际项目中应调用 advancedSearch API）
  useEffect(() => {
    setLoading(true);
    
    // 模拟网络延迟
    const timer = setTimeout(() => {
      // 构建筛选参数（只包含非空值）
      const mockFilters: Record<string, string> = {};
      if (filters.types?.[0]) {
        mockFilters.type = filters.types[0];
      }
      if (filters.sources?.[0]) {
        mockFilters.source = filters.sources[0];
      }
      if (filters.keyword) {
        mockFilters.keyword = filters.keyword;
      }

      // 使用模拟数据
      const response = getMockListResponse(page, limit, mockFilters);

      // 排序
      let items = [...response.items];
      
      if (filters.sort_by === 'created_at') {
        items.sort((a, b) => {
          const diff = new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
          return filters.sort_order === 'desc' ? diff : -diff;
        });
      } else if (filters.sort_by === 'deadline') {
        items.sort((a, b) => {
          if (!a.deadline) return 1;
          if (!b.deadline) return -1;
          const diff = new Date(a.deadline).getTime() - new Date(b.deadline).getTime();
          return filters.sort_order === 'asc' ? diff : -diff;
        });
      } else if (filters.sort_by === 'title') {
        items.sort((a, b) => {
          const diff = a.title.localeCompare(b.title, 'zh-CN');
          return filters.sort_order === 'asc' ? diff : -diff;
        });
      }

      // 标签筛选
      if (filters.tags && filters.tags.length > 0) {
        items = items.filter((item) =>
          item.tags?.some((tag) => filters.tags!.includes(tag))
        );
      }

      // 状态筛选
      if (filters.status) {
        items = items.filter((item) => item.status === filters.status);
      }

      // 有截止日期筛选
      if (filters.has_deadline) {
        items = items.filter((item) => item.deadline !== null);
      }

      setOpportunities(items);
      setTotal(response.total);
      setLoading(false);
    }, 300);

    return () => clearTimeout(timer);
  }, [filters, page, limit]);

  /**
   * 处理筛选条件变更
   */
  const handleFilterChange = useCallback((newFilters: AdvancedFilter) => {
    setFilters(newFilters);
    setPage(1); // 筛选条件变更时重置页码
  }, [setFilters]);

  /**
   * 处理移除单个筛选条件
   */
  const handleRemoveFilter = useCallback((key: keyof AdvancedFilter, value?: string) => {
    if (value && Array.isArray(filters[key])) {
      const array = filters[key] as string[];
      updateFilters({
        [key]: array.filter((item) => item !== value),
      });
    } else {
      updateFilters({
        [key]: undefined,
      });
    }
    setPage(1);
  }, [filters, updateFilters]);

  /**
   * 处理清除所有筛选条件
   */
  const handleClearAllFilters = useCallback(() => {
    resetFilters();
    setPage(1);
  }, [resetFilters]);

  /**
   * 判断是否有活跃的筛选条件
   */
  const hasActiveFilters = () => {
    return (
      (filters.keyword && filters.keyword.length > 0) ||
      (filters.types && filters.types.length > 0) ||
      (filters.sources && filters.sources.length > 0) ||
      (filters.tags && filters.tags.length > 0) ||
      !!filters.status ||
      filters.has_deadline !== undefined ||
      !!filters.deadline_start ||
      !!filters.deadline_end ||
      !!filters.created_start ||
      !!filters.created_end
    );
  };

  return (
    <div className="min-h-screen py-8">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* 页面标题 */}
        <div className="mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold text-[var(--text-primary)]">
            机会列表
          </h1>
          <p className="text-[var(--text-muted)] mt-1">
            浏览和筛选所有 AI 开发者机会
          </p>
        </div>

        {/* 高级筛选栏 */}
        <div className="mb-6">
          <AdvancedFilterComponent
            onFilterChange={handleFilterChange}
            initialFilters={filters}
          />
        </div>

        {/* 筛选摘要 */}
        {hasActiveFilters() && (
          <div className="mb-6">
            <FilterSummary
              filters={filters}
              onRemove={handleRemoveFilter}
              onClearAll={handleClearAllFilters}
            />
          </div>
        )}

        {/* 结果统计 */}
        {!loading && (
          <div className="mb-4 text-sm text-[var(--text-muted)]">
            共找到 <span className="text-[var(--text-primary)] font-medium">{total}</span> 个机会
          </div>
        )}

        {/* 加载状态 */}
        {loading && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
        )}

        {/* 空状态 */}
        {!loading && opportunities.length === 0 && (
          <EmptyState
            type="no-results"
            title="没有找到匹配的机会"
            description="试试调整筛选条件或搜索关键词"
          />
        )}

        {/* 卡片网格列表 */}
        {!loading && opportunities.length > 0 && (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
              {opportunities.map((opportunity) => (
                <OpportunityCard
                  key={opportunity.id}
                  opportunity={opportunity}
                />
              ))}
            </div>

            {/* 分页 */}
            <Pagination
              currentPage={page}
              total={total}
              limit={limit}
              onPageChange={setPage}
            />
          </>
        )}
      </div>
    </div>
  );
}

/**
 * 机会列表页面（带 Suspense 边界）
 */
export default function OpportunitiesPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen py-8">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <CardSkeleton key={i} />
              ))}
            </div>
          </div>
        </div>
      }
    >
      <OpportunitiesContent />
    </Suspense>
  );
}
