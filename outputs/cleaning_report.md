# Data Cleaning Report

- Customers: 1200 -> 1200
- Orders: 13084 -> 12309
- Tickets: 164 -> 160
- Policy eval rows: 14
- Products: 40

## Decisions
- Cities normalised; invalid ages and negative delivery minutes set to missing.
- Duplicate order_id rows kept at latest order_ts.
- Empty ticket text removed.