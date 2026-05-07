export interface PaperOut {
  id: string;
  title: string;
  authors: string[];
  abstract: string | null;
  journal: string | null;
  publication_date: string | null;
  url: string | null;
  doi: string | null;
  source: string;
  language: string;
  ai_summary: string | null;
  keywords_matched: string[];
}

export interface DigestSection {
  source: string;
  source_label: string;
  count: number;
  papers: PaperOut[];
}

export interface DailyDigestOut {
  date: string;
  total_count: number;
  sections: DigestSection[];
}

export interface TimelineDay {
  date: string;
  total_count: number;
}

export interface StatsOut {
  total_papers: number;
  papers_by_source: Record<string, number>;
  recent_days_count: number;
}

export interface SearchOut {
  total: number;
  page: number;
  size: number;
  papers: PaperOut[];
}

export const SOURCE_LABELS: Record<string, string> = {
  arxiv: 'arXiv',
  google_scholar: 'Google Scholar',
  semantic_scholar: 'Semantic Scholar',
  nssd: '国家哲学社科期刊库',
  journal_rss: '期刊官网',
  cnki: 'CNKI知网',
};
