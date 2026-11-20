CREATE OR REPLACE VIEW vw_geographic_performance AS

SELECT
    cu.customer_state,

    COUNT(DISTINCT cu.customer_unique_id)
        AS unique_customers,

    COUNT(DISTINCT o.order_id)
        AS total_orders,

    COUNT(DISTINCT o.customer_id)
        AS purchasing_customers,

    ROUND(
        SUM(os.merchandise_value), 2
    ) AS merchandise_revenue,

    ROUND(
        SUM(os.freight_value), 2
    ) AS freight_revenue,

    ROUND(
        SUM(os.total_order_value), 2
    ) AS total_sales_value,

    ROUND(
        SUM(os.total_order_value) /
        NULLIF(COUNT(DISTINCT o.order_id), 0),
        2
    ) AS average_order_value

FROM customers cu

JOIN orders o
    ON cu.customer_id = o.customer_id

JOIN vw_order_sales os
    ON o.order_id = os.order_id

GROUP BY cu.customer_state;
