-- Instamart Co-Pilot — validation and analytics SQL
-- Database: database/Instamart_DB.sqlite (SQLite)
-- Run example: sqlite3 database/Instamart_DB.sqlite ".read sql/queries.sql"

-- ---------------------------------------------------------------------------
-- 1. Row counts per table (compare with outputs/db_validation.txt)
-- ---------------------------------------------------------------------------
SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'tickets', COUNT(*) FROM tickets;

-- ---------------------------------------------------------------------------
-- 2. Order status distribution
-- ---------------------------------------------------------------------------
SELECT order_status, COUNT(*) AS order_count
FROM orders
GROUP BY order_status
ORDER BY order_count DESC;

-- ---------------------------------------------------------------------------
-- 3. Completed-order revenue summary (aligns with EDA avg order value)
-- ---------------------------------------------------------------------------
SELECT
    COUNT(*) AS completed_orders,
    ROUND(SUM(order_amount), 2) AS total_revenue,
    ROUND(AVG(order_amount), 4) AS avg_order_value
FROM orders
WHERE order_status = 'Completed';

-- ---------------------------------------------------------------------------
-- 4. RFM-style customer metrics (completed orders only)
-- ---------------------------------------------------------------------------
SELECT
    o.customer_id,
    MAX(o.order_date) AS last_order_date,
    COUNT(DISTINCT o.order_id) AS frequency,
    ROUND(SUM(o.order_amount), 2) AS monetary
FROM orders o
WHERE o.order_status = 'Completed'
GROUP BY o.customer_id
ORDER BY monetary DESC
LIMIT 10;

-- ---------------------------------------------------------------------------
-- 5. Ticket category volume
-- ---------------------------------------------------------------------------
SELECT category_label, COUNT(*) AS ticket_count
FROM tickets
GROUP BY category_label
ORDER BY ticket_count DESC;

-- ---------------------------------------------------------------------------
-- 6. Parameterised order lookup pattern (used by refund agent)
-- ---------------------------------------------------------------------------
-- Replace :order_id when running from application code; example value below:
SELECT order_id, customer_id, order_date, order_status, order_amount, city
FROM orders
WHERE order_id = 'ORD000001';

-- ---------------------------------------------------------------------------
-- 7. Customers with no orders
-- ---------------------------------------------------------------------------
SELECT c.customer_id, c.city, c.registration_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL
LIMIT 20;
