CREATE OR REPLACE VIEW vw_payment_performance AS

WITH payment_summary AS (
    SELECT
        order_id,
        COUNT(*) AS payment_record_count,
        COUNT(DISTINCT payment_type) AS payment_method_count,
        STRING_AGG(
            DISTINCT payment_type,
            ', '
        ) AS payment_methods,
        SUM(payment_value) AS total_payment_value,
        SUM(payment_installments) AS total_installments,
        MAX(payment_installments) AS maximum_installments
    FROM order_payments
    GROUP BY order_id
)

SELECT
    order_id,
    payment_record_count,
    payment_method_count,
    payment_methods,
    ROUND(total_payment_value, 2) AS total_payment_value,
    total_installments,
    maximum_installments,

    CASE
        WHEN payment_method_count > 1 THEN 'MULTIPLE_METHODS'
        ELSE 'SINGLE_METHOD'
    END AS payment_method_category

FROM payment_summary;
