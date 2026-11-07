"""
Filtering logic for deals, stop words, price ranges, and local priority.
"""

import re

from models import Offer, SearchTarget


class DealFilter:
    def __init__(
        self,
        global_stop_words: list[str],
        priority_region_id: int = 13,
        priority_region_name: str = "Івано-Франківськ",
        priority_cities: list[str] | None = None,
    ):
        self.global_stop_words = [w.strip().lower() for w in global_stop_words if w.strip()]
        self.priority_region_id = priority_region_id
        self.priority_region_name = priority_region_name.lower()
        self.priority_cities = [c.strip().lower() for c in (priority_cities or []) if c.strip()]

    def evaluate(self, offer: Offer, target: SearchTarget) -> tuple[bool, str]:
        """
        Evaluates whether an offer matches the target criteria.
        Returns: (passes_filter: bool, reason: str)
        """
        title_lower = offer.title.lower()

        # 1. Price checks
        if offer.price is not None:
            if target.min_price is not None and offer.price < target.min_price:
                return False, f"Ціна {offer.price} нижча за мінімум {target.min_price}"
            if target.max_price is not None and offer.price > target.max_price:
                return False, f"Ціна {offer.price} вища за максимум {target.max_price}"
        elif target.min_price is not None or target.max_price is not None:
            return False, "Ціна не вказана (пропуск для цільового пошуку з ціновими межами)"

        # 2. Stop-words checking with word boundaries to avoid false positives (e.g. 'диск' in 'дисконт')
        combined_stop_words = self.global_stop_words + [
            w.strip().lower() for w in target.stop_words if w.strip()
        ]

        for stop_word in combined_stop_words:
            # Match word boundary or exact phrase
            pattern = rf"\b{re.escape(stop_word)}\b"
            if re.search(pattern, title_lower):
                return False, f"Знайдено стоп-слово: '{stop_word}'"

        # 3. Whitelist checking (if specified, at least one must be present)
        if target.whitelist:
            whitelist_lower = [w.strip().lower() for w in target.whitelist if w.strip()]
            matches = [w for w in whitelist_lower if re.search(rf"\b{re.escape(w)}\b", title_lower)]
            if not matches:
                return False, "Не містить жодного слова з обов'язкового білого списку"

        # 4. Check if offer is from local priority region (Ivano-Frankivsk and region)
        is_local_region = (
            (offer.region_id is not None and offer.region_id == self.priority_region_id)
            or (self.priority_region_name in offer.region.lower())
            or (self.priority_region_name in offer.city.lower())
            or any(town in offer.city.lower() for town in self.priority_cities)
        )

        offer.is_local = is_local_region

        return True, "Підходить під усі критерії"
