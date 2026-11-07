"""
Telegram notification module using aiogram with rich card formatting, photo previews, and interactive buttons.
"""

import asyncio
import html
import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from models import Offer

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token.strip()
        self.chat_id = chat_id.strip()
        self.bot: Bot | None = None

        if self.bot_token and self.chat_id:
            self.bot = Bot(
                token=self.bot_token,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML),
            )

    @property
    def is_configured(self) -> bool:
        return bool(self.bot and self.chat_id)

    async def close(self) -> None:
        if self.bot and self.bot.session:
            await self.bot.session.close()

    def _format_price(self, price: int | None, currency: str = "UAH") -> str:
        if price is None:
            return "Не вказана"
        curr_label = "грн" if currency in ("UAH", "грн") else currency
        return f"{price:,}".replace(",", " ") + f" {curr_label}"

    def _build_caption(self, offer: Offer, target_name: str) -> str:
        safe_title = html.escape(offer.title)
        safe_city = html.escape(offer.city or "Невідомо")
        safe_region = html.escape(offer.region or "Україна")
        safe_target = html.escape(target_name)
        safe_url = html.escape(offer.url, quote=True)

        lines = []

        # Local badge (High priority for sniper)
        if offer.is_local:
            lines.append("⚡ <b>[ЛОКАЛЬНО: ІВАНО-ФРАНКІВСЬК / ОБЛАСТЬ]</b>")
            lines.append("<i>(Можна забрати особисто / оглянути на місці!)</i>\n")

        # Header: New or Price Drop
        if offer.is_price_drop and offer.old_price:
            drop_pct = offer.price_drop_percent or 0
            lines.append(f"📉 <b>ЦІНУ ЗНИЖЕНО НА {drop_pct}%!</b>")
            lines.append(f"💰 Було: <s>{self._format_price(offer.old_price, offer.currency)}</s>")
            lines.append(f"🔥 Стало: <b>{self._format_price(offer.price, offer.currency)}</b>")
        else:
            lines.append("🎯 <b>НОВЕ ОГОЛОШЕННЯ!</b>")
            lines.append(f"💰 Ціна: <b>{self._format_price(offer.price, offer.currency)}</b>")

        lines.append(f"\n📦 <b>{safe_title}</b>")
        lines.append(f"🏷 Категорія: <i>{safe_target}</i>")
        lines.append(f"📍 Локація: <b>{safe_city}</b> ({safe_region})")

        if offer.created_time:
            time_str = offer.created_time.replace("T", " ").split("+")[0]
            lines.append(f"🕒 Опубліковано: {time_str}")

        # Valuation and flipping analysis block
        if offer.market_price and offer.discount_pct is not None:
            lines.append("\n━━━━━━━━━━━━━━━━━━━━")
            if offer.deal_verdict:
                lines.append(f"<b>{offer.deal_verdict}</b>")

            sign = "-" if offer.discount_pct > 0 else "+"
            lines.append(f"📊 Оцінка ринку: ~<b>{self._format_price(offer.market_price, offer.currency)}</b>")
            lines.append(f"📉 Різниця з ринком: <b>{sign}{abs(offer.discount_pct)}%</b>")

            if offer.resale_price:
                lines.append(f"💵 Можна продати швидко: ~<b>{self._format_price(offer.resale_price, offer.currency)}</b>")
            if offer.estimated_profit and offer.estimated_profit > 0:
                lines.append(f"💸 Орієнтовний профіт: ~<b>+{self._format_price(offer.estimated_profit, offer.currency)}</b>")
            if offer.liquidity_label:
                lines.append(f"⚡ Ліквідність: <b>{offer.liquidity_label}</b>")
            lines.append("━━━━━━━━━━━━━━━━━━━━")

        lines.append(f'\n👉 <a href="{safe_url}"><b>ВІДКРИТИ НА OLX</b></a>')

        return "\n".join(lines)

    def _build_inline_keyboard(self, offer: Offer) -> InlineKeyboardMarkup:
        """Constructs interactive buttons below the notification."""
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="👉 Відкрити на OLX", url=offer.url),
                ],
                [
                    InlineKeyboardButton(text="⭐ В обране", callback_data=f"fav:{offer.id}"),
                    InlineKeyboardButton(text="📊 Ринкова ціна", callback_data=f"stats:{offer.id}"),
                ],
            ]
        )

    async def send_deal_notification(self, offer: Offer, target_name: str) -> bool:
        """
        Sends an ad card to Telegram with photo preview and interactive buttons.
        Falls back to a formatted text message if photo fails.
        """
        if not self.is_configured or not self.bot:
            logger.warning("TelegramNotifier is not configured. Skipping alert.")
            return False

        caption = self._build_caption(offer, target_name)
        reply_markup = self._build_inline_keyboard(offer)

        try:
            if offer.photo_url:
                try:
                    await self.bot.send_photo(
                        chat_id=self.chat_id,
                        photo=offer.photo_url,
                        caption=caption,
                        reply_markup=reply_markup,
                    )
                    return True
                except TelegramRetryAfter as e:
                    logger.warning(f"Telegram flood limit: sleeping {e.retry_after + 1}s")
                    await asyncio.sleep(e.retry_after + 1)
                    await self.bot.send_photo(
                        chat_id=self.chat_id,
                        photo=offer.photo_url,
                        caption=caption,
                        reply_markup=reply_markup,
                    )
                    return True
                except Exception as photo_err:  # noqa: BLE001
                    logger.debug(f"Could not send photo ({photo_err}), sending text fallback...")

            # Fallback to text message
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=caption,
                reply_markup=reply_markup,
                disable_web_page_preview=False,
            )
            return True

        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to send Telegram notification for offer {offer.id}: {e}")
            return False

    async def send_system_message(self, text: str) -> bool:
        """Sends a simple system status / startup message."""
        if not self.is_configured or not self.bot:
            return False
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=text)
            return True
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to send system message: {e}")
            return False
