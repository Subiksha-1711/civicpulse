"""
CivicPulse — Track A: Model Evaluation
========================================

Evaluates the current complaint classification models using
Stratified K-Fold Cross-Validation.

Models compared:
1. TF-IDF + Logistic Regression
2. TF-IDF + Linear SVM

Tasks evaluated:
- Category classification
- Subcategory classification

Metrics:
- Accuracy
- Precision
- Recall
- F1-score

The purpose of this file is to establish a reliable baseline
before modifying the production classification pipeline.
"""

from pathlib import Path

import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC

from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline

from sklearn.metrics import make_scorer
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)



# ============================================================
# 1. LOAD DATASET
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "civicpulse_dataset_v2.csv"

df = pd.read_csv(DATASET_PATH)

print("=" * 70)
print("CIVICPULSE — TRACK A MODEL EVALUATION")
print("=" * 70)

print(f"\nDataset path : {DATASET_PATH}")
print(f"Total rows   : {len(df)}")

print("\nColumns:")
print(list(df.columns))


# ============================================================
# 2. BASIC DATASET INSPECTION
# ============================================================

print("\n" + "=" * 70)
print("CATEGORY DISTRIBUTION")
print("=" * 70)

print(df["category"].value_counts())

print("\n" + "=" * 70)
print("SUBCATEGORY DISTRIBUTION")
print("=" * 70)

print(df["subcategory"].value_counts())


# Check missing descriptions / labels
print("\n" + "=" * 70)
print("DATA QUALITY CHECK")
print("=" * 70)

print(f"Missing descriptions : {df['description'].isna().sum()}")
print(f"Missing categories   : {df['category'].isna().sum()}")
print(f"Missing subcategories: {df['subcategory'].isna().sum()}")

print(f"Duplicate complaint IDs: {df['complaint_id'].duplicated().sum()}")


# Remove rows that cannot be used for supervised learning
df = df.dropna(subset=["description", "category", "subcategory"]).copy()

X = df["description"]

y_category = df["category"]

y_subcategory = df["subcategory"]


# ============================================================
# 3. CROSS-VALIDATION CONFIGURATION
# ============================================================

# Stratified K-Fold preserves the class distribution in each fold.

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)


# ============================================================
# 4. EVALUATION METRICS
# ============================================================

scoring = {
    "accuracy": "accuracy",

    "precision_macro": make_scorer(
        precision_score,
        average="macro",
        zero_division=0
    ),

    "recall_macro": make_scorer(
        recall_score,
        average="macro",
        zero_division=0
    ),

    "f1_macro": make_scorer(
        f1_score,
        average="macro",
        zero_division=0
    ),

    "f1_weighted": make_scorer(
        f1_score,
        average="weighted",
        zero_division=0
    ),
}


# ============================================================
# 5. MODEL DEFINITIONS
# ============================================================

def create_logistic_pipeline():
    """
    TF-IDF + Logistic Regression
    """

    return Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.9,
                sublinear_tf=True
            )
        ),

        (
            "classifier",
            LogisticRegression(
                max_iter=2000,
                C=5.0
            )
        )
    ])


def create_svm_pipeline():
    """
    TF-IDF + Linear SVM
    """

    return Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.9,
                sublinear_tf=True
            )
        ),

        (
            "classifier",
            LinearSVC(
                C=1.0
            )
        )
    ])


# ============================================================
# 6. EVALUATION FUNCTION
# ============================================================

def evaluate_model(model, X, y, model_name, task_name):
    """
    Run cross-validation and print averaged metrics.
    """

    print("\n" + "-" * 70)
    print(f"MODEL   : {model_name}")
    print(f"TASK    : {task_name}")
    print("-" * 70)

    results = cross_validate(
        model,
        X,
        y,
        cv=cv,
        scoring=scoring,
        n_jobs=-1
    )

    metrics = {
        "accuracy": results["test_accuracy"].mean(),
        "precision_macro": results["test_precision_macro"].mean(),
        "recall_macro": results["test_recall_macro"].mean(),
        "f1_macro": results["test_f1_macro"].mean(),
        "f1_weighted": results["test_f1_weighted"].mean(),
    }

    for metric, value in metrics.items():
        print(f"{metric:<20}: {value:.4f}")

    return metrics


# ============================================================
# 7. CATEGORY EVALUATION
# ============================================================

print("\n" + "=" * 70)
print("CATEGORY CLASSIFICATION")
print("=" * 70)

category_results = {}

category_results["Logistic Regression"] = evaluate_model(
    create_logistic_pipeline(),
    X,
    y_category,
    "TF-IDF + Logistic Regression",
    "Category"
)

category_results["Linear SVM"] = evaluate_model(
    create_svm_pipeline(),
    X,
    y_category,
    "TF-IDF + Linear SVM",
    "Category"
)


# ============================================================
# 8. SUBCATEGORY EVALUATION
# ============================================================

print("\n" + "=" * 70)
print("SUBCATEGORY CLASSIFICATION")
print("=" * 70)

subcategory_results = {}

subcategory_results["Logistic Regression"] = evaluate_model(
    create_logistic_pipeline(),
    X,
    y_subcategory,
    "TF-IDF + Logistic Regression",
    "Subcategory"
)

subcategory_results["Linear SVM"] = evaluate_model(
    create_svm_pipeline(),
    X,
    y_subcategory,
    "TF-IDF + Linear SVM",
    "Subcategory"
)


# ============================================================
# 9. COMPARISON TABLE
# ============================================================

print("\n" + "=" * 70)
print("MODEL COMPARISON — CATEGORY")
print("=" * 70)

category_table = pd.DataFrame(category_results).T

print(
    category_table[
        [
            "accuracy",
            "precision_macro",
            "recall_macro",
            "f1_macro",
            "f1_weighted",
        ]
    ].round(4)
)


print("\n" + "=" * 70)
print("MODEL COMPARISON — SUBCATEGORY")
print("=" * 70)

subcategory_table = pd.DataFrame(subcategory_results).T

print(
    subcategory_table[
        [
            "accuracy",
            "precision_macro",
            "recall_macro",
            "f1_macro",
            "f1_weighted",
        ]
    ].round(4)
)


# ============================================================
# 10. BEST MODEL
# ============================================================

best_category_model = max(
    category_results,
    key=lambda model: category_results[model]["f1_macro"]
)

best_subcategory_model = max(
    subcategory_results,
    key=lambda model: subcategory_results[model]["f1_macro"]
)


print("\n" + "=" * 70)
print("BEST MODELS")
print("=" * 70)

print(
    f"\nBest Category Model     : {best_category_model}"
)

print(
    f"Category Macro F1       : "
    f"{category_results[best_category_model]['f1_macro']:.4f}"
)

print(
    f"\nBest Subcategory Model  : {best_subcategory_model}"
)

print(
    f"Subcategory Macro F1    : "
    f"{subcategory_results[best_subcategory_model]['f1_macro']:.4f}"
)


# ============================================================
# 11. SAVE RESULTS
# ============================================================

results_output = []

for model_name, metrics in category_results.items():

    results_output.append({
        "task": "category",
        "model": model_name,
        **metrics
    })


for model_name, metrics in subcategory_results.items():

    results_output.append({
        "task": "subcategory",
        "model": model_name,
        **metrics
    })


results_df = pd.DataFrame(results_output)

output_path = BASE_DIR / "model_evaluation_results.csv"

results_df.to_csv(
    output_path,
    index=False
)

print(
    f"\nEvaluation results saved to:\n{output_path}"
)

print("\nEvaluation complete.")