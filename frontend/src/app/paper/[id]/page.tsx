'use client';

import { useParams } from 'next/navigation';
import useSWR from 'swr';
import { getPaper } from '@/lib/api';
import type { PaperOut } from '@/lib/types';
import AIBadge from '@/components/AIBadge';
import PaperMeta from '@/components/PaperMeta';
import SkeletonCard from '@/components/SkeletonCard';
import Link from 'next/link';

export default function PaperDetailPage() {
  const { id } = useParams<{ id: string }>();

  const { data: paper, isLoading, error } = useSWR<PaperOut>(
    id ? `paper-${id}` : null,
    () => getPaper(id)
  );

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto px-6 py-12">
        <SkeletonCard lines={6} />
      </div>
    );
  }

  if (error || !paper) {
    return (
      <div className="max-w-2xl mx-auto px-6 py-12 text-center">
        <p className="text-ink-muted">论文未找到</p>
        <Link href="/" className="text-bronze-600 hover:underline mt-3 inline-block text-sm">
          返回首页
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-6 py-12">
      <Link
        href="/"
        className="text-xs text-ink-muted hover:text-bronze-600 transition-colors mb-6 inline-block"
      >
        ← 返回日报
      </Link>

      <article>
        <h1 className="font-serif font-bold text-xl leading-relaxed text-ink mb-4">
          {paper.title}
        </h1>

        <PaperMeta
          authors={paper.authors}
          journal={paper.journal}
          publicationDate={paper.publication_date}
        />

        {paper.ai_summary && (
          <div className="mt-4 mb-6">
            <AIBadge summary={paper.ai_summary} />
          </div>
        )}

        {paper.abstract && (
          <div className="mt-6">
            <h3 className="text-sm font-medium text-ink mb-2 border-l-2 border-bronze-300 pl-3">
              摘要
            </h3>
            <p className="text-sm text-ink-light leading-relaxed whitespace-pre-line">
              {paper.abstract}
            </p>
          </div>
        )}

        {paper.keywords_matched && paper.keywords_matched.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-6">
            {paper.keywords_matched.map((kw) => (
              <span
                key={kw}
                className="text-xs px-2 py-0.5 rounded bg-paper-dark text-ink-muted"
              >
                {kw}
              </span>
            ))}
          </div>
        )}

        {paper.url && (
          <a
            href={paper.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block mt-6 text-sm text-bronze-600 hover:text-bronze-700 underline"
          >
            查看原文 →
          </a>
        )}
      </article>
    </div>
  );
}
