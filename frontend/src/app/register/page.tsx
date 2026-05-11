/**
 * 注册页面
 * 用户注册入口
 */

'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Mail, Lock, Eye, EyeOff, Loader2, AlertCircle, User } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { cn } from '@/lib/utils';

export default function RegisterPage() {
  const router = useRouter();
  const { register, loading, error, isAuthenticated, clearError } = useAuth();

  // 表单状态
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  // 已登录用户重定向到首页
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/');
    }
  }, [isAuthenticated, router]);

  // 清除错误
  useEffect(() => {
    return () => {
      clearError();
    };
  }, [clearError]);

  /**
   * 表单验证
   */
  const validateForm = (): boolean => {
    // 邮箱验证
    if (!email.trim()) {
      setFormError('请输入邮箱地址');
      return false;
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setFormError('请输入有效的邮箱地址');
      return false;
    }

    // 用户名验证
    if (!username.trim()) {
      setFormError('请输入用户名');
      return false;
    }
    if (username.trim().length < 2) {
      setFormError('用户名至少需要 2 个字符');
      return false;
    }
    if (username.trim().length > 20) {
      setFormError('用户名不能超过 20 个字符');
      return false;
    }

    // 密码验证
    if (!password) {
      setFormError('请输入密码');
      return false;
    }
    if (password.length < 6) {
      setFormError('密码至少需要 6 个字符');
      return false;
    }

    // 确认密码验证
    if (!confirmPassword) {
      setFormError('请确认密码');
      return false;
    }
    if (password !== confirmPassword) {
      setFormError('两次输入的密码不一致');
      return false;
    }

    return true;
  };

  /**
   * 表单提交处理
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    if (!validateForm()) {
      return;
    }

    // 调用注册 API
    const result = await register({
      email: email.trim(),
      username: username.trim(),
      password,
    });

    if (result.success) {
      router.push('/');
    }
  };

  const displayError = formError || error;

  return (
    <div className="min-h-[calc(100vh-200px)] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        {/* 标题 */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-[var(--text-primary)] mb-2">
            创建账户
          </h1>
          <p className="text-[var(--text-secondary)]">
            加入 AI Dev Hub，发现更多机会
          </p>
        </div>

        {/* 注册表单 */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* 错误提示 */}
          {displayError && (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
              <AlertCircle className="h-4 w-4 flex-shrink-0" />
              <span>{displayError}</span>
            </div>
          )}

          {/* 邮箱输入框 */}
          <div className="space-y-1.5">
            <label htmlFor="email" className="block text-sm font-medium text-[var(--text-primary)]">
              邮箱地址
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-[var(--text-muted)]" />
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="请输入邮箱"
                className={cn(
                  'w-full pl-10 pr-4 py-2.5 rounded-lg',
                  'bg-[var(--bg-secondary)] border border-[var(--border-color)]',
                  'text-[var(--text-primary)] placeholder:text-[var(--text-muted)]',
                  'focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500',
                  'transition-all'
                )}
                disabled={loading}
              />
            </div>
          </div>

          {/* 用户名输入框 */}
          <div className="space-y-1.5">
            <label htmlFor="username" className="block text-sm font-medium text-[var(--text-primary)]">
              用户名
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-[var(--text-muted)]" />
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="请输入用户名"
                maxLength={20}
                className={cn(
                  'w-full pl-10 pr-4 py-2.5 rounded-lg',
                  'bg-[var(--bg-secondary)] border border-[var(--border-color)]',
                  'text-[var(--text-primary)] placeholder:text-[var(--text-muted)]',
                  'focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500',
                  'transition-all'
                )}
                disabled={loading}
              />
            </div>
            <p className="text-xs text-[var(--text-muted)]">2-20 个字符</p>
          </div>

          {/* 密码输入框 */}
          <div className="space-y-1.5">
            <label htmlFor="password" className="block text-sm font-medium text-[var(--text-primary)]">
              密码
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-[var(--text-muted)]" />
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="请输入密码"
                className={cn(
                  'w-full pl-10 pr-12 py-2.5 rounded-lg',
                  'bg-[var(--bg-secondary)] border border-[var(--border-color)]',
                  'text-[var(--text-primary)] placeholder:text-[var(--text-muted)]',
                  'focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500',
                  'transition-all'
                )}
                disabled={loading}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
                aria-label={showPassword ? '隐藏密码' : '显示密码'}
              >
                {showPassword ? (
                  <EyeOff className="h-5 w-5" />
                ) : (
                  <Eye className="h-5 w-5" />
                )}
              </button>
            </div>
            <p className="text-xs text-[var(--text-muted)]">至少 6 个字符</p>
          </div>

          {/* 确认密码输入框 */}
          <div className="space-y-1.5">
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-[var(--text-primary)]">
              确认密码
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-[var(--text-muted)]" />
              <input
                id="confirmPassword"
                type={showConfirmPassword ? 'text' : 'password'}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="请再次输入密码"
                className={cn(
                  'w-full pl-10 pr-12 py-2.5 rounded-lg',
                  'bg-[var(--bg-secondary)] border border-[var(--border-color)]',
                  'text-[var(--text-primary)] placeholder:text-[var(--text-muted)]',
                  'focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500',
                  'transition-all'
                )}
                disabled={loading}
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
                aria-label={showConfirmPassword ? '隐藏密码' : '显示密码'}
              >
                {showConfirmPassword ? (
                  <EyeOff className="h-5 w-5" />
                ) : (
                  <Eye className="h-5 w-5" />
                )}
              </button>
            </div>
          </div>

          {/* 注册按钮 */}
          <button
            type="submit"
            disabled={loading}
            className={cn(
              'w-full py-2.5 rounded-lg font-medium',
              'bg-gradient-to-r from-primary-500 to-accent-500',
              'text-white shadow-lg shadow-primary-500/20',
              'hover:shadow-primary-500/40 hover:scale-[1.02]',
              'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100',
              'transition-all duration-200'
            )}
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <Loader2 className="h-5 w-5 animate-spin" />
                注册中...
              </span>
            ) : (
              '注册'
            )}
          </button>
        </form>

        {/* 登录链接 */}
        <p className="mt-6 text-center text-sm text-[var(--text-secondary)]">
          已有账户？{' '}
          <Link
            href="/login"
            className="text-primary-400 hover:text-primary-300 font-medium transition-colors"
          >
            立即登录
          </Link>
        </p>
      </div>
    </div>
  );
}
