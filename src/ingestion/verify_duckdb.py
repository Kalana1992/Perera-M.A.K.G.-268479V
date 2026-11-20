from pathlib import Path
import duckdb
import json

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "database" / "ecommerce.duckdb"
REPORT_PATH = (
    PROJECT_ROOT / "reports" / "generated"
    / "duckdb_ingestion_report.json"
)


def main():
    print("=" * 65)
    print("ECOMMERCE CAPSTONE - DATABASE VERIFICATION")
    print("=" * 65)

    with open(REPORT_PATH, "r", encoding="utf-8") as file:
        ingestion_report = json.load(file)

    connection = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        existing_tables = {
            row[0] for row in connection.execute("SHOW TABLES").fetchall()
        }

        passed = 0
        failed = 0
        verification_results = []

        for dataset in ingestion_report["datasets"]:
            table_name = dataset["table_name"]
            expected_rows = dataset["row_count"]

            if table_name not in existing_tables:
                print(f"[FAIL] {table_name}: Table not found")
                failed += 1
                continue

            actual_rows = connection.execute(
                f'SELECT COUNT(*) FROM "{table_name}"'
            ).fetchone()[0]

            column_info = connection.execute(
                f"PRAGMA table_info('{table_name}')"
            ).fetchall()

            columns = [
                {
                    "name": column[1],
                    "data_type": column[2]
                }
                for column in column_info
            ]

            row_check = actual_rows == expected_rows
            column_check = len(columns) == dataset["column_count"]

            status = "PASS" if row_check and column_check else "FAIL"

            if status == "PASS":
                passed += 1
            else:
                failed += 1

            print(
                f"[{status}] {table_name}: "
                f"{actual_rows:,} rows, {len(columns)} columns"
            )

            verification_results.append({
                "table_name": table_name,
                "expected_rows": expected_rows,
                "actual_rows": actual_rows,
                "column_count": len(columns),
                "columns": columns,
                "status": status
            })

        expected_tables = {
            item["table_name"]
            for item in ingestion_report["datasets"]
        }

        extra_tables = existing_tables - expected_tables

        overall_status = (
            "PASS" if failed == 0 and not extra_tables else "FAIL"
        )

        verification_report = {
            "total_tables_expected": len(expected_tables),
            "total_tables_found": len(existing_tables),
            "passed": passed,
            "failed": failed,
            "extra_tables": sorted(extra_tables),
            "results": verification_results,
            "overall_status": overall_status
        }

        output_path = (
            PROJECT_ROOT / "reports" / "generated"
            / "duckdb_verification_report.json"
        )

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(verification_report, file, indent=4)

        print("\n" + "=" * 65)
        print("DATABASE VERIFICATION SUMMARY")
        print("=" * 65)
        print(f"Tables found : {len(existing_tables)}")
        print(f"Passed       : {passed}")
        print(f"Failed       : {failed}")
        print(f"Overall      : {overall_status}")
        print(f"Report       : {output_path}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
