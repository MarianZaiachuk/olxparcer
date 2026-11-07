"""
Main orchestrator for OLX Deal Sniper with interactive Telegram bot handlers.
"""

import argparse
import asyncio
import logging
import random
import signal
import sys
from datetime import datetime

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

from aiogram import Dispatcher

from bot_handlers import create_bot_router
from config import AppConfig, load_config
from filter import DealFilter
from notifier import TelegramNotifier
from scraper import OLXScraper
from storage import Storage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("OLXSniper")


class DealSniper:
    def __init__(self, config: AppConfig, dry_run: bool = False):
        self.config = config
        self.dry_run = dry_run
        self.storage = Storage(config.database.path)
        self.deal_filter = DealFilter(
            global_stop_words=config.global_stop_words,
            priority_region_id=config.regions.priority_region_id,
            priority_region_name=config.regions.priority_region_name,
            priority_cities=config.regions.priority_cities,
        )
        self.scraper = OLXScraper()
        self.notifier = TelegramNotifier(
            bot_token=config.telegram.bot_token,
            chat_id=config.telegram.chat_id,
        )
        self.is_running = True
        self.stop_event = asyncio.Event()
        self._cleaned_up = False

        self.dp: Dispatcher | None = None
        self.bot_task: asyncio.Task | None = None

        if self.notifier.is_configured and self.notifier.bot and not self.dry_run:
            self.dp = Dispatcher()
            self.dp.include_router(create_bot_router(self.storage))

    async def initialize(self) -> None:
        """Verifies components and sends startup notification."""
        stats = self.storage.get_stats()
        logger.info(
            f"База даних підключена: {stats['total_offers']} оголошень, "
            f"{stats['total_price_drops']} зафіксованих знижень цін, "
            f"{stats['total_favorites']} в обраному."
        )

        if not self.dry_run and self.notifier.is_configured:
            # Start background bot polling for interactive buttons and commands
            if self.dp and self.notifier.bot:
                logger.info("🤖 Запуск інтерактивного Telegram-бота (команди /favorites, /stats, кнопки)...")
                self.bot_task = asyncio.create_task(
                    self.dp.start_polling(self.notifier.bot, handle_signals=False)
                )

            targets_count = len(self.config.searches)
            await self.notifier.send_system_message(
                f"🚀 <b>OLX Deal Sniper запущено!</b>\n"
                f"🎯 Активних пошуків: <b>{targets_count}</b>\n"
                f"⏱ Інтервал опитування: <b>{self.config.monitoring.check_interval_seconds}s (±{self.config.monitoring.jitter_seconds}s)</b>\n"
                f"📍 Пріоритет: <b>{self.config.regions.priority_region_name} (обл. ID {self.config.regions.priority_region_id})</b>\n\n"
                f"💡 <i>Використовуйте /favorites для перегляду збережених угод або /stats для аналізу цін.</i>"
            )

    async def check_target(self, target, is_first_run: bool) -> int:
        """
        Polls a single search target, applies filters, updates DB, and sends alerts.
        Returns the number of notifications sent.
        """
        logger.info(f"🔎 Перевірка категорії: '{target.name}'...")
        offers = await self.scraper.fetch_offers(
            target=target,
            limit=self.config.monitoring.offers_limit,
        )

        notifications_sent = 0

        for offer in offers:
            # 1. Apply filter rules (stop words, whitelist, prices)
            passes, reason = self.deal_filter.evaluate(offer, target)
            if not passes:
                logger.debug(f"Пропуск ID {offer.id} ('{offer.title}'): {reason}")
                continue

            # 2. Check storage for duplicates or price drops
            is_new, _old_price = self.storage.check_and_update(offer)

            # Cold start logic: skip sending flood on startup if configured
            if is_first_run and not self.config.monitoring.notify_on_startup:
                continue

            # 3. Notify if new offer or price dropped
            if is_new or offer.is_price_drop:
                badge = "📍 [ЛОКАЛЬНО]" if offer.is_local else "🌐 [РЕГІОНИ]"
                action_type = "ЦІНУ ЗНИЖЕНО" if offer.is_price_drop else "НОВЕ"
                logger.info(
                    f"🔥 {badge} [{action_type}] Знайдено: {offer.title} | "
                    f"Ціна: {offer.price} {offer.currency} | Місто: {offer.city}"
                )

                if not self.dry_run:
                    sent = await self.notifier.send_deal_notification(offer, target.name)
                    if sent:
                        notifications_sent += 1
                        # Small delay between multiple Telegram messages to avoid flood
                        await asyncio.sleep(1.0)
                else:
                    logger.info("[DRY-RUN] Сповіщення не відправлено (увімкнено сухий запуск).")

        return notifications_sent

    async def run_cycle(self, is_first_run: bool) -> None:
        """Runs one full cycle over all configured targets with target-level isolation."""
        for target in self.config.searches:
            if not self.is_running or self.stop_event.is_set():
                break
            try:
                await self.check_target(target, is_first_run=is_first_run)
            except Exception as e:  # noqa: BLE001
                logger.error(f"Помилка при перевірці цілі '{target.name}': {e}")

            # Gentle delay between different target queries
            try:
                await asyncio.wait_for(self.stop_event.wait(), timeout=2.0)
                break
            except TimeoutError:
                pass

    async def start(self, once: bool = False) -> None:
        """Main monitoring loop with responsive stop event handling."""
        await self.initialize()

        first_run = True
        logger.info("📡 Моніторинг активовано. Очікування нових оголошень...")

        while self.is_running and not self.stop_event.is_set():
            cycle_start = datetime.now()
            try:
                await self.run_cycle(is_first_run=first_run)
                first_run = False
                elapsed = (datetime.now() - cycle_start).total_seconds()
                logger.debug(f"Цикл моніторингу завершено за {elapsed:.2f} сек.")

                if once:
                    logger.info("Параметр --once активний: завершення роботи після першого циклу.")
                    break

                # Calculate sleep with random jitter
                base_interval = self.config.monitoring.check_interval_seconds
                jitter = self.config.monitoring.jitter_seconds
                actual_sleep = max(5.0, base_interval + random.uniform(-jitter, jitter))

                logger.info(f"💤 Наступна перевірка через {actual_sleep:.1f} сек...")
                try:
                    await asyncio.wait_for(self.stop_event.wait(), timeout=actual_sleep)
                    break  # Stop event was triggered
                except TimeoutError:
                    pass   # Normal timeout elapsed, continue next cycle

            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Непередбачена помилка в головному циклі")
                logger.info("Перезапуск через 10 секунд...")
                try:
                    await asyncio.wait_for(self.stop_event.wait(), timeout=10.0)
                    break
                except TimeoutError:
                    pass

        await self.cleanup()

    async def cleanup(self) -> None:
        """Cleans up bot polling, network sessions, and resources."""
        if self._cleaned_up:
            return
        self._cleaned_up = True
        logger.info("Зупинка сервісу та закриття сесій...")

        if self.dp and self.notifier.bot:
            await self.dp.stop_polling()

        if self.bot_task:
            self.bot_task.cancel()
            try:
                await self.bot_task
            except asyncio.CancelledError:
                pass

        await self.scraper.close()
        await self.notifier.close()
        logger.info("Роботу коректно завершено.")


def main():
    parser = argparse.ArgumentParser(description="OLX Deal Sniper Monitor")
    parser.add_argument("--config", default="config.yaml", help="Шлях до config.yaml")
    parser.add_argument("--dry-run", action="store_true", help="Запуск без надсилання в Telegram")
    parser.add_argument("--once", action="store_true", help="Виконати один цикл перевірки та вийти")
    args = parser.parse_args()

    config = load_config(args.config)
    sniper = DealSniper(config=config, dry_run=args.dry_run)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def shutdown():
        sniper.is_running = False
        sniper.stop_event.set()

    # Cross-platform signal handling
    try:
        loop.add_signal_handler(signal.SIGINT, shutdown)
        loop.add_signal_handler(signal.SIGTERM, shutdown)
    except NotImplementedError:
        pass

    try:
        loop.run_until_complete(sniper.start(once=args.once))
    except KeyboardInterrupt:
        sniper.is_running = False
        sniper.stop_event.set()
        loop.run_until_complete(sniper.cleanup())
    finally:
        loop.close()


if __name__ == "__main__":
    main()
