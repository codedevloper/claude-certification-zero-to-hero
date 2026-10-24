"""Unit tests for invoicing.totals, using synthetic line items only."""
import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from invoicing.totals import invoice_total, subtotal  # noqa: E402

ITEMS = [("Pallet transport Rotterdam-Lyon", 3, Decimal("280.00")), ("Tail-lift surcharge", 1, Decimal("45.50"))]


class TotalsTest(unittest.TestCase):
    def test_subtotal(self):
        self.assertEqual(subtotal(ITEMS), Decimal("885.50"))

    def test_total_with_discount_and_vat(self):
        self.assertEqual(invoice_total(ITEMS, discount_pct=Decimal("10")), Decimal("956.34"))

    def test_rejects_negative_price(self):
        with self.assertRaises(ValueError):
            subtotal([("Refund line", 1, Decimal("-5"))])

    def test_rejects_bad_discount(self):
        with self.assertRaises(ValueError):
            invoice_total(ITEMS, discount_pct=Decimal("120"))


if __name__ == "__main__":
    unittest.main()
