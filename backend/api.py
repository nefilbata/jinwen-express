import logging
from datetime import date, datetime, timedelta

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
from models import Keyword, Paper, CrawlLog
from schemas import (
    DailyDigestOut,
    PaperOut,
    SearchOut,
    StatsOut,
    TimelineDay,
    CrawlResultOut,
    CrawlStatusOut,
)
from services.digest import DigestService
from services.dedup import DedupService
from services.ai_summary import AISummaryService
from crawlers.manager import CrawlerManager, CrawlRecorder
from crawlers.arxiv import ArxivCrawler
from crawlers.google_scholar import GoogleScholarCrawler
from crawlers.semantic_scholar import SemanticScholarCrawler
from crawlers.journal_rss import JournalRSSCrawler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")

ADMIN_KEY = settings.admin_api_key


def verify_admin(api_key: str = Query(...)) -> None:
    if api_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")


# ── Public endpoints ──


@router.get("/papers/daily/today", response_model=DailyDigestOut)
async def daily_today(db: AsyncSession = Depends(get_db)):
    today = date.today()
    svc = DigestService()
    return await svc.build_daily_digest(db, today)


@router.get("/papers/daily/{target_date}", response_model=DailyDigestOut)
async def daily_date(target_date: str, db: AsyncSession = Depends(get_db)):
    try:
        d = datetime.strptime(target_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format, use YYYY-MM-DD")

    svc = DigestService()
    return await svc.build_daily_digest(db, d)


@router.get("/papers/{paper_id}", response_model=PaperOut)
async def paper_detail(paper_id: str, db: AsyncSession = Depends(get_db)):
    stmt = sa.select(Paper).where(Paper.id == paper_id)
    result = await db.execute(stmt)
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return PaperOut.model_validate(paper)


@router.get("/timeline", response_model=list[TimelineDay])
async def timeline(days: int = 30, db: AsyncSession = Depends(get_db)):
    cutoff = date.today() - timedelta(days=days)
    stmt = (
        sa.select(
            Paper.publication_date,
            sa.func.count(Paper.id).label("total"),
        )
        .where(Paper.publication_date >= cutoff, Paper.is_visible == True)
        .group_by(Paper.publication_date)
        .order_by(Paper.publication_date.desc())
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [
        TimelineDay(date=row[0].isoformat() if row[0] else "", total_count=row[1])
        for row in rows
    ]


@router.get("/search", response_model=SearchOut)
async def search_papers(
    q: str = "",
    source: str = "",
    page: int = 1,
    size: int = 20,
    db: AsyncSession = Depends(get_db),
):
    stmt = sa.select(Paper).where(Paper.is_visible == True)

    if q:
        stmt = stmt.where(
            sa.or_(
                Paper.title_normalized.contains(q.lower()),
                Paper.abstract.contains(q),
            )
        )
    if source:
        stmt = stmt.where(Paper.source == source)

    # Count
    count_stmt = sa.select(sa.func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # Paginate
    stmt = stmt.order_by(Paper.publication_date.desc()).offset(
        (page - 1) * size
    ).limit(size)
    result = await db.execute(stmt)
    papers = result.scalars().all()

    return SearchOut(
        total=total,
        page=page,
        size=size,
        papers=[PaperOut.model_validate(p) for p in papers],
    )


@router.get("/stats", response_model=StatsOut)
async def stats(db: AsyncSession = Depends(get_db)):
    count_stmt = sa.select(sa.func.count(Paper.id)).where(Paper.is_visible == True)
    total = (await db.execute(count_stmt)).scalar() or 0

    source_stmt = (
        sa.select(Paper.source, sa.func.count(Paper.id))
        .where(Paper.is_visible == True)
        .group_by(Paper.source)
    )
    source_result = await db.execute(source_stmt)
    by_source = {row[0]: row[1] for row in source_result.all()}

    recent_stmt = sa.select(sa.func.count(Paper.id)).where(
        Paper.publication_date >= date.today() - timedelta(days=7),
        Paper.is_visible == True,
    )
    recent = (await db.execute(recent_stmt)).scalar() or 0

    return StatsOut(
        total_papers=total,
        papers_by_source=by_source,
        recent_days_count=recent,
    )


# ── Multi-view endpoints ──


@router.get("/latest", response_model=SearchOut)
async def latest_papers(
    source: str = "",
    page: int = 1,
    size: int = 30,
    db: AsyncSession = Depends(get_db),
):
    """Latest papers from the last 60 days, ordered by publication date."""
    cutoff = date.today() - timedelta(days=60)
    stmt = sa.select(Paper).where(
        Paper.is_visible == True,
        Paper.publication_date >= cutoff,
        Paper.keywords_matched != None,
    )
    if source:
        stmt = stmt.where(Paper.source == source)

    count_stmt = sa.select(sa.func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.order_by(Paper.publication_date.desc()).offset(
        (page - 1) * size
    ).limit(size)
    result = await db.execute(stmt)
    papers = result.scalars().all()

    return SearchOut(
        total=total,
        page=page,
        size=size,
        papers=[PaperOut.model_validate(p) for p in papers],
    )


@router.get("/feed", response_model=SearchOut)
async def all_feed(
    source: str = "",
    page: int = 1,
    size: int = 30,
    days: int = 30,
    db: AsyncSession = Depends(get_db),
):
    """Flat timeline of all recent papers (like AIHOT 全部AI动态)."""
    cutoff = date.today() - timedelta(days=days)
    stmt = sa.select(Paper).where(
        Paper.is_visible == True, Paper.publication_date >= cutoff
    )
    if source:
        stmt = stmt.where(Paper.source == source)

    count_stmt = sa.select(sa.func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.order_by(Paper.crawled_at.desc()).offset(
        (page - 1) * size
    ).limit(size)
    result = await db.execute(stmt)
    papers = result.scalars().all()

    return SearchOut(
        total=total,
        page=page,
        size=size,
        papers=[PaperOut.model_validate(p) for p in papers],
    )


@router.get("/featured", response_model=SearchOut)
async def featured(
    page: int = 1,
    size: int = 20,
    days: int = 30,
    db: AsyncSession = Depends(get_db),
):
    """Featured papers: those with AI summaries (like AIHOT 精选)."""
    cutoff = date.today() - timedelta(days=days)
    stmt = sa.select(Paper).where(
        Paper.is_visible == True,
        Paper.publication_date >= cutoff,
        Paper.ai_summary != None,
    )

    count_stmt = sa.select(sa.func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.order_by(Paper.crawled_at.desc()).offset(
        (page - 1) * size
    ).limit(size)
    result = await db.execute(stmt)
    papers = result.scalars().all()

    return SearchOut(
        total=total,
        page=page,
        size=size,
        papers=[PaperOut.model_validate(p) for p in papers],
    )


# ── Admin endpoints ──


@router.post("/admin/crawl", response_model=CrawlResultOut)
async def trigger_crawl(
    api_key: str = Query(...),
    days_back: int = 3,
    db: AsyncSession = Depends(get_db),
):
    verify_admin(api_key)

    # Load keywords
    kw_result = await db.execute(
        sa.select(Keyword.keyword).where(Keyword.is_active == True)
    )
    keywords = [row[0] for row in kw_result.all()]

    if not keywords:
        raise HTTPException(status_code=400, detail="No keywords configured")

    # Init crawlers
    crawlers = [
        ArxivCrawler(),
        GoogleScholarCrawler(),
        SemanticScholarCrawler(),
        JournalRSSCrawler(),
    ]

    manager = CrawlerManager(crawlers)
    new_papers = await manager.run_all(keywords, days_back)

    # Dedup
    dedup_svc = DedupService()
    unique = dedup_svc.deduplicate(new_papers)

    # Filter: only keep papers that matched at least one keyword
    filtered = [p for p in unique if p.keywords_matched]
    logger.info(f"Keyword filter: {len(unique)} -> {len(filtered)} papers")
    unique = filtered

    # Store in DB
    recorder = CrawlRecorder(db)
    stored = 0
    for rp in unique:
        try:
            existing = await db.execute(
                sa.select(Paper).where(
                    Paper.source == rp.source,
                    Paper.source_id == rp.source_id,
                )
            )
            if existing.scalar_one_or_none():
                continue

            p = Paper(
                title=rp.title,
                title_normalized=rp.title.lower().strip(),
                authors=rp.authors,
                abstract=rp.abstract,
                journal=rp.journal,
                publication_date=rp.publication_date or date.today(),
                url=rp.url,
                doi=rp.doi,
                source=rp.source,
                source_id=rp.source_id,
                keywords_matched=rp.keywords_matched,
                language=rp.language,
                crawled_at=datetime.now(),
            )
            db.add(p)
            stored += 1
        except Exception as e:
            logger.error(f"Error storing paper '{rp.title[:60]}': {e}")

    await db.commit()

    # AI summaries for new papers
    ai_svc = AISummaryService(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        model=settings.openai_model,
    )

    paper_result = await db.execute(
        sa.select(Paper).where(Paper.ai_summary == None).limit(50)
    )
    uns_summarized = paper_result.scalars().all()

    summed = 0
    for p in uns_summarized:
        summary = await ai_svc.generate_summary(
            p.title, p.abstract or ""
        )
        if summary:
            p.ai_summary = summary
            p.ai_summary_generated_at = datetime.now()
            summed += 1

    await db.commit()

    return CrawlResultOut(
        status="success",
        total_papers=len(unique),
        new_papers=stored,
        sources=[
            CrawlStatusOut(source=c.source_name, papers_found=0)
            for c in crawlers
        ],
    )


@router.get("/admin/sources", response_model=list[CrawlStatusOut])
async def source_status(
    api_key: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    verify_admin(api_key)
    subq = (
        sa.select(
            CrawlLog.source,
            sa.func.max(CrawlLog.finished_at).label("last_run"),
        )
        .group_by(CrawlLog.source)
        .subquery()
    )

    stmt = (
        sa.select(
            CrawlLog.source,
            CrawlLog.status,
            CrawlLog.finished_at,
            CrawlLog.papers_found,
        )
        .join(subq, CrawlLog.source == subq.c.source)
        .where(CrawlLog.finished_at == subq.c.last_run)
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [
        CrawlStatusOut(
            source=row[0],
            last_status=row[1],
            last_run=row[2].isoformat() if row[2] else None,
            papers_found=row[3],
        )
        for row in rows
    ]
