from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
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
from sklearn.preprocessing import StandardScaler, OneHotEncoder


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
    / "logistic_regression_baseline.joblib"
)

METRICS_PATH = (
    PROJECT_ROOT / "reports" / "generated"
    / "logistic_regression_threshold_metrics.json"
)

THRESHOLD_PATH = (
    PROJECT_ROOT / "models" / "artifacts"
    / "logistic_regression_optimal_threshold.json"
)

OOF_PATH = (
    PROJECT_ROOT / "reports" / "generated"
    / "logistic_regression_oof_predictions.csv"
)

CONFUSION_MATRIX_PATH = (
    PROJECT_ROOT / "reports" / "generated"
    / "logistic_regression_threshold_confusion_matrix.csv"
)


# =========================================================
# CONFIGURATION
# =========================================================

RANDOM_STATE = 42
N_SPLITS = 5
TARGET = "late_delivery_flag"


# =========================================================
# MODEL PIPELINE
# =========================================================

def build_model(numerical_features, categorical_features):

    numerical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ]
    )

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

    classifier = LogisticRegression(
        class_weight="balanced",
        max_iter=2000,
        random_state=RANDOM_STATE
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier)
        ]
    )


# =========================================================
# MAIN FUNCTION
# =========================================================

def main():

    print("=" * 65)
    print("LOGISTIC REGRESSION THRESHOLD OPTIMIZATION")
    print("=" * 65)

    # 1. Load dataset and existing baseline model

    if not DATASET_PATH.exists():
        raise FileNotFoundError(DATASET_PATH)

    if not MODEL_PATH.exists():
        raise FileNotFoundError(MODEL_PATH)

    df = pd.read_csv(DATASET_PATH)

    X = df.drop(columns=[TARGET])
    y = df[TARGET]

    existing_model = joblib.load(MODEL_PATH)

    print(f"\nDataset records: {len(df):,}")

    # 2. Identify feature types

    numerical_features = X.select_dtypes(
        include=["int64", "float64"]
    ).columns.tolist()

    categorical_features = X.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    print("Numerical features:", len(numerical_features))
    print("Categorical features:", len(categorical_features))

    # 3. Reproduce original train/test split

    groups = pd.util.hash_pandas_object(
        X,
        index=False
    ).to_numpy()

    outer_splitter = StratifiedGroupKFold(
        n_splits=N_SPLITS,
        shuffle=True,
        random_state=RANDOM_STATE
    )

    train_indices, test_indices = next(
        outer_splitter.split(X, y, groups=groups)
    )

    X_train = X.iloc[train_indices]
    X_test = X.iloc[test_indices]

    y_train = y.iloc[train_indices]
    y_test = y.iloc[test_indices]

    groups_train = groups[train_indices]

    print("\nOriginal split verification")
    print("---------------------------")
    print(f"Training records: {len(X_train):,}")
    print(f"Testing records: {len(X_test):,}")
    print(f"Training late rate: {y_train.mean():.2%}")
    print(f"Testing late rate: {y_test.mean():.2%}")

    # 4. Generate out-of-fold training predictions

    print("\nGenerating out-of-fold predictions...")
    print("Five Logistic Regression training folds will be executed.")

    cv_splitter = StratifiedGroupKFold(
        n_splits=N_SPLITS,
        shuffle=True,
        random_state=RANDOM_STATE
    )

    oof_probabilities = np.full(
        len(X_train),
        np.nan
    )

    for fold, (fit_indices, validation_indices) in enumerate(
        cv_splitter.split(
            X_train,
            y_train,
            groups=groups_train
        ),
        start=1
    ):

        print(f"\nTraining fold {fold}/{N_SPLITS}...")

        fold_model = build_model(
            numerical_features,
            categorical_features
        )

        fold_model.fit(
            X_train.iloc[fit_indices],
            y_train.iloc[fit_indices]
        )

        fold_probabilities = fold_model.predict_proba(
            X_train.iloc[validation_indices]
        )[:, 1]

        oof_probabilities[validation_indices] = fold_probabilities

        print(
            f"Fold {fold} completed. "
            f"Validation records: {len(validation_indices):,}"
        )

    if np.isnan(oof_probabilities).any():
        raise ValueError(
            "Some training records did not receive OOF predictions."
        )

    # 5. Select threshold using training OOF predictions

    print("\nSelecting classification threshold...")

    thresholds = np.arange(0.01, 0.501, 0.005)

    threshold_results = []

    for threshold in thresholds:

        predictions = (
            oof_probabilities >= threshold
        ).astype(int)

        threshold_results.append({
            "threshold": float(threshold),
            "precision": float(
                precision_score(
                    y_train,
                    predictions,
                    zero_division=0
                )
            ),
            "recall": float(
                recall_score(
                    y_train,
                    predictions,
                    zero_division=0
                )
            ),
            "f1_score": float(
                f1_score(
                    y_train,
                    predictions,
                    zero_division=0
                )
            )
        })

    threshold_df = pd.DataFrame(threshold_results)

    best_row = threshold_df.sort_values(
        by=["f1_score", "precision", "threshold"],
        ascending=[False, False, False]
    ).iloc[0]

    optimal_threshold = float(best_row["threshold"])

    print("\nSelected threshold")
    print("------------------")
    print(f"Threshold: {optimal_threshold:.3f}")
    print(f"OOF Precision: {best_row['precision']:.4f}")
    print(f"OOF Recall: {best_row['recall']:.4f}")
    print(f"OOF F1-score: {best_row['f1_score']:.4f}")

    # 6. Save OOF predictions

    oof_df = pd.DataFrame({
        "actual_late_delivery": y_train.to_numpy(),
        "predicted_late_probability": oof_probabilities
    })

    oof_df.to_csv(OOF_PATH, index=False)

    # 7. Evaluate existing baseline model on untouched test set

    print("\nEvaluating on untouched test set...")

    test_probabilities = existing_model.predict_proba(
        X_test
    )[:, 1]

    default_predictions = (
        test_probabilities >= 0.50
    ).astype(int)

    tuned_predictions = (
        test_probabilities >= optimal_threshold
    ).astype(int)

    # 8. Calculate evaluation metrics

    metrics = {
        "model": "Logistic Regression with Optimized Threshold",
        "threshold_selection_method": (
            "Maximum F1-score from 5-fold "
            "StratifiedGroupKFold OOF predictions"
        ),
        "selected_threshold": optimal_threshold,
        "random_state": RANDOM_STATE,
        "training_records": int(len(X_train)),
        "testing_records": int(len(X_test)),
        "oof_precision": float(best_row["precision"]),
        "oof_recall": float(best_row["recall"]),
        "oof_f1_score": float(best_row["f1_score"]),
        "test_default_threshold_0_50": {
            "precision": float(
                precision_score(
                    y_test,
                    default_predictions,
                    zero_division=0
                )
            ),
            "recall": float(
                recall_score(
                    y_test,
                    default_predictions,
                    zero_division=0
                )
            ),
            "f1_score": float(
                f1_score(
                    y_test,
                    default_predictions,
                    zero_division=0
                )
            )
        },
        "test_optimized_threshold": {
            "threshold": optimal_threshold,
            "accuracy": float(
                accuracy_score(y_test, tuned_predictions)
            ),
            "precision": float(
                precision_score(
                    y_test,
                    tuned_predictions,
                    zero_division=0
                )
            ),
            "recall": float(
                recall_score(
                    y_test,
                    tuned_predictions,
                    zero_division=0
                )
            ),
            "f1_score": float(
                f1_score(
                    y_test,
                    tuned_predictions,
                    zero_division=0
                )
            ),
            "roc_auc": float(
                roc_auc_score(
                    y_test,
                    test_probabilities
                )
            ),
            "pr_auc": float(
                average_precision_score(
                    y_test,
                    test_probabilities
                )
            ),
            "classification_report": classification_report(
                y_test,
                tuned_predictions,
                output_dict=True,
                zero_division=0
            )
        }
    }

    cm = confusion_matrix(
        y_test,
        tuned_predictions,
        labels=[0, 1]
    )

    # 9. Save reports

    for path in [
        METRICS_PATH,
        THRESHOLD_PATH,
        OOF_PATH,
        CONFUSION_MATRIX_PATH
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)

    with open(METRICS_PATH, "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=4)

    with open(THRESHOLD_PATH, "w", encoding="utf-8") as file:
        json.dump({
            "model": "Logistic Regression",
            "optimal_threshold": optimal_threshold,
            "selection_method": "Maximum OOF F1-score",
            "cross_validation_folds": N_SPLITS,
            "random_state": RANDOM_STATE
        }, file, indent=4)

    confusion_df = pd.DataFrame(
        cm,
        index=["Actual_On_Time", "Actual_Late"],
        columns=["Predicted_On_Time", "Predicted_Late"]
    )

    confusion_df.to_csv(CONFUSION_MATRIX_PATH)

    # 10. Display final results

    print("\n" + "=" * 65)
    print("LOGISTIC REGRESSION THRESHOLD OPTIMIZATION RESULTS")
    print("=" * 65)

    print("\nDefault threshold (0.50)")
    print("------------------------")

    for name, value in metrics[
        "test_default_threshold_0_50"
    ].items():
        print(f"{name}: {value:.4f}")

    print("\nOptimized threshold")
    print("-------------------")
    print(f"Threshold: {optimal_threshold:.3f}")

    for name, value in metrics[
        "test_optimized_threshold"
    ].items():
        if isinstance(value, float):
            print(f"{name}: {value:.4f}")

    print("\nOptimized Confusion Matrix")
    print("--------------------------")
    print(cm)

    print("\nClassification Report")
    print("---------------------")

    print(
        classification_report(
            y_test,
            tuned_predictions,
            target_names=["ON_TIME_OR_EARLY", "LATE"],
            zero_division=0
        )
    )

    print("\nSaved outputs:")
    print(METRICS_PATH)
    print(THRESHOLD_PATH)
    print(OOF_PATH)
    print(CONFUSION_MATRIX_PATH)

    print("\nThreshold optimization completed.")


if __name__ == "__main__":
    main()
