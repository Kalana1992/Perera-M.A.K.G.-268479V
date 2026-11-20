
"""
Olist E-Commerce Dataset Profiler
Project: E-Commerce Business Intelligence and Decision Support System

Purpose:
    Profile all raw CSV datasets and generate a structured
    data quality report.
"""

from pathlib import Path
import json
import pandas as pd


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
REPORT_DIR = PROJECT_ROOT / "reports" / "generated"

REPORT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. DATASET PROFILING FUNCTION
# --------------------------------------------------

def profile_dataset(file_path: Path) -> dict:
    """Profile one CSV dataset."""

    print(f"\nProfiling: {file_path.name}")

    df = pd.read_csv(file_path)

    total_rows, total_columns = df.shape

    missing_values = df.isnull().sum()
    duplicate_rows = int(df.duplicated().sum())

    column_details = []

    for column in df.columns:
        column_details.append({
            "column_name": column,
            "data_type": str(df[column].dtype),
            "missing_count": int(missing_values[column]),
            "missing_percentage": round(
                float(missing_values[column] / total_rows * 100), 2
            ) if total_rows else 0.0,
            "unique_values": int(df[column].nunique(dropna=True))
        })

    dataset_report = {
        "dataset_name": file_path.name,
        "row_count": int(total_rows),
        "column_count": int(total_columns),
        "duplicate_rows": duplicate_rows,
        "memory_usage_mb": round(
            float(df.memory_usage(deep=True).sum() / (1024 ** 2)), 2
        ),
        "columns": column_details
    }

    print(f"Rows: {total_rows:,}")
    print(f"Columns: {total_columns}")
    print(f"Duplicate rows: {duplicate_rows:,}")

    return dataset_report


# --------------------------------------------------
# 3. PROFILE ALL CSV FILES
# --------------------------------------------------

def main():

    csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in {RAW_DATA_DIR}"
        )

    print("=" * 65)
    print("OLIST E-COMMERCE DATASET PROFILING")
    print("=" * 65)

    all_reports = []

    for csv_file in csv_files:
        report = profile_dataset(csv_file)
        all_reports.append(report)

    # --------------------------------------------------
    # 4. GENERATE JSON REPORT
    # --------------------------------------------------

    output_file = REPORT_DIR / "dataset_profile_report.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(all_reports, file, indent=4, ensure_ascii=False)

    # --------------------------------------------------
    # 5. GENERATE SUMMARY TABLE
    # --------------------------------------------------

    summary = pd.DataFrame([
        {
            "Dataset": report["dataset_name"],
            "Rows": report["row_count"],
            "Columns": report["column_count"],
            "Duplicate Rows": report["duplicate_rows"],
            "Memory (MB)": report["memory_usage_mb"]
        }
        for report in all_reports
    ])

    print("\n" + "=" * 65)
    print("DATASET PROFILING SUMMARY")
    print("=" * 65)

    print(summary.to_string(index=False))

    print(f"\nProfiling report saved to: {output_file}")


# --------------------------------------------------
# 6. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    main()
