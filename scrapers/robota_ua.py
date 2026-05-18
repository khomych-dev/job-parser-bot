from __future__ import annotations

import html as html_module
from urllib.parse import urlencode, urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup, Tag

from scrapers.base import ScrapedVacancy
from scrapers.curl_base import CurlCffiBaseScraper


class RobotaUaScraper(CurlCffiBaseScraper):
    platform = "robota_ua"
    BASE_URL = "https://robota.ua/zapros/python/ukraine"
    SITE_ORIGIN = "https://robota.ua"
    API_URL = "https://api.robota.ua/vacancy/search"

    def build_search_url(self) -> str:
        params = {"scheduleIds": "3"}
        return f"{self.BASE_URL}?{urlencode(params)}"

    async def fetch_page(self, url: str) -> str:
        """Fetch listings via public API (SPA shell has no vacancy HTML) and wrap as HTML."""
        response = await self.curl_session.get(
            self.API_URL,
            params={"keyword": "python", "scheduleId": 3},
        )
        response.raise_for_status()
        return self._api_payload_to_html(response.json())

    @staticmethod
    def _api_payload_to_html(payload: dict) -> str:
        parts = ['<div class="robota-search-results">']
        for doc in payload.get("documents", []):
            vacancy_id = doc.get("id")
            if vacancy_id is None:
                continue
            notebook_id = doc.get("notebookId") or 0
            title = html_module.escape(str(doc.get("name", "")))
            description = html_module.escape(str(doc.get("shortDescription", "")))
            vacancy_url = (
                f"{RobotaUaScraper.SITE_ORIGIN}/company{notebook_id}/vacancy{vacancy_id}"
            )
            parts.append(
                f'<article class="vacancy-card" data-id="{vacancy_id}">'
                f'<a class="vacancy-title" href="{vacancy_url}">{title}</a>'
                f'<p class="vacancy-description">{description}</p>'
                f"</article>"
            )
        parts.append("</div>")
        return "".join(parts)

    def parse_vacancies(self, html: str) -> list[ScrapedVacancy]:
        soup = BeautifulSoup(html, "html.parser")
        vacancies: list[ScrapedVacancy] = []
        seen_ids: set[str] = set()

        for card in soup.select("article.vacancy-card"):
            vacancy = self._parse_vacancy_card(card)
            if vacancy is None or vacancy.external_id in seen_ids:
                continue
            seen_ids.add(vacancy.external_id)
            vacancies.append(vacancy)

        return vacancies

    def _parse_vacancy_card(self, card: Tag) -> ScrapedVacancy | None:
        external_id = card.get("data-id", "").strip()
        if not external_id:
            return None

        title_link = card.select_one("a.vacancy-title")
        if title_link is None:
            return None

        title = title_link.get_text(strip=True)
        if not title:
            return None

        href = title_link.get("href", "").strip()
        url = self._normalize_url(urljoin(self.SITE_ORIGIN, href))

        desc_el = card.select_one("p.vacancy-description")
        description = desc_el.get_text(" ", strip=True) if desc_el else ""

        return ScrapedVacancy(
            external_id=external_id,
            title=title,
            url=url,
            description=description,
        )

    @staticmethod
    def _normalize_url(url: str) -> str:
        parsed = urlparse(url)
        return urlunparse(parsed._replace(query="", fragment=""))
