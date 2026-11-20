
from pathlib import Path
import json

import duckdb


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = PROJECT_ROOT / "database" / "ecommerce.duckdb"

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "delivery_ml_dataset.csv"
)

REPORT_PATH = (
    PROJECT_ROOT
    / "reports"
    / "generated"
    / "delivery_ml_dataset_report.json"
)


# =========================================================
# SQL QUERY: DELIVERY ML DATASET
# =========================================================

QUERY = """
WITH eligible_orders AS (

    SELECT
        order_id,
        order_purchase_timestamp,
        order_approved_at,
        order_estimated_delivery_date,
        order_delivered_customer_date,
        customer_id,

        CASE
            WHEN CAST(order_delivered_customer_date AS DATE)
                 > CAST(order_estimated_delivery_date AS DATE)
            THEN 1
            ELSE 0
        END AS late_delivery_flag

    FROM orders

    WHERE order_status = 'delivered'
      AND order_approved_at IS NOT NULL
      AND order_delivered_customer_date IS NOT NULL
      AND order_estimated_delivery_date IS NOT NULL
),

item_features AS (

    SELECT
        oi.order_id,

        COUNT(*) AS item_count,
        COUNT(DISTINCT oi.seller_id) AS seller_count,

        SUM(oi.price) AS total_merchandise_value,
        SUM(oi.freight_value) AS total_freight_value,

        AVG(p.product_weight_g) AS avg_product_weight_g,
        AVG(p.product_length_cm) AS avg_product_length_cm,
        AVG(p.product_height_cm) AS avg_product_height_cm,
        AVG(p.product_width_cm) AS avg_product_width_cm,
        AVG(p.product_photos_qty) AS avg_product_photos_qty,

        MODE(p.product_category_name) AS dominant_product_category,
        MODE(s.seller_state) AS dominant_seller_state,

        COUNT(DISTINCT p.product_category_name)
            AS product_category_count,

        COUNT(DISTINCT s.seller_state)
            AS seller_state_count

    FROM order_items oi

    LEFT JOIN products p
        ON oi.product_id = p.product_id

    LEFT JOIN sellers s
        ON oi.seller_id = s.seller_id

    GROUP BY oi.order_id
),

customer_features AS (

    SELECT
        customer_id,
        customer_state

    FROM customers
)

SELECT

    -- Internal validation identifier
    o.order_id,

    -- Time features available at approval
    EXTRACT(YEAR FROM o.order_approved_at)
        AS approval_year,

    EXTRACT(MONTH FROM o.order_approved_at)
        AS approval_month,

    EXTRACT(DOW FROM o.order_approved_at)
        AS approval_day_of_week,

    EXTRACT(HOUR FROM o.order_approved_at)
        AS approval_hour,

    DATE_DIFF(
        'hour',
        o.order_purchase_timestamp,
        o.order_approved_at
    ) AS purchase_to_approval_hours,

    -- Estimated delivery promise
    DATE_DIFF(
        'day',
        CAST(o.order_approved_at AS DATE),
        CAST(o.order_estimated_delivery_date AS DATE)
    ) AS estimated_delivery_lead_days,

    -- Customer characteristics
    c.customer_state,

    -- Order and product characteristics
    i.item_count,
    i.seller_count,
    i.total_merchandise_value,
    i.total_freight_value,

    i.avg_product_weight_g,
    i.avg_product_length_cm,
    i.avg_product_height_cm,
    i.avg_product_width_cm,
    i.avg_product_photos_qty,

    i.dominant_product_category,
    i.product_category_count,

    -- Seller characteristics
    i.dominant_seller_state,
    i.seller_state_count,

    -- Prediction target
    o.late_delivery_flag

FROM eligible_orders o

INNER JOIN item_features i
    ON o.order_id = i.order_id

LEFT JOIN customer_features c
    ON o.customer_id = c.customer_id

ORDER BY o.order_approved_at, o.order_id
"""


# =========================================================
# MAIN DATASET PREPARATION FUNCTION
# =========================================================

def main():

    print("Starting delivery ML dataset preparation...")

    # Check database availability
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}"
        )

    # Create output directories if required
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Connect to DuckDB in read-only mode
    con = duckdb.connect(
        str(DATABASE_PATH),
        read_only=True
    )

    try:

        # -------------------------------------------------
        # Extract dataset
        # -------------------------------------------------

        print("Extracting historical delivery records...")

        df = con.execute(QUERY).fetchdf()

        if df.empty:
            raise ValueError("ML dataset is empty.")

        print(f"Extracted records: {len(df):,}")

        # -------------------------------------------------
        # Validate prediction target
        # -------------------------------------------------

        if df["late_delivery_flag"].isna().any():
            raise ValueError(
                "Missing target values detected."
            )

        if not set(
            df["late_delivery_flag"].unique()
        ).issubset({0, 1}):

            raise ValueError(
                "Unexpected target values detected."
            )

        # -------------------------------------------------
        # Validate unique order identifiers
        # -------------------------------------------------

        duplicate_orders = int(
            df["order_id"].duplicated().sum()
        )

        if duplicate_orders > 0:
            raise ValueError(
                f"Duplicate order IDs detected: {duplicate_orders}"
            )

        print("Order ID uniqueness validation: PASSED")

        # -------------------------------------------------
        # Remove identifier from ML features
        # -------------------------------------------------

        df = df.drop(
            columns=["order_id"]
        )

        # -------------------------------------------------
        # Handle missing product categories
        # -------------------------------------------------

        df["dominant_product_category"] = (
            df["dominant_product_category"].fillna("UNKNOWN")
        )

        # -------------------------------------------------
        # Validate remaining missing values
        # -------------------------------------------------

        missing_values = (
            df.isna()
            .sum()
            .loc[lambda x: x > 0]
            .to_dict()
        )

        allowed_missing_columns = {
            "avg_product_weight_g",
            "avg_product_length_cm",
            "avg_product_height_cm",
            "avg_product_width_cm",
            "avg_product_photos_qty"
        }

        unexpected_missing = (
            set(missing_values.keys())
            - allowed_missing_columns
        )

        if unexpected_missing:
            raise ValueError(
                f"Unexpected missing values: {unexpected_missing}"
            )

        print("Missing-value validation: PASSED")

        # -------------------------------------------------
        # Export processed dataset
        # -------------------------------------------------

        df.to_csv(
            OUTPUT_PATH,
            index=False
        )

        # -------------------------------------------------
        # Calculate target distribution
        # -------------------------------------------------

        target_counts = (
            df["late_delivery_flag"]
            .value_counts()
            .sort_index()
            .to_dict()
        )

        # -------------------------------------------------
        # Generate dataset quality report
        # -------------------------------------------------

        report = {

            "dataset_name": "Olist Delivery Risk Prediction",

            "source_database": str(DATABASE_PATH),

            "prediction_point": "Order approval time",

            "prediction_target": "late_delivery_flag",

            "target_definition": (
                "1 = delivered after estimated delivery date; "
                "0 = delivered on or before estimated delivery date"
            ),

            "estimated_delivery_date_assumption": (
                "Assumed available at order approval time; "
                "historical availability has not been independently verified."
            ),

            "total_records": int(len(df)),

            "total_features_including_target": int(len(df.columns)),

            "feature_columns": [
                col
                for col in df.columns
                if col != "late_delivery_flag"
            ],

            "target_distribution": {
                str(k): int(v)
                for k, v in target_counts.items()
            },

            "late_delivery_rate": float(
                df["late_delivery_flag"].mean()
            ),

            "duplicate_order_ids": duplicate_orders,

            "missing_values": {
                col: int(count)
                for col, count in df.isna().sum().items()
            },

            "missing_value_treatment": {
                "dominant_product_category": (
                    "Missing categories replaced with UNKNOWN"
                ),
                "numerical_product_features": (
    "Missing values retained for imputation "
    "within the model training pipeline"
)
            },

            "excluded_information": [
                "Actual delivery timestamp",
                "Carrier handover timestamp",
                "Actual delivery duration",
                "Actual delivery difference",
                "Shipping deadline",
                "Payment information",
                "Order identifier"
            ],

            "dataset_path": str(OUTPUT_PATH)
        }

        with open(
            REPORT_PATH,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                report,
                file,
                indent=4
            )

        # -------------------------------------------------
        # Final output
        # -------------------------------------------------

        print("\n" + "=" * 55)
        print("DELIVERY ML DATASET PREPARATION SUCCESSFUL")
        print("=" * 55)

        print(f"Total records: {len(df):,}")

        print(
            f"Total ML features: {len(df.columns) - 1}"
        )

        print(
            f"Late delivery rate: "
            f"{df['late_delivery_flag'].mean():.2%}"
        )

        print(
            f"On-time/early orders: "
            f"{target_counts.get(0, 0):,}"
        )

        print(
            f"Late orders: "
            f"{target_counts.get(1, 0):,}"
        )

        print(
            f"Duplicate order IDs: {duplicate_orders}"
        )

        print("\nRemaining missing values:")

        if missing_values:
            for column, count in missing_values.items():
                print(f"  {column}: {count}")
        else:
            print("  None")

        print(f"\nDataset saved: {OUTPUT_PATH}")

        print(f"Report saved: {REPORT_PATH}")

        print("=" * 55)

    finally:

        con.close()


# =========================================================
# EXECUTION
# =========================================================

if __name__ == "__main__":
    main()
