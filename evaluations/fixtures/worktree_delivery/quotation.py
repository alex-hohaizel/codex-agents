"""Quote formatting used by the synthetic service."""

from __future__ import annotations

from decimal import Decimal


def quote(raw_price: str, quantity: int) -> dict[str, str | int]:
    return {"quantity": quantity, "total": str(Decimal(raw_price) * quantity)}
