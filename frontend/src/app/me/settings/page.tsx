/**
 * 用户设置页面
 * 
 * 包含：
 * - 订阅偏好设置
 * - 通知设置
 * - 账号设置
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ChevronRight, Home, Settings as SettingsIcon, Bell, User } from 'lucide-react';
import SubscriptionSettings from '@/components/subscription/SubscriptionSettings';
import { useUserStore } from '@/store';

export default function SettingsPage() {
  const router = useRouter();
  const { isAuthenticated, user } = useUserStore();

  // 未登录时重定向到登录页
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login?redirect=/me/settings');
    }
  }, [isAuthenticated, router]);

  // 未登录时不渲染内容
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen py-8">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        {/* 面包屑导航 */}
        <nav className="flex items-center gap-2 text-sm text-[var(--text-muted)] mb-8">
          <Link
            href="/"
            className="hover:text-[var(--text-primary)] transition-colors flex items-center gap-1"
          >
            <Home className="h-3.5 w-3.5" />
            首页
          </Link>
          <ChevronRight className="h-3.5 w-3.5" />
          <Link
            href="/me"
            className="hover:text-[var(--text-primary)] transition-colors"
          >
            个人中心
          </Link>
          <ChevronRight className="h-3.5 w-3.5" />
          <span className="text-[var(--text-primary)]">设置</span>
        </nav>

        {/* 页面标题 */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <SettingsIcon className="h-6 w-6 text-primary-400" />
            <h1 className="text-2xl font-bold text-[var(--text-primary)]">
              设置
            </h1>
          </div>
          <p className="text-[var(--text-secondary)]">
            管理你的订阅偏好和通知设置
          </p>
        </div>

        {/* 设置标签页导航 */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          <Link
            href="#subscription"
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium bg-primary-500/20 text-primary-400 border border-primary-500/50"
          >
            <Bell className="h-4 w-4" />
            订阅偏好
          </Link>
          <Link
            href="#account"
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium bg-[var(--bg-secondary)] text-[var(--text-secondary)] border border-[var(--border-color)] hover:bg-[var(--bg-tertiary)] transition-colors"
          >
            <User className="h-4 w-4" />
            账号设置
          </Link>
        </div>

        {/* 订阅偏好设置 */}
        <section id="subscription">
          <SubscriptionSettings />
        </section>

        {/* 账号设置（预留） */}
        <section id="account" className="mt-8">
          <div className="card-base p-6">
            <div className="flex items-center gap-2 mb-4">
              <User className="h-5 w-5 text-primary-400" />
              <h3 className="text-lg font-semibold text-[var(--text-primary)]">
                账号设置
              </h3>
            </div>
            
            {/* 用户信息展示 */}
            <div className="space-y-4">
              <div className="p-4 rounded-lg bg-[var(--bg-secondary)]">
                <p className="text-xs text-[var(--text-muted)] mb-1">邮箱</p>
                <p className="text-sm text-[var(--text-primary)]">{user?.email}</p>
              </div>
              
              <div className="p-4 rounded-lg bg-[var(--bg-secondary)]">
                <p className="text-xs text-[var(--text-muted)] mb-1">用户名</p>
                <p className="text-sm text-[var(--text-primary)]">
                  {user?.username || '未设置'}
                </p>
              </div>

              <div className="p-4 rounded-lg bg-[var(--bg-secondary)]">
                <p className="text-xs text-[var(--text-muted)] mb-1">注册时间</p>
                <p className="text-sm text-[var(--text-primary)]">
                  {user?.created_at
                    ? new Date(user.created_at).toLocaleDateString('zh-CN')
                    : '未知'}
                </p>
              </div>
            </div>

            {/* 功能预告 */}
            <div className="mt-6 p-4 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border-color)]">
              <p className="text-sm text-[var(--text-muted)]">
                更多账号设置功能即将上线，包括修改密码、绑定第三方账号等。
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
