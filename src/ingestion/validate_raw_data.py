from pathlib import Path
import csv
import json
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
REPORT_DIR = PROJECT_ROOT / "reports" / "generated"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_SCHEMAS = {
    "olist_orders_dataset.csv": [
        "order_id", "customer_id", "order_status",
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "olist_order_items_dataset.csv": [
        "order_id", "order_item_id", "product_id",
        "seller_id", "shipping_limit_date", "price",
        "freight_value",
    ],
    "olist_order_payments_dataset.csv": [
        "order_id", "payment_sequential", "payment_type",
        "payment_installments", "payment_value",
    ],
    "olist_order_reviews_dataset.csv": [
        "review_id", "order_id", "review_score",
        "review_comment_title", "review_comment_message",
        "review_creation_date", "review_answer_timestamp",
    ],
    "olist_customers_dataset.csv": [
        "customer_id", "customer_unique_id",
        "customer_zip_code_prefix", "customer_city",
        "customer_state",
    ],
    "olist_sellers_dataset.csv": [
        "seller_id", "seller_zip_code_prefix",
        "seller_city", "seller_state",
    ],
    "olist_products_dataset.csv": [
        "product_id", "product_category_name",
        "product_name_lenght", "product_description_lenght",
        "product_photos_qty", "product_weight_g",
        "product_length_cm", "product_height_cm",
        "product_width_cm",
    ],
    "olist_geolocation_dataset.csv": [
        "geolocation_zip_code_prefix", "geolocation_lat",
        "geolocation_lng", "geolocation_city",
        "geolocation_state",
    ],
    "product_category_name_translation.csv": [
        "product_category_name",
        "product_category_name_english",
    ],
}

def validate_csv(filename, required_columns):
    file_path = RAW_DIR / filename

    result = {
        "filename": filename,
        "file_exists": file_path.is_file(),
        "file_size_bytes": 0,
        "row_count": 0,
        "missing_columns": [],
        "unexpected_columns": [],
        "status": "FAIL",
        "errors": [],
    }

    if not file_path.is_file():
        result["errors"].append("File does not exist.")
        return result

    result["file_size_bytes"] = file_path.stat().st_size

    if result["file_size_bytes"] == 0:
        result["errors"].append("File is empty.")
        return result

    try:
        with open(
            file_path, "r", encoding="utf-8-sig", newline=""
        ) as file:
            reader = csv.reader(file)
            headers = next(reader, None)

            if not headers:
                result["errors"].append("CSV header is missing.")
                return result

            result["missing_columns"] = [
                col for col in required_columns if col not in headers
            ]

            result["unexpected_columns"] = [
                col for col in headers if col not in required_columns
            ]

            result["row_count"] = sum(1 for _ in reader)

            if result["row_count"] == 0:
                result["errors"].append("Dataset contains no records.")

            if result["missing_columns"]:
                result["errors"].append("Required columns are missing.")

            if not result["errors"]:
                result["status"] = "PASS"

    except Exception as error:
        result["errors"].append(str(error))

    return result


def main():
    print("=" * 65)
    print("ECOMMERCE CAPSTONE - RAW DATA VALIDATION")
    print("=" * 65)

    results = []

    for filename, required_columns in EXPECTED_SCHEMAS.items():
        result = validate_csv(filename, required_columns)
        results.append(result)

        print(
            f"[{result['status']}] {filename} | "
            f"Rows: {result['row_count']:,}"
        )

        for error in result["errors"]:
            print(f"       ERROR: {error}")

    passed = sum(r["status"] == "PASS" for r in results)
    failed = len(results) - passed

    report = {
        "project": "E-Commerce BI and Decision Support System",
        "validation_timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "total_datasets": len(results),
        "passed_datasets": passed,
        "failed_datasets": failed,
        "overall_status": "PASS" if failed == 0 else "FAIL",
        "datasets": results,
    }

    report_path = REPORT_DIR / "raw_data_validation_report.json"

    with open(report_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("\n" + "=" * 65)
    print("VALIDATION SUMMARY")
    print("=" * 65)
    print(f"Total datasets : {len(results)}")
    print(f"Passed         : {passed}")
    print(f"Failed         : {failed}")
    print(f"Overall status : {report['overall_status']}")
    print(f"\nReport saved: {report_path}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
