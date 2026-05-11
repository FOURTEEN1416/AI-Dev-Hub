/**
 * 标签云组件
 * 展示热门标签，点击可跳转到对应筛选
 */

'use client';

import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';

/** 模拟热门标签数据 */
const hotTags = [
  { name: 'GPT-4', count: 42 },
  { name: 'LLM', count: 38 },
  { name: '计算机视觉', count: 31 },
  { name: 'NLP', count: 28 },
  { name: '机器学习', count: 25 },
  { name: '深度学习', count: 23 },
  { name: 'API', count: 21 },
  { name: '开源', count: 19 },
  { name: 'Prompt Engineering', count: 17 },
  { name: 'RAG', count: 15 },
  { name: '多模态', count: 14 },
  { name: '代码生成', count: 13 },
  { name: '图像生成', count: 12 },
  { name: '语音识别', count: 11 },
  { name: '强化学习', count: 10 },
  { name: '数据科学', count: 9 },
  { name: 'MLOps', count: 8 },
  { name: '微调', count: 7 },
  { name: 'Embedding', count: 6 },
  { name: 'Agent', count: 5 },
];

export default function TagCloud() {
  const router = useRouter();

  const handleTagClick = (tagName: string) => {
    router.push(`/opportunities?keyword=${encodeURIComponent(tagName)}`);
  };

  return (
    <section className="py-12">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="card-base p-6 sm:p-8">
          <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-6">
            热门标签
          </h2>
          <div className="flex flex-wrap gap-2.5">
            {hotTags.map((tag) => {
              // 根据数量计算大小
              const maxCount = Math.max(...hotTags.map((t) => t.count));
              const minCount = Math.min(...hotTags.map((t) => t.count));
              const ratio = (tag.count - minCount) / (maxCount - minCount);

              return (
                <button
                  key={tag.name}
                  onClick={() => handleTagClick(tag.name)}
                  className={cn(
                    'px-3 py-1.5 rounded-lg border transition-all',
                    'border-[var(--border-color)] text-[var(--text-secondary)]',
                    'hover:border-primary-500/30 hover:text-primary-400 hover:bg-primary-500/5',
                    ratio > 0.7 && 'text-base font-medium',
                    ratio > 0.4 && ratio <= 0.7 && 'text-sm',
                    ratio <= 0.4 && 'text-xs'
                  )}
                >
                  {tag.name}
                  <span className="ml-1.5 text-[var(--text-muted)] text-xs">
                    {tag.count}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
