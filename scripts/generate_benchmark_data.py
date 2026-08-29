from __future__ import annotations

import argparse
import csv
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

BASE = datetime(2026, 8, 29, 10, 0, tzinfo=UTC)


def generate(out: Path, customer_count: int, product_count: int, order_count: int) -> Path:
    out.mkdir(parents=True, exist_ok=True)

    with (out / "customers.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file, fieldnames=["customer_id", "first_name", "last_name", "email", "updated_at"]
        )
        writer.writeheader()
        for index in range(customer_count):
            writer.writerow(
                {
                    "customer_id": f"C{index:07d}",
                    "first_name": "Customer",
                    "last_name": f"{index:07d}",
                    "email": f"customer{index}@example.com",
                    "updated_at": BASE.isoformat().replace("+00:00", "Z"),
                }
            )

    with (out / "products.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["product_id", "name", "unit_price", "updated_at"])
        writer.writeheader()
        for index in range(product_count):
            writer.writerow(
                {
                    "product_id": f"P{index:05d}",
                    "name": f"Product {index:05d}",
                    "unit_price": f"{10 + (index % 190):.2f}",
                    "updated_at": BASE.isoformat().replace("+00:00", "Z"),
                }
            )

    with (out / "orders.jsonl").open("w", encoding="utf-8") as file:
        for index in range(order_count):
            event_time = BASE + timedelta(seconds=index % 86_400)
            row = {
                "event_id": f"EV-{index:012d}",
                "order_id": f"O{index:012d}",
                "customer_id": f"C{index % customer_count:07d}",
                "product_id": f"P{index % product_count:05d}",
                "quantity": 1 + index % 4,
                "unit_price": float(10 + (index % 190)),
                "event_time": event_time.isoformat().replace("+00:00", "Z"),
            }
            file.write(json.dumps(row, separators=(",", ":")) + "\n")

    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic benchmark input data")
    parser.add_argument("--out", default="sample_data/benchmark")
    parser.add_argument("--customers", type=int, default=10_000)
    parser.add_argument("--products", type=int, default=1_000)
    parser.add_argument("--orders", type=int, default=100_000)
    args = parser.parse_args()

    if min(args.customers, args.products, args.orders) < 1:
        raise SystemExit("customers, products and orders must all be positive")

    print(generate(Path(args.out), args.customers, args.products, args.orders))


if __name__ == "__main__":
    main()
