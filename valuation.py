"""
Automated deal valuation, liquidity scoring, and resale profit estimation engine.
"""

import re

from pydantic import BaseModel

from models import Offer
from storage import Storage


class DealValuation(BaseModel):
    market_price: int
    discount_pct: float
    quick_resale_price: int
    normal_resale_price: int
    estimated_profit: int
    liquidity_score: float
    liquidity_label: str
    verdict: str


# Liquidity heuristics for Ukrainian classifieds market
HIGH_LIQUIDITY_PATTERNS = [
    (r"\biphone\s*(1[3-6])\b", 9.6, "Дуже висока 🚀 (1-2 дні)"),
    (r"\biphone\s*(1[1-2])\b", 9.2, "Висока ⚡ (2-4 дні)"),
    (r"\bplaystation\s*5\b|\bps5\b", 9.5, "Дуже висока 🚀 (1-3 дні)"),
    (r"\bsteam\s*deck\b", 9.0, "Висока ⚡ (2-4 дні)"),
    (r"\bmacbook\s*(air|pro)?\s*(m[1-3])\b", 9.1, "Висока ⚡ (2-5 днів)"),
    (r"\becoflow\b|\bbluetti\b", 9.3, "Дуже висока 🔥 (1-3 дні)"),
    (r"\bairpods\s*pro\b|\bairpods\s*max\b", 9.2, "Висока ⚡ (1-3 дні)"),
    (r"\bnintendo\s*switch\s*oled\b", 8.8, "Висока ⚡ (3-5 днів)"),
    (r"\brtx\s*(30[6-8]0|40[6-8]0)\b", 8.9, "Висока ⚡ (2-4 дні)"),
    (r"\bipad\s*(air|pro|mini)?\b", 8.2, "Середня-висока ⚖️ (4-7 днів)"),
    (r"\bapple\s*watch\b", 7.8, "Середня ⚖️ (5-8 днів)"),
]


class DealValuator:
    def __init__(self, storage: Storage):
        self.storage = storage

    def estimate_liquidity(self, title: str) -> tuple[float, str]:
        """Estimates liquidity score (1.0 to 10.0) based on title patterns."""
        title_lower = title.lower()
        for pattern, score, label in HIGH_LIQUIDITY_PATTERNS:
            if re.search(pattern, title_lower):
                return score, label
        return 7.0, "Помірна ⚖️ (1-2 тижні)"

    def evaluate(self, offer: Offer) -> DealValuation | None:
        """
        Analyzes the offer price against accumulated market data or baseline.
        Returns valuation metrics: discount %, resale price, profit, and liquidity.
        """
        if not offer.price or offer.price <= 0:
            return None

        # 1. Clean title into search keywords (e.g. 'iphone', '14', 'pro')
        cleaned = re.sub(r"[^\w\s]", " ", offer.title.lower())
        words = cleaned.split()
        stop = {"продам", "новий", "бу", "нова", "стан", "ідеал", "гарний", "терміново", "торг", "чохол"}
        meaningful = [w for w in words if w not in stop]
        query = " ".join(meaningful[:3]) if meaningful else offer.title[:15]

        # 2. Get market stats from DB
        stats = self.storage.get_market_statistics(query)

        market_price = None
        if stats and stats["sample_count"] >= 3:
            market_price = stats["median_price"]

        # If insufficient DB history, we skip or require at least some baseline
        if not market_price:
            return None

        # 3. Calculate discount vs market
        discount_pct = round(((market_price - offer.price) / market_price) * 100, 1)

        # 4. Calculate resale targets
        # Quick resale: 93-95% of market median for fast liquidation
        quick_resale = round(market_price * 0.94)
        normal_resale = market_price

        # Estimated profit on fast liquidation
        estimated_profit = quick_resale - offer.price

        # 5. Liquidity & verdict
        liquidity_score, liquidity_label = self.estimate_liquidity(offer.title)

        if discount_pct >= 20 and estimated_profit >= 2500:
            verdict = "🔥 ТОП ПРОПОЗИЦІЯ (Високий прибуток!)"
        elif discount_pct >= 12 and estimated_profit >= 1500:
            verdict = "⭐ ВИГІДНА ЦІНА (Гарна маржа)"
        elif discount_pct > 0:
            verdict = "👍 Трохи дешевше ринку"
        else:
            verdict = "⚖️ По ринку або вище"

        valuation = DealValuation(
            market_price=market_price,
            discount_pct=discount_pct,
            quick_resale_price=quick_resale,
            normal_resale_price=normal_resale,
            estimated_profit=estimated_profit,
            liquidity_score=liquidity_score,
            liquidity_label=liquidity_label,
            verdict=verdict,
        )

        # Attach metrics directly to offer
        offer.market_price = market_price
        offer.discount_pct = discount_pct
        offer.resale_price = quick_resale
        offer.estimated_profit = estimated_profit
        offer.liquidity_score = liquidity_score
        offer.liquidity_label = liquidity_label
        offer.deal_verdict = verdict

        return valuation
