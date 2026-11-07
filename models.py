"""
Data models for OLX Deal Sniper.
"""

from pydantic import BaseModel, Field, field_validator


class Offer(BaseModel):
    id: int
    title: str
    url: str
    price: int | None = None
    currency: str = "UAH"
    price_label: str | None = None
    created_time: str | None = None
    city: str = "Невідомо"
    region: str = "Україна"
    region_id: int | None = None
    photo_url: str | None = None
    is_local: bool = False
    is_price_drop: bool = False
    old_price: int | None = None
    # Market valuation & liquidity metrics
    market_price: int | None = None
    discount_pct: float | None = None
    resale_price: int | None = None
    estimated_profit: int | None = None
    liquidity_score: float | None = None
    liquidity_label: str | None = None
    deal_verdict: str | None = None

    @field_validator("city", mode="before")
    @classmethod
    def set_default_city(cls, v):
        return v if v else "Невідомо"

    @field_validator("region", mode="before")
    @classmethod
    def set_default_region(cls, v):
        return v if v else "Україна"

    @property
    def price_drop_percent(self) -> float | None:
        if self.is_price_drop and self.old_price and self.price and self.old_price > self.price:
            return round(((self.old_price - self.price) / self.old_price) * 100, 1)
        return None


class SearchTarget(BaseModel):
    name: str
    query: str | None = None
    url: str | None = None
    min_price: int | None = None
    max_price: int | None = None
    category_id: int | None = None
    region_id: int | None = None
    stop_words: list[str] = Field(default_factory=list)
    whitelist: list[str] = Field(default_factory=list)
