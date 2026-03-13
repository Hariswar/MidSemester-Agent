from __future__ import annotations

import sqlite3
from pathlib import Path

from app.data import OrderRecord


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "orders.db"


def _connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                carrier TEXT NOT NULL,
                tracking_number TEXT NOT NULL,
                destination_city TEXT NOT NULL,
                destination_state TEXT NOT NULL,
                expected_delivery_date TEXT NOT NULL,
                status TEXT NOT NULL
            )
            """
        )
        conn.executemany(
            """
            INSERT OR IGNORE INTO orders (
                order_id, customer_name, carrier, tracking_number,
                destination_city, destination_state, expected_delivery_date, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    "ORDER-1001",
                    "Alex Taylor",
                    "UPS",
                    "1Z999AA10123456784",
                    "Rolla",
                    "MO",
                    "2026-03-14",
                    "in transit",
                ),
                (
                    "ORDER-1002",
                    "Jordan Lee",
                    "FedEx",
                    "123456789012",
                    "St. Louis",
                    "MO",
                    "2026-03-15",
                    "label created",
                ),
            ],
        )


def get_order(order_id: str) -> OrderRecord | None:
    with _connection() as conn:
        row = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
        if not row:
            return None
        return OrderRecord(**dict(row))
