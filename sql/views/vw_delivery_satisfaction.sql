CREATE OR REPLACE VIEW vw_delivery_satisfaction AS

WITH order_reviews_aggregated AS (
    SELECT
        order_id,
        COUNT(*) AS review_count,
        ROUND(AVG(review_score), 2) AS average_review_score,
        COUNT(*) FILTER (
            WHERE review_score <= 2
        ) AS negative_review_count
    FROM order_reviews
    GROUP BY order_id
)

SELECT
    dp.order_id,
    dp.delivery_status,
    dp.delivery_duration_days,
    dp.delivery_difference_days,
    dp.late_delivery_flag,

    r.review_count,
    r.average_review_score,

    CASE
        WHEN r.average_review_score <= 2
            THEN 'NEGATIVE'
        WHEN r.average_review_score < 4
            THEN 'NEUTRAL'
        ELSE 'POSITIVE'
    END AS customer_sentiment

FROM vw_delivery_performance dp

INNER JOIN order_reviews_aggregated r
    ON dp.order_id = r.order_id;
