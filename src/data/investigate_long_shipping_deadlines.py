from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "generated"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load source datasets
orders = pd.read_csv(RAW_DIR / "olist_orders_dataset.csv")
items = pd.read_csv(RAW_DIR / "olist_order_items_dataset.csv")

# Convert timestamps
orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"], errors="coerce"
)

items["shipping_limit_date"] = pd.to_datetime(
    items["shipping_limit_date"], errors="coerce"
)

# Join order information to order items
data = items.merge(
    orders[
        ["order_id", "order_status", "order_purchase_timestamp"]
    ],
    on="order_id",
    how="left",
    validate="many_to_one",
)

# Calculate shipping deadline interval
data["deadline_days_after_purchase"] = (
    data["shipping_limit_date"] - data["order_purchase_timestamp"]
).dt.total_seconds() / 86400

# Select unusually long deadlines
long_deadlines = data[
    data["deadline_days_after_purchase"] > 30
].copy()

# Group by order status
status_summary = (
    long_deadlines.groupby("order_status")
    .agg(
        item_records=("order_id", "size"),
        unique_orders=("order_id", "nunique"),
        average_deadline_days=("deadline_days_after_purchase", "mean"),
        maximum_deadline_days=("deadline_days_after_purchase", "max"),
    )
    .reset_index()
)

# Group by seller
seller_summary = (
    long_deadlines.groupby("seller_id")
    .agg(
        item_records=("order_id", "size"),
        unique_orders=("order_id", "nunique"),
        average_deadline_days=("deadline_days_after_purchase", "mean"),
        maximum_deadline_days=("deadline_days_after_purchase", "max"),
    )
    .sort_values("item_records", ascending=False)
    .reset_index()
)

# Display results
print("\nLONG SHIPPING DEADLINE ANALYSIS")
print(f"Total item records above 30 days: {len(long_deadlines)}")
print(f"Unique orders affected: {long_deadlines['order_id'].nunique()}")
print(f"Unique sellers affected: {long_deadlines['seller_id'].nunique()}")

print("\nANALYSIS BY ORDER STATUS")
print(status_summary.to_string(index=False))

print("\nTOP 15 SELLERS WITH LONG SHIPPING DEADLINES")
print(seller_summary.head(15).to_string(index=False))

print("\nDEADLINE INTERVAL DISTRIBUTION")
print(long_deadlines["deadline_days_after_purchase"].describe())

# Export evidence
long_deadlines.to_csv(
    OUTPUT_DIR / "long_shipping_deadline_records.csv",
    index=False,
)

status_summary.to_csv(
    OUTPUT_DIR / "long_shipping_deadline_status_summary.csv",
    index=False,
)

seller_summary.to_csv(
    OUTPUT_DIR / "long_shipping_deadline_seller_summary.csv",
    index=False,
)

print("\nAnalysis reports saved successfully.")
