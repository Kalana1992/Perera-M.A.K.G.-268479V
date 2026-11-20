CREATE OR REPLACE VIEW vw_delivery_performance AS

WITH delivered_orders AS (
    SELECT
        order_id,
        customer_id,
        order_purchase_timestamp,
        order_delivered_carrier_date,
        order_delivered_customer_date,
        order_estimated_delivery_date,

        DATE_DIFF(
            'day',
            CAST(order_purchase_timestamp AS DATE),
            CAST(order_delivered_customer_date AS DATE)
        ) AS delivery_duration_days,

        DATE_DIFF(
            'day',
            CAST(order_estimated_delivery_date AS DATE),
            CAST(order_delivered_customer_date AS DATE)
        ) AS delivery_difference_days

    FROM orders
    WHERE order_status = 'delivered'
      AND order_delivered_customer_date IS NOT NULL
      AND order_estimated_delivery_date IS NOT NULL
)

SELECT
    order_id,
    customer_id,
    order_purchase_timestamp,
    order_delivered_carrier_date,
    order_delivered_customer_date,
    order_estimated_delivery_date,
    delivery_duration_days,
    delivery_difference_days,

    CASE
        WHEN delivery_difference_days > 0 THEN 'LATE'
        ELSE 'ON_TIME_OR_EARLY'
    END AS delivery_status,

    CASE
        WHEN delivery_difference_days > 0 THEN 1
        ELSE 0
    END AS late_delivery_flag

FROM delivered_orders;
