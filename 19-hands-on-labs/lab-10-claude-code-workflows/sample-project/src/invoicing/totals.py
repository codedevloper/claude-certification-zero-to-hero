"""Invoice maths for the fictional Acme Logistics invoicing service."""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

LineItem = tuple[str, int, Decimal]
CENT = Decimal("0.01")


def subtotal(items: list[LineItem]) -> Decimal:
    """Return the sum of quantity x unit price. Raises ValueError on negative values."""
    total = Decimal("0")
    for description, quantity, unit_price in items:
        if quantity < 0 or unit_price < 0:
            raise ValueError(f"negative quantity or price on line {description!r}")
        total += quantity * unit_price
    return total


def invoice_total(items: list[LineItem], discount_pct: Decimal = Decimal("0"), vat_pct: Decimal = Decimal("20")) -> Decimal:
    """Return the total after discount, then VAT, rounded half-up to cents."""
    if not Decimal("0") <= discount_pct <= Decimal("100"):
        raise ValueError("discount_pct must be between 0 and 100")
    discounted = subtotal(items) * (1 - discount_pct / 100)
    return (discounted * (1 + vat_pct / 100)).quantize(CENT, rounding=ROUND_HALF_UP)
