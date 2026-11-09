-- Instamart capstone — SQL against database/Instamart_DB.sqlite
-- Schema after Part A cleaning: status, order_ts, delivery_minutes

SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'tickets', COUNT(*) FROM tickets
UNION ALL
SELECT 'products', COUNT(*) FROM products;

SELECT status, COUNT(*) AS order_count
FROM orders
GROUP BY status
ORDER BY order_count DESC;

SELECT
    COUNT(*) AS completed_orders,
    ROUND(SUM(order_amount), 4) AS total_revenue,
    ROUND(AVG(order_amount), 4) AS avg_order_value
FROM orders
WHERE status = 'completed';

SELECT
    o.customer_id,
    MAX(o.order_ts) AS last_order_ts,
    COUNT(DISTINCT o.order_id) AS frequency,
    ROUND(SUM(o.order_amount), 2) AS monetary
FROM orders o
WHERE o.status = 'completed'
GROUP BY o.customer_id
ORDER BY monetary DESC
LIMIT 10;

SELECT true_category, COUNT(*) AS ticket_count
FROM tickets
GROUP BY true_category
ORDER BY ticket_count DESC;

SELECT order_id, customer_id, order_ts, status, order_amount, delivery_minutes
FROM orders
WHERE order_id = 'ORD-100001';

SELECT c.customer_id, c.city, c.signup_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL
LIMIT 20;
