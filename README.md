# Job Parser Bot

Job Parser Bot is an asynchronous Telegram bot that periodically scrapes major Ukrainian job portals for relevant Python development vacancies and sends immediate notifications to specified Telegram chats.

By default, the bot is configured to look for **Remote Python** positions while filtering out junior, trainee, or internship roles, aiming primarily at Middle/Senior level opportunities.

## Features

- **Multi-source Scraping**: Automatically aggregates job listings from multiple popular Ukrainian job boards.
- **Smart Filtering**: Built-in keywords filtering to exclude unwanted positions (e.g., Trainee, Junior, Intern).
- **Automated Scheduling**: Runs scrapes periodically in the background (default: every 20 minutes).
- **Duplicate Prevention**: Uses an SQLite database to track seen vacancies and ensure you only receive alerts for *new* jobs.
- **Telegram Notifications**: Pushes new matched vacancies directly to your configured Telegram chat(s) in real-time.

## Supported Job Boards

- [Djinni](https://djinni.co/)
- [DOU](https://jobs.dou.ua/)
- [Robota.ua](https://robota.ua/)
- [Work.ua](https://www.work.ua/)

## Tech Stack

- **Language:** Python 3.12+
- **Bot Framework:** [aiogram 3.x](https://docs.aiogram.dev/)
- **Scraping:** [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), [aiohttp](https://docs.aiohttp.org/), [curl-cffi](https://github.com/yifeikong/curl_cffi) (to bypass Cloudflare/bot protections)
- **Database:** SQLite with [SQLAlchemy 2.0](https://www.sqlalchemy.org/) and [aiosqlite](https://aiosqlite.omnilib.dev/)
- **Task Scheduling:** [APScheduler](https://apscheduler.readthedocs.io/)
- **Package Manager:** `uv` (recommended) or `pip`

## Prerequisites

- Python 3.12 or newer.
- A Telegram Bot Token. You can get one by creating a new bot via [@BotFather](https://t.me/BotFather) on Telegram.
- Your Telegram Chat ID(s) to receive notifications.

## Installation and Setup

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd job_parser_bot
   ```

2. **Set up the virtual environment and install dependencies:**
   This project uses `uv` for dependency management, but you can also use standard `pip`.

   Using `uv`:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   uv pip install -r pyproject.toml
   ```

   Using `pip`:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   pip install .
   ```

3. **Configure Environment Variables:**
   Copy the example environment file and edit it with your credentials:
   ```bash
   cp .env.example .env
   ```
   Open the `.env` file and fill in the required variables:
   - `BOT_TOKEN`: Your Telegram Bot Token.
   - `ADMIN_CHAT_IDS`: Comma-separated list of Telegram Chat IDs to receive notifications.
   - `SCRAPE_INTERVAL_MINUTES`: (Optional) Scrape frequency in minutes. Default is 20.
   - `DATABASE_URL`: (Optional) Path to your SQLite DB. Default creates `jobs.db` in the `data/` folder.

## Usage

Start the bot and the scheduler by running the main entry point:

```bash
python run.py
```

Upon startup, the bot will immediately initialize the database, execute a first scraping run across all configured platforms, and then start the background scheduler and Telegram polling. New jobs will be sent to the configured `ADMIN_CHAT_IDS`.

## Customizing Filters

If you wish to change the search criteria or the exclusion keywords, you can modify the constants in `config.py`:

- `SEARCH_KEYWORDS`: The primary terms to search for (e.g., `("Python", "Remote")`).
- `TITLE_FILTER_KEYWORDS`: Titles containing these words will be ignored (e.g., `"junior"`, `"trainee"`, `"intern"`).

## Running Tests

To run the test suite, ensure you have the development dependencies installed:

```bash
uv pip install pytest pytest-asyncio
pytest
```
