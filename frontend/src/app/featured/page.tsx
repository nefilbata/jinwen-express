'use client';

import { useState } from 'react';
import useSWR from 'swr';
import { getFeatured } from '@/lib/api';
import type { PaperOut, SearchOut } from '@/lib/types';
import { formatDate, cn } from '@/lib/utils';

const DELAYS = ['fade-in-1','fade-in-2','fade-in-3','fade-in-4','fade-in-5','fade-in-6','fade-in-7','fade-in-8'];

export default function FeaturedPage() {
  const [page, setPage] = useState(1);

  const { data, isLoading } = useSWR<SearchOut>(
    `featured-${page}`,
    () => getFeatured(page),
    { keepPreviousData: true }
  );

  const papers = data?.papers || [];
  const total = data?.total || 0;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
      <section className="mb-10">
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mb-2">
          <div>
            <h1 className="font-serif font-black text-2xl sm:text-3xl m-0" style={{ color: 'var(--fg)' }}>
              精选
            </h1>
            <p className="mt-2 text-sm m-0" style={{ color: 'var(--fg-muted)' }}>
              AI 自动解读的高价值论文
            </p>
          </div>
          <span className="text-xs px-3 py-1.5 rounded-full"
            style={{ background: 'var(--patina-bg)', color: 'var(--patina)' }}>
            AI 精选 · {total} 篇
          </span>
        </div>
      </section>

      {isLoading ? (
        <div className="space-y-4">
          {Array.from({ length: 5 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : papers.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-6xl mb-6 opacity-25">🏺</div>
          <h2 className="font-serif text-lg m-0 mb-2" style={{ color: 'var(--fg)' }}>暂无精选</h2>
          <p className="text-sm m-0" style={{ color: 'var(--fg-muted)' }}>
            配置 AI API Key 后自动生成论文解读
          </p>
        </div>
      ) : (
        <>
          <div className="space-y-3">
            {papers.map((paper, i) => (
              <FeaturedCard key={paper.id} paper={paper} className={DELAYS[i % DELAYS.length]} />
            ))}
          </div>

          {total > 20 && (
            <div className="flex items-center justify-center gap-3 mt-10">
              <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}
                className="filter-pill disabled:opacity-30 disabled:cursor-not-allowed">← 前页</button>
              <span className="text-xs" style={{ color: 'var(--fg-muted)' }}>{page} / {Math.ceil(total / 20)}</span>
              <button onClick={() => setPage(p => p + 1)} disabled={page >= Math.ceil(total / 20)}
                className="filter-pill disabled:opacity-30 disabled:cursor-not-allowed">后页 →</button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function FeaturedCard({ paper, className }: { paper: PaperOut; className: string }) {
  return (
    <article className={cn('paper-card fade-in', className)}>
      <div className="flex items-start gap-4">
        <div className="hidden sm:flex flex-col items-center pt-1.5 shrink-0" style={{ width: 32 }}>
          <div className="timeline-dot" style={{ background: 'var(--patina)' }} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span className="text-xs">🔬</span>
            {paper.journal && <span className="journal-tag">{paper.journal}</span>}
            <span className="text-xs" style={{ color: 'var(--fg-muted)' }}>{formatDate(paper.publication_date)}</span>
          </div>
          <h3 className="font-serif font-semibold text-[15px] leading-relaxed m-0 mb-1.5">
            {paper.url ? (
              <a href={paper.url} target="_blank" rel="noopener noreferrer" className="hover:underline"
                style={{ color: 'var(--fg)', textDecorationColor: 'var(--bronze-light)', textUnderlineOffset: '3px' }}>
                {paper.title}
              </a>
            ) : paper.title}
          </h3>
          {paper.authors && paper.authors.length > 0 && (
            <p className="text-xs m-0 mb-2" style={{ color: 'var(--fg-muted)' }}>
              {paper.authors.slice(0, 3).join('、')}{paper.authors.length > 3 ? ' 等' : ''}
            </p>
          )}
          {paper.ai_summary && (
            <div className="mb-2">
              <span className="ai-badge">{paper.ai_summary}</span>
            </div>
          )}
          {paper.abstract && (
            <p className="text-[13px] leading-relaxed m-0 line-clamp-3" style={{ color: 'var(--fg-light)' }}>
              {paper.abstract}
            </p>
          )}
        </div>
      </div>
    </article>
  );
}

function SkeletonCard() {
  return (
    <div className="paper-card">
      <div className="flex items-start gap-4">
        <div className="hidden sm:flex flex-col items-center pt-1.5 shrink-0" style={{ width: 32 }}>
          <div className="skeleton-line" style={{ width: 8, height: 8, borderRadius: '50%' }} />
        </div>
        <div className="flex-1 space-y-2.5">
          <div className="skeleton-line" style={{ width: '35%' }} />
          <div className="skeleton-line" style={{ width: '80%', height: 18 }} />
          <div className="skeleton-line" style={{ width: '25%' }} />
          <div className="skeleton-line" style={{ width: '90%' }} />
        </div>
      </div>
    </div>
  );
}
