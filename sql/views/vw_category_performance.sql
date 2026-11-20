CREATE OR REPLACE VIEW vw_category_performance AS
SELECT
    ps.product_category_english,
    COUNT(DISTINCT ps.product_id) AS total_products,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    COUNT(oi.order_id) AS total_items,
    ROUND(COALESCE(SUM(oi.price), 0), 2) AS merchandise_revenue,
    ROUND(COALESCE(SUM(oi.freight_value), 0), 2) AS freight_revenue,
    ROUND(COALESCE(SUM(oi.price + oi.freight_value), 0), 2) AS total_sales_value,
    ROUND(
        COALESCE(SUM(oi.price), 0) / NULLIF(COUNT(oi.order_id), 0),
        2
    ) AS average_item_price
FROM vw_product_sales ps
LEFT JOIN order_items oi
    ON ps.product_id = oi.product_id
GROUP BY ps.product_category_english;
