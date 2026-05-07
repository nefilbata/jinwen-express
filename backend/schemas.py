from datetime import date, datetime
from typing import List, Any

from pydantic import BaseModel, field_validator


class PaperOut(BaseModel):
    id: str
    title: str
    authors: list[str] = []
    abstract: str | None = None
    journal: str | None = None
    publication_date: str | None = None
    url: str | None = None
    doi: str | None = None
    source: str
    language: str = "zh"
    ai_summary: str | None = None
    keywords_matched: list[str] = []

    class Config:
        from_attributes = True

    @field_validator("publication_date", mode="before")
    @classmethod
    def coerce_date(cls, v: Any) -> str | None:
        if v is None:
            return None
        if isinstance(v, date):
            return v.isoformat()
        return str(v) if v else None


class DigestSection(BaseModel):
    source: str
    source_label: str
    count: int
    papers: list[PaperOut]


class DailyDigestOut(BaseModel):
    date: str
    total_count: int
    sections: list[DigestSection]


class TimelineDay(BaseModel):
    date: str
    total_count: int


class CrawlStatusOut(BaseModel):
    source: str
    last_run: str | None = None
    last_status: str | None = None
    papers_found: int = 0


class CrawlResultOut(BaseModel):
    status: str
    total_papers: int
    new_papers: int
    sources: list[CrawlStatusOut]


class SearchOut(BaseModel):
    total: int
    page: int
    size: int
    papers: list[PaperOut]


class StatsOut(BaseModel):
    total_papers: int
    papers_by_source: dict[str, int]
    recent_days_count: int
