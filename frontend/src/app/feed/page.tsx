'use client';

import { useState } from 'react';
import useSWR from 'swr';
import { getFeed } from '@/lib/api';
import PaperList from '@/components/PaperList';
import SourceFilter from '@/components/SourceFilter';
import SkeletonCard from '@/components/SkeletonCard';
import type { PaperOut } from '@/lib/types';

export default function FeedPage() {
  const [source, setSource] = useState('');
  const [page, setPage] = useState(1);

  const { data, isLoading, error } = useSWR(
    `feed-${source}-${page}`,
    () => getFeed(source, page)
  );

  const papers: PaperOut[] = data?.papers || [];
  const total = data?.total || 0;

  return (
    <div className="max-w-3xl mx-auto px-6 py-8">
      <h1 className="font-serif font-bold text-xl text-ink mb-6">
        全部 AI 动态
      </h1>

      <SourceFilter value={source} onChange={(v) => { setSource(v); setPage(1); }} />

      {isLoading ? (
        <div className="space-y-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonCard key={i} lines={3} />
          ))}
        </div>
      ) : error ? (
        <div className="text-center py-12 text-ink-muted">
          加载失败，请稍后重试
        </div>
      ) : papers.length === 0 ? (
        <div className="text-center py-16">
          <div className="text-5xl mb-4 opacity-30">📜</div>
          <p className="text-ink-muted">暂无数据</p>
        </div>
      ) : (
        <>
          <PaperList papers={papers} />

          {/* Pagination */}
          {total > 30 && (
            <div className="flex items-center justify-center gap-4 mt-8">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="px-4 py-2 text-sm rounded-md border border-bronze-200 text-ink-muted hover:bg-paper-dark disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                上一页
              </button>
              <span className="text-sm text-ink-muted">
                {page} / {Math.ceil(total / 30)}
              </span>
              <button
                onClick={() => setPage(page + 1)}
                disabled={page >= Math.ceil(total / 30)}
                className="px-4 py-2 text-sm rounded-md border border-bronze-200 text-ink-muted hover:bg-paper-dark disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                下一页
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
