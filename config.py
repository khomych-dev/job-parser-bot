from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

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


def _load_dotenv(path: Path | None = None) -> None:
    env_path = path or BASE_DIR / ".env"
    if not env_path.is_file():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()


def _parse_chat_ids(raw: str) -> tuple[int, ...]:
    if not raw.strip():
        return ()
    return tuple(int(part.strip()) for part in raw.split(",") if part.strip())


BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
ADMIN_CHAT_IDS: tuple[int, ...] = _parse_chat_ids(os.getenv("ADMIN_CHAT_IDS", ""))
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{BASE_DIR / 'data' / 'jobs.db'}",
)
SCRAPE_INTERVAL_MINUTES = int(
    os.getenv("SCRAPE_INTERVAL_MINUTES", str(_DEFAULT_SCRAPE_INTERVAL_MINUTES))
)
