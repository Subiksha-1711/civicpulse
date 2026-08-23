"""
CivicPulse — Dataset V2 Audit
==============================

Purpose:
    Validate the synthetic CivicPulse dataset before using it
    for ML training and evaluation.

Checks:
    1. Schema integrity
    2. Missing values / duplicate IDs
    3. Category-subcategory hierarchy
    4. Subcategory balance
    5. Text quality
    6. Exact duplicate descriptions
    7. Issue-cluster consistency
    8. Singleton vs clustered issue structure
    9. Geographic consistency
    10. Timestamp validity
    11. Potential near-duplicate descriptions
    12. Potential label leakage / suspicious text patterns

IMPORTANT:
    This is a DATASET AUDIT only.
    It does not train or modify any ML model.
"""

from pathlib import Path
from collections import Counter

import re
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# 1. CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = BASE_DIR / "civicpulse_dataset_v2.csv"

EXPECTED_COLUMNS = [
    "complaint_id",
    "description",
    "category",
    "subcategory",
    "latitude",
    "longitude",
    "timestamp",
    "ground_truth_issue_id",
    "is_duplicate",
]

EXPECTED_HIERARCHY = {
    "Road": {
        "Pothole",
        "Road damage",
        "Traffic signal",
    },
    "Streetlight": {
        "Broken streetlight",
    },
    "Sanitation": {
        "Garbage collection",
        "Waste dumping",
    },
    "Drainage": {
        "Drain overflow",
        "Waterlogging",
    },
    "Water": {
        "Water supply",
        "Water quality",
    },
    "Electricity": {
        "Power outage",
        "Electrical hazard",
    },
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def print_header(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def pass_check(message):
    print(f"✓ {message}")


def warning(message):
    print(f"⚠ {message}")


def fail_check(message):
    print(f"✗ {message}")


# ============================================================
# 2. LOAD DATASET
# ============================================================

print_header("CIVICPULSE DATASET V2 AUDIT")

print(f"Dataset: {DATASET_PATH}")

if not DATASET_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found:\n{DATASET_PATH}"
    )

df = pd.read_csv(DATASET_PATH)

print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")


# ============================================================
# 3. SCHEMA CHECK
# ============================================================

print_header("1. SCHEMA INTEGRITY")

actual_columns = list(df.columns)

if actual_columns == EXPECTED_COLUMNS:
    pass_check("Column names and order are correct.")
else:
    fail_check("Column structure does not match expected schema.")

    print("\nExpected:")
    print(EXPECTED_COLUMNS)

    print("\nActual:")
    print(actual_columns)


if len(df) == 1200:
    pass_check("Dataset contains exactly 1,200 records.")
else:
    warning(
        f"Expected 1,200 records but found {len(df)}."
    )


# ============================================================
# 4. MISSING VALUES
# ============================================================

print_header("2. MISSING VALUES")

missing = df[EXPECTED_COLUMNS].isna().sum()

total_missing = int(missing.sum())

if total_missing == 0:
    pass_check("No missing values detected.")
else:
    fail_check(
        f"{total_missing} missing values detected."
    )

    print(missing[missing > 0])


# ============================================================
# 5. DUPLICATE IDS
# ============================================================

print_header("3. UNIQUE IDENTIFIERS")

duplicate_ids = df["complaint_id"].duplicated().sum()

if duplicate_ids == 0:
    pass_check("All complaint IDs are unique.")
else:
    fail_check(
        f"{duplicate_ids} duplicate complaint IDs found."
    )


duplicate_issue_ids = df["ground_truth_issue_id"].duplicated().sum()

print(
    f"Unique underlying issues: "
    f"{df['ground_truth_issue_id'].nunique()}"
)


# ============================================================
# 6. CATEGORY / SUBCATEGORY HIERARCHY
# ============================================================

print_header("4. CATEGORY → SUBCATEGORY HIERARCHY")

hierarchy_errors = []

for _, row in df.iterrows():

    category = row["category"]
    subcategory = row["subcategory"]

    if category not in EXPECTED_HIERARCHY:
        hierarchy_errors.append(
            f"Unknown category: {category}"
        )
        continue

    if subcategory not in EXPECTED_HIERARCHY[category]:
        hierarchy_errors.append(
            f"{category} → {subcategory}"
        )


if not hierarchy_errors:
    pass_check(
        "Every category/subcategory combination is valid."
    )
else:
    fail_check(
        f"{len(hierarchy_errors)} invalid hierarchy records."
    )

    for error in hierarchy_errors[:20]:
        print("  ", error)


# ============================================================
# 7. CATEGORY DISTRIBUTION
# ============================================================

print_header("5. CATEGORY DISTRIBUTION")

category_counts = df["category"].value_counts()

print(category_counts.to_string())

print(
    f"\nNumber of categories: "
    f"{df['category'].nunique()}"
)


# ============================================================
# 8. SUBCATEGORY DISTRIBUTION
# ============================================================

print_header("6. SUBCATEGORY DISTRIBUTION")

subcategory_counts = df["subcategory"].value_counts()

print(subcategory_counts.to_string())

print(
    f"\nNumber of subcategories: "
    f"{df['subcategory'].nunique()}"
)

min_count = subcategory_counts.min()

if min_count >= 50:
    pass_check(
        f"All subcategories have at least 50 examples. "
        f"Minimum = {min_count}"
    )
else:
    warning(
        f"Smallest subcategory contains only {min_count} examples."
    )


# ============================================================
# 9. TEXT QUALITY
# ============================================================

print_header("7. TEXT QUALITY")

descriptions = df["description"].astype(str)

empty_text = (
    descriptions.str.strip().eq("").sum()
)

if empty_text == 0:
    pass_check("No empty complaint descriptions.")
else:
    fail_check(
        f"{empty_text} empty descriptions found."
    )


text_lengths = descriptions.str.len()

print(
    f"Minimum description length: {text_lengths.min()}"
)

print(
    f"Maximum description length: {text_lengths.max()}"
)

print(
    f"Average description length: "
    f"{text_lengths.mean():.1f}"
)


# Very short descriptions
very_short = df[text_lengths < 20]

if len(very_short) == 0:
    pass_check(
        "No extremely short descriptions (<20 characters)."
    )
else:
    warning(
        f"{len(very_short)} descriptions are under 20 characters."
    )


# ============================================================
# 10. EXACT DUPLICATE TEXT
# ============================================================

print_header("8. EXACT DUPLICATE DESCRIPTIONS")

duplicate_text_mask = descriptions.duplicated(
    keep=False
)

duplicate_text_count = duplicate_text_mask.sum()

if duplicate_text_count == 0:
    pass_check("No exact duplicate complaint descriptions.")
else:
    warning(
        f"{duplicate_text_count} records belong to exact "
        f"duplicate-description groups."
    )

    print(
        df.loc[
            duplicate_text_mask,
            [
                "complaint_id",
                "description",
                "ground_truth_issue_id",
            ],
        ].head(20).to_string(index=False)
    )


# ============================================================
# 11. DUPLICATE / CLUSTER STRUCTURE
# ============================================================

print_header("9. ISSUE CLUSTER STRUCTURE")

cluster_sizes = (
    df.groupby("ground_truth_issue_id")
    .size()
)

num_issues = len(cluster_sizes)

singleton_count = (
    cluster_sizes == 1
).sum()

clustered_issue_count = (
    cluster_sizes > 1
).sum()

clustered_complaints = (
    cluster_sizes[cluster_sizes > 1].sum()
)

print(f"Unique underlying issues : {num_issues}")
print(f"Singleton issues         : {singleton_count}")
print(f"Clustered issues         : {clustered_issue_count}")
print(f"Clustered complaints     : {clustered_complaints}")

print(
    f"Minimum cluster size     : {cluster_sizes.min()}"
)

print(
    f"Maximum cluster size     : {cluster_sizes.max()}"
)

print(
    f"Average cluster size     : {cluster_sizes.mean():.2f}"
)


# ============================================================
# 12. is_duplicate CONSISTENCY
# ============================================================

print_header("10. DUPLICATE FLAG CONSISTENCY")

flag_errors = []

for issue_id, group in df.groupby(
    "ground_truth_issue_id"
):

    cluster_size = len(group)

    expected_duplicate = cluster_size > 1

    actual_values = set(
        group["is_duplicate"]
    )

    if actual_values != {expected_duplicate}:

        flag_errors.append({
            "issue_id": issue_id,
            "cluster_size": cluster_size,
            "flags": actual_values,
        })


if not flag_errors:
    pass_check(
        "is_duplicate flags are consistent with issue cluster size."
    )
else:
    fail_check(
        f"{len(flag_errors)} issue clusters have inconsistent "
        f"is_duplicate flags."
    )

    for error in flag_errors[:20]:
        print(error)


# ============================================================
# 13. CLUSTER LABEL CONSISTENCY
# ============================================================

print_header("11. CLUSTER LABEL CONSISTENCY")

cluster_label_errors = []

for issue_id, group in df.groupby(
    "ground_truth_issue_id"
):

    category_count = group["category"].nunique()
    subcategory_count = group["subcategory"].nunique()

    if category_count > 1 or subcategory_count > 1:

        cluster_label_errors.append({
            "issue_id": issue_id,
            "categories": group["category"].unique().tolist(),
            "subcategories": group["subcategory"].unique().tolist(),
        })


if not cluster_label_errors:
    pass_check(
        "Every underlying issue has consistent category "
        "and subcategory labels."
    )
else:
    warning(
        f"{len(cluster_label_errors)} clusters contain "
        f"mixed category/subcategory labels."
    )

    for error in cluster_label_errors[:20]:
        print(error)


# ============================================================
# 14. GEOGRAPHIC VALIDATION
# ============================================================

print_header("12. GEOGRAPHIC DATA")

lat_valid = (
    df["latitude"].between(10.8, 11.2)
).all()

lon_valid = (
    df["longitude"].between(76.7, 77.2)
).all()

if lat_valid and lon_valid:
    pass_check(
        "All coordinates fall within the expected "
        "Coimbatore region."
    )
else:
    warning(
        "Some coordinates fall outside the expected "
        "Coimbatore bounding region."
    )


# ============================================================
# 15. GEOGRAPHIC CLUSTER COHERENCE
# ============================================================

print_header("13. GEOGRAPHIC CLUSTER COHERENCE")

geo_issues = []

for issue_id, group in df.groupby(
    "ground_truth_issue_id"
):

    if len(group) <= 1:
        continue

    lat_range = (
        group["latitude"].max()
        - group["latitude"].min()
    )

    lon_range = (
        group["longitude"].max()
        - group["longitude"].min()
    )

    # Rough sanity threshold.
    # This is not a physical distance calculation.
    if lat_range > 0.02 or lon_range > 0.02:

        geo_issues.append({
            "issue_id": issue_id,
            "cluster_size": len(group),
            "lat_range": lat_range,
            "lon_range": lon_range,
        })


if not geo_issues:
    pass_check(
        "No obviously geographically scattered issue clusters."
    )
else:
    warning(
        f"{len(geo_issues)} issue clusters have unusually "
        f"large geographic spread."
    )

    for issue in geo_issues[:20]:
        print(issue)


# ============================================================
# 16. TIMESTAMP VALIDATION
# ============================================================

print_header("14. TIMESTAMP VALIDATION")

timestamps = pd.to_datetime(
    df["timestamp"],
    errors="coerce"
)

invalid_timestamps = timestamps.isna().sum()

if invalid_timestamps == 0:
    pass_check("All timestamps are valid.")
else:
    fail_check(
        f"{invalid_timestamps} invalid timestamps found."
    )

print(
    f"Earliest timestamp: {timestamps.min()}"
)

print(
    f"Latest timestamp:   {timestamps.max()}"
)


# ============================================================
# 17. LANGUAGE / TEMPLATE LEAKAGE CHECK
# ============================================================

print_header("15. POTENTIAL TEXT LEAKAGE")

print(
    "Checking for highly similar complaint descriptions..."
)

sample_size = min(
    len(df),
    1200
)

texts = descriptions.tolist()[:sample_size]

vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    min_df=1
)

tfidf_matrix = vectorizer.fit_transform(texts)

similarity_matrix = cosine_similarity(
    tfidf_matrix
)

# Only inspect upper triangle.
pairs = []

for i in range(sample_size):

    for j in range(i + 1, sample_size):

        similarity = similarity_matrix[i, j]

        if similarity >= 0.90:

            pairs.append({
                "i": i,
                "j": j,
                "similarity": similarity,
            })


if not pairs:
    pass_check(
        "No extremely similar complaint pairs "
        "(cosine similarity >= 0.90)."
    )
else:
    warning(
        f"{len(pairs)} highly similar complaint pairs detected."
    )

    print(
        "\nTop suspicious pairs:"
    )

    pairs = sorted(
        pairs,
        key=lambda x: x["similarity"],
        reverse=True
    )

    for pair in pairs[:15]:

        i = pair["i"]
        j = pair["j"]

        print(
            f"\nSimilarity: "
            f"{pair['similarity']:.3f}"
        )

        print(
            f"A: {df.iloc[i]['description']}"
        )

        print(
            f"B: {df.iloc[j]['description']}"
        )

        print(
            f"A label: "
            f"{df.iloc[i]['category']} → "
            f"{df.iloc[i]['subcategory']}"
        )

        print(
            f"B label: "
            f"{df.iloc[j]['category']} → "
            f"{df.iloc[j]['subcategory']}"
        )


# ============================================================
# 18. LABEL-LEAKAGE KEYWORD CHECK
# ============================================================

print_header("16. OBVIOUS LABEL WORD CHECK")

label_terms = {
    "Pothole": ["pothole"],
    "Road damage": ["road damage"],
    "Traffic signal": ["traffic signal", "traffic light"],
    "Broken streetlight": ["streetlight", "street light"],
    "Garbage collection": ["garbage collection"],
    "Waste dumping": ["waste dumping"],
    "Drain overflow": ["drain overflow"],
    "Waterlogging": ["waterlogging"],
    "Water supply": ["water supply"],
    "Water quality": ["water quality"],
    "Power outage": ["power outage"],
    "Electrical hazard": ["electrical hazard"],
}

label_leak_counts = {}

for subcategory, terms in label_terms.items():

    count = 0

    for text in descriptions.str.lower():

        if any(term in text for term in terms):

            count += 1

    label_leak_counts[subcategory] = count


for subcategory, count in label_leak_counts.items():

    percentage = (
        count / len(df) * 100
    )

    print(
        f"{subcategory:<22} "
        f"{count:>4} records "
        f"({percentage:.1f}% of dataset)"
    )


# ============================================================
# 19. FINAL SUMMARY
# ============================================================

print_header("FINAL DATASET AUDIT SUMMARY")

checks = {
    "Schema": actual_columns == EXPECTED_COLUMNS,
    "Row count": len(df) == 1200,
    "No missing values": total_missing == 0,
    "Unique complaint IDs": duplicate_ids == 0,
    "Valid hierarchy": len(hierarchy_errors) == 0,
    "No exact duplicate text": duplicate_text_count == 0,
    "Duplicate flags consistent": len(flag_errors) == 0,
    "Cluster labels consistent": len(cluster_label_errors) == 0,
    "Valid coordinates": lat_valid and lon_valid,
    "Valid timestamps": invalid_timestamps == 0,
}


for check_name, result in checks.items():

    if result:
        print(f"✓ {check_name}")

    else:
        print(f"✗ {check_name}")


failed_checks = [
    name
    for name, result in checks.items()
    if not result
]


print("\n" + "-" * 70)

if not failed_checks:

    print(
        "DATASET STATUS: STRUCTURALLY VALID"
    )

    print(
        "\nImportant:"
        "\nStructural validity does NOT guarantee that "
        "the dataset is free from synthetic-template leakage."
        "\nReview the similarity warnings above before "
        "using model accuracy as a final claim."
    )

else:

    print(
        "DATASET STATUS: REQUIRES FIXES"
    )

    print(
        "\nFailed checks:"
    )

    for failure in failed_checks:
        print(
            f"  ✗ {failure}"
        )


print("\nAudit complete.")