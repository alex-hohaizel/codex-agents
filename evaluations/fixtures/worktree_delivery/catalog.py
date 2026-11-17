"""Small catalog containing synthetic produce and fixed unit prices."""

PRICES = {"PEAR-7": "1.25", "PLUM-2": "2.05"}


def sku_key(raw: str) -> str:
    """Return an exact known catalog entry."""
    if raw not in PRICES:
        raise ValueError("unknown sku")
    return raw
