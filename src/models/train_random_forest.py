from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report
)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


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

METRICS_PATH = (
    PROJECT_ROOT / "reports" / "generated"
    / "random_forest_metrics.json"
)

CONFUSION_MATRIX_PATH = (
    PROJECT_ROOT / "reports" / "generated"
    / "random_forest_confusion_matrix.csv"
)


# =========================================================
# CONFIGURATION
# =========================================================

RANDOM_STATE = 42
N_SPLITS = 5


# =========================================================
# MAIN FUNCTION
# =========================================================

def main():

    print("=" * 60)
    print("RANDOM FOREST IMPROVED MODEL")
    print("=" * 60)

    # 1. Load dataset

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    df = pd.read_csv(DATASET_PATH)

    print(f"\nDataset records: {len(df):,}")

    target = "late_delivery_flag"

    if target not in df.columns:
        raise ValueError("Target column not found.")

    X = df.drop(columns=[target])
    y = df[target]

    if y.nunique() != 2:
        raise ValueError("Expected a binary classification target.")

    # 2. Identify feature types

    numerical_features = X.select_dtypes(
        include=["int64", "float64"]
    ).columns.tolist()

    categorical_features = X.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    print("\nFeature information")
    print("-------------------")
    print("Numerical features:", len(numerical_features))
    print("Categorical features:", len(categorical_features))
    print("Total predictors:", X.shape[1])

    # 3. Reproduce the baseline grouping logic

    groups = pd.util.hash_pandas_object(
        X,
        index=False
    ).to_numpy()

    print(
        "\nUnique predictor groups:",
        len(np.unique(groups))
    )

    # 4. Reproduce the exact baseline train/test split

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

    train_groups = set(groups[train_indices])
    test_groups = set(groups[test_indices])

    if train_groups.intersection(test_groups):
        raise ValueError(
            "Identical predictor groups found in both datasets."
        )

    print("\nTrain/test split")
    print("----------------")
    print(f"Training records: {len(X_train):,}")
    print(f"Testing records: {len(X_test):,}")
    print(f"Training late rate: {y_train.mean():.2%}")
    print(f"Testing late rate: {y_test.mean():.2%}")

    # 5. Numerical preprocessing

    numerical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median"))
        ]
    )

    # 6. Categorical preprocessing

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="most_frequent")
            ),
            (
                "encoder",
                OneHotEncoder(handle_unknown="ignore")
            )
        ]
    )

    # 7. Combine preprocessing

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numerical",
                numerical_pipeline,
                numerical_features
            ),
            (
                "categorical",
                categorical_pipeline,
                categorical_features
            )
        ]
    )

    # 8. Configure Random Forest

    classifier = RandomForestClassifier(
        n_estimators=400,
        max_features="sqrt",
        max_depth=None,
        min_samples_leaf=2,
        class_weight="balanced_subsample",
        random_state=RANDOM_STATE,
        n_jobs=-1
    )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier)
        ]
    )

    # 9. Train model

    print("\nTraining Random Forest...")
    print("This may take several minutes.")

    model.fit(X_train, y_train)

    print("Model training completed.")

    # 10. Generate predictions

    y_pred = model.predict(X_test)

    y_probability = model.predict_proba(X_test)[:, 1]

    # 11. Evaluate model

    metrics = {
        "model": "Random Forest Improved Model",
        "random_state": RANDOM_STATE,
        "split_method": "StratifiedGroupKFold",
        "n_splits": N_SPLITS,
        "training_records": int(len(X_train)),
        "testing_records": int(len(X_test)),
        "training_late_rate": float(y_train.mean()),
        "testing_late_rate": float(y_test.mean()),
        "hyperparameters": {
            "n_estimators": 400,
            "max_features": "sqrt",
            "max_depth": None,
            "min_samples_leaf": 2,
            "class_weight": "balanced_subsample"
        },
        "accuracy": float(
            accuracy_score(y_test, y_pred)
        ),
        "precision": float(
            precision_score(y_test, y_pred, zero_division=0)
        ),
        "recall": float(
            recall_score(y_test, y_pred, zero_division=0)
        ),
        "f1_score": float(
            f1_score(y_test, y_pred, zero_division=0)
        ),
        "roc_auc": float(
            roc_auc_score(y_test, y_probability)
        ),
        "pr_auc": float(
            average_precision_score(y_test, y_probability)
        ),
        "classification_report": classification_report(
            y_test,
            y_pred,
            output_dict=True,
            zero_division=0
        )
    }

    cm = confusion_matrix(
        y_test,
        y_pred,
        labels=[0, 1]
    )

    # 12. Display results

    print("\n" + "=" * 60)
    print("RANDOM FOREST MODEL EVALUATION")
    print("=" * 60)

    for metric, value in metrics.items():
        if isinstance(value, float):
            print(f"{metric}: {value:.4f}")

    print("\nConfusion Matrix")
    print("----------------")
    print(cm)

    print("\nClassification Report")
    print("---------------------")

    print(
        classification_report(
            y_test,
            y_pred,
            target_names=["ON_TIME_OR_EARLY", "LATE"],
            zero_division=0
        )
    )

    # 13. Save model and reports

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODEL_PATH)

    with open(METRICS_PATH, "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=4)

    confusion_df = pd.DataFrame(
        cm,
        index=["Actual_On_Time", "Actual_Late"],
        columns=["Predicted_On_Time", "Predicted_Late"]
    )

    confusion_df.to_csv(CONFUSION_MATRIX_PATH)

    print("\n" + "=" * 60)
    print("RANDOM FOREST MODEL DEVELOPMENT COMPLETED")
    print("=" * 60)

    print(f"Saved model: {MODEL_PATH}")
    print(f"Metrics report: {METRICS_PATH}")
    print(f"Confusion matrix: {CONFUSION_MATRIX_PATH}")


if __name__ == "__main__":
    main()
