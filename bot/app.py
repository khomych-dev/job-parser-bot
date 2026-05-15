from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.handlers import router
from config import BOT_TOKEN


def create_bot() -> Bot:
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set. Copy .env.example to .env and configure it.")
    return Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(router)
    return dp
