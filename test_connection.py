"""
Diagnostic test script to verify OLX API bypass, SQLite storage, and Telegram credentials.
"""

import asyncio
import sys

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

from config import load_config
from models import SearchTarget
from notifier import TelegramNotifier
from scraper import OLXScraper
from storage import Storage


async def run_diagnostics():
    print("=" * 60)
    print("🚀 OLX DEAL SNIPER: ДІАГНОСТИКА СИСТЕМИ ТА ПІДКЛЮЧЕННЯ")
    print("=" * 60)

    # 1. Завантаження конфігурації
    print("\n[1/4] Завантаження конфігурації (config.yaml / .env)...")
    try:
        cfg = load_config("config.yaml")
        print("  ✅ Конфігурація успішно завантажена.")
        print(f"  🎯 Знайдено цільових пошуків: {len(cfg.searches)}")
        print(f"  📍 Пріоритетний регіон: {cfg.regions.priority_region_name} (ID: {cfg.regions.priority_region_id})")
    except Exception as e:  # noqa: BLE001
        print(f"  ❌ Помилка конфігурації: {e}")
        return

    # 2. Перевірка SQLite бази даних
    print("\n[2/4] Перевірка SQLite бази даних...")
    try:
        storage = Storage(cfg.database.path)
        stats = storage.get_stats()
        print(f"  ✅ База даних активна: {cfg.database.path}")
        print(f"  📊 Збережених оголошень: {stats['total_offers']}, знижень цін: {stats['total_price_drops']}")
    except Exception as e:  # noqa: BLE001
        print(f"  ❌ Помилка бази даних: {e}")
        return

    # 3. Тест підключення до OLX API (Обхід CloudFront/Cloudflare)
    print("\n[3/4] Тест з'єднання з OLX API (TLS Impersonation)...")
    scraper = OLXScraper()
    test_target = SearchTarget(
        name="Діагностика iPhone",
        query="iphone 14",
        min_price=15000,
        max_price=35000,
    )
    try:
        offers = await scraper.fetch_offers(test_target, limit=5)
        if offers:
            print(f"  ✅ Успішно! Отримано {len(offers)} оголошень з OLX без блокувань.")
            sample = offers[0]
            print(f"  📌 Приклад: {sample.title}")
            print(f"     Ціна: {sample.price} {sample.currency} | Локація: {sample.city} ({sample.region})")
            print(f"     URL: {sample.url}")
        else:
            print("  ⚠️ Запит виконано, але оголошень не знайдено.")
    except Exception as e:  # noqa: BLE001
        print(f"  ❌ Помилка зв'язку з OLX: {e}")
    finally:
        await scraper.close()

    # 4. Тест підключення до Telegram
    print("\n[4/4] Перевірка Telegram бота...")
    token = cfg.telegram.bot_token
    chat_id = cfg.telegram.chat_id

    if not token or not chat_id:
        print("  ⚠️ Токен або Chat ID не заповнені.")
        print("     Додайте їх у файл .env (TELEGRAM_BOT_TOKEN та TELEGRAM_CHAT_ID)")
        print("     або безпосередньо у config.yaml.")
    else:
        notifier = TelegramNotifier(bot_token=token, chat_id=chat_id)
        try:
            print(f"  🤖 Спроба відправки тестового сповіщення на Chat ID {chat_id}...")
            ok = await notifier.send_system_message(
                "🟢 <b>OLX Deal Sniper успішно підключено!</b>\n\n"
                "Система моніторингу готова до роботи. Очікуйте повідомлень про нові вигідні пропозиції!"
            )
            if ok:
                print("  ✅ Тестове повідомлення успішно надіслано у ваш Telegram!")
            else:
                print("  ❌ Не вдалося надіслати повідомлення (перевірте токен або чи запустили ви /start у боті).")
        except Exception as e:  # noqa: BLE001
            print(f"  ❌ Помилка Telegram API: {e}")
        finally:
            await notifier.close()

    print("\n" + "=" * 60)
    print("Діагностику завершено!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_diagnostics())
