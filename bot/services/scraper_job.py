from __future__ import annotations

import logging

from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from config import ADMIN_CHAT_IDS
from database.models import Vacancy
from database.session import async_session_factory
from scrapers import DjinniScraper, DouScraper

logger = logging.getLogger(__name__)


async def run_scraper_job(bot: Bot | None = None) -> int:
    """Scrape all platforms, persist new vacancies, optionally notify admins."""
    scrapers = (DjinniScraper(), DouScraper())
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
                    if bot and ADMIN_CHAT_IDS:
                        text = (
                            f"<b>{item.title}</b>\n"
                            f"Platform: {scraper.platform}\n"
                            f"<a href=\"{item.url}\">Open vacancy</a>"
                        )
                        for chat_id in ADMIN_CHAT_IDS:
                            await bot.send_message(chat_id, text)

    logger.info("Scraper job finished, %s new vacancies saved", new_count)
    return new_count
