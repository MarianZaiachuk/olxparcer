[English](README.en.md)

# OLX Deal Sniper

Сервіс моніторингу оголошень на `olx.ua` зі збереженням історії цін у SQLite, оцінкою ринкової вартості та сповіщеннями в Telegram.

**Онлайн-демо:** [marianzaiachuk.github.io/olxparcer](https://marianzaiachuk.github.io/olxparcer/) — інтерактивна симуляція фільтрації, оцінки вигоди, симуляції зниження ціни та Telegram-карток прямо в браузері (на тестових даних).

## Можливості

- HTTP-запити до внутрішнього API `olx.ua/api/v1/offers/` через `curl_cffi` з ротацією TLS-профілів та випадковим джиттером інтервалу
- Фільтрація за межами цін, білими списками та стоп-словами з урахуванням меж слів (`\b...\b`)
- Визначення пріоритетного регіону/міст для самовивозу
- Дедуплікація та трекінг знижень ціни (`price_history`) у SQLite (`data/seen_ads.db`)
- Розрахунок медіанної ціни ринку (окремо для UAH та USD), орієнтовної ціни швидкого перепродажу та ліквідності товару
- Інтерактивний Telegram-бот на `aiogram 3` з кнопками під кожним оголошенням і командами `/favorites`, `/stats`, `/status`

## Швидкий старт (`uv`)

```bash
git clone https://github.com/MarianZaiachuk/olxparcer.git
cd olxparcer
uv sync
cp .env.example .env
```

Заповніть `TELEGRAM_BOT_TOKEN` і `TELEGRAM_CHAT_ID` у `.env`, налаштуйте пошукові запити в `config.yaml` та перевірте підключення:

```bash
uv run python test_connection.py
uv run python main.py --dry-run --once
```

Звичайний запуск моніторингу:

```bash
uv run python main.py
```

Додатково можна передати проксі через `--proxy http://user:pass@host:port` або змінну `OLX_PROXY`.

## Запуск 24/7 у Docker

```bash
cp .env.example .env
docker compose up -d --build
```

База `data/seen_ads.db` та конфіг `config.yaml` підключаються через volumes, тому історія оголошень зберігається між перезапусками контейнера.

## Команди Telegram-бота

- `/status` — кількість збережених оголошень, знижень ціни, обраного та активних пошуків
- `/favorites` — список збережених угод
- `/stats <модель>` — медіанна/середня ціна ринку та рекомендована ціна викупу (напр. `/stats iphone 14`)
- `/help` — довідка по командах

## Тести та лінтинг

```bash
uv run pytest -v
uv run ruff check .
```

## Ліцензія

[MIT](LICENSE)
