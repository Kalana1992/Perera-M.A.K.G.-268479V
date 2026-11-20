CREATE OR REPLACE VIEW vw_customer_performance AS

WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        c.customer_city,
        c.customer_state,
        o.order_id,
        o.order_purchase_timestamp,
        os.total_order_value
    FROM customers c
    JOIN orders o
        ON c.customer_id = o.customer_id
    LEFT JOIN vw_order_sales os
        ON o.order_id = os.order_id
),

customer_summary AS (
    SELECT
        customer_unique_id,
        MAX(customer_city) AS customer_city,
        MAX(customer_state) AS customer_state,
        COUNT(DISTINCT order_id) AS total_orders,
        ROUND(SUM(total_order_value), 2) AS total_spending,
        ROUND(AVG(total_order_value), 2) AS average_order_value,
        MIN(order_purchase_timestamp) AS first_purchase_date,
        MAX(order_purchase_timestamp) AS last_purchase_date
    FROM customer_orders
    GROUP BY customer_unique_id
)

SELECT
    *,
    CASE
        WHEN total_orders = 1 THEN 'ONE_TIME'
        ELSE 'REPEAT_CUSTOMER'
    END AS customer_type
FROM customer_summary;
