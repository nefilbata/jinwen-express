import logging
from datetime import date, datetime, timedelta
import asyncio

import httpx

from crawlers.base import BaseCrawler, RawPaper

logger = logging.getLogger(__name__)

SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"


class SemanticScholarCrawler(BaseCrawler):
    source_name = "semantic_scholar"

    async def search(
        self, keywords: list[str], days_back: int = 1
    ) -> list[RawPaper]:
        papers = []

        async with httpx.AsyncClient(timeout=30) as client:
            for keyword in keywords:
                try:
                    params = {
                        "query": keyword,
                        "limit": "20",
                        "fields": "title,authors,abstract,publicationDate,url,externalIds,journal",
                    }
                    resp = await client.get(SEMANTIC_SCHOLAR_URL, params=params)
                    resp.raise_for_status()
                    data = resp.json()

                    for item in data.get("data", []):
                        pub_date_str = item.get("publicationDate", "")
                        pub_date = None
                        if pub_date_str:
                            try:
                                pub_date = datetime.strptime(
                                    pub_date_str, "%Y-%m-%d"
                                ).date()
                            except ValueError:
                                continue

                        cutoff = date.today() - timedelta(days=days_back)
                        if pub_date and pub_date < cutoff:
                            continue

                        title = item.get("title", "")
                        abstract = item.get("abstract", "") or ""

                        authors = [
                            a.get("name", "") for a in item.get("authors", [])
                        ]

                        ext_ids = item.get("externalIds", {}) or {}
                        doi = ext_ids.get("DOI", "")

                        source_id = item.get("paperId", "") or title

                        matched = [
                            k
                            for k in keywords
                            if k.lower() in title.lower()
                            or k.lower() in abstract.lower()
                        ]

                        journal = ""
                        jinfo = item.get("journal")
                        if jinfo:
                            journal = jinfo.get("name", "") or ""

                        papers.append(
                            RawPaper(
                                title=title,
                                authors=authors,
                                abstract=abstract,
                                journal=journal,
                                publication_date=pub_date,
                                url=item.get("url", ""),
                                doi=doi,
                                source="semantic_scholar",
                                source_id=source_id,
                                keywords_matched=matched,
                                language=self._detect_lang(title),
                            )
                        )
                except Exception as e:
                    logger.error(
                        f"Semantic Scholar error for '{keyword}': {e}"
                    )
                    continue
                await asyncio.sleep(0.5)  # avoid 429 rate limiting

        logger.info(f"Semantic Scholar: found {len(papers)} papers")
        return papers

    def _detect_lang(self, text: str) -> str:
        for ch in text:
            if "一" <= ch <= "鿿":
                return "zh"
        return "en"
