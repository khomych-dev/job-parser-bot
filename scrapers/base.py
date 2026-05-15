from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import aiohttp

from config import SEARCH_KEYWORDS, TITLE_FILTER_KEYWORDS


@dataclass(frozen=True, slots=True)
class ScrapedVacancy:
    external_id: str
    title: str
    url: str
    description: str = ""


class BaseScraper(ABC):
    platform: str

    def __init__(self, session: aiohttp.ClientSession | None = None) -> None:
        self._session = session
        self._owns_session = session is None

    async def __aenter__(self) -> BaseScraper:
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args: object) -> None:
        if self._owns_session and self._session is not None:
            await self._session.close()

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None:
            raise RuntimeError("Scraper session is not initialized. Use async with scraper.")
        return self._session

    @abstractmethod
    def build_search_url(self) -> str:
        """Return the platform search URL for configured criteria."""

    @abstractmethod
    async def fetch_page(self, url: str) -> str:
        """Download raw HTML for the given URL."""

    @abstractmethod
    def parse_vacancies(self, html: str) -> list[ScrapedVacancy]:
        """Parse vacancy cards from HTML."""

    def matches_keyword_filter(self, vacancy: ScrapedVacancy) -> bool:
        haystack = f"{vacancy.title} {vacancy.description}".casefold()
        return any(keyword.casefold() in haystack for keyword in TITLE_FILTER_KEYWORDS)

    async def scrape(self) -> list[ScrapedVacancy]:
        url = self.build_search_url()
        html = await self.fetch_page(url)
        vacancies = self.parse_vacancies(html)
        return [v for v in vacancies if self.matches_keyword_filter(v)]

    @staticmethod
    def search_terms() -> tuple[str, ...]:
        return SEARCH_KEYWORDS
