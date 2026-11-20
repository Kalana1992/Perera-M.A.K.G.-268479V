CREATE OR REPLACE VIEW vw_payment_method_performance AS

SELECT
    payment_type,

    COUNT(*) AS total_payment_records,

    COUNT(DISTINCT order_id) AS total_orders,

    ROUND(SUM(payment_value), 2) AS total_payment_value,

    ROUND(AVG(payment_value), 2) AS average_payment_value,

    ROUND(AVG(payment_installments), 2) AS average_installments,

    ROUND(
        100.0 * SUM(payment_value) /
        SUM(SUM(payment_value)) OVER (),
        2
    ) AS payment_value_percentage

FROM order_payments

GROUP BY payment_type;
