/**
 * 用户菜单组件
 * 未登录显示登录/注册按钮，已登录显示用户下拉菜单
 */

'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { User, Heart, LogOut, ChevronDown, Loader2 } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { cn } from '@/lib/utils';

interface UserMenuProps {
  /** 自定义样式 */
  className?: string;
}

export default function UserMenu({ className }: UserMenuProps) {
  const { user, isAuthenticated, loading, logout, initialized } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // 点击外部关闭下拉菜单
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  /**
   * 退出登录
   */
  const handleLogout = async () => {
    setDropdownOpen(false);
    await logout();
  };

  // 加载中状态
  if (!initialized || loading) {
    return (
      <div className={cn('flex items-center', className)}>
        <Loader2 className="h-5 w-5 animate-spin text-[var(--text-muted)]" />
      </div>
    );
  }

  // 未登录状态
  if (!isAuthenticated || !user) {
    return (
      <div className={cn('flex items-center gap-2', className)}>
        <Link
          href="/login"
          className={cn(
            'px-3 py-1.5 rounded-lg text-sm font-medium',
            'text-[var(--text-secondary)] hover:text-[var(--text-primary)]',
            'hover:bg-[var(--bg-secondary)] transition-all'
          )}
        >
          登录
        </Link>
        <Link
          href="/register"
          className={cn(
            'px-3 py-1.5 rounded-lg text-sm font-medium',
            'bg-gradient-to-r from-primary-500 to-accent-500',
            'text-white shadow-sm',
            'hover:shadow-primary-500/30 hover:scale-[1.02]',
            'transition-all'
          )}
        >
          注册
        </Link>
      </div>
    );
  }

  // 已登录状态
  return (
    <div className={cn('relative', className)} ref={dropdownRef}>
      {/* 触发按钮 */}
      <button
        onClick={() => setDropdownOpen(!dropdownOpen)}
        className={cn(
          'flex items-center gap-2 px-2 py-1.5 rounded-lg',
          'hover:bg-[var(--bg-secondary)] transition-colors',
          dropdownOpen && 'bg-[var(--bg-secondary)]'
        )}
        aria-label="用户菜单"
        aria-expanded={dropdownOpen}
      >
        {/* 头像 */}
        <div className="w-7 h-7 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white text-sm font-medium">
          {user.username?.charAt(0).toUpperCase() || user.email.charAt(0).toUpperCase()}
        </div>
        {/* 用户名 */}
        <span className="hidden sm:block text-sm font-medium text-[var(--text-primary)] max-w-[100px] truncate">
          {user.username || user.email.split('@')[0]}
        </span>
        <ChevronDown
          className={cn(
            'h-4 w-4 text-[var(--text-muted)] transition-transform',
            dropdownOpen && 'rotate-180'
          )}
        />
      </button>

      {/* 下拉菜单 */}
      {dropdownOpen && (
        <div
          className={cn(
            'absolute right-0 mt-2 w-48 py-1 rounded-lg',
            'bg-[var(--bg-primary)] border border-[var(--border-color)]',
            'shadow-lg shadow-black/20 animate-in fade-in slide-in-from-top-2',
            'z-50'
          )}
        >
          {/* 用户信息 */}
          <div className="px-3 py-2 border-b border-[var(--border-color)]">
            <p className="text-sm font-medium text-[var(--text-primary)] truncate">
              {user.username || '用户'}
            </p>
            <p className="text-xs text-[var(--text-muted)] truncate">
              {user.email}
            </p>
          </div>

          {/* 菜单项 */}
          <div className="py-1">
            <Link
              href="/me"
              onClick={() => setDropdownOpen(false)}
              className={cn(
                'flex items-center gap-2 px-3 py-2 text-sm',
                'text-[var(--text-secondary)] hover:text-[var(--text-primary)]',
                'hover:bg-[var(--bg-secondary)] transition-colors'
              )}
            >
              <User className="h-4 w-4" />
              个人中心
            </Link>
            <Link
              href="/me/favorites"
              onClick={() => setDropdownOpen(false)}
              className={cn(
                'flex items-center gap-2 px-3 py-2 text-sm',
                'text-[var(--text-secondary)] hover:text-[var(--text-primary)]',
                'hover:bg-[var(--bg-secondary)] transition-colors'
              )}
            >
              <Heart className="h-4 w-4" />
              我的收藏
            </Link>
          </div>

          {/* 退出登录 */}
          <div className="border-t border-[var(--border-color)] pt-1">
            <button
              onClick={handleLogout}
              className={cn(
                'w-full flex items-center gap-2 px-3 py-2 text-sm',
                'text-red-400 hover:text-red-300',
                'hover:bg-red-500/10 transition-colors'
              )}
            >
              <LogOut className="h-4 w-4" />
              退出登录
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
