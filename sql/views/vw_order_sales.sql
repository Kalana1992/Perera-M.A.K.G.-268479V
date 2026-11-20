
-- =========================================================
-- View: Order-Level Sales Analytics
-- Purpose: Consolidate sales, payments and order details
-- Grain: One row per order
-- =========================================================

CREATE OR REPLACE VIEW vw_order_sales AS

WITH item_summary AS (

    SELECT
        order_id,
        COUNT(*) AS total_items,
        SUM(price) AS merchandise_value,
        SUM(freight_value) AS freight_value,
        SUM(price + freight_value) AS total_order_value

    FROM order_items
    GROUP BY order_id

),

payment_summary AS (

    SELECT
        order_id,
        COUNT(*) AS payment_record_count,
        SUM(payment_value) AS total_payment_value,
        COUNT(DISTINCT payment_type) AS payment_method_count,
        STRING_AGG(
            DISTINCT payment_type,
            ', ' ORDER BY payment_type
        ) AS payment_methods

    FROM order_payments
    GROUP BY order_id

)

SELECT

    o.order_id,
    o.customer_id,
    o.order_status,

    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,

    COALESCE(i.total_items, 0) AS total_items,
    COALESCE(i.merchandise_value, 0) AS merchandise_value,
    COALESCE(i.freight_value, 0) AS freight_value,
    COALESCE(i.total_order_value, 0) AS total_order_value,

    COALESCE(p.payment_record_count, 0)
        AS payment_record_count,

    COALESCE(p.total_payment_value, 0)
        AS total_payment_value,

    COALESCE(p.payment_method_count, 0)
        AS payment_method_count,

    p.payment_methods

FROM orders o

LEFT JOIN item_summary i
    ON o.order_id = i.order_id

LEFT JOIN payment_summary p
    ON o.order_id = p.order_id;
