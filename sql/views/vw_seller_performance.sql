CREATE OR REPLACE VIEW vw_seller_performance AS

WITH seller_sales AS (
    SELECT
        seller_id,
        COUNT(*) AS total_items_sold,
        COUNT(DISTINCT order_id) AS total_orders,
        ROUND(SUM(price), 2) AS merchandise_revenue,
        ROUND(SUM(freight_value), 2) AS freight_revenue,
        ROUND(SUM(price + freight_value), 2) AS total_sales_value
    FROM order_items
    GROUP BY seller_id
),

seller_orders AS (
    SELECT DISTINCT
        seller_id,
        order_id
    FROM order_items
),

seller_delivery AS (
    SELECT
        so.seller_id,
        COUNT(dp.order_id) AS delivered_orders,
        SUM(dp.late_delivery_flag) AS late_deliveries,
        ROUND(AVG(dp.delivery_duration_days), 2)
            AS average_delivery_days,
        ROUND(100.0 * AVG(dp.late_delivery_flag), 2)
            AS late_delivery_percentage
    FROM seller_orders so
    LEFT JOIN vw_delivery_performance dp
        ON so.order_id = dp.order_id
    GROUP BY so.seller_id
)

SELECT
    s.seller_id,
    s.seller_city,
    s.seller_state,
    ss.total_orders,
    ss.total_items_sold,
    ss.merchandise_revenue,
    ss.freight_revenue,
    ss.total_sales_value,
    COALESCE(sd.delivered_orders, 0) AS delivered_orders,
    COALESCE(sd.late_deliveries, 0) AS late_deliveries,
    sd.average_delivery_days,
    sd.late_delivery_percentage

FROM sellers s
LEFT JOIN seller_sales ss
    ON s.seller_id = ss.seller_id
LEFT JOIN seller_delivery sd
    ON s.seller_id = sd.seller_id;
