CREATE OR REPLACE VIEW vw_seller_geographic_performance AS

SELECT
    s.seller_state,

    COUNT(DISTINCT s.seller_id) AS total_sellers,

    COUNT(DISTINCT oi.order_id) AS total_orders,

    COUNT(*) AS total_items_sold,

    ROUND(SUM(oi.price), 2) AS merchandise_revenue,

    ROUND(SUM(oi.freight_value), 2) AS freight_revenue,

    ROUND(
        SUM(oi.price + oi.freight_value), 2
    ) AS total_sales_value,

    ROUND(
        SUM(oi.price + oi.freight_value) /
        NULLIF(COUNT(DISTINCT s.seller_id), 0),
        2
    ) AS average_sales_per_seller

FROM sellers s

JOIN order_items oi
    ON s.seller_id = oi.seller_id

GROUP BY s.seller_state;
