from pathlib import Path
import json

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.inspection import permutation_importance
from sklearn.metrics import average_precision_score
from sklearn.model_selection import StratifiedGroupKFold


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT / "data" / "processed"
    / "delivery_ml_dataset.csv"
)

MODEL_PATH = (
    PROJECT_ROOT / "models" / "artifacts"
    / "random_forest_improved.joblib"
)

CSV_PATH = (
    PROJECT_ROOT / "reports" / "generated"
    / "random_forest_permutation_importance.csv"
)

JSON_PATH = (
    PROJECT_ROOT / "reports" / "generated"
    / "random_forest_permutation_importance.json"
)

PLOT_PATH = (
    PROJECT_ROOT / "reports" / "figures"
    / "random_forest_permutation_importance.png"
)


# =========================================================
# CONFIGURATION
# =========================================================

RANDOM_STATE = 42
N_SPLITS = 5
N_REPEATS = 5
SCORING = "average_precision"
TOP_N = 15


# =========================================================
# MAIN FUNCTION
# =========================================================

def main():

    print("=" * 65)
    print("RANDOM FOREST PERMUTATION FEATURE IMPORTANCE")
    print("=" * 65)

    # 1. Verify inputs

    for path in [DATASET_PATH, MODEL_PATH]:
        if not path.exists():
            raise FileNotFoundError(f"Required file not found: {path}")

    # 2. Load dataset

    print("\nLoading dataset...")

    df = pd.read_csv(DATASET_PATH)

    target = "late_delivery_flag"

    X = df.drop(columns=[target])
    y = df[target]

    print(f"Dataset records: {len(df):,}")
    print(f"Predictor count: {X.shape[1]}")

    # 3. Recreate original group-aware split

    groups = pd.util.hash_pandas_object(
        X,
        index=False
    ).to_numpy()

    splitter = StratifiedGroupKFold(
        n_splits=N_SPLITS,
        shuffle=True,
        random_state=RANDOM_STATE
    )

    train_indices, test_indices = next(
        splitter.split(X, y, groups=groups)
    )

    X_train = X.iloc[train_indices]
    X_test = X.iloc[test_indices]

    y_train = y.iloc[train_indices]
    y_test = y.iloc[test_indices]

    if set(groups[train_indices]).intersection(
        set(groups[test_indices])
    ):
        raise ValueError("Train/test group overlap detected.")

    print("\nRecreated test set")
    print("------------------")
    print(f"Training records: {len(X_train):,}")
    print(f"Testing records: {len(X_test):,}")
    print(f"Test late-delivery rate: {y_test.mean():.2%}")

    # 4. Load existing fitted model

    print("\nLoading existing Random Forest model...")
    print("No model retraining will be performed.")

    model = joblib.load(MODEL_PATH)

    print("Existing model loaded successfully.")

    # 5. Calculate baseline PR-AUC

    print("\nCalculating baseline Average Precision...")

    baseline_probabilities = model.predict_proba(X_test)[:, 1]

    baseline_score = average_precision_score(
        y_test,
        baseline_probabilities
    )

    print(f"Baseline Average Precision: {baseline_score:.4f}")

    # 6. Calculate permutation importance

    print("\nCalculating permutation importance...")
    print(f"Scoring metric: {SCORING}")
    print(f"Repeats per feature: {N_REPEATS}")
    print(f"Features: {X_test.shape[1]}")
    print("This may take several minutes.")

    result = permutation_importance(
        estimator=model,
        X=X_test,
        y=y_test,
        scoring=SCORING,
        n_repeats=N_REPEATS,
        random_state=RANDOM_STATE,
        n_jobs=1
    )

    # 7. Prepare ranked results

    importance_df = pd.DataFrame({
        "feature": X_test.columns,
        "importance_mean": result.importances_mean,
        "importance_std": result.importances_std
    })

    importance_df = importance_df.sort_values(
        by="importance_mean",
        ascending=False
    ).reset_index(drop=True)

    importance_df.insert(
        0,
        "rank",
        np.arange(1, len(importance_df) + 1)
    )

    # 8. Save CSV

    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    PLOT_PATH.parent.mkdir(parents=True, exist_ok=True)

    importance_df.to_csv(CSV_PATH, index=False)

    # 9. Save JSON summary

    summary = {
        "analysis": "Permutation Feature Importance",
        "model": "Random Forest Improved Model",
        "scoring_metric": SCORING,
        "baseline_average_precision": float(baseline_score),
        "random_state": RANDOM_STATE,
        "n_repeats": N_REPEATS,
        "training_records": int(len(X_train)),
        "testing_records": int(len(X_test)),
        "test_late_delivery_rate": float(y_test.mean()),
        "features_analyzed": int(X_test.shape[1]),
        "feature_importance": [
            {
                "rank": int(row.rank),
                "feature": row.feature,
                "importance_mean": float(row.importance_mean),
                "importance_std": float(row.importance_std)
            }
            for row in importance_df.itertuples(index=False)
        ]
    }

    with JSON_PATH.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4)

    # 10. Generate feature-importance chart

    plot_df = importance_df.head(TOP_N).sort_values(
        by="importance_mean",
        ascending=True
    )

    plt.figure(figsize=(11, 8))

    plt.barh(
        plot_df["feature"],
        plot_df["importance_mean"],
        xerr=plot_df["importance_std"],
        capsize=3
    )

    plt.axvline(0, linewidth=0.8)

    plt.xlabel("Decrease in Average Precision (PR-AUC)")
    plt.ylabel("Feature")
    plt.title(
        "Random Forest - Permutation Feature Importance\n"
        "Scoring metric: Average Precision"
    )

    plt.tight_layout()
    plt.savefig(PLOT_PATH, dpi=300, bbox_inches="tight")
    plt.close()

    # 11. Display results

    print("\n" + "=" * 65)
    print("FEATURE IMPORTANCE RESULTS")
    print("=" * 65)

    print(
        importance_df.head(TOP_N).to_string(
            index=False,
            formatters={
                "importance_mean": "{:.6f}".format,
                "importance_std": "{:.6f}".format
            }
        )
    )

    print("\nSaved outputs:")
    print(CSV_PATH)
    print(JSON_PATH)
    print(PLOT_PATH)

    print("\nFeature importance analysis completed.")


if __name__ == "__main__":
    main()
