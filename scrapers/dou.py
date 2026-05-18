from __future__ import annotations

import re
from urllib.parse import urlencode, urljoin, urlparse, urlunparse

import aiohttp
from bs4 import BeautifulSoup, Tag

from scrapers.base import BaseScraper, ScrapedVacancy

_VACANCY_ID_RE = re.compile(r"/vacancies/(\d+)(?:/|$|\?)")


class DouScraper(BaseScraper):
    platform = "dou"
    BASE_URL = "https://jobs.dou.ua/vacancies/"
    SITE_ORIGIN = "https://jobs.dou.ua"

    REQUEST_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,uk;q=0.8",
    }

    async def __aenter__(self) -> DouScraper:
        if self._session is None:
            self._session = aiohttp.ClientSession(headers=self.REQUEST_HEADERS)
        return self

    def build_search_url(self) -> str:
        params = {
            "category": "Python",
            "remote": "yes",
        }
        return f"{self.BASE_URL}?{urlencode(params)}"

    async def fetch_page(self, url: str) -> str:
        async with self.session.get(url, headers=self.REQUEST_HEADERS) as response:
            response.raise_for_status()
            return await response.text()

    def parse_vacancies(self, html: str) -> list[ScrapedVacancy]:
        soup = BeautifulSoup(html, "html.parser")
        vacancies: list[ScrapedVacancy] = []
        seen_ids: set[str] = set()

        for item in soup.select("li.l-vacancy"):
            vacancy = self._parse_vacancy_item(item)
            if vacancy is None or vacancy.external_id in seen_ids:
                continue
            seen_ids.add(vacancy.external_id)
            vacancies.append(vacancy)

        return vacancies

    def _parse_vacancy_item(self, item: Tag) -> ScrapedVacancy | None:
        link = item.select_one("a.vt[href*='/vacancies/']")
        if link is None:
            link = item.select_one("a[href*='/vacancies/']")
        if link is None:
            return None

        href = link.get("href", "").strip()
        external_id = self._extract_vacancy_id(href)
        if not external_id:
            return None

        title = link.get_text(strip=True)
        if not title:
            return None

        url = self._normalize_url(urljoin(self.SITE_ORIGIN, href))
        description = self._extract_description(item)

        return ScrapedVacancy(
            external_id=external_id,
            title=title,
            url=url,
            description=description,
        )

    @classmethod
    def _extract_vacancy_id(cls, href: str) -> str | None:
        match = _VACANCY_ID_RE.search(href)
        return match.group(1) if match else None

    @staticmethod
    def _extract_description(item: Tag) -> str:
        desc = item.select_one("div.sh-info")
        if desc is None:
            return ""
        return desc.get_text(" ", strip=True)

    @staticmethod
    def _normalize_url(url: str) -> str:
        parsed = urlparse(url)
        return urlunparse(parsed._replace(query="", fragment=""))
