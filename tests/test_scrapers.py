from __future__ import annotations

import pytest
from sqlalchemy import select

from database.models import Vacancy
from scrapers import DjinniScraper, DouScraper
from scrapers.base import ScrapedVacancy


@pytest.mark.asyncio
async def test_djinni_scraper_stub_returns_empty_list() -> None:
    scraper = DjinniScraper()
    assert scraper.parse_vacancies("") == []


@pytest.mark.asyncio
async def test_dou_scraper_stub_returns_empty_list() -> None:
    scraper = DouScraper()
    assert scraper.parse_vacancies("") == []


def test_keyword_filter_matches_junior_in_title() -> None:
    scraper = DjinniScraper()
    vacancy = ScrapedVacancy(
        external_id="1",
        title="Python Junior Developer",
        url="https://example.com/1",
        description="Remote work",
    )
    assert scraper.matches_keyword_filter(vacancy) is True


def test_keyword_filter_rejects_without_keywords() -> None:
    scraper = DouScraper()
    vacancy = ScrapedVacancy(
        external_id="2",
        title="Senior Python Developer",
        url="https://example.com/2",
        description="Remote work",
    )
    assert scraper.matches_keyword_filter(vacancy) is False


@pytest.mark.asyncio
async def test_vacancy_persists_in_memory_db(async_session) -> None:
    vacancy = Vacancy(
        external_id="dj-100",
        title="Python Trainee",
        url="https://djinni.co/jobs/100",
        platform="djinni",
    )
    async_session.add(vacancy)
    await async_session.commit()

    result = await async_session.scalar(
        select(Vacancy).where(Vacancy.external_id == "dj-100")
    )
    assert result is not None
    assert result.title == "Python Trainee"
    assert result.platform == "djinni"
