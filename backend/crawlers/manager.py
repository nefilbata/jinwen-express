import logging
from datetime import date, datetime

from crawlers.base import BaseCrawler, RawPaper

logger = logging.getLogger(__name__)


class CrawlerManager:
    def __init__(self, crawlers: list[BaseCrawler]):
        self.crawlers = crawlers

    async def run_all(
        self, keywords: list[str], days_back: int = 1
    ) -> list[RawPaper]:
        all_papers: list[RawPaper] = []
        for crawler in self.crawlers:
            try:
                papers = await crawler.search(keywords, days_back)
                all_papers.extend(papers)
                logger.info(
                    f"{crawler.source_name}: found {len(papers)} papers"
                )
            except Exception as e:
                logger.error(f"{crawler.source_name} failed: {e}")
                continue
        return all_papers


class CrawlRecorder:
    def __init__(self, db_session):
        self.db = db_session

    async def record_start(self, source: str, keywords: list[str]) -> str:
        from models import CrawlLog

        log = CrawlLog(
            source=source,
            started_at=datetime.now(),
            status="running",
            keywords_used=keywords,
        )
        self.db.add(log)
        await self.db.commit()
        return log.id

    async def record_success(self, log_id: str, found: int, new: int):
        import sqlalchemy as sa
        from models import CrawlLog

        stmt = (
            sa.update(CrawlLog)
            .where(CrawlLog.id == log_id)
            .values(
                status="success",
                finished_at=datetime.now(),
                papers_found=found,
                papers_new=new,
            )
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def record_failure(self, log_id: str, error: str):
        import sqlalchemy as sa
        from models import CrawlLog

        stmt = (
            sa.update(CrawlLog)
            .where(CrawlLog.id == log_id)
            .values(
                status="failed",
                finished_at=datetime.now(),
                error_message=error,
            )
        )
        await self.db.execute(stmt)
        await self.db.commit()
