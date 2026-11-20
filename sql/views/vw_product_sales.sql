

-- =========================================================
-- View: Product and Category Sales Analytics
-- Purpose: Analyse product-level sales performance
-- Grain: One row per product
-- =========================================================

CREATE OR REPLACE VIEW vw_product_sales AS

SELECT

    p.product_id,

    p.product_category_name,

    COALESCE(
        t.product_category_name_english,
        'Unknown'
    ) AS product_category_english,

    COUNT(oi.order_id) AS total_item_records,

    COUNT(DISTINCT oi.order_id) AS total_orders,

    COUNT(DISTINCT oi.seller_id) AS total_sellers,

    ROUND(SUM(oi.price), 2) AS merchandise_revenue,

    ROUND(SUM(oi.freight_value), 2) AS freight_revenue,

    ROUND(
        SUM(oi.price + oi.freight_value),
        2
    ) AS total_sales_value

FROM products p

LEFT JOIN category_translation t
    ON p.product_category_name = t.product_category_name

LEFT JOIN order_items oi
    ON p.product_id = oi.product_id

GROUP BY
    p.product_id,
    p.product_category_name,
    t.product_category_name_english;
