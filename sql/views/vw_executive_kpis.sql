CREATE OR REPLACE VIEW vw_executive_kpis AS

SELECT
    (SELECT COUNT(*) FROM orders)
        AS total_orders,

    (SELECT COUNT(DISTINCT customer_unique_id)
     FROM customers)
        AS unique_customers,

    (SELECT COUNT(*) FROM sellers)
        AS total_sellers,

    (SELECT COUNT(*) FROM products)
        AS total_products,

    (SELECT ROUND(SUM(total_order_value), 2)
     FROM vw_order_sales)
        AS total_sales,

    (SELECT ROUND(AVG(total_order_value), 2)
     FROM vw_order_sales)
        AS average_order_value,

    (SELECT ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE delivery_status = 'LATE'
        ) / COUNT(*), 2
     )
     FROM vw_delivery_performance)
        AS late_delivery_percentage,

    (SELECT ROUND(AVG(review_score), 2)
     FROM order_reviews)
        AS average_review_score;
