'use client';

import { useState } from 'react';
import useSWR from 'swr';
import { getLatest, getStats } from '@/lib/api';
import type { PaperOut, SearchOut, StatsOut } from '@/lib/types';
import { formatDate, cn } from '@/lib/utils';

/* ── helpers ── */

const SOURCE_META: Record<string, { icon: string; label: string }> = {
  journal_rss: { icon: '📰', label: '期刊' },
  semantic_scholar: { icon: '🔬', label: 'Semantic Scholar' },
  arxiv: { icon: '📄', label: 'arXiv' },
  google_scholar: { icon: '🎓', label: 'Google Scholar' },
  cnki: { icon: '📚', label: 'CNKI' },
};

const DELAYS = ['fade-in-1','fade-in-2','fade-in-3','fade-in-4','fade-in-5','fade-in-6','fade-in-7','fade-in-8'];

/* ── Page ── */

export default function LatestPage() {
  const [source, setSource] = useState('');
  const [page, setPage] = useState(1);

  const { data, isLoading } = useSWR<SearchOut>(
    `latest-${source}-${page}`,
    () => getLatest(source, page),
    { keepPreviousData: true }
  );

  const { data: stats } = useSWR<StatsOut>('stats', getStats);

  const papers = data?.papers || [];
  const total = data?.total || 0;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
      {/* ── Hero ── */}
      <section className="mb-10">
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mb-6">
          <div>
            <h1 className="font-serif font-black text-2xl sm:text-3xl m-0" style={{ color: 'var(--fg)' }}>
              最新论文
            </h1>
            <p className="mt-2 text-sm m-0" style={{ color: 'var(--fg-muted)' }}>
              近 60 天金文与古文字研究学术论文
            </p>
          </div>
          {stats && (
            <div className="flex items-center gap-4 text-xs" style={{ color: 'var(--fg-muted)' }}>
              <StatBox value={stats.total_papers} label="收录" />
              <StatBox value={Object.keys(stats.papers_by_source).length} label="信源" />
              <StatBox value={stats.recent_days_count} label="近7天" />
            </div>
          )}
        </div>

        {/* Filter */}
        <FilterBar value={source} onChange={(v) => { setSource(v); setPage(1); }} />
      </section>

      {/* ── Content ── */}
      {isLoading ? (
        <div className="space-y-4">
          {Array.from({ length: 7 }).map((_, i) => (
            <SkeletonPaperCard key={i} />
          ))}
        </div>
      ) : papers.length === 0 ? (
        <EmptyState source={source} />
      ) : (
        <>
          <div className="space-y-3">
            {papers.map((paper, i) => (
              <PaperCard
                key={paper.id}
                paper={paper}
                className={DELAYS[i % DELAYS.length]}
              />
            ))}
          </div>

          <Pagination page={page} total={total} size={30} onChange={setPage} />
        </>
      )}
    </div>
  );
}

/* ── Sub-components ── */

function StatBox({ value, label }: { value: number; label: string }) {
  return (
    <div className="text-center px-3 py-2 rounded-md" style={{ background: 'var(--bg-card)', border: '1px solid var(--divider)' }}>
      <div className="font-serif font-bold text-lg" style={{ color: 'var(--bronze)' }}>{value}</div>
      <div className="text-[10px] uppercase tracking-wider">{label}</div>
    </div>
  );
}

function FilterBar({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  const sources = [
    { v: '', label: '全部' },
    { v: 'journal_rss', label: '期刊' },
    { v: 'semantic_scholar', label: 'Semantic Scholar' },
    { v: 'arxiv', label: 'arXiv' },
    { v: 'google_scholar', label: 'Google Scholar' },
  ];

  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-xs mr-1" style={{ color: 'var(--fg-muted)' }}>信源</span>
      {sources.map((s) => (
        <button
          key={s.v}
          onClick={() => onChange(s.v)}
          className={cn('filter-pill', value === s.v && 'active')}
        >
          {s.label}
        </button>
      ))}
    </div>
  );
}

function PaperCard({ paper, className }: { paper: PaperOut; className: string }) {
  const meta = SOURCE_META[paper.source] || { icon: '📄', label: paper.source };

  return (
    <article className={cn('paper-card fade-in', className)}>
      <div className="flex items-start gap-4">
        {/* Timeline indicator */}
        <div className="hidden sm:flex flex-col items-center pt-1.5 shrink-0" style={{ width: 32 }}>
          <div className="timeline-dot" />
        </div>

        <div className="flex-1 min-w-0">
          {/* Meta line */}
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span className="text-xs" role="img" aria-label={meta.label}>{meta.icon}</span>
            {paper.journal && <span className="journal-tag">{paper.journal}</span>}
            <span className="text-xs" style={{ color: 'var(--fg-muted)' }}>
              {formatDate(paper.publication_date)}
            </span>
          </div>

          {/* Title */}
          <h3 className="font-serif font-semibold text-[15px] leading-relaxed m-0 mb-1.5">
            {paper.url ? (
              <a
                href={paper.url}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:underline"
                style={{ color: 'var(--fg)', textDecorationColor: 'var(--bronze-light)', textUnderlineOffset: '3px' }}
              >
                {paper.title}
              </a>
            ) : (
              paper.title
            )}
          </h3>

          {/* Authors */}
          {paper.authors && paper.authors.length > 0 && (
            <p className="text-xs m-0 mb-2" style={{ color: 'var(--fg-muted)' }}>
              {paper.authors.slice(0, 3).join('、')}
              {paper.authors.length > 3 && ' 等'}
            </p>
          )}

          {/* AI summary */}
          {paper.ai_summary && (
            <div className="mb-2">
              <span className="ai-badge">{paper.ai_summary}</span>
            </div>
          )}

          {/* Abstract */}
          {paper.abstract && (
            <p
              className="text-[13px] leading-relaxed m-0 line-clamp-2"
              style={{ color: 'var(--fg-light)' }}
            >
              {paper.abstract}
            </p>
          )}
        </div>
      </div>
    </article>
  );
}

function SkeletonPaperCard() {
  return (
    <div className="paper-card">
      <div className="flex items-start gap-4">
        <div className="hidden sm:flex flex-col items-center pt-1.5 shrink-0" style={{ width: 32 }}>
          <div className="skeleton-line" style={{ width: 8, height: 8, borderRadius: '50%' }} />
        </div>
        <div className="flex-1 space-y-2.5">
          <div className="skeleton-line" style={{ width: '40%' }} />
          <div className="skeleton-line" style={{ width: '85%', height: 18 }} />
          <div className="skeleton-line" style={{ width: '30%' }} />
          <div className="skeleton-line" style={{ width: '95%' }} />
        </div>
      </div>
    </div>
  );
}

function EmptyState({ source }: { source: string }) {
  return (
    <div className="text-center py-20">
      <div className="text-6xl mb-6 opacity-25">🏺</div>
      <h2 className="font-serif text-lg m-0 mb-2" style={{ color: 'var(--fg)' }}>
        {source ? '该信源暂无论文' : '暂无论文'}
      </h2>
      <p className="text-sm m-0" style={{ color: 'var(--fg-muted)' }}>
        {source
          ? '试试切换为「全部」信源查看其他来源的论文'
          : '学术论文发表有周期性，系统会在新论文上线时自动收录'}
      </p>
    </div>
  );
}

function Pagination({
  page, total, size, onChange,
}: { page: number; total: number; size: number; onChange: (p: number) => void }) {
  const totalPages = Math.ceil(total / size);
  if (totalPages <= 1) return null;

  return (
    <div className="flex items-center justify-center gap-3 mt-10">
      <button
        onClick={() => onChange(page - 1)}
        disabled={page === 1}
        className="filter-pill disabled:opacity-30 disabled:cursor-not-allowed"
      >
        ← 前页
      </button>
      <span className="text-xs" style={{ color: 'var(--fg-muted)' }}>
        {page} / {totalPages}
      </span>
      <button
        onClick={() => onChange(page + 1)}
        disabled={page >= totalPages}
        className="filter-pill disabled:opacity-30 disabled:cursor-not-allowed"
      >
        后页 →
      </button>
    </div>
  );
}
