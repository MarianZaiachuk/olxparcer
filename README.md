# 🦅 OLX Deal Sniper (olx.ua)

Швидкий, модульний та стійкий до блокувань сервіс моніторингу вигідних пропозицій на OLX Україна з миттєвими сповіщеннями в Telegram.

---

## ⚡ Особливості архітектури
- **Обхід Cloudflare / CloudFront TLS Fingerprinting:** Використовує бібліотеку `curl_cffi` з емуляцією сучасних відбитків браузера Chrome 124+ (JA3/JA4) для миттєвих легких HTTP-запитів до внутрішнього API `olx.ua/api/v1/offers/`.
- **Розумна фільтрація вигоди:**
  - Фільтри діапазону цін (від / до).
  - Глобальний та локальний чорний список стоп-слів (брак, на запчастини, iCloud lock, MDM, підробки, обмін).
  - Білий список (обов'язкова наявність ключових характеристик).
- **Пріоритет локальних угод (Івано-Франківськ та область):**
  - Автоматичне маркування та підсвічування пропозицій з вашого регіону (`📍 [ЛОКАЛЬНО: Івано-Франківськ]`) для безпечного самовивозу та огляду товару на місці.
- **Відстеження динаміки цін (Price Drop Alerts):**
  - Якщо продавець знижує ціну на вже опублікований товар, бот надсилає сповіщення `📉 ЦІНУ ЗНИЖЕНО НА X%` із порівнянням старої та нової ціни.
- **SQLite сховище:**
  - База даних `data/seen_ads.db` гарантує відсутність дублікатів та зберігає повну історію зміни цін.
- **Rich Telegram Cards:**
  - Попередній перегляд повнорозмірних фото товару, клікабельні прямі посилання, форматування цін та дати публікації.
- **Антибан-механіка:**
  - Рандомізований джиттер (плаваючий інтервал перевірки $\pm 15$ сек).
  - Затримки між запитами категорій.
  - Автоматичний reconnect та ротація TLS-сесій при HTTP 429/403.

---

## 🚀 Швидкий старт

### 1. Встановлення залежностей
Проєкт використовує швидкий менеджер пакетів `uv`:

```powershell
# Клонуйте або відкрийте папку проєкту
cd c:\Users\OPIUM\Downloads\olxparcer

# Всі залежності встановлюються автоматично через uv
uv sync
```

### 2. Налаштування Telegram бота
Створіть файл `.env` на основі `.env.example`:

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ
TELEGRAM_CHAT_ID=123456789
```

> **Як отримати токен та Chat ID:**
> 1. Створіть бота через [@BotFather](https://t.me/BotFather) у Telegram і скопіюйте API токен.
> 2. Запустіть створеного бота (натисніть `/start`).
> 3. Дізнайтеся свій числовий Chat ID через бота [@userinfobot](https://t.me/userinfobot).

### 3. Діагностика з'єднання
Перед запуском виконайте автоматичний тест:

```powershell
uv run python test_connection.py
```
Скрипт перевірить обхід захисту OLX, підключення до бази та надішле тестове повідомлення у ваш Telegram.

### 4. Запуск моніторингу

#### Звичайний запуск:
```powershell
uv run python main.py
```

#### Тестовий прогін без Telegram (Dry Run):
```powershell
uv run python main.py --dry-run --once
```

---

## ⚙️ Налаштування пошуків (`config.yaml`)

Усі категорії, цінові межі та стоп-слова редагуються у `config.yaml`:

```yaml
monitoring:
  check_interval_seconds: 45 # Інтервал опитування
  jitter_seconds: 15         # Випадкове відхилення +/- секунд
  notify_on_startup: false   # false = не спамити старими оголошеннями при старті

regions:
  priority_region_id: 13     # 13 = Івано-Франківська область
  priority_region_name: "Івано-Франківськ"

searches:
  - name: "Apple iPhone"
    query: "iphone"
    min_price: 10000
    max_price: 45000
    stop_words:
      - "чохол"
      - "скло"

  - name: "Apple MacBook M-серії"
    query: "macbook"
    min_price: 15000
    max_price: 60000
```

---

## 🕒 Фоновий запуск 24/7

### Варіант А: Через PM2 (рекомендовано для Windows і Linux)
```powershell
# Встановлення PM2 (якщо ще немає NodeJS)
npm install -g pm2

# Запуск снайпера під контролем PM2
pm2 start "uv run python main.py" --name "olx-sniper"

# Перевірка статусу та логів
pm2 status
pm2 logs olx-sniper

# Збереження для автостарту при перезавантаженні системи
pm2 save
```

### Варіант Б: Фоновий процес Windows (PowerShell)
```powershell
Start-Process -NoNewWindow -FilePath "uv" -ArgumentList "run", "python", "main.py"
```

### Варіант В: Systemd сервіс (для Linux VPS сервісу)
Створіть файл `/etc/systemd/system/olx-sniper.service`:
```ini
[Unit]
Description=OLX Deal Sniper Daemon
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/olxparcer
ExecStart=/root/.cargo/bin/uv run python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```
Увімкніть автозапуск:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now olx-sniper
sudo systemctl status olx-sniper
```
