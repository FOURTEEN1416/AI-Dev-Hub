/**
 * 底部栏组件
 */

import { Github, ExternalLink } from 'lucide-react';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t border-[var(--border-color)] bg-[var(--bg-secondary)]">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* 品牌信息 */}
          <div>
            <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-3">
              AI Dev Hub
            </h3>
            <p className="text-sm text-[var(--text-muted)] leading-relaxed">
              聚合全球 AI 开发者机会，帮助你发现最新的开发者计划、竞赛、免费额度和社区动态。
            </p>
          </div>

          {/* 数据来源说明 */}
          <div>
            <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-3">
              数据来源
            </h3>
            <ul className="space-y-2 text-sm text-[var(--text-muted)]">
              <li className="flex items-center gap-1.5">
                <ExternalLink className="h-3.5 w-3.5" />
                <span>OpenAI Developer Platform</span>
              </li>
              <li className="flex items-center gap-1.5">
                <ExternalLink className="h-3.5 w-3.5" />
                <span>Kaggle Competitions</span>
              </li>
              <li className="flex items-center gap-1.5">
                <ExternalLink className="h-3.5 w-3.5" />
                <span>GitHub Trending</span>
              </li>
              <li className="flex items-center gap-1.5">
                <ExternalLink className="h-3.5 w-3.5" />
                <span>Hacker News</span>
              </li>
            </ul>
          </div>

          {/* 链接 */}
          <div>
            <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-3">
              链接
            </h3>
            <div className="flex flex-col gap-2">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-sm text-[var(--text-muted)] hover:text-primary-400 transition-colors"
              >
                <Github className="h-4 w-4" />
                <span>GitHub 仓库</span>
              </a>
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-sm text-[var(--text-muted)] hover:text-primary-400 transition-colors"
              >
                <ExternalLink className="h-4 w-4" />
                <span>提交反馈</span>
              </a>
            </div>
          </div>
        </div>

        {/* 版权信息 */}
        <div className="mt-8 pt-6 border-t border-[var(--border-color)] flex flex-col sm:flex-row items-center justify-between gap-2">
          <p className="text-xs text-[var(--text-muted)]">
            &copy; {currentYear} AI Dev Hub. 保留所有权利。
          </p>
          <p className="text-xs text-[var(--text-muted)]">
            数据仅供参考，请以官方平台信息为准
          </p>
        </div>
      </div>
    </footer>
  );
}
