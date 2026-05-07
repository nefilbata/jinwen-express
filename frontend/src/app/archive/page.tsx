'use client';

import useSWR from 'swr';
import { getStats } from '@/lib/api';
import type { StatsOut } from '@/lib/types';

const SOURCE_NAMES: Record<string, string> = {
  journal_rss: '期刊 RSS',
  semantic_scholar: 'Semantic Scholar',
  arxiv: 'arXiv',
  google_scholar: 'Google Scholar',
  cnki: 'CNKI 知网',
};

const SOURCE_COLORS: Record<string, string> = {
  journal_rss: '#b8860b',
  semantic_scholar: '#6b8b7a',
  arxiv: '#b34b4b',
  google_scholar: '#4b7fb3',
  cnki: '#b3772e',
};

export default function ArchivePage() {
  const { data: stats, isLoading } = useSWR<StatsOut>('stats', getStats);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
      <section className="mb-10">
        <h1 className="font-serif font-black text-2xl sm:text-3xl m-0" style={{ color: 'var(--fg)' }}>
          归档
        </h1>
        <p className="mt-2 text-sm m-0" style={{ color: 'var(--fg-muted)' }}>
          论文收录统计
        </p>
      </section>

      {isLoading ? (
        <div className="space-y-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="paper-card">
              <div className="space-y-2">
                <div className="skeleton-line" style={{ width: '60%', height: 20 }} />
                <div className="skeleton-line" style={{ width: '40%' }} />
              </div>
            </div>
          ))}
        </div>
      ) : !stats ? (
        <div className="text-center py-20">
          <p style={{ color: 'var(--fg-muted)' }}>加载失败</p>
        </div>
      ) : (
        <>
          {/* Big numbers */}
          <div className="grid grid-cols-3 gap-4 mb-10">
            <div className="paper-card text-center py-6">
              <div className="font-serif font-black text-4xl" style={{ color: 'var(--bronze)' }}>
                {stats.total_papers}
              </div>
              <div className="text-xs mt-2 uppercase tracking-wider" style={{ color: 'var(--fg-muted)' }}>
                收录论文
              </div>
            </div>
            <div className="paper-card text-center py-6">
              <div className="font-serif font-black text-4xl" style={{ color: 'var(--patina)' }}>
                {stats.recent_days_count}
              </div>
              <div className="text-xs mt-2 uppercase tracking-wider" style={{ color: 'var(--fg-muted)' }}>
                近 7 天新增
              </div>
            </div>
            <div className="paper-card text-center py-6">
              <div className="font-serif font-black text-4xl" style={{ color: 'var(--fg)' }}>
                {Object.keys(stats.papers_by_source).length}
              </div>
              <div className="text-xs mt-2 uppercase tracking-wider" style={{ color: 'var(--fg-muted)' }}>
                活跃信源
              </div>
            </div>
          </div>

          {/* Source breakdown */}
          <h2 className="font-serif font-bold text-lg m-0 mb-4" style={{ color: 'var(--fg)' }}>
            各信源统计
          </h2>
          <div className="space-y-2">
            {Object.entries(stats.papers_by_source)
              .sort(([, a], [, b]) => (b as number) - (a as number))
              .map(([source, count]) => {
                const pct = ((count as number) / stats.total_papers) * 100;
                return (
                  <div key={source} className="paper-card py-4">
                    <div className="flex items-center gap-4">
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium" style={{ color: 'var(--fg)' }}>
                            {SOURCE_NAMES[source] || source}
                          </span>
                          <span className="text-sm font-serif font-bold" style={{ color: 'var(--fg)' }}>
                            {count as number}
                            <span className="text-xs font-normal ml-1" style={{ color: 'var(--fg-muted)' }}>篇</span>
                          </span>
                        </div>
                        <div className="w-full h-1.5 rounded-full" style={{ background: 'var(--divider)' }}>
                          <div
                            className="h-full rounded-full transition-all duration-700"
                            style={{
                              width: `${Math.max(pct, 3)}%`,
                              background: SOURCE_COLORS[source] || 'var(--bronze)',
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
          </div>
        </>
      )}
    </div>
  );
}
