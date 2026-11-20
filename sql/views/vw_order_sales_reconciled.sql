-- =========================================================
-- View: Order Sales Financial Reconciliation
-- Purpose: Independent financial data-quality indicators
-- Grain: One row per order
-- =========================================================

CREATE OR REPLACE VIEW vw_order_sales_reconciled AS

SELECT
    *,

    ROUND(
        total_payment_value - total_order_value,
        2
    ) AS payment_difference,

    CASE
        WHEN total_items = 0 THEN 1
        ELSE 0
    END AS missing_items_flag,

    CASE
        WHEN payment_record_count = 0 THEN 1
        ELSE 0
    END AS missing_payment_flag,

    CASE
        WHEN ABS(total_payment_value - total_order_value) > 0.01
            THEN 1
        ELSE 0
    END AS payment_mismatch_flag

FROM vw_order_sales;
