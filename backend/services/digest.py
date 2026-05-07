import logging
from datetime import date

logger = logging.getLogger(__name__)


class DigestService:
    async def build_daily_digest(self, db, target_date: date) -> dict:
        """Build a daily digest grouped by source."""
        import sqlalchemy as sa
        from models import Paper

        stmt = (
            sa.select(Paper)
            .where(Paper.publication_date == target_date, Paper.is_visible == True)
            .order_by(Paper.crawled_at.desc())
        )
        result = await db.execute(stmt)
        papers = result.scalars().all()

        sections = {}
        for p in papers:
            source = p.source
            if source not in sections:
                sections[source] = {
                    "source": source,
                    "source_label": self._source_label(source),
                    "count": 0,
                    "papers": [],
                }
            sections[source]["count"] += 1
            sections[source]["papers"].append(self._paper_to_dict(p))

        return {
            "date": target_date.isoformat(),
            "total_count": len(papers),
            "sections": list(sections.values()),
        }

    def _source_label(self, source: str) -> str:
        labels = {
            "arxiv": "arXiv",
            "google_scholar": "Google Scholar",
            "semantic_scholar": "Semantic Scholar",
            "nssd": "国家哲学社科期刊库",
            "journal_rss": "期刊官网",
            "cnki": "CNKI知网",
        }
        return labels.get(source, source)

    def _paper_to_dict(self, paper) -> dict:
        return {
            "id": paper.id,
            "title": paper.title,
            "authors": paper.authors or [],
            "abstract": paper.abstract,
            "journal": paper.journal,
            "publication_date": (
                paper.publication_date.isoformat()
                if paper.publication_date
                else None
            ),
            "url": paper.url,
            "doi": paper.doi,
            "source": paper.source,
            "language": paper.language,
            "ai_summary": paper.ai_summary,
            "keywords_matched": paper.keywords_matched or [],
        }
