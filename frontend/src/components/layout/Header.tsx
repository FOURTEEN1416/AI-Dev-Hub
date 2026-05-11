/**
 * 顶部导航栏
 * 包含 Logo、导航链接、搜索框、主题切换和移动端菜单
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, X, Sun, Moon, Sparkles, Search } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useThemeStore } from '@/store';
import SearchBar from '@/components/common/SearchBar';
import UserMenu from '@/components/auth/UserMenu';

/** 导航链接配置 */
const navLinks = [
  { href: '/', label: '首页' },
  { href: '/opportunities', label: '机会列表' },
  { href: '/stats', label: '数据看板' },
  { href: '/about', label: '关于' },
];

export default function Header() {
  const pathname = usePathname();
  const { isDark, toggleTheme } = useThemeStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 glass">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group">
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-accent-500 shadow-lg shadow-primary-500/20 group-hover:shadow-primary-500/40 transition-shadow">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <span className="text-lg font-bold text-[var(--text-primary)] hidden sm:block">
              AI Dev Hub
            </span>
          </Link>

          {/* 桌面端导航链接 */}
          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  'px-3 py-2 rounded-lg text-sm font-medium transition-all',
                  pathname === link.href
                    ? 'text-primary-400 bg-primary-500/10'
                    : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-secondary)]'
                )}
              >
                {link.label}
              </Link>
            ))}
          </nav>

          {/* 右侧操作区 */}
          <div className="flex items-center gap-2">
            {/* 桌面端搜索框 */}
            <div className="hidden md:block w-64">
              <SearchBar
                placeholder="快速搜索..."
                size="sm"
              />
            </div>

            {/* 移动端搜索按钮 */}
            <button
              onClick={() => setSearchOpen(!searchOpen)}
              className="md:hidden p-2 rounded-lg text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-secondary)] transition-colors"
              aria-label="搜索"
            >
              <Search className="h-5 w-5" />
            </button>

            {/* 主题切换 */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-secondary)] transition-colors"
              aria-label={isDark ? '切换到亮色模式' : '切换到暗色模式'}
            >
              {isDark ? (
                <Sun className="h-5 w-5" />
              ) : (
                <Moon className="h-5 w-5" />
              )}
            </button>

            {/* 用户菜单 */}
            <UserMenu />

            {/* 移动端菜单按钮 */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-secondary)] transition-colors"
              aria-label="菜单"
            >
              {mobileMenuOpen ? (
                <X className="h-5 w-5" />
              ) : (
                <Menu className="h-5 w-5" />
              )}
            </button>
          </div>
        </div>

        {/* 移动端搜索框展开 */}
        {searchOpen && (
          <div className="md:hidden pb-3 animate-in">
            <SearchBar placeholder="搜索机会..." size="md" />
          </div>
        )}

        {/* 移动端菜单展开 */}
        {mobileMenuOpen && (
          <div className="md:hidden pb-4 animate-in">
            <nav className="flex flex-col gap-1">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={cn(
                    'px-3 py-2.5 rounded-lg text-sm font-medium transition-all',
                    pathname === link.href
                      ? 'text-primary-400 bg-primary-500/10'
                      : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-secondary)]'
                  )}
                >
                  {link.label}
                </Link>
              ))}
            </nav>
          </div>
        )}
      </div>
    </header>
  );
}
