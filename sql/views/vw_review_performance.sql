CREATE OR REPLACE VIEW vw_review_performance AS

SELECT
    review_score,

    COUNT(*) AS total_reviews,

    COUNT(DISTINCT review_id) AS unique_review_ids,

    COUNT(DISTINCT order_id) AS reviewed_orders,

    ROUND(
        100.0 * COUNT(*) /
        SUM(COUNT(*)) OVER (),
        2
    ) AS review_percentage,

    CASE
        WHEN review_score <= 2 THEN 'NEGATIVE'
        WHEN review_score = 3 THEN 'NEUTRAL'
        ELSE 'POSITIVE'
    END AS sentiment_category

FROM order_reviews

GROUP BY review_score;
