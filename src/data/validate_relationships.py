from pathlib import Path
import duckdb
import json
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "database" / "ecommerce.duckdb"
REPORT_DIR = PROJECT_ROOT / "reports" / "generated"

REPORT_DIR.mkdir(parents=True, exist_ok=True)


def check_primary_key(connection, table_name, column_name):
    """Check uniqueness and null values in a proposed key."""

    result = connection.execute(
        f"""
        SELECT
            COUNT(*) AS total_rows,
            COUNT(DISTINCT {column_name}) AS unique_values,
            COUNT(*) FILTER (
                WHERE {column_name} IS NULL
            ) AS null_values
        FROM {table_name}
        """
    ).fetchone()

    total_rows, unique_values, null_values = result

    return {
        "table": table_name,
        "column": column_name,
        "total_rows": total_rows,
        "unique_values": unique_values,
        "null_values": null_values,
        "duplicate_values": total_rows - null_values - unique_values,
        "is_valid": (
            null_values == 0 and unique_values == total_rows
        )
    }

def check_foreign_key(connection, parent_table, parent_column,
                      child_table, child_column):
    """Check whether child records reference valid parent records."""

    result = connection.execute(
        f"""
        SELECT
            COUNT(*) AS total_child_rows,
            COUNT(*) FILTER (
                WHERE child.{child_column} IS NULL
            ) AS null_values,
            COUNT(*) FILTER (
                WHERE child.{child_column} IS NOT NULL
                AND parent.{parent_column} IS NULL
            ) AS unmatched_values
        FROM {child_table} AS child
        LEFT JOIN {parent_table} AS parent
            ON child.{child_column} = parent.{parent_column}
        """
    ).fetchone()

    total_rows, null_values, unmatched_values = result

    return {
        "parent_table": parent_table,
        "parent_column": parent_column,
        "child_table": child_table,
        "child_column": child_column,
        "total_child_rows": total_rows,
        "null_values": null_values,
        "unmatched_values": unmatched_values,
        "is_valid": unmatched_values == 0
    }

def main():
    print("=" * 70)
    print("ECOMMERCE CAPSTONE - RELATIONSHIP VALIDATION")
    print("=" * 70)

    connection = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        # Proposed primary keys
        primary_keys = [
            ("orders", "order_id"),
            ("customers", "customer_id"),
            ("products", "product_id"),
            ("sellers", "seller_id"),
            ("order_reviews", "review_id"),
        ]

        primary_key_results = []

        print("\nPRIMARY KEY VALIDATION")

        for table, column in primary_keys:
            result = check_primary_key(connection, table, column)
            primary_key_results.append(result)

            status = "PASS" if result["is_valid"] else "INVESTIGATE"

            print(
                f"[{status}] {table}.{column} | "
                f"Rows: {result['total_rows']:,} | "
                f"Unique: {result['unique_values']:,} | "
                f"Nulls: {result['null_values']:,} | "
                f"Duplicates: {result['duplicate_values']:,}"
            )

        # Foreign key relationships
        relationships = [
            ("customers", "customer_id", "orders", "customer_id"),
            ("orders", "order_id", "order_items", "order_id"),
            ("orders", "order_id", "order_payments", "order_id"),
            ("orders", "order_id", "order_reviews", "order_id"),
            ("products", "product_id", "order_items", "product_id"),
            ("sellers", "seller_id", "order_items", "seller_id"),
        ]

        foreign_key_results = []

        print("\nFOREIGN KEY VALIDATION")

        for parent_table, parent_column, child_table, child_column in relationships:
            result = check_foreign_key(
                connection,
                parent_table,
                parent_column,
                child_table,
                child_column
            )

            foreign_key_results.append(result)

            status = "PASS" if result["is_valid"] else "INVESTIGATE"

            print(
                f"[{status}] {child_table}.{child_column} -> "
                f"{parent_table}.{parent_column} | "
                f"Unmatched: {result['unmatched_values']:,} | "
                f"Nulls: {result['null_values']:,}"
            )

        report = {
            "execution_timestamp": datetime.now(timezone.utc).isoformat(),
            "primary_key_checks": primary_key_results,
            "foreign_key_checks": foreign_key_results,
        }

        report_path = REPORT_DIR / "relationship_validation_report.json"

        with open(report_path, "w", encoding="utf-8") as file:
            json.dump(report, file, indent=4)

        print("\n" + "=" * 70)
        print("RELATIONSHIP VALIDATION COMPLETED")
        print("=" * 70)
        print(f"Primary key checks: {len(primary_key_results)}")
        print(f"Foreign key checks: {len(foreign_key_results)}")
        print(f"Report: {report_path}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
