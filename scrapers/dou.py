from __future__ import annotations

from urllib.parse import urlencode

from scrapers.base import BaseScraper, ScrapedVacancy


class DouScraper(BaseScraper):
    platform = "dou"
    BASE_URL = "https://jobs.dou.ua/vacancies/"

    def build_search_url(self) -> str:
        params = {
            "category": "Python",
            "remote": "",
        }
        return f"{self.BASE_URL}?{urlencode(params)}"

    async def fetch_page(self, url: str) -> str:
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.text()

    def parse_vacancies(self, html: str) -> list[ScrapedVacancy]:
        # TODO: implement BeautifulSoup parsing for DOU job cards
        _ = html
        return []
