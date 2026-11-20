CREATE OR REPLACE VIEW vw_monthly_sales_performance AS

WITH date_range AS (
    SELECT
        DATE_TRUNC('month', MIN(order_purchase_timestamp))::DATE AS first_month,
        DATE_TRUNC('month', MAX(order_purchase_timestamp))::DATE AS last_month
    FROM orders
),

monthly_totals AS (
    SELECT
        DATE_TRUNC('month', order_purchase_timestamp)::DATE AS sales_month,
        COUNT(*) AS total_orders,
        SUM(total_items) AS total_items,
        ROUND(SUM(merchandise_value), 2) AS merchandise_revenue,
        ROUND(SUM(freight_value), 2) AS freight_revenue,
        ROUND(SUM(total_order_value), 2) AS total_sales
    FROM vw_order_sales
    GROUP BY 1
)

SELECT
    m.*,
    CASE
        WHEN m.sales_month = d.first_month
          OR m.sales_month = d.last_month
        THEN 'PARTIAL_MONTH'
        ELSE 'FULL_MONTH'
    END AS month_coverage_status
FROM monthly_totals m
CROSS JOIN date_range d;
