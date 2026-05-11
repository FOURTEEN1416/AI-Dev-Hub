/**
 * 行为追踪组件
 * 
 * 自动追踪用户行为：
 * - 页面停留时间
 * - 点击事件
 * - 滚动深度
 * 
 * 用于推荐算法优化
 */

'use client';

import { useEffect, useRef, useCallback } from 'react';
import { recordBehavior } from '@/lib/api';
import { useUserStore } from '@/store';
import type { UserBehavior } from '@/types';

interface BehaviorTrackerProps {
  /** 机会 ID */
  opportunityId: number;
  /** 是否启用追踪，默认 true */
  enabled?: boolean;
  /** 最小停留时间（毫秒），低于此时间不记录，默认 3000ms */
  minDuration?: number;
  /** 滚动深度阈值，达到此深度时记录，默认 50% */
  scrollDepthThreshold?: number;
}

/**
 * 行为追踪组件
 * 用于追踪用户在机会详情页的行为数据
 */
export default function BehaviorTracker({
  opportunityId,
  enabled = true,
  minDuration = 3000,
  scrollDepthThreshold = 50,
}: BehaviorTrackerProps) {
  const { isAuthenticated } = useUserStore();
  
  // 追踪状态
  const startTimeRef = useRef<number>(Date.now());
  const hasRecordedViewRef = useRef(false);
  const hasRecordedScrollRef = useRef(false);
  const maxScrollDepthRef = useRef(0);

  /**
   * 记录行为到服务器
   */
  const trackBehavior = useCallback(
    async (behavior: Omit<UserBehavior, 'opportunity_id'>) => {
      // 未登录时不记录
      if (!isAuthenticated || !enabled) return;

      try {
        await recordBehavior({
          opportunity_id: opportunityId,
          ...behavior,
        });
      } catch (error) {
        // 静默失败，不影响用户体验
        console.debug('行为记录失败:', error);
      }
    },
    [opportunityId, isAuthenticated, enabled]
  );

  /**
   * 记录页面停留时间
   */
  const recordDuration = useCallback(() => {
    const duration = Date.now() - startTimeRef.current;
    
    // 只记录超过最小停留时间的访问
    if (duration >= minDuration && !hasRecordedViewRef.current) {
      hasRecordedViewRef.current = true;
      trackBehavior({
        behavior_type: 'view',
        duration: Math.floor(duration / 1000), // 转换为秒
      });
    }
  }, [minDuration, trackBehavior]);

  /**
   * 处理滚动事件
   */
  const handleScroll = useCallback(() => {
    if (hasRecordedScrollRef.current) return;

    // 计算滚动深度
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const scrollPercent = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;

    // 更新最大滚动深度
    if (scrollPercent > maxScrollDepthRef.current) {
      maxScrollDepthRef.current = scrollPercent;
    }

    // 达到阈值时记录
    if (maxScrollDepthRef.current >= scrollDepthThreshold) {
      hasRecordedScrollRef.current = true;
      trackBehavior({
        behavior_type: 'click', // 使用 click 表示深度交互
        duration: Math.floor((Date.now() - startTimeRef.current) / 1000),
      });
    }
  }, [scrollDepthThreshold, trackBehavior]);

  /**
   * 处理点击事件
   */
  const handleClick = useCallback(
    (e: MouseEvent) => {
      // 检查是否点击了重要元素（链接、按钮等）
      const target = e.target as HTMLElement;
      const isInteractive =
        target.tagName === 'A' ||
        target.tagName === 'BUTTON' ||
        target.closest('a') ||
        target.closest('button');

      if (isInteractive) {
        trackBehavior({
          behavior_type: 'click',
        });
      }
    },
    [trackBehavior]
  );

  // 初始化追踪
  useEffect(() => {
    if (!enabled || !isAuthenticated) return;

    // 重置状态
    startTimeRef.current = Date.now();
    hasRecordedViewRef.current = false;
    hasRecordedScrollRef.current = false;
    maxScrollDepthRef.current = 0;

    // 添加事件监听
    window.addEventListener('scroll', handleScroll, { passive: true });
    document.addEventListener('click', handleClick, { passive: true });

    // 页面卸载时记录停留时间
    const handleBeforeUnload = () => {
      recordDuration();
    };
    window.addEventListener('beforeunload', handleBeforeUnload);

    // 页面隐藏时也记录（移动端切换标签等场景）
    const handleVisibilityChange = () => {
      if (document.hidden) {
        recordDuration();
      }
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      // 清理事件监听
      window.removeEventListener('scroll', handleScroll);
      document.removeEventListener('click', handleClick);
      window.removeEventListener('beforeunload', handleBeforeUnload);
      document.removeEventListener('visibilitychange', handleVisibilityChange);

      // 组件卸载时记录停留时间
      recordDuration();
    };
  }, [enabled, isAuthenticated, handleScroll, handleClick, recordDuration]);

  // 此组件不渲染任何内容
  return null;
}

/**
 * 行为追踪 Hook
 * 用于在非组件场景下追踪行为
 */
export function useBehaviorTracker() {
  const { isAuthenticated } = useUserStore();

  /**
   * 追踪分享行为
   */
  const trackShare = useCallback(
    async (opportunityId: number) => {
      if (!isAuthenticated) return;

      try {
        await recordBehavior({
          opportunity_id: opportunityId,
          behavior_type: 'share',
        });
      } catch (error) {
        console.debug('分享行为记录失败:', error);
      }
    },
    [isAuthenticated]
  );

  /**
   * 追踪收藏行为
   */
  const trackFavorite = useCallback(
    async (opportunityId: number) => {
      if (!isAuthenticated) return;

      try {
        await recordBehavior({
          opportunity_id: opportunityId,
          behavior_type: 'favorite',
        });
      } catch (error) {
        console.debug('收藏行为记录失败:', error);
      }
    },
    [isAuthenticated]
  );

  return {
    trackShare,
    trackFavorite,
  };
}
