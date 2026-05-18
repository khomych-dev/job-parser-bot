from __future__ import annotations

from curl_cffi.requests import AsyncSession

from scrapers.base import BaseScraper


class CurlCffiBaseScraper(BaseScraper):
    """Base scraper that fetches pages with curl_cffi (browser impersonation)."""

    IMPERSONATE = "chrome120"

    def __init__(self, session: AsyncSession | None = None) -> None:
        self._curl_session = session
        self._owns_session = session is None
        self._session = None

    async def __aenter__(self) -> CurlCffiBaseScraper:
        if self._curl_session is None:
            self._curl_session = AsyncSession(impersonate=self.IMPERSONATE)
        return self

    async def __aexit__(self, *args: object) -> None:
        if self._owns_session and self._curl_session is not None:
            await self._curl_session.close()

    @property
    def curl_session(self) -> AsyncSession:
        if self._curl_session is None:
            raise RuntimeError(
                "Curl session is not initialized. Use 'async with scraper'."
            )
        return self._curl_session
