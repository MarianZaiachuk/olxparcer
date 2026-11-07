"""
SQLite storage for tracking seen ads and price drop history.
"""

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from models import Offer


class Storage:
    def __init__(self, db_path: str = "data/seen_ads.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS seen_offers (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    price INTEGER,
                    currency TEXT,
                    url TEXT,
                    city TEXT,
                    region TEXT,
                    first_seen_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    offer_id INTEGER NOT NULL,
                    old_price INTEGER NOT NULL,
                    new_price INTEGER NOT NULL,
                    changed_at TEXT NOT NULL,
                    FOREIGN KEY (offer_id) REFERENCES seen_offers(id)
                )
                """
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_price_history_offer_id ON price_history(offer_id)"
            )
            conn.commit()

    def check_and_update(self, offer: Offer) -> tuple[bool, int | None]:
        """
        Processes an offer:
        - If new: inserts into DB and returns (True, None).
        - If seen before and price dropped: records price drop, updates price, and returns (False, old_price).
        - If seen before and price increased: updates baseline price and returns (False, None).
        - If seen before with same price: updates timestamp and returns (False, None).
        """
        now_iso = datetime.now(UTC).isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, price FROM seen_offers WHERE id = ?", (offer.id,))
            row = cursor.fetchone()

            if row is None:
                # Brand new offer
                cursor.execute(
                    """
                    INSERT INTO seen_offers (
                        id, title, price, currency, url, city, region, first_seen_at, last_seen_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        offer.id,
                        offer.title,
                        offer.price,
                        offer.currency,
                        offer.url,
                        offer.city,
                        offer.region,
                        now_iso,
                        now_iso,
                    ),
                )
                conn.commit()
                return True, None

            # Already seen offer: check for price changes
            old_price = row["price"]

            if offer.price is not None and old_price is not None:
                if offer.price < old_price:
                    # Price dropped!
                    cursor.execute(
                        """
                        INSERT INTO price_history (offer_id, old_price, new_price, changed_at)
                        VALUES (?, ?, ?, ?)
                        """,
                        (offer.id, old_price, offer.price, now_iso),
                    )
                    cursor.execute(
                        """
                        UPDATE seen_offers
                        SET price = ?, last_seen_at = ?, title = ?
                        WHERE id = ?
                        """,
                        (offer.price, now_iso, offer.title, offer.id),
                    )
                    conn.commit()
                    offer.is_price_drop = True
                    offer.old_price = old_price
                    return False, old_price

                elif offer.price > old_price:
                    # Price increased (update baseline price so future drops calculate correctly)
                    cursor.execute(
                        """
                        UPDATE seen_offers
                        SET price = ?, last_seen_at = ?, title = ?
                        WHERE id = ?
                        """,
                        (offer.price, now_iso, offer.title, offer.id),
                    )
                    conn.commit()
                    return False, None

            # Price is unchanged or null - update last_seen_at
            cursor.execute(
                "UPDATE seen_offers SET last_seen_at = ? WHERE id = ?",
                (now_iso, offer.id),
            )
            conn.commit()
            return False, None

    def get_stats(self) -> dict[str, int]:
        """Returns statistics about tracked offers."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM seen_offers")
            total_offers = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM price_history")
            total_price_drops = cursor.fetchone()[0]

            return {
                "total_offers": total_offers,
                "total_price_drops": total_price_drops,
            }
