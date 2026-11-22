[Українською](README.md)

# OLX Deal Sniper

`olx.ua` listing monitor with SQLite price-drop history, median market valuation, and interactive Telegram notifications.

**Live demo:** [marianzaiachuk.github.io/olxparcer](https://marianzaiachuk.github.io/olxparcer/) — browser-based simulation of filtering rules, price-drop alerts, market stats, and Telegram cards on sample listings.

## Features

- Queries `olx.ua/api/v1/offers/` via `curl_cffi` with TLS profile rotation on retries and jittered polling intervals
- Filters by min/max price, global and per-target stop-words (word-boundary aware), and optional whitelists
- Highlights listings from a configured priority region and city list
- Stores seen ads and tracks price drops in SQLite (`data/seen_ads.db`)
- Estimates market median (isolated by currency), quick-resale target, profit margin, and liquidity score
- `aiogram 3` Telegram bot with inline `[Open on OLX]`, `[Add to Favorites]`, `[Market Price]` buttons and `/favorites`, `/stats`, `/status` commands

## Quick Start (`uv`)

```bash
git clone https://github.com/MarianZaiachuk/olxparcer.git
cd olxparcer
uv sync
cp .env.example .env
```

Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`, adjust `config.yaml`, then run:

```bash
uv run python test_connection.py
uv run python main.py --dry-run --once
uv run python main.py
```

Optional proxy support via `--proxy` or `OLX_PROXY` env var.

## Docker (24/7)

```bash
cp .env.example .env
docker compose up -d --build
```

`./data` and `./config.yaml` are mounted as volumes so the SQLite database persists across restarts.

## Bot Commands

- `/status` — tracked offers, price drops, favorites count, and active targets
- `/favorites` — list bookmarked listings
- `/stats <model>` — market median, price range, and recommended buy price
- `/help` — command summary

## Tests & Lint

```bash
uv run pytest -v
uv run ruff check .
```

## License

[MIT](LICENSE)
