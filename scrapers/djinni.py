from __future__ import annotations

import re
from urllib.parse import urlencode, urljoin

import aiohttp
from bs4 import BeautifulSoup, Tag

from scrapers.base import BaseScraper, ScrapedVacancy

_JOB_ID_RE = re.compile(r"/jobs/(\d+)(?:[-/?]|$)")


class DjinniScraper(BaseScraper):
    platform = "djinni"
    BASE_URL = "https://djinni.co/jobs/"
    SITE_ORIGIN = "https://djinni.co"

    REQUEST_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,uk;q=0.8",
    }

    async def __aenter__(self) -> DjinniScraper:
        if self._session is None:
            self._session = aiohttp.ClientSession(headers=self.REQUEST_HEADERS)
        return self

    def build_search_url(self) -> str:
        params = {
            "primary_keyword": "Python",
            "employment": "remote",
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

        for item in soup.select("div.job-item"):
            vacancy = self._parse_job_item(item)
            if vacancy is None or vacancy.external_id in seen_ids:
                continue
            seen_ids.add(vacancy.external_id)
            vacancies.append(vacancy)

        return vacancies

    def _parse_job_item(self, item: Tag) -> ScrapedVacancy | None:
        link = item.select_one("a.job_item__header-link[href*='/jobs/']")
        if link is None:
            link = item.select_one("a[href*='/jobs/']")
        if link is None:
            return None

        href = link.get("href", "").strip()
        external_id = self._extract_job_id(href)
        if not external_id:
            item_id = item.get("id", "")
            id_match = re.search(r"job-item-(\d+)", item_id)
            external_id = id_match.group(1) if id_match else None
        if not external_id:
            return None

        title_el = item.select_one("h2.job-item__position")
        title = title_el.get_text(strip=True) if title_el else link.get_text(strip=True)
        if not title:
            return None

        url = urljoin(self.SITE_ORIGIN, href)
        description = self._extract_description(item)

        return ScrapedVacancy(
            external_id=external_id,
            title=title,
            url=url,
            description=description,
        )

    @classmethod
    def _extract_job_id(cls, href: str) -> str | None:
        match = _JOB_ID_RE.search(href)
        return match.group(1) if match else None

    @staticmethod
    def _extract_description(item: Tag) -> str:
        desc_root = item.select_one("[id^='job-description-']")
        if desc_root is None:
            return ""

        snippet = desc_root.select_one(".js-truncated-text")
        source = snippet if snippet is not None else desc_root
        return source.get_text(" ", strip=True)
