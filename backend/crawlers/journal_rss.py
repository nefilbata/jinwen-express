"""
Journal RSS + website crawler.

Reads journal sources from journals.txt (one per line: name | url).
- If URL contains 'rss' or ends in '.xml', treats as RSS feed (parsed via feedparser).
- Otherwise scrapes the page for article titles matching 金文/古文字 keywords.
"""

import logging
import re
import os
from datetime import date, datetime, timedelta
from urllib.parse import urljoin

import httpx
import feedparser
from bs4 import BeautifulSoup

from crawlers.base import BaseCrawler, RawPaper

logger = logging.getLogger(__name__)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "journals.txt")


def load_journals() -> list[dict]:
    """Load journal sources from config file."""
    sources = []
    path = CONFIG_PATH
    if not os.path.exists(path):
        logger.warning(f"journals.txt not found at {path}")
        return sources

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("|", 1)
            if len(parts) == 2:
                name = parts[0].strip()
                url = parts[1].strip()
                is_rss = "rss" in url.lower() or url.endswith(".xml")
                sources.append({"name": name, "url": url, "is_rss": is_rss})

    return sources


class JournalRSSCrawler(BaseCrawler):
    source_name = "journal_rss"

    async def search(
        self, keywords: list[str], days_back: int = 30
    ) -> list[RawPaper]:
        sources = load_journals()
        if not sources:
            logger.info("No journal sources configured in journals.txt")
            return []

        papers = []
        for src in sources:
            try:
                if src["is_rss"]:
                    found = await self._fetch_rss(src, keywords, days_back)
                else:
                    found = await self._scrape_site(src, keywords)
                papers.extend(found)
                logger.info(f"  {src['name']}: {len(found)} papers")
            except Exception as e:
                logger.warning(f"  {src['name']}: {e}")

        return papers

    async def _fetch_rss(
        self, src: dict, keywords: list[str], days_back: int
    ) -> list[RawPaper]:
        papers = []

        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            resp = await client.get(
                src["url"],
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/130.0.0.0 Safari/537.36"
                    ),
                },
            )
            if resp.status_code != 200:
                return papers

            feed = feedparser.parse(resp.text)
            for entry in feed.entries:
                title = entry.get("title", "").strip()
                if not title:
                    continue

                abstract = entry.get("summary", "") or entry.get("description", "")
                abstract = re.sub(r"<[^>]+>", " ", abstract)
                abstract = re.sub(r"\s+", " ", abstract).strip()

                link = entry.get("link", "")

                pub_date = None
                for field in ("published_parsed", "updated_parsed"):
                    tp = entry.get(field)
                    if tp:
                        try:
                            pub_date = date(tp[0], tp[1], tp[2])
                        except Exception:
                            pass

                matched = [k for k in keywords if k.lower() in title.lower()]

                if pub_date or matched:
                    papers.append(
                        RawPaper(
                            title=title,
                            abstract=abstract[:2000],
                            journal=src["name"],
                            publication_date=pub_date or date.today(),
                            url=link,
                            source="journal_rss",
                            source_id=link[:500] if link else title[:500],
                            language="zh",
                            keywords_matched=matched,
                        )
                    )

        return papers

    async def _scrape_site(
        self, src: dict, keywords: list[str]
    ) -> list[RawPaper]:
        papers = []

        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            resp = await client.get(
                src["url"],
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/130.0.0.0 Safari/537.36"
                    ),
                },
            )
            if resp.status_code != 200:
                return papers

            soup = BeautifulSoup(resp.text, "html.parser")

            for a in soup.find_all("a", href=True):
                text = a.get_text(strip=True)
                href = a["href"]
                full_url = urljoin(src["url"], href)

                if not self._is_relevant(text, keywords):
                    continue

                matched = [k for k in keywords if k.lower() in text.lower()]

                papers.append(
                    RawPaper(
                        title=text,
                        authors=[],
                        abstract="",
                        journal=src["name"],
                        publication_date=date.today(),
                        url=full_url,
                        source="journal_rss",
                        source_id=full_url[:500],
                        language="zh",
                        keywords_matched=matched,
                    )
                )

        return papers

    def _is_relevant(self, text: str, keywords: list[str]) -> bool:
        skip = [
            "首页", "English", "清华官网", "中心概况", "新闻动态",
            "通知公告", "师资队伍", "招生招聘", "友情链接",
            "了解更多", "了解详细", "More", "上页", "下页",
            "Copyright", "地址", "电话", "登录", "注册",
            "返回", "上一篇", "下一篇", "点击", "下载",
            "投稿", "招聘", "公告", "博士后", "menu", "nav",
            "footer", "header", "search", "附件",
        ]
        for s in skip:
            if s.lower() in text.lower():
                return False

        if len(text) < 5 or len(text) > 200:
            return False

        scholarly = [
            "：", "——", "―", ":", "—",
            "考", "释", "研究", "论", "说", "读", "探", "析", "编",
            "金文", "铭文", "青铜", "甲骨", "古文字", "简帛",
            "出土", "战国", "西周", "殷周", "商周", "先秦",
            "文字", "文献", "竹简", "帛书", "铜器", "彝器",
            "考释", "释读", "断代", "铭", "鼎", "簋", "编钟",
            "paleography", "bronze", "inscription", "manuscript",
        ]
        return any(ind in text for ind in scholarly)
