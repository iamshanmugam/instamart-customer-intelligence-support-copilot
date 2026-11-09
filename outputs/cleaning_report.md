# Data Cleaning Report

- Customers: 506 -> 500 (dedupe by customer_id)
- Orders: 3829 -> 3829 (invalid customers/amounts handled)
- Tickets: 800 -> 800
- Policy rows: 5

## Decisions
- City/gender standardized; placeholder email for missing emails (not dropped).
- Negative/zero order amounts imputed with median.
- Orders/tickets without valid customer_id removed.