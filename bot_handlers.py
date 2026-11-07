"""
Telegram bot handlers for interactive commands, favorites management, and market analytics.
"""

import html
import logging
import re

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from storage import Storage

logger = logging.getLogger(__name__)


def create_bot_router(storage: Storage) -> Router:
    router = Router()

    @router.message(Command("start", "help"))
    async def cmd_start(message: Message) -> None:
        text = (
            "🦅 <b>OLX Deal Sniper Bot</b> — ваш автоматизований помічник для викупу та перепродажу.\n\n"
            "<b>Доступні команди:</b>\n"
            "⭐ /favorites — переглянути збережені вигідні товари\n"
            "📊 /stats <code>&lt;модель&gt;</code> — розрахувати ринкову аналітику за моделлю\n"
            "   <i>(Приклад: <code>/stats iphone 14</code> або <code>/stats playstation 5</code>)</i>\n"
            "ℹ️ /help — ця довідка\n\n"
            "Під кожним новим повідомленням про товар є кнопки <b>[⭐ В обране]</b> та <b>[📊 Ринкова ціна]</b>."
        )
        await message.answer(text)

    @router.message(Command("favorites", "fav"))
    async def cmd_favorites(message: Message) -> None:
        favs = storage.get_favorites(limit=25)
        if not favs:
            await message.answer(
                "⭐ <b>Список обраного порожній.</b>\n\n"
                "Натискайте кнопку <b>[⭐ В обране]</b> під сповіщеннями про вигідні оголошення, щоб збирати їх сюди."
            )
            return

        lines = [f"⭐ <b>Ваші збережені пропозиції ({len(favs)}):</b>\n"]
        for idx, item in enumerate(favs, 1):
            title = html.escape(item["title"])
            price_str = f"{item['price']:,}".replace(",", " ") + " грн" if item.get("price") else "Ціна не вказана"
            city = html.escape(item.get("city") or "Невідомо")
            url = html.escape(item["url"], quote=True)

            lines.append(f"{idx}. <b>{title}</b>")
            lines.append(f"   💰 Ціна: <b>{price_str}</b> | 📍 {city}")
            lines.append(f'   🔗 <a href="{url}">Відкрити на OLX</a>\n')

        await message.answer("\n".join(lines), disable_web_page_preview=True)

    @router.message(Command("stats"))
    async def cmd_stats(message: Message) -> None:
        args = message.text.split(maxsplit=1) if message.text else []
        if len(args) < 2 or not args[1].strip():
            await message.answer(
                "📊 <b>Будь ласка, вкажіть назву товару.</b>\n"
                "Приклад: <code>/stats iphone 13 pro</code> або <code>/stats ps5</code>"
            )
            return

        query = args[1].strip()
        stats = storage.get_market_statistics(query)

        if not stats:
            await message.answer(
                f"📊 Недостатньо даних у базі для розрахунку ринкової ціни за запитом <b>'{html.escape(query)}'</b>.\n\n"
                "💡 <i>Бот безперервно збирає оголошення. Зачекайте кілька годин моніторингу або спробуйте більш загальний запит.</i>"
            )
            return

        report = format_market_report(stats)
        await message.answer(report)

    @router.callback_query(F.data.startswith("fav:"))
    async def cb_add_favorite(callback: CallbackQuery) -> None:
        offer_id = int(callback.data.split(":")[1])
        success, msg = storage.add_favorite(offer_id)

        if success:
            await callback.answer("⭐ Товар додано в Обране!", show_alert=False)
            # Update inline keyboard button to show saved status
            if callback.message and callback.message.reply_markup:
                new_keyboard = []
                for row in callback.message.reply_markup.inline_keyboard:
                    new_row = []
                    for btn in row:
                        if btn.callback_data == f"fav:{offer_id}":
                            new_row.append(
                                InlineKeyboardButton(text="✅ В обраному", callback_data=f"unfav:{offer_id}")
                            )
                        else:
                            new_row.append(btn)
                    new_keyboard.append(new_row)
                try:
                    await callback.message.edit_reply_markup(
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=new_keyboard)
                    )
                except Exception as edit_err:  # noqa: BLE001
                    logger.debug(f"Could not update button: {edit_err}")
        else:
            await callback.answer(msg, show_alert=False)

    @router.callback_query(F.data.startswith("unfav:"))
    async def cb_remove_favorite(callback: CallbackQuery) -> None:
        offer_id = int(callback.data.split(":")[1])
        storage.remove_favorite(offer_id)
        await callback.answer("❌ Видалено з Обраного", show_alert=False)

        # Restore original button
        if callback.message and callback.message.reply_markup:
            new_keyboard = []
            for row in callback.message.reply_markup.inline_keyboard:
                new_row = []
                for btn in row:
                    if btn.callback_data == f"unfav:{offer_id}":
                        new_row.append(
                            InlineKeyboardButton(text="⭐ В обране", callback_data=f"fav:{offer_id}")
                        )
                    else:
                        new_row.append(btn)
                new_keyboard.append(new_row)
            try:
                await callback.message.edit_reply_markup(
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=new_keyboard)
                )
            except Exception as edit_err:  # noqa: BLE001
                logger.debug(f"Could not restore button: {edit_err}")

    @router.callback_query(F.data.startswith("stats:"))
    async def cb_show_stats(callback: CallbackQuery) -> None:
        offer_id = int(callback.data.split(":")[1])
        offer = storage.get_offer_by_id(offer_id)

        if not offer:
            await callback.answer("⚠️ Оголошення не знайдено в базі.", show_alert=True)
            return

        # Extract search keywords from offer title (e.g. "iPhone 14 Pro 128gb" -> "iPhone 14")
        query = clean_title_for_stats(offer["title"])
        stats = storage.get_market_statistics(query)

        if not stats or stats["sample_count"] < 2:
            await callback.answer(
                f"📊 Замало даних у базі для точної оцінки '{query}'. Бот продовжує збирати статистику.",
                show_alert=True,
            )
            return

        await callback.answer()
        report = format_market_report(stats)
        if callback.message:
            await callback.message.reply(report)

    return router


def clean_title_for_stats(title: str) -> str:
    """Extracts base model name from ad title for cleaner market grouping."""
    cleaned = re.sub(r"[^\w\s]", " ", title.lower())
    words = cleaned.split()
    # Remove common junk words
    stop = {"продам", "новий", "бу", "нова", "стан", "ідеал", "гарний", "терміново", "торг"}
    meaningful = [w for w in words if w not in stop]
    # Take first 3 core tokens (e.g. 'iphone', '14', 'pro')
    return " ".join(meaningful[:3]) if meaningful else title[:20]


def format_market_report(stats: dict, liquidity_label: str = "Висока ⚡ (1-3 дні)") -> str:
    query_safe = html.escape(stats["query"])
    min_p = f"{stats['min_price']:,}".replace(",", " ")
    max_p = f"{stats['max_price']:,}".replace(",", " ")
    avg_p = f"{stats['avg_price']:,}".replace(",", " ")
    med_p = f"{stats['median_price']:,}".replace(",", " ")
    quick_p = f"{round(stats['median_price'] * 0.94):,}".replace(",", " ")
    buy_p = f"{stats['target_buy_price']:,}".replace(",", " ")
    margin_p = f"{stats['estimated_margin']:,}".replace(",", " ")

    return (
        f"📊 <b>РИНКОВА АНАЛІТИКА:</b> <code>{query_safe}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 Проаналізовано пропозицій: <b>{stats['sample_count']}</b>\n"
        f"💰 Середня ціна ринку: <b>{avg_p} грн</b>\n"
        f"📈 Медіанна ринкова ціна: <b>{med_p} грн</b>\n"
        f"📉 Діапазон цін: від <b>{min_p}</b> до <b>{max_p} грн</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💵 <b>Швидкий перепродаж (1-3 дні):</b> ~<b>{quick_p} грн</b>\n"
        f"🎯 <b>Рекомендована ціна викупу:</b> до <b>{buy_p} грн</b>\n"
        f"💸 <b>Орієнтовний чистий профіт:</b> ~<b>{margin_p} грн</b> (~18-20%)\n"
        f"⚡ <b>Ліквідність:</b> {liquidity_label}\n"
    )
