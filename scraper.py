"""
Scraper module for OLX API with Cloudflare/CloudFront bypass using curl_cffi TLS impersonation.
"""

import asyncio
import logging
import re
from typing import ClassVar
from urllib.parse import parse_qs, unquote, urlparse

from curl_cffi.requests import AsyncSession

from models import Offer, SearchTarget

logger = logging.getLogger(__name__)


class OLXScraper:
    API_URL = "https://www.olx.ua/api/v1/offers/"

    DEFAULT_HEADERS: ClassVar[dict[str, str]] = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.olx.ua/",
    }

    FALLBACK_PROFILES: ClassVar[list[str]] = ["chrome120", "chrome124", "edge101"]

    def __init__(self, impersonate_profile: str = "chrome120", proxy: str | None = None):
        self.impersonate_profile = impersonate_profile
        self.proxy = proxy
        self.session: AsyncSession | None = None
        self._active_profile: str | None = None

    async def _get_session(self, profile: str | None = None) -> AsyncSession:
        target_profile = profile or self.impersonate_profile
        if self.session is not None and target_profile != self._active_profile:
            await self.close()
        if self.session is None:
            self.session = AsyncSession(
                impersonate=target_profile,
                headers=self.DEFAULT_HEADERS,
                proxy=self.proxy,
                timeout=30.0,
            )
            self._active_profile = target_profile
        return self.session

    async def close(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None
            self._active_profile = None

    def _build_params(self, target: SearchTarget, limit: int = 20) -> dict:
        """
        Builds query parameters for the OLX API from a SearchTarget.
        Supports both query parameters and path-based OLX search URLs (/q-query/).
        """
        params = {
            "offset": 0,
            "limit": limit,
            "sort_by": "created_at:desc",
        }

        # If a full URL is provided in target.url, extract query params
        if target.url:
            parsed = urlparse(target.url)
            qs = parse_qs(parsed.query)

            if "query" in qs:
                params["query"] = qs["query"][0]
            elif "/q-" in parsed.path:
                match = re.search(r"/q-([^/]+)", parsed.path)
                if match:
                    params["query"] = unquote(match.group(1)).replace("-", " ")

            if "search[filter_float_price:from]" in qs:
                params["filter_float_price:from"] = qs["search[filter_float_price:from]"][0]
            if "search[filter_float_price:to]" in qs:
                params["filter_float_price:to"] = qs["search[filter_float_price:to]"][0]
            if "category_id" in qs:
                params["category_id"] = qs["category_id"][0]

        # Explicit target fields take precedence
        if target.query:
            params["query"] = target.query
        if target.min_price is not None:
            params["filter_float_price:from"] = target.min_price
        if target.max_price is not None:
            params["filter_float_price:to"] = target.max_price
        if target.category_id is not None:
            params["category_id"] = target.category_id
        if target.region_id is not None:
            params["region_id"] = target.region_id

        return params

    def _parse_offer(self, item: dict) -> Offer | None:
        """
        Parses a single JSON offer from OLX API into an Offer model with null safety.
        """
        try:
            offer_id = item.get("id")
            title = item.get("title")
            url = item.get("url")

            if not offer_id or not title or not url:
                return None

            # Extract price info from params list
            price_val = None
            price_label = None
            currency = "UAH"

            for param in item.get("params") or []:
                if param.get("key") == "price":
                    val_data = param.get("value") or {}
                    price_val = val_data.get("value")
                    price_label = val_data.get("label")
                    currency = val_data.get("currency") or "UAH"
                    break

            parsed_price = None
            if price_val is not None:
                try:
                    parsed_price = int(float(price_val))
                except (ValueError, TypeError):
                    parsed_price = None

            # Extract location safely against null fields
            loc = item.get("location") or {}
            city_data = loc.get("city") or {}
            city = city_data.get("name") or "Невідомо"
            region_data = loc.get("region") or {}
            region = region_data.get("name") or "Україна"
            region_id = region_data.get("id")

            # Extract photo (high quality)
            photo_url = None
            photos = item.get("photos") or []
            if photos:
                raw_photo = photos[0].get("link") or ""
                if raw_photo:
                    photo_url = raw_photo.replace("{width}", "800").replace("{height}", "600")

            return Offer(
                id=offer_id,
                title=title,
                url=url,
                price=parsed_price,
                currency=currency,
                price_label=price_label,
                created_time=item.get("created_time"),
                city=city,
                region=region,
                region_id=region_id,
                photo_url=photo_url,
            )
        except Exception as e:  # noqa: BLE001
            logger.debug(f"Error parsing offer {item.get('id')}: {e}")
            return None

    async def fetch_offers(self, target: SearchTarget, limit: int = 20, retries: int = 3) -> list[Offer]:
        """
        Fetches latest offers for a target with automatic retries and TLS session rotation.
        """
        params = self._build_params(target, limit=limit)

        for attempt in range(1, retries + 1):
            profile = self.FALLBACK_PROFILES[(attempt - 1) % len(self.FALLBACK_PROFILES)]
            session = await self._get_session(profile=profile)
            try:
                response = await session.get(self.API_URL, params=params)

                if response.status_code == 200:
                    data = response.json()
                    raw_items = data.get("data") or []
                    offers = []
                    for item in raw_items:
                        parsed = self._parse_offer(item)
                        if parsed:
                            offers.append(parsed)
                    logger.debug(f"Fetched {len(offers)} offers for '{target.name}'")
                    return offers

                elif response.status_code in (403, 429):
                    logger.warning(
                        f"Rate limit / Cloudflare challenge (HTTP {response.status_code}) on attempt {attempt}/{retries}. "
                        "Rotating TLS session and backing off..."
                    )
                    await self.close()
                    await asyncio.sleep(3 * attempt)

                else:
                    logger.warning(
                        f"OLX API returned HTTP {response.status_code} for target '{target.name}'. Attempt {attempt}/{retries}"
                    )
                    await asyncio.sleep(2 * attempt)

            except Exception as e:  # noqa: BLE001
                logger.warning(f"Тимчасова затримка мережі для '{target.name}' (спроба {attempt}/{retries}): {e}")
                await self.close()
                await asyncio.sleep(2 * attempt)

        logger.error(f"Не вдалося отримати дані для '{target.name}' після {retries} спроб.")
        return []
