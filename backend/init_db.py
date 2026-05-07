import logging

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from models import Base, Keyword

logger = logging.getLogger(__name__)

DEFAULT_KEYWORDS = [
    # Core 金文 terms
    ("金文", "core"),
    ("青铜器铭文", "core"),
    ("殷周金文", "core"),
    ("西周金文", "core"),
    # Related paleography
    ("甲骨文", "related"),
    ("古文字", "related"),
    ("铭文考释", "related"),
    ("青铜器", "related"),
    ("金文编", "related"),
    ("金文研究", "related"),
    ("金文释读", "related"),
    ("青铜器断代", "related"),
    # English
    ("bronze inscription China", "english"),
    ("bronze script ancient China", "english"),
    ("Chinese paleography", "english"),
]


async def init_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        for kw, cat in DEFAULT_KEYWORDS:
            existing = await session.execute(
                sa.select(Keyword).where(Keyword.keyword == kw)
            )
            if existing.scalar_one_or_none():
                continue
            session.add(Keyword(keyword=kw, category=cat))

        await session.commit()

    logger.info(f"Database initialized with {len(DEFAULT_KEYWORDS)} keywords")
