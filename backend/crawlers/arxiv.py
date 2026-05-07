import logging
from datetime import date, datetime, timedelta

import httpx

from crawlers.base import BaseCrawler, RawPaper

logger = logging.getLogger(__name__)

ARXIV_SEARCH_URL = "https://export.arxiv.org/api/query"


def _build_query(keywords: list[str]) -> str:
    terms = " OR ".join(f'all:"{k}"' for k in keywords)
    return f"({terms})"


def _parse_arxiv_date(date_str: str) -> date | None:
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


class ArxivCrawler(BaseCrawler):
    source_name = "arxiv"

    async def search(
        self, keywords: list[str], days_back: int = 1
    ) -> list[RawPaper]:
        query = _build_query(keywords)
        params = {
            "search_query": query,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": "30",
            "start": "0",
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(ARXIV_SEARCH_URL, params=params)
            resp.raise_for_status()

        import xml.etree.ElementTree as ET

        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom",
        }
        root = ET.fromstring(resp.text)
        entries = root.findall("atom:entry", ns)

        papers = []
        cutoff = date.today() - timedelta(days=days_back)

        for entry in entries:
            title_el = entry.find("atom:title", ns)
            title = title_el.text.strip().replace("\n", " ") if title_el is not None else ""

            published_el = entry.find("atom:published", ns)
            pub_date = None
            if published_el is not None and published_el.text:
                pub_date = _parse_arxiv_date(published_el.text)

            if pub_date and pub_date < cutoff:
                continue

            authors = [
                a.find("atom:name", ns).text or ""
                for a in entry.findall("atom:author", ns)
            ]

            summary_el = entry.find("atom:summary", ns)
            abstract = summary_el.text.strip().replace("\n", " ") if summary_el is not None else ""

            id_el = entry.find("atom:id", ns)
            arxiv_id = id_el.text.strip() if id_el is not None else ""

            link_el = entry.find("atom:link[@href]", ns)
            url = link_el.get("href", "") if link_el is not None else ""

            matched = [k for k in keywords if k.lower() in title.lower() or k.lower() in abstract.lower()]

            papers.append(
                RawPaper(
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    publication_date=pub_date,
                    url=url,
                    source="arxiv",
                    source_id=arxiv_id,
                    keywords_matched=matched,
                    language="en",
                )
            )

        logger.info(f"arXiv: found {len(papers)} papers for {len(keywords)} keywords")
        return papers
