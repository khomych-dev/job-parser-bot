from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import select

from database.models import Vacancy
from scrapers import DjinniScraper, DouScraper, RobotaUaScraper, WorkUaScraper
from scrapers.base import ScrapedVacancy

FIXTURES_DIR = Path(__file__).parent / "fixtures"
DJINNI_MOCK_HTML = (FIXTURES_DIR / "djinni_jobs.html").read_text(encoding="utf-8")
DOU_MOCK_HTML = (FIXTURES_DIR / "dou_jobs.html").read_text(encoding="utf-8")
WORK_UA_MOCK_HTML = (FIXTURES_DIR / "work_ua_jobs.html").read_text(encoding="utf-8")
ROBOTA_UA_MOCK_HTML = (FIXTURES_DIR / "robota_ua_jobs.html").read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_djinni_parse_vacancies_from_mock_html() -> None:
    scraper = DjinniScraper()
    vacancies = scraper.parse_vacancies(DJINNI_MOCK_HTML)

    assert len(vacancies) == 3

    junior = next(v for v in vacancies if v.external_id == "100001")
    assert junior.title == "Python Junior Developer"
    assert junior.url == "https://djinni.co/jobs/100001-python-junior-developer/"
    assert "junior engineer" in junior.description

    senior = next(v for v in vacancies if v.external_id == "100002")
    assert senior.title == "Senior Python Developer"
    assert senior.url == "https://djinni.co/jobs/100002-senior-python-developer/"

    intern = next(v for v in vacancies if v.external_id == "100003")
    assert intern.title == "Python Developer"
    assert "стажування" in intern.description


@pytest.mark.asyncio
async def test_djinni_scrape_filters_non_matching_jobs(monkeypatch: pytest.MonkeyPatch) -> None:
    scraper = DjinniScraper()

    async def mock_fetch_page(_url: str) -> str:
        return DJINNI_MOCK_HTML

    monkeypatch.setattr(scraper, "fetch_page", mock_fetch_page)

    async with scraper:
        vacancies = await scraper.scrape()

    assert len(vacancies) == 2
    ids = {v.external_id for v in vacancies}
    assert ids == {"100001", "100003"}
    assert "100002" not in ids


def test_djinni_keyword_filter_case_insensitive() -> None:
    scraper = DjinniScraper()
    vacancy = ScrapedVacancy(
        external_id="200",
        title="Python Developer",
        url="https://djinni.co/jobs/200",
        description="Great opportunity for a TRAINEE with mentorship.",
    )
    assert scraper.matches_keyword_filter(vacancy) is True


@pytest.mark.asyncio
async def test_dou_parse_vacancies_from_mock_html() -> None:
    scraper = DouScraper()
    vacancies = scraper.parse_vacancies(DOU_MOCK_HTML)

    assert len(vacancies) == 3

    junior = next(v for v in vacancies if v.external_id == "200001")
    assert junior.title == "Python Junior Developer"
    assert junior.url == "https://jobs.dou.ua/companies/acme/vacancies/200001/"
    assert "junior Python" in junior.description

    senior = next(v for v in vacancies if v.external_id == "200002")
    assert senior.title == "Senior Python Developer"
    assert senior.url == "https://jobs.dou.ua/companies/acme/vacancies/200002/"

    intern = next(v for v in vacancies if v.external_id == "200003")
    assert intern.title == "Python Developer"
    assert intern.url == "https://jobs.dou.ua/companies/startup/vacancies/200003/"
    assert "стажування" in intern.description


@pytest.mark.asyncio
async def test_dou_scrape_filters_non_matching_jobs(monkeypatch: pytest.MonkeyPatch) -> None:
    scraper = DouScraper()

    async def mock_fetch_page(_url: str) -> str:
        return DOU_MOCK_HTML

    monkeypatch.setattr(scraper, "fetch_page", mock_fetch_page)

    async with scraper:
        vacancies = await scraper.scrape()

    assert len(vacancies) == 2
    ids = {v.external_id for v in vacancies}
    assert ids == {"200001", "200003"}
    assert "200002" not in ids


@pytest.mark.asyncio
async def test_work_ua_parse_vacancies_from_mock_html() -> None:
    scraper = WorkUaScraper()
    vacancies = scraper.parse_vacancies(WORK_UA_MOCK_HTML)

    assert len(vacancies) == 3

    junior = next(v for v in vacancies if v.external_id == "300001")
    assert junior.title == "Python Junior Developer"
    assert junior.url == "https://www.work.ua/jobs/300001/"
    assert "junior Python" in junior.description

    senior = next(v for v in vacancies if v.external_id == "300002")
    assert senior.title == "Senior Python Developer"

    intern = next(v for v in vacancies if v.external_id == "300003")
    assert "стажування" in intern.description


@pytest.mark.asyncio
async def test_work_ua_scrape_filters_non_matching_jobs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scraper = WorkUaScraper()

    async def mock_fetch_page(_url: str) -> str:
        return WORK_UA_MOCK_HTML

    monkeypatch.setattr(scraper, "fetch_page", mock_fetch_page)

    async with scraper:
        vacancies = await scraper.scrape()

    assert len(vacancies) == 2
    ids = {v.external_id for v in vacancies}
    assert ids == {"300001", "300003"}


@pytest.mark.asyncio
async def test_robota_ua_parse_vacancies_from_mock_html() -> None:
    scraper = RobotaUaScraper()
    vacancies = scraper.parse_vacancies(ROBOTA_UA_MOCK_HTML)

    assert len(vacancies) == 3

    junior = next(v for v in vacancies if v.external_id == "400001")
    assert junior.title == "Python Junior Developer"
    assert junior.url == "https://robota.ua/company100/vacancy400001"
    assert "junior Python" in junior.description

    senior = next(v for v in vacancies if v.external_id == "400002")
    assert senior.title == "Senior Python Developer"

    intern = next(v for v in vacancies if v.external_id == "400003")
    assert "стажування" in intern.description


@pytest.mark.asyncio
async def test_robota_ua_scrape_filters_non_matching_jobs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scraper = RobotaUaScraper()

    async def mock_fetch_page(_url: str) -> str:
        return ROBOTA_UA_MOCK_HTML

    monkeypatch.setattr(scraper, "fetch_page", mock_fetch_page)

    async with scraper:
        vacancies = await scraper.scrape()

    assert len(vacancies) == 2
    ids = {v.external_id for v in vacancies}
    assert ids == {"400001", "400003"}


def test_dou_keyword_filter_case_insensitive() -> None:
    scraper = DouScraper()
    vacancy = ScrapedVacancy(
        external_id="300",
        title="Python Developer",
        url="https://jobs.dou.ua/companies/acme/vacancies/300/",
        description="Internship program for beginners.",
    )
    assert scraper.matches_keyword_filter(vacancy) is True


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
