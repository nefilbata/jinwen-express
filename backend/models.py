import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, Date, Boolean, DateTime, Integer, JSON, Float
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Paper(Base):
    __tablename__ = "papers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(Text, nullable=False)
    title_normalized = Column(Text, nullable=False, index=True)
    authors = Column(JSON, default=[])
    abstract = Column(Text, nullable=True)
    journal = Column(String(500), nullable=True)
    publication_date = Column(Date, nullable=True)
    url = Column(String(2000), nullable=True)
    doi = Column(String(500), nullable=True)
    source = Column(String(50), nullable=False, index=True)
    source_id = Column(String(500), nullable=True)
    keywords_matched = Column(JSON, default=[])
    language = Column(String(10), default="zh")
    ai_summary = Column(Text, nullable=True)
    ai_summary_generated_at = Column(DateTime, nullable=True)
    is_visible = Column(Boolean, default=True)
    crawled_at = Column(DateTime, nullable=False)

    class Config:
        unique_constraints = [("source", "source_id")]


class CrawlLog(Base):
    __tablename__ = "crawl_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String(50), nullable=False)
    started_at = Column(DateTime, nullable=False)
    finished_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="running")  # running | success | failed
    papers_found = Column(Integer, default=0)
    papers_new = Column(Integer, default=0)
    keywords_used = Column(JSON, default=[])
    error_message = Column(Text, nullable=True)


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    keyword = Column(String(200), nullable=False, unique=True)
    category = Column(String(50), default="core")
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)
