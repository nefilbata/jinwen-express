import logging
from datetime import date, datetime, timedelta

from crawlers.base import BaseCrawler, RawPaper

logger = logging.getLogger(__name__)


class GoogleScholarCrawler(BaseCrawler):
    source_name = "google_scholar"

    async def search(
        self, keywords: list[str], days_back: int = 1
    ) -> list[RawPaper]:
        try:
            from scholarly import scholarly
        except ImportError:
            logger.warning("scholarly not installed, skipping Google Scholar")
            return []

        papers = []
        cutoff = date.today() - timedelta(days=days_back)

        for keyword in keywords:
            try:
                search_query = scholarly.search_pubs(keyword)
                count = 0
                for result in search_query:
                    if count >= 20:
                        break
                    count += 1

                    pub = result.get("bib", {})

                    title = pub.get("title", "")
                    if not title:
                        continue

                    authors = pub.get("author", [])
                    if isinstance(authors, str):
                        authors = [authors]
                    if not isinstance(authors, list):
                        authors = []

                    abstract = pub.get("abstract", "") or ""

                    pub_year = pub.get("pub_year", "")
                    pub_date = None
                    if pub_year:
                        try:
                            pub_date = date(int(pub_year), 1, 1)
                        except (ValueError, TypeError):
                            pass

                    url = pub.get("pub_url", "") or result.get("url_scholarbib", "") or ""

                    source_id = result.get("author_id", "") + (pub.get("title", "") or "")
                    source_id = source_id[:500] if source_id else title[:500]

                    # Check if match keyword
                    matched = [k for k in keywords if k.lower() in title.lower()
                               or (abstract and k.lower() in abstract.lower())]

                    papers.append(
                        RawPaper(
                            title=title,
                            authors=authors,
                            abstract=abstract,
                            publication_date=pub_date,
                            url=url,
                            source="google_scholar",
                            source_id=source_id,
                            keywords_matched=matched,
                            language=self._detect_lang(title),
                        )
                    )
            except Exception as e:
                logger.error(f"Google Scholar error for keyword '{keyword}': {e}")
                continue

        logger.info(f"Google Scholar: found {len(papers)} papers")
        return papers

    def _detect_lang(self, text: str) -> str:
        for ch in text:
            if "一" <= ch <= "鿿":
                return "zh"
        return "en"
