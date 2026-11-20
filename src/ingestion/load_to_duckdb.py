from pathlib import Path
import duckdb
import json
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATABASE_DIR = PROJECT_ROOT / "database"
REPORT_DIR = PROJECT_ROOT / "reports" / "generated"

DATABASE_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATABASE_DIR / "ecommerce.duckdb"

DATASETS = {
    "olist_orders_dataset.csv": "orders",
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "order_payments",
    "olist_order_reviews_dataset.csv": "order_reviews",
    "olist_customers_dataset.csv": "customers",
    "olist_sellers_dataset.csv": "sellers",
    "olist_products_dataset.csv": "products",
    "olist_geolocation_dataset.csv": "geolocation",
    "product_category_name_translation.csv": "category_translation",
}


def load_datasets():
    """Load all raw CSV datasets into the DuckDB database."""

    connection = duckdb.connect(str(DB_PATH))
    ingestion_results = []

    try:
        for filename, table_name in DATASETS.items():
            csv_path = RAW_DIR / filename

            print(f"\nLoading: {filename}")

            if not csv_path.exists():
                raise FileNotFoundError(
                    f"Required dataset not found: {csv_path}"
                )

            csv_path_sql = str(csv_path).replace("'", "''")

            connection.execute(
                f"""
                CREATE OR REPLACE TABLE {table_name} AS
                SELECT *
                FROM read_csv_auto(
                    '{csv_path_sql}',
                    header = true,
                    sample_size = -1
                )
                """
            )

            row_count = connection.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            ).fetchone()[0]

            column_info = connection.execute(
                f"PRAGMA table_info('{table_name}')"
            ).fetchall()

            columns = [column[1] for column in column_info]

            ingestion_results.append({
                "source_file": filename,
                "table_name": table_name,
                "row_count": row_count,
                "column_count": len(columns),
                "columns": columns,
                "status": "PASS"
            })

            print(
                f"[PASS] {table_name}: "
                f"{row_count:,} rows, {len(columns)} columns"
            )

    finally:
        connection.close()

    return ingestion_results


def main():
    """Run database ingestion and generate a report."""

    print("=" * 65)
    print("ECOMMERCE CAPSTONE - DUCKDB DATA INGESTION")
    print("=" * 65)

    start_time = datetime.now(timezone.utc)

    results = load_datasets()

    total_rows = sum(item["row_count"] for item in results)

    end_time = datetime.now(timezone.utc)
    duration_seconds = (end_time - start_time).total_seconds()

    report = {
        "project": "E-Commerce Business Intelligence and Decision Support System",
        "database": str(DB_PATH),
        "execution_timestamp": start_time.isoformat(),
        "total_datasets": len(results),
        "total_rows_loaded": total_rows,
        "duration_seconds": round(duration_seconds, 2),
        "datasets": results,
        "overall_status": "PASS"
    }

    report_path = REPORT_DIR / "duckdb_ingestion_report.json"

    with open(report_path, "w", encoding="utf-8") as report_file:
        json.dump(report, report_file, indent=4)

    print("\n" + "=" * 65)
    print("INGESTION SUMMARY")
    print("=" * 65)
    print(f"Datasets loaded : {len(results)}")
    print(f"Total rows      : {total_rows:,}")
    print(f"Execution time  : {duration_seconds:.2f} seconds")
    print(f"Database        : {DB_PATH}")
    print(f"Report          : {report_path}")
    print("\nOverall status: PASS")


if __name__ == "__main__":
    main()
