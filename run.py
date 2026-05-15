from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot import create_bot, create_dispatcher
from bot.services import run_scraper_job
from config import BASE_DIR, SCRAPE_INTERVAL_MINUTES
from database import create_tables

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def _ensure_data_dir() -> None:
    data_dir = BASE_DIR / "data"
    data_dir.mkdir(exist_ok=True)


async def main() -> None:
    _ensure_data_dir()
    await create_tables()

    bot = create_bot()
    dp = create_dispatcher()
    scheduler = AsyncIOScheduler()

    async def scheduled_scrape() -> None:
        try:
            await run_scraper_job(bot)
        except Exception:
            logger.exception("Scheduled scraper job failed")

    scheduler.add_job(
        scheduled_scrape,
        trigger="interval",
        minutes=SCRAPE_INTERVAL_MINUTES,
        id="scrape_jobs",
        replace_existing=True,
        max_instances=1,
    )
    scheduler.start()
    logger.info("Scheduler started (every %s minutes)", SCRAPE_INTERVAL_MINUTES)

    await run_scraper_job(bot)

    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
