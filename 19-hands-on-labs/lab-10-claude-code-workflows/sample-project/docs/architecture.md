# Architecture notes

- `invoicing.totals` is a pure calculation module with no I/O, so it is safe to test in isolation.
- Callers pass line items as `(description, quantity, unit_price)` tuples with `Decimal` prices.
- VAT is applied to the discounted subtotal. The default VAT rate is 20% and callers may override it.
- A future `invoicing.export` module will write PDF invoices; it must never log line-item descriptions.
