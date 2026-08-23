"""
CivicPulse — Track A: Issue-Level Evaluation
==============================================

Evaluates complaint classification while preventing leakage
between complaints belonging to the same underlying civic issue.

Instead of randomly splitting individual complaints, we split
using ground_truth_issue_id.

Therefore, all complaints from one civic issue stay entirely
inside either TRAIN or TEST.

This gives us a more realistic estimate of generalization.
"""

from pathlib import Path

import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC

from sklearn.pipeline import Pipeline

from sklearn.model_selection import GroupShuffleSplit

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)


# ============================================================
# 1. LOAD DATASET
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = BASE_DIR / "civicpulse_dataset_v2.csv"

df = pd.read_csv(DATASET_PATH)

print("=" * 70)
print("CIVICPULSE — ISSUE-LEVEL MODEL EVALUATION")
print("=" * 70)

print(f"\nDataset: {DATASET_PATH}")
print(f"Total complaints: {len(df)}")
print(
    f"Unique underlying issues: "
    f"{df['ground_truth_issue_id'].nunique()}"
)


# ============================================================
# 2. GROUP-AWARE TRAIN / TEST SPLIT
# ============================================================

X = df["description"]

y_category = df["category"]

y_subcategory = df["subcategory"]

groups = df["ground_truth_issue_id"]


splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.20,
    random_state=42
)

train_idx, test_idx = next(
    splitter.split(
        X,
        y_category,
        groups=groups
    )
)


X_train = X.iloc[train_idx]
X_test = X.iloc[test_idx]

y_category_train = y_category.iloc[train_idx]
y_category_test = y_category.iloc[test_idx]

y_subcategory_train = y_subcategory.iloc[train_idx]
y_subcategory_test = y_subcategory.iloc[test_idx]

groups_train = groups.iloc[train_idx]
groups_test = groups.iloc[test_idx]


print("\n" + "=" * 70)
print("ISSUE-LEVEL SPLIT")
print("=" * 70)

print(
    f"Training complaints : {len(X_train)}"
)

print(
    f"Testing complaints  : {len(X_test)}"
)

print(
    f"Training issues     : {groups_train.nunique()}"
)

print(
    f"Testing issues      : {groups_test.nunique()}"
)


# ============================================================
# 3. VERIFY NO ISSUE LEAKAGE
# ============================================================

train_issues = set(groups_train)

test_issues = set(groups_test)

overlap = train_issues.intersection(test_issues)

print(
    f"\nIssue overlap between train/test: {len(overlap)}"
)

if overlap:
    raise RuntimeError(
        "DATA LEAKAGE DETECTED: "
        "Some ground_truth_issue_id values appear "
        "in both train and test."
    )

print(
    "✓ No underlying civic issue appears in both "
    "training and testing."
)


# ============================================================
# 4. MODEL DEFINITIONS
# ============================================================

def logistic_model():

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


def svm_model():

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
# 5. EVALUATION FUNCTION
# ============================================================

def evaluate(
    model,
    model_name,
    task_name,
    X_train,
    X_test,
    y_train,
    y_test
):

    print("\n" + "-" * 70)
    print(f"MODEL: {model_name}")
    print(f"TASK : {task_name}")
    print("-" * 70)

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        average="macro",
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        average="macro",
        zero_division=0
    )

    f1_macro = f1_score(
        y_test,
        predictions,
        average="macro",
        zero_division=0
    )

    f1_weighted = f1_score(
        y_test,
        predictions,
        average="weighted",
        zero_division=0
    )

    print(
        f"Accuracy          : {accuracy:.4f}"
    )

    print(
        f"Macro Precision   : {precision:.4f}"
    )

    print(
        f"Macro Recall      : {recall:.4f}"
    )

    print(
        f"Macro F1          : {f1_macro:.4f}"
    )

    print(
        f"Weighted F1       : {f1_weighted:.4f}"
    )

    return {
        "model": model_name,
        "task": task_name,
        "accuracy": accuracy,
        "precision_macro": precision,
        "recall_macro": recall,
        "f1_macro": f1_macro,
        "f1_weighted": f1_weighted,
        "predictions": predictions,
    }


# ============================================================
# 6. CATEGORY EVALUATION
# ============================================================

print("\n" + "=" * 70)
print("CATEGORY CLASSIFICATION")
print("=" * 70)

category_logistic = evaluate(
    logistic_model(),
    "TF-IDF + Logistic Regression",
    "Category",
    X_train,
    X_test,
    y_category_train,
    y_category_test
)

category_svm = evaluate(
    svm_model(),
    "TF-IDF + Linear SVM",
    "Category",
    X_train,
    X_test,
    y_category_train,
    y_category_test
)


# ============================================================
# 7. SUBCATEGORY EVALUATION
# ============================================================

print("\n" + "=" * 70)
print("SUBCATEGORY CLASSIFICATION")
print("=" * 70)

subcategory_logistic = evaluate(
    logistic_model(),
    "TF-IDF + Logistic Regression",
    "Subcategory",
    X_train,
    X_test,
    y_subcategory_train,
    y_subcategory_test
)

subcategory_svm = evaluate(
    svm_model(),
    "TF-IDF + Linear SVM",
    "Subcategory",
    X_train,
    X_test,
    y_subcategory_train,
    y_subcategory_test
)


# ============================================================
# 8. DETAILED CLASSIFICATION REPORTS
# ============================================================

print("\n" + "=" * 70)
print("BEST CATEGORY MODEL — DETAILED REPORT")
print("=" * 70)

if (
    category_logistic["f1_macro"]
    >= category_svm["f1_macro"]
):

    best_category_model = logistic_model()
    best_category_model.fit(
        X_train,
        y_category_train
    )

    category_predictions = (
        best_category_model.predict(X_test)
    )

    best_category_name = (
        "TF-IDF + Logistic Regression"
    )

else:

    best_category_model = svm_model()
    best_category_model.fit(
        X_train,
        y_category_train
    )

    category_predictions = (
        best_category_model.predict(X_test)
    )

    best_category_name = (
        "TF-IDF + Linear SVM"
    )


print(
    f"\nSelected model: {best_category_name}\n"
)

print(
    classification_report(
        y_category_test,
        category_predictions,
        zero_division=0
    )
)


# ============================================================
# 9. BEST SUBCATEGORY MODEL
# ============================================================

print("\n" + "=" * 70)
print("BEST SUBCATEGORY MODEL — DETAILED REPORT")
print("=" * 70)

if (
    subcategory_logistic["f1_macro"]
    >= subcategory_svm["f1_macro"]
):

    best_subcategory_model = logistic_model()

    best_subcategory_model.fit(
        X_train,
        y_subcategory_train
    )

    subcategory_predictions = (
        best_subcategory_model.predict(X_test)
    )

    best_subcategory_name = (
        "TF-IDF + Logistic Regression"
    )

else:

    best_subcategory_model = svm_model()

    best_subcategory_model.fit(
        X_train,
        y_subcategory_train
    )

    subcategory_predictions = (
        best_subcategory_model.predict(X_test)
    )

    best_subcategory_name = (
        "TF-IDF + Linear SVM"
    )


print(
    f"\nSelected model: {best_subcategory_name}\n"
)

print(
    classification_report(
        y_subcategory_test,
        subcategory_predictions,
        zero_division=0
    )
)


# ============================================================
# 10. CONFUSION MATRICES
# ============================================================

print("\n" + "=" * 70)
print("CATEGORY CONFUSION MATRIX")
print("=" * 70)

category_labels = sorted(
    y_category.unique()
)

category_cm = confusion_matrix(
    y_category_test,
    category_predictions,
    labels=category_labels
)

print(
    pd.DataFrame(
        category_cm,
        index=category_labels,
        columns=category_labels
    )
)


print("\n" + "=" * 70)
print("SUBCATEGORY CONFUSION MATRIX")
print("=" * 70)

subcategory_labels = sorted(
    y_subcategory.unique()
)

subcategory_cm = confusion_matrix(
    y_subcategory_test,
    subcategory_predictions,
    labels=subcategory_labels
)

print(
    pd.DataFrame(
        subcategory_cm,
        index=subcategory_labels,
        columns=subcategory_labels
    )
)


# ============================================================
# 11. SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("ISSUE-LEVEL EVALUATION SUMMARY")
print("=" * 70)

print(
    "\nCATEGORY"
)

print(
    f"Logistic Regression Macro F1: "
    f"{category_logistic['f1_macro']:.4f}"
)

print(
    f"Linear SVM Macro F1         : "
    f"{category_svm['f1_macro']:.4f}"
)

print(
    "\nSUBCATEGORY"
)

print(
    f"Logistic Regression Macro F1: "
    f"{subcategory_logistic['f1_macro']:.4f}"
)

print(
    f"Linear SVM Macro F1         : "
    f"{subcategory_svm['f1_macro']:.4f}"
)

print("\n✓ Issue-level evaluation complete.")