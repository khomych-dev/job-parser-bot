from __future__ import annotations

import html
import logging

from aiogram import Bot
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramNotFound,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from config import ADMIN_CHAT_IDS
from database.models import Vacancy
from database.session import async_session_factory
from scrapers import DjinniScraper, DouScraper, RobotaUaScraper, WorkUaScraper

logger = logging.getLogger(__name__)

_PLATFORM_LABEL = {
    "djinni": "Djinni",
    "dou": "DOU",
    "work_ua": "Work.ua",
    "robota_ua": "Robota.ua",
}


def _platform_label(platform: str) -> str:
    return _PLATFORM_LABEL.get(platform, html.escape(platform))


def _format_new_vacancy_message(platform: str, title: str, url: str) -> str:
    safe_title = html.escape(title)
    safe_url = html.escape(url, quote=True)
    label = html.escape(_platform_label(platform))
    return (
        f"🔥 <b>Нова вакансія ({label})</b>\n"
        f"<b>Посада:</b> {safe_title}\n"
        f'<a href="{safe_url}">Переглянути вакансію</a>'
    )


async def _notify_new_vacancy(bot: Bot, platform: str, title: str, url: str) -> None:
    if not ADMIN_CHAT_IDS:
        return
    text = _format_new_vacancy_message(platform, title, url)
    for chat_id in ADMIN_CHAT_IDS:
        try:
            await bot.send_message(chat_id, text)
        except TelegramForbiddenError:
            logger.warning(
                "Could not notify chat_id=%s: bot was blocked or kicked (forbidden)",
                chat_id,
            )
        except TelegramNotFound:
            logger.warning(
                "Could not notify chat_id=%s: chat not found (check ADMIN_CHAT_IDS)",
                chat_id,
            )
        except TelegramBadRequest as e:
            logger.warning(
                "Could not notify chat_id=%s: bad request — %s",
                chat_id,
                e,
            )


async def run_scraper_job(bot: Bot | None = None) -> int:
    """Scrape all platforms, persist new vacancies, optionally notify admins."""
    scrapers = (DjinniScraper(), DouScraper(), WorkUaScraper(), RobotaUaScraper())
    new_count = 0
    session_factory = async_session_factory()

    for scraper in scrapers:
        async with scraper:
            vacancies = await scraper.scrape()
            async with session_factory() as session:
                for item in vacancies:
                    exists = await session.scalar(
                        select(Vacancy.id).where(
                            (Vacancy.external_id == item.external_id)
                            & (Vacancy.platform == scraper.platform)
                        )
                    )
                    if exists:
                        continue

                    vacancy = Vacancy(
                        external_id=item.external_id,
                        title=item.title,
                        url=item.url,
                        platform=scraper.platform,
                    )
                    session.add(vacancy)
                    try:
                        await session.commit()
                    except IntegrityError:
                        await session.rollback()
                        continue

                    new_count += 1
                    if bot is not None:
                        await _notify_new_vacancy(
                            bot, scraper.platform, item.title, item.url
                        )

    logger.info("Scraper job finished, %s new vacancies saved", new_count)
    return new_count
