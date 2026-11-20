
from pathlib import Path
import pandas as pd
import json

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "generated"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load source datasets
orders = pd.read_csv(RAW_DIR / "olist_orders_dataset.csv")
items = pd.read_csv(RAW_DIR / "olist_order_items_dataset.csv")

# Convert date columns
date_columns = [
    "order_purchase_timestamp",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

for column in date_columns:
    orders[column] = pd.to_datetime(orders[column], errors="coerce")

items["shipping_limit_date"] = pd.to_datetime(
    items["shipping_limit_date"], errors="coerce"
)

# Merge order-level information into item-level data
data = items.merge(
    orders[
        [
            "order_id",
            "order_status",
            "order_purchase_timestamp",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
        ]
    ],
    on="order_id",
    how="left",
    validate="many_to_one",
)

# Calculate shipping deadline interval
data["deadline_days_after_purchase"] = (
    data["shipping_limit_date"] - data["order_purchase_timestamp"]
).dt.total_seconds() / 86400

# Quality flags
quality_summary = {
    "total_order_items": int(len(data)),
    "missing_purchase_timestamp": int(
        data["order_purchase_timestamp"].isna().sum()
    ),
    "deadlines_before_purchase": int(
        (data["deadline_days_after_purchase"] < 0).sum()
    ),
    "deadlines_over_30_days": int(
        (data["deadline_days_after_purchase"] > 30).sum()
    ),
    "deadlines_over_365_days": int(
        (data["deadline_days_after_purchase"] > 365).sum()
    ),
    "deadlines_after_latest_purchase_date": int(
        (
            data["shipping_limit_date"]
            > orders["order_purchase_timestamp"].max()
        ).sum()
    ),
    "exact_duplicate_item_rows": int(items.duplicated().sum()),
}

# Save report
output_file = OUTPUT_DIR / "data_quality_assessment.json"

with open(output_file, "w", encoding="utf-8") as file:
    json.dump(quality_summary, file, indent=4)

print("DATA QUALITY ASSESSMENT COMPLETED")
print(json.dumps(quality_summary, indent=4))
print(f"\nReport saved to: {output_file}")
