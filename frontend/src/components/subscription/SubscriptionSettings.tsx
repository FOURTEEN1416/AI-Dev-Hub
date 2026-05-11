/**
 * 订阅设置组件
 * 
 * 包含：
 * - 感兴趣的类型选择
 * - 感兴趣的来源选择
 * - 感兴趣的标签选择
 * - 通知频率选择
 * - 邮件通知开关
 */

'use client';

import { useState, useEffect } from 'react';
import {
  Bell,
  Mail,
  Tag,
  Globe,
  Type,
  Clock,
  Save,
  Loader2,
  CheckCircle,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { getSubscription, updateSubscription, getTypes, getSources, getPopularTags } from '@/lib/api';
import type { UserSubscription } from '@/types';

/** 机会类型选项 */
const OPPORTUNITY_TYPES = [
  { value: 'developer_program', label: '开发者计划' },
  { value: 'competition', label: '比赛/竞赛' },
  { value: 'free_credits', label: '免费额度' },
  { value: 'community', label: '社区动态' },
];

/** 通知频率选项 */
const FREQUENCY_OPTIONS = [
  { value: 'daily', label: '每天', description: '每天发送一次通知' },
  { value: 'weekly', label: '每周', description: '每周发送一次通知' },
];

/**
 * 订阅设置组件
 * 管理用户的订阅偏好设置
 */
export default function SubscriptionSettings() {
  // 状态
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 订阅设置
  const [settings, setSettings] = useState<UserSubscription>({
    preferred_types: [],
    preferred_sources: [],
    preferred_tags: [],
    email_notification: false,
    notification_frequency: 'daily',
  });

  // 可选项
  const [availableTypes, setAvailableTypes] = useState<string[]>([]);
  const [availableSources, setAvailableSources] = useState<string[]>([]);
  const [availableTags, setAvailableTags] = useState<string[]>([]);

  // 加载数据
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        
        // 并行加载所有数据
        const [subscriptionData, typesData, sourcesData, tagsData] = await Promise.all([
          getSubscription().catch(() => null),
          getTypes().catch(() => OPPORTUNITY_TYPES.map(t => t.value)),
          getSources().catch(() => []),
          getPopularTags(20).catch(() => []),
        ]);

        if (subscriptionData) {
          setSettings(subscriptionData);
        }
        setAvailableTypes(typesData as string[]);
        setAvailableSources(sourcesData as string[]);
        setAvailableTags(tagsData as string[]);
      } catch (err) {
        console.error('加载订阅设置失败:', err);
        setError('加载设置失败，请刷新页面重试');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  /**
   * 保存设置
   */
  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      
      await updateSubscription(settings);
      setSaved(true);
      
      // 3秒后清除保存成功提示
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error('保存订阅设置失败:', err);
      setError('保存失败，请重试');
    } finally {
      setSaving(false);
    }
  };

  /**
   * 切换类型选择
   */
  const toggleType = (type: string) => {
    setSettings((prev) => ({
      ...prev,
      preferred_types: prev.preferred_types.includes(type)
        ? prev.preferred_types.filter((t) => t !== type)
        : [...prev.preferred_types, type],
    }));
  };

  /**
   * 切换来源选择
   */
  const toggleSource = (source: string) => {
    setSettings((prev) => ({
      ...prev,
      preferred_sources: prev.preferred_sources.includes(source)
        ? prev.preferred_sources.filter((s) => s !== source)
        : [...prev.preferred_sources, source],
    }));
  };

  /**
   * 切换标签选择
   */
  const toggleTag = (tag: string) => {
    setSettings((prev) => ({
      ...prev,
      preferred_tags: prev.preferred_tags.includes(tag)
        ? prev.preferred_tags.filter((t) => t !== tag)
        : [...prev.preferred_tags, tag],
    }));
  };

  // 加载状态
  if (loading) {
    return (
      <div className="card-base p-6">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary-400" />
          <span className="ml-3 text-[var(--text-secondary)]">加载中...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 错误提示 */}
      {error && (
        <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400">
          {error}
        </div>
      )}

      {/* 成功提示 */}
      {saved && (
        <div className="p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center gap-2">
          <CheckCircle className="h-5 w-5" />
          设置已保存
        </div>
      )}

      {/* 感兴趣的类型 */}
      <div className="card-base p-6">
        <div className="flex items-center gap-2 mb-4">
          <Type className="h-5 w-5 text-primary-400" />
          <h3 className="text-lg font-semibold text-[var(--text-primary)]">
            感兴趣的类型
          </h3>
        </div>
        <p className="text-sm text-[var(--text-muted)] mb-4">
          选择你感兴趣的机会类型，我们将为你推荐相关内容
        </p>
        <div className="flex flex-wrap gap-2">
          {OPPORTUNITY_TYPES.map((type) => (
            <button
              key={type.value}
              onClick={() => toggleType(type.value)}
              className={cn(
                'px-4 py-2 rounded-lg text-sm font-medium transition-all',
                'border border-[var(--border-color)]',
                settings.preferred_types.includes(type.value)
                  ? 'bg-primary-500/20 text-primary-400 border-primary-500/50'
                  : 'bg-[var(--bg-secondary)] text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)]'
              )}
            >
              {type.label}
            </button>
          ))}
        </div>
      </div>

      {/* 感兴趣的来源 */}
      {availableSources.length > 0 && (
        <div className="card-base p-6">
          <div className="flex items-center gap-2 mb-4">
            <Globe className="h-5 w-5 text-primary-400" />
            <h3 className="text-lg font-semibold text-[var(--text-primary)]">
              感兴趣的来源
            </h3>
          </div>
          <p className="text-sm text-[var(--text-muted)] mb-4">
            选择你关注的来源平台
          </p>
          <div className="flex flex-wrap gap-2">
            {availableSources.map((source) => (
              <button
                key={source}
                onClick={() => toggleSource(source)}
                className={cn(
                  'px-4 py-2 rounded-lg text-sm font-medium transition-all',
                  'border border-[var(--border-color)]',
                  settings.preferred_sources.includes(source)
                    ? 'bg-primary-500/20 text-primary-400 border-primary-500/50'
                    : 'bg-[var(--bg-secondary)] text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)]'
                )}
              >
                {source}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 感兴趣的标签 */}
      {availableTags.length > 0 && (
        <div className="card-base p-6">
          <div className="flex items-center gap-2 mb-4">
            <Tag className="h-5 w-5 text-primary-400" />
            <h3 className="text-lg font-semibold text-[var(--text-primary)]">
              感兴趣的标签
            </h3>
          </div>
          <p className="text-sm text-[var(--text-muted)] mb-4">
            选择你感兴趣的技术标签
          </p>
          <div className="flex flex-wrap gap-2">
            {availableTags.map((tag) => (
              <button
                key={tag}
                onClick={() => toggleTag(tag)}
                className={cn(
                  'px-3 py-1.5 rounded-full text-sm transition-all',
                  'border border-[var(--border-color)]',
                  settings.preferred_tags.includes(tag)
                    ? 'bg-primary-500/20 text-primary-400 border-primary-500/50'
                    : 'bg-[var(--bg-secondary)] text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)]'
                )}
              >
                {tag}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 通知设置 */}
      <div className="card-base p-6">
        <div className="flex items-center gap-2 mb-4">
          <Bell className="h-5 w-5 text-primary-400" />
          <h3 className="text-lg font-semibold text-[var(--text-primary)]">
            通知设置
          </h3>
        </div>

        <div className="space-y-4">
          {/* 邮件通知开关 */}
          <div className="flex items-center justify-between p-4 rounded-lg bg-[var(--bg-secondary)]">
            <div className="flex items-center gap-3">
              <Mail className="h-5 w-5 text-[var(--text-muted)]" />
              <div>
                <p className="text-sm font-medium text-[var(--text-primary)]">
                  邮件通知
                </p>
                <p className="text-xs text-[var(--text-muted)]">
                  接收新机会的邮件提醒
                </p>
              </div>
            </div>
            <button
              onClick={() =>
                setSettings((prev) => ({
                  ...prev,
                  email_notification: !prev.email_notification,
                }))
              }
              className={cn(
                'relative w-12 h-6 rounded-full transition-colors',
                settings.email_notification
                  ? 'bg-primary-500'
                  : 'bg-[var(--bg-tertiary)]'
              )}
            >
              <span
                className={cn(
                  'absolute top-1 w-4 h-4 rounded-full bg-white transition-transform',
                  settings.email_notification ? 'left-7' : 'left-1'
                )}
              />
            </button>
          </div>

          {/* 通知频率 */}
          {settings.email_notification && (
            <div className="p-4 rounded-lg bg-[var(--bg-secondary)]">
              <div className="flex items-center gap-2 mb-3">
                <Clock className="h-5 w-5 text-[var(--text-muted)]" />
                <p className="text-sm font-medium text-[var(--text-primary)]">
                  通知频率
                </p>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {FREQUENCY_OPTIONS.map((option) => (
                  <button
                    key={option.value}
                    onClick={() =>
                      setSettings((prev) => ({
                        ...prev,
                        notification_frequency: option.value as 'daily' | 'weekly',
                      }))
                    }
                    className={cn(
                      'p-3 rounded-lg text-left transition-all',
                      'border border-[var(--border-color)]',
                      settings.notification_frequency === option.value
                        ? 'bg-primary-500/20 border-primary-500/50'
                        : 'hover:bg-[var(--bg-tertiary)]'
                    )}
                  >
                    <p
                      className={cn(
                        'text-sm font-medium',
                        settings.notification_frequency === option.value
                          ? 'text-primary-400'
                          : 'text-[var(--text-primary)]'
                      )}
                    >
                      {option.label}
                    </p>
                    <p className="text-xs text-[var(--text-muted)] mt-1">
                      {option.description}
                    </p>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 保存按钮 */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={saving}
          className={cn(
            'btn-primary inline-flex items-center gap-2 px-6 py-3',
            saving && 'opacity-50 cursor-not-allowed'
          )}
        >
          {saving ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              保存中...
            </>
          ) : (
            <>
              <Save className="h-4 w-4" />
              保存设置
            </>
          )}
        </button>
      </div>
    </div>
  );
}
