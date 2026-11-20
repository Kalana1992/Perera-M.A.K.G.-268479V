CREATE OR REPLACE VIEW vw_installment_performance AS

SELECT
    payment_installments,

    COUNT(*) AS payment_records,

    COUNT(DISTINCT order_id) AS unique_orders,

    ROUND(SUM(payment_value), 2) AS total_payment_value,

    ROUND(AVG(payment_value), 2) AS average_payment_value,

    ROUND(
        100.0 * COUNT(*) /
        SUM(COUNT(*)) OVER (),
        2
    ) AS payment_record_percentage

FROM order_payments

WHERE payment_type = 'credit_card'

GROUP BY payment_installments;
