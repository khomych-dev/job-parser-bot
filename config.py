from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

SEARCH_KEYWORDS = ("Python", "Remote")
TITLE_FILTER_KEYWORDS = (
    "навчання",
    "trainee",
    "без досвіду",
    "junior",
    "intern",
    "стажування",
)
_DEFAULT_SCRAPE_INTERVAL_MINUTES = 20


def _parse_admin_chat_ids(raw: str | None) -> list[int]:
    """Parse comma-separated Telegram chat/user IDs; empty means no admin notifications."""
    if raw is None or not raw.strip():
        return []
    result: list[int] = []
    for segment in raw.split(","):
        part = segment.strip()
        if not part:
            continue
        try:
            result.append(int(part))
        except ValueError as e:
            raise ValueError(
                f"ADMIN_CHAT_IDS must be comma-separated integers, invalid segment: {part!r}"
            ) from e
    return result


BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
ADMIN_CHAT_IDS: list[int] = _parse_admin_chat_ids(os.getenv("ADMIN_CHAT_IDS"))
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{BASE_DIR / 'data' / 'jobs.db'}",
)
SCRAPE_INTERVAL_MINUTES = int(
    os.getenv("SCRAPE_INTERVAL_MINUTES", str(_DEFAULT_SCRAPE_INTERVAL_MINUTES))
)
