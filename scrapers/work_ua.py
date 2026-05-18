from __future__ import annotations

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from scrapers.base import ScrapedVacancy
from scrapers.curl_base import CurlCffiBaseScraper

_JOB_ID_RE = re.compile(r"/jobs/(\d+)/?")


class WorkUaScraper(CurlCffiBaseScraper):
    platform = "work_ua"
    BASE_URL = "https://www.work.ua/jobs-remote-python/"
    SITE_ORIGIN = "https://www.work.ua"

    def build_search_url(self) -> str:
        return self.BASE_URL

    async def fetch_page(self, url: str) -> str:
        response = await self.curl_session.get(url)
        response.raise_for_status()
        return response.text

    def parse_vacancies(self, html: str) -> list[ScrapedVacancy]:
        soup = BeautifulSoup(html, "html.parser")
        vacancies: list[ScrapedVacancy] = []
        seen_ids: set[str] = set()

        for card in soup.select("div.card.job-link"):
            vacancy = self._parse_job_card(card)
            if vacancy is None or vacancy.external_id in seen_ids:
                continue
            seen_ids.add(vacancy.external_id)
            vacancies.append(vacancy)

        return vacancies

    def _parse_job_card(self, card: Tag) -> ScrapedVacancy | None:
        title_link = card.select_one("h2 a[href*='/jobs/']")
        if title_link is None:
            return None

        href = title_link.get("href", "").strip()
        external_id = self._extract_job_id(href)
        if not external_id:
            saved = card.select_one(".saved-jobs[data-id]")
            if saved is not None:
                external_id = saved.get("data-id", "").strip() or None
        if not external_id:
            return None

        title = title_link.get_text(strip=True)
        if not title:
            return None

        url = urljoin(self.SITE_ORIGIN, href)
        description = self._extract_description(card)

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
    def _extract_description(card: Tag) -> str:
        desc = card.select_one("p.ellipsis")
        if desc is None:
            return ""
        return desc.get_text(" ", strip=True)
