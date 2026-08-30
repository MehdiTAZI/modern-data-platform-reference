from __future__ import annotations

import csv
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

BASE = datetime(2026, 8, 29, 10, 0, tzinfo=UTC)

CUSTOMERS = [
    {
        "customer_id": "C001",
        "first_name": "Aya",
        "last_name": "Ben",
        "email": "aya@example.com",
        "updated_at": "2026-08-29T09:00:00Z",
    },
    {
        "customer_id": "C002",
        "first_name": "Noah",
        "last_name": "Lee",
        "email": "noah@example.com",
        "updated_at": "2026-08-29T09:01:00Z",
    },
    {
        "customer_id": "C001",
        "first_name": "Aya",
        "last_name": "Bennani",
        "email": "aya@example.com",
        "updated_at": "2026-08-29T09:10:00Z",
    },
    {
        "customer_id": "C003",
        "first_name": "Bad",
        "last_name": "Email",
        "email": "not-an-email",
        "updated_at": "2026-08-29T09:11:00Z",
    },
]

REFERENCE_CATCHUP_CUSTOMERS = [
    {
        "customer_id": "C999",
        "first_name": "Late",
        "last_name": "Reference",
        "email": "late.reference@example.com",
        # The file arrives later, but the business-effective customer state predates order O003.
        "updated_at": "2026-08-29T09:30:00Z",
    }
]

PRODUCTS = [
    {
        "product_id": "P001",
        "name": "Running Shoe",
        "unit_price": "89.90",
        "updated_at": "2026-08-29T09:00:00Z",
    },
    {
        "product_id": "P002",
        "name": "Backpack",
        "unit_price": "49.00",
        "updated_at": "2026-08-29T09:00:00Z",
    },
    {
        "product_id": "P003",
        "name": "Broken Price",
        "unit_price": "-5.00",
        "updated_at": "2026-08-29T09:00:00Z",
    },
]


def _order(order_id: str, customer: str, product: str, qty: int, minutes: int) -> dict:
    return {
        "event_id": f"EV-{order_id}",
        "order_id": order_id,
        "customer_id": customer,
        "product_id": product,
        "quantity": qty,
        "unit_price": 10.0,
        "event_time": (BASE + timedelta(minutes=minutes)).isoformat().replace("+00:00", "Z"),
    }


ORDERS = [
    _order("O001", "C001", "P001", 1, 0),
    _order("O002", "C002", "P002", 2, 1),
    _order("O002", "C002", "P002", 2, 1),  # duplicate event
    _order("O003", "C999", "P001", 1, 2),  # unknown until recovery/customer catch-up
    _order("O004", "C001", "P001", -1, 3),  # invalid qty
    _order("O005", "C001", "P002", 1, -180),  # deliberately late
]


def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def generate(out: str | Path) -> Path:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)

    _write_csv(out / "customers.csv", CUSTOMERS)
    _write_csv(out / "products.csv", PRODUCTS)

    with (out / "orders.jsonl").open("w", encoding="utf-8") as file:
        for row in ORDERS:
            file.write(json.dumps(row) + "\n")
        file.write('{"event_id":"EV-CORRUPT",bad-json}\n')

    recovery = out / "recovery"
    recovery.mkdir(parents=True, exist_ok=True)
    _write_csv(recovery / "customers-reference-catchup.csv", REFERENCE_CATCHUP_CUSTOMERS)

    return out
