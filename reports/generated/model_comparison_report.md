# Model Evaluation and Comparative Analysis
## E-Commerce Business Intelligence and Decision Support System

### 1. Evaluation Objective

This evaluation compares two supervised machine learning classifiers developed to predict whether an e-commerce order will be delivered later than its estimated delivery date.

The models are:

1. Logistic Regression – baseline model.
2. Random Forest – improved model.

The positive class is LATE (1), and the negative class is ON_TIME_OR_EARLY (0).

The objective is to identify a model that provides useful early delivery-risk predictions while considering the operational consequences of false alerts and missed late deliveries.

### 2. Dataset and Experimental Setup

The models were trained and evaluated using the prepared delivery ML dataset.

| Item | Value |
|---|---:|
| Total eligible records | 96,456 |
| Training records | 77,164 |
| Testing records | 19,292 |
| Late deliveries in test set | 1,307 |
| On-time or early deliveries in test set | 17,985 |
| Test-set late delivery rate | 6.77% |
| Random state | 42 |
| Data splitting strategy | StratifiedGroupKFold |

Both models use the same training and test partitions. Group-aware splitting was used to reduce the risk of identical predictor combinations appearing in both partitions.

The test set was not used to select the classification thresholds.

### 3. Model Configuration

#### 3.1 Logistic Regression – Baseline

The baseline model uses:

- Median imputation for numerical features.
- Standard scaling for numerical features.
- Most-frequent imputation for categorical features.
- One-hot encoding for categorical features.
- Logistic Regression with class_weight="balanced".
- Maximum iterations: 2,000.
- Random state: 42.

#### 3.2 Random Forest – Improved Model

The improved model uses:

- Median imputation for numerical features.
- Most-frequent imputation for categorical features.
- One-hot encoding for categorical features.
- 400 decision trees.
- Maximum features: sqrt.
- Maximum depth: unrestricted.
- Minimum samples per leaf: 2.
- Class weighting: balanced_subsample.
- Random state: 42.

### 4. Classification Threshold Selection

Both models initially used the default classification threshold of 0.50.

Threshold selection was subsequently performed using five-fold StratifiedGroupKFold out-of-fold predictions generated from the training partition.

The threshold producing the maximum F1-score was selected. The original test set remained untouched during this selection process.

| Model | Selected threshold | OOF precision | OOF recall | OOF F1 |
|---|---:|---:|---:|---:|
| Logistic Regression | 0.50 | 0.1177 | 0.6340 | 0.1985 |
| Random Forest | 0.33 | 0.2773 | 0.3976 | 0.3267 |

Logistic Regression retained its default threshold of 0.50. Random Forest benefited from a lower threshold of 0.33.

### 5. Test Set Performance Comparison

The following results were obtained on the same untouched test set, using each model's selected threshold.

| Metric | Logistic Regression (0.50) | Random Forest (0.33) |
|---|---:|---:|
| Accuracy | 0.6637 | 0.8924 |
| Precision | 0.1242 | 0.2975 |
| Recall | 0.6549 | 0.4323 |
| F1-score | 0.2088 | 0.3525 |
| ROC-AUC | 0.7108 | 0.7992 |
| PR-AUC | 0.1588 | 0.2871 |

#### 5.1 Interpretation

**Accuracy:** Random Forest achieves higher accuracy. However, accuracy alone is not sufficient because only approximately 6.77% of the test records represent late deliveries.

**Precision:** Random Forest achieves higher precision (29.75% compared with 12.42%). Its late-delivery alerts are therefore more reliable.

**Recall:** Logistic Regression achieves higher recall (65.49% compared with 43.23%). It identifies more of the actual late deliveries.

**F1-score:** Random Forest achieves a higher F1-score (0.3525 compared with 0.2088), indicating a better balance between precision and recall.

**ROC-AUC:** Random Forest achieves 0.7992 compared with 0.7108, showing better ranking discrimination between late and non-late deliveries.

**PR-AUC:** Random Forest achieves 0.2871 compared with 0.1588. This is particularly relevant for the imbalanced target because it evaluates precision-recall performance.

#### 5.2 Effect of Random Forest Threshold Optimisation

The Random Forest model was initially evaluated using the default threshold of 0.50. The threshold was subsequently reduced to 0.33 based on five-fold out-of-fold predictions.

| Metric | Default (0.50) | Selected (0.33) |
|---|---:|---:|
| Accuracy | 0.9289 | 0.8924 |
| Precision | 0.4360 | 0.2975 |
| Recall | 0.1668 | 0.4323 |
| F1-score | 0.2413 | 0.3525 |
| True positives | 218 | 565 |
| False positives | 282 | 1,334 |

The lower threshold increased the number of correctly identified late deliveries from 218 to 565, detecting 347 additional late deliveries. Recall increased from 16.68% to 43.23%, and F1-score increased from 0.2413 to 0.3525.

This improvement came at the cost of lower precision and accuracy, alongside an increase in false-positive alerts. The threshold adjustment therefore represents a deliberate trade-off to improve late-delivery detection rather than maximise overall accuracy.

### 6. Confusion Matrix Analysis

#### 6.1 Logistic Regression

| Actual / Predicted | On-time | Late |
|---|---:|---:|
| Actual on-time | 11,948 | 6,037 |
| Actual late | 451 | 856 |

- True negatives: 11,948
- False positives: 6,037
- False negatives: 451
- True positives: 856

The baseline identifies 856 of the 1,307 actual late deliveries. However, it generates 6,037 false late-delivery alerts.

#### 6.2 Random Forest

| Actual / Predicted | On-time | Late |
|---|---:|---:|
| Actual on-time | 16,651 | 1,334 |
| Actual late | 742 | 565 |

- True negatives: 16,651
- False positives: 1,334
- False negatives: 742
- True positives: 565

Random Forest substantially reduces false alerts but misses more actual late deliveries than Logistic Regression.

### 7. Business Interpretation

The two models provide different operational benefits.

**Logistic Regression: Higher-risk coverage**

The baseline detects 856 actual late deliveries, compared with 565 detected by Random Forest. This may be useful where the cost of missing a late delivery is particularly high.

However, its 6,037 false alerts could create a substantial workload for customer service and logistics teams.

**Random Forest: More selective risk identification**

Random Forest reduces false alerts to 1,334 and provides higher precision. This could help operational teams focus their attention on a smaller set of orders with a higher probability of late delivery.

However, it misses 742 actual late deliveries, so relying exclusively on its alerts could leave a significant proportion of late orders unidentified.

### 8. Model Selection

Based on the evaluated results, Random Forest is selected as the preferred overall model for the current decision support system.

The selection is supported by:

- Higher F1-score.
- Higher precision.
- Higher ROC-AUC.
- Higher PR-AUC.
- Fewer false-positive alerts.

The selected threshold is 0.33.

This is an overall model-selection decision based on the evaluated metrics, not proof that Random Forest is optimal for every operational scenario.

If the business places a higher cost on missing late deliveries, Logistic Regression's higher recall may be preferable. The final operational threshold should therefore be informed by the relative costs of false positives and false negatives.

### 9. Limitations and Trade-offs

1. **Class imbalance:** Only approximately 6.77% of eligible delivered orders were late. This affects classification performance and makes accuracy alone misleading.

2. **Historical completed orders:** The training population consists of delivered orders with the required timestamps. The model may not generalise fully to cancelled, unavailable, or currently undelivered orders.

3. **Estimated delivery date assumption:** The estimated delivery date is treated as available at the order approval prediction point. The source data does not independently establish exactly when this estimate was first generated.

4. **Historical data quality:** Temporal anomalies were identified in some carrier and delivery timestamps. Actual post-prediction delivery timestamps were excluded from model predictors to avoid target leakage.

5. **Threshold trade-off:** A lower threshold can increase recall but also increase false alerts. The selected threshold should be reviewed against operational costs.

6. **Generalisation:** Results are based on a historical Brazilian e-commerce dataset. Further validation is required before applying the model to another platform, country, or operational environment.

7. **Model interpretation:** Random Forest provides a stronger overall predictive result, but additional feature-importance and explainability analysis is needed to understand the main drivers of predicted delivery risk.

### 10. Conclusion

The comparative evaluation demonstrates that the Random Forest model outperforms the Logistic Regression baseline on F1-score, precision, ROC-AUC, and PR-AUC when evaluated using their selected classification thresholds.

The Logistic Regression model nevertheless achieves higher recall and detects more late deliveries, highlighting the trade-off between risk coverage and alert reliability.

Random Forest with a threshold of 0.33 is therefore selected as the current preferred model for integration into the E-Commerce Business Intelligence and Decision Support System.

The model should be treated as a decision-support component rather than a guarantee of delivery outcomes. Operational validation, explainability analysis, and monitoring are recommended before deployment.

---

**Evaluation reproducibility references**

- `src/models/train_logistic_regression.py`
- `src/models/optimize_logistic_regression_threshold.py`
- `src/models/train_random_forest.py`
- `src/models/optimize_random_forest_threshold.py`
- `reports/generated/logistic_regression_metrics.json`
- `reports/generated/logistic_regression_threshold_metrics.json`
- `reports/generated/random_forest_metrics.json`
- `reports/generated/random_forest_threshold_metrics.json`
- `reports/generated/logistic_regression_threshold_confusion_matrix.csv`
- `reports/generated/random_forest_threshold_confusion_matrix.csv`
