"""
Unit tests for OLX Deal Sniper components.
"""

import tempfile
from pathlib import Path

from filter import DealFilter
from models import Offer, SearchTarget
from scraper import OLXScraper
from storage import Storage


def test_offer_price_drop_calculation():
    offer = Offer(
        id=1,
        title="iPhone 15 Pro",
        url="https://olx.ua/test",
        price=30000,
        is_price_drop=True,
        old_price=35000,
    )
    # (35000 - 30000) / 35000 = 14.28% -> 14.3%
    assert offer.price_drop_percent == 14.3


def test_filter_price_range():
    flt = DealFilter(global_stop_words=["дефект"])
    target = SearchTarget(name="Test", min_price=10000, max_price=20000)

    # Valid price
    offer_ok = Offer(id=1, title="iPhone 13", url="url", price=15000)
    passes, _ = flt.evaluate(offer_ok, target)
    assert passes is True

    # Too cheap
    offer_cheap = Offer(id=2, title="iPhone 13", url="url", price=5000)
    passes, reason = flt.evaluate(offer_cheap, target)
    assert passes is False
    assert "нижча за мінімум" in reason

    # Too expensive
    offer_exp = Offer(id=3, title="iPhone 13", url="url", price=25000)
    passes, reason = flt.evaluate(offer_exp, target)
    assert passes is False
    assert "вища за максимум" in reason


def test_filter_stop_words():
    flt = DealFilter(global_stop_words=["на запчастини", "дефект"])
    target = SearchTarget(name="Test", stop_words=["чохол", "коробка"])

    # Global stop-word
    offer_bad_global = Offer(id=1, title="iPhone 14 на запчастини", url="url", price=15000)
    passes, reason = flt.evaluate(offer_bad_global, target)
    assert passes is False
    assert "Знайдено стоп-слово: 'на запчастини'" in reason

    # Target specific stop-word
    offer_bad_target = Offer(id=2, title="Оригінальний чохол iPhone 14", url="url", price=15000)
    passes, reason = flt.evaluate(offer_bad_target, target)
    assert passes is False
    assert "Знайдено стоп-слово: 'чохол'" in reason

    # Clean title
    offer_clean = Offer(id=3, title="iPhone 14 128GB Neverlock", url="url", price=15000)
    passes, _ = flt.evaluate(offer_clean, target)
    assert passes is True


def test_filter_whitelist():
    flt = DealFilter(global_stop_words=[])
    target = SearchTarget(name="MacBook M1", whitelist=["m1", "m2"])

    offer_matches = Offer(id=1, title="Apple MacBook Air M1 256GB", url="url", price=20000)
    passes, _ = flt.evaluate(offer_matches, target)
    assert passes is True

    offer_no_match = Offer(id=2, title="Apple MacBook Air Intel Core i5", url="url", price=20000)
    passes, reason = flt.evaluate(offer_no_match, target)
    assert passes is False
    assert "білого списку" in reason


def test_filter_local_priority_tagging():
    flt = DealFilter(
        global_stop_words=[],
        priority_region_id=13,
        priority_region_name="Івано-Франківськ",
        priority_cities=["калуш", "коломия", "надвірна"],
    )
    target = SearchTarget(name="Test")

    # Local by region_id
    offer_by_id = Offer(
        id=1,
        title="iPhone 13",
        url="url",
        region_id=13,
        region="Івано-Франківська область",
        city="Івано-Франківськ",
    )
    flt.evaluate(offer_by_id, target)
    assert offer_by_id.is_local is True

    # Local by town name (e.g. Kalush)
    offer_by_town = Offer(
        id=2,
        title="iPhone 13",
        url="url",
        region_id=99,
        region="Область",
        city="Калуш",
    )
    flt.evaluate(offer_by_town, target)
    assert offer_by_town.is_local is True

    # Non-local (Kyiv)
    offer_kyiv = Offer(
        id=3,
        title="iPhone 13",
        url="url",
        region_id=25,
        region="Київська область",
        city="Київ",
    )
    flt.evaluate(offer_kyiv, target)
    assert offer_kyiv.is_local is False


def test_storage_deduplication_and_price_drops():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "test_seen.db")
        storage = Storage(db_path)

        offer = Offer(
            id=101,
            title="iPhone 13 128GB",
            url="https://olx.ua/test-101",
            price=20000,
            city="Івано-Франківськ",
            region="Івано-Франківська область",
        )

        # 1. First time seeing offer
        is_new, old_price = storage.check_and_update(offer)
        assert is_new is True
        assert old_price is None

        # 2. Second time seeing same offer with same price
        is_new_2, old_price_2 = storage.check_and_update(offer)
        assert is_new_2 is False
        assert old_price_2 is None

        # 3. Third time seeing offer with LOWER price (price drop!)
        offer.price = 18000
        is_new_3, old_price_3 = storage.check_and_update(offer)
        assert is_new_3 is False
        assert old_price_3 == 20000
        assert offer.is_price_drop is True
        assert offer.old_price == 20000

        # Verify stats
        stats = storage.get_stats()
        assert stats["total_offers"] == 1
        assert stats["total_price_drops"] == 1


def test_scraper_build_params():
    scraper = OLXScraper()
    target = SearchTarget(
        name="Test Target",
        query="playstation 5",
        min_price=12000,
        max_price=18000,
        region_id=13,
    )
    params = scraper._build_params(target, limit=25)
    assert params["query"] == "playstation 5"
    assert params["filter_float_price:from"] == 12000
    assert params["filter_float_price:to"] == 18000
    assert params["region_id"] == 13
    assert params["limit"] == 25
    assert params["sort_by"] == "created_at:desc"
