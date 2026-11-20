from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

orders = pd.read_csv(RAW_DIR / "olist_orders_dataset.csv")
items = pd.read_csv(RAW_DIR / "olist_order_items_dataset.csv")

orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"], errors="coerce"
)

items["shipping_limit_date"] = pd.to_datetime(
    items["shipping_limit_date"], errors="coerce"
)

data = items.merge(
    orders[
        ["order_id", "order_status", "order_purchase_timestamp"]
    ],
    on="order_id",
    how="left",
    validate="many_to_one",
)

data["deadline_days_after_purchase"] = (
    data["shipping_limit_date"] - data["order_purchase_timestamp"]
).dt.total_seconds() / 86400

anomalies = data[
    data["deadline_days_after_purchase"] > 365
].copy()

columns = [
    "order_id",
    "seller_id",
    "order_status",
    "order_purchase_timestamp",
    "shipping_limit_date",
    "deadline_days_after_purchase",
]

print("\nSHIPPING DEADLINE ANOMALIES")
print(anomalies[columns].to_string(index=False))
print(f"\nTotal anomalous records: {len(anomalies)}")

# Save investigation results
OUTPUT_DIR = PROJECT_ROOT / "reports" / "generated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

output_file = OUTPUT_DIR / "shipping_deadline_anomalies.csv"
anomalies[columns].to_csv(output_file, index=False)

print(f"\nAnomaly report saved to: {output_file}")

