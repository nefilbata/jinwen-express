from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import List


@dataclass
class RawPaper:
    title: str
    authors: List[str] = field(default_factory=list)
    abstract: str | None = None
    journal: str | None = None
    publication_date: date | None = None
    url: str = ""
    source: str = ""
    source_id: str = ""
    keywords_matched: List[str] = field(default_factory=list)
    language: str = "zh"
    doi: str | None = None


class BaseCrawler(ABC):
    source_name: str

    @abstractmethod
    async def search(
        self, keywords: List[str], days_back: int = 1
    ) -> List[RawPaper]:
        ...
