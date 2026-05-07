import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import settings

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def setup_scheduler(app):
    @scheduler.scheduled_job(
        CronTrigger(hour=settings.crawl_hour, minute=settings.crawl_minute),
        id="daily_crawl",
    )
    async def daily_crawl():
        logger.info("Daily crawl triggered by scheduler")
        # The actual crawl logic is in the admin endpoint;
        # here we run the same logic as trigger_crawl
        from sqlalchemy.ext.asyncio import AsyncSession
        from database import async_session
        from api import trigger_crawl

        async with async_session() as db:
            try:
                result = await trigger_crawl(
                    api_key=settings.admin_api_key,
                    days_back=settings.days_back,
                    db=db,
                )
                logger.info(
                    f"Daily crawl complete: {result.total_papers} total, "
                    f"{result.new_papers} new"
                )
            except Exception as e:
                logger.error(f"Daily crawl failed: {e}")

    scheduler.start()
    logger.info(
        f"Scheduler started, daily crawl at {settings.crawl_hour:02d}:{settings.crawl_minute:02d}"
    )

    return scheduler
