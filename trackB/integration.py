"""
CivicPulse — Track A + Track B Integration

Interactive end-to-end complaint processing.

Input:
    - Complaint description
    - Latitude
    - Longitude

Track A:
    - Category
    - Subcategory
    - Department
    - Severity

Track B:
    - Existing issue detection
    - NEW_ISSUE / RELATED_ISSUE / DUPLICATE_ISSUE
    - Existing issue ID when applicable
"""

import os
import sys
from datetime import datetime

import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(__file__)
)

TRACK_A_DIR = os.path.join(
    BASE_DIR,
    "trackA"
)

DATASET_PATH = os.path.join(
    TRACK_A_DIR,
    "civicpulse_dataset_v2.csv"
)


# ============================================================
# IMPORT TRACK A
# ============================================================

if TRACK_A_DIR not in sys.path:
    sys.path.insert(0, TRACK_A_DIR)

import classify


# ============================================================
# IMPORT TRACK B
# ============================================================

from issue_index import build_issue_index
from issue_detector import (
    Complaint,
    find_best_issue_match,
)


# ============================================================
# LOAD TRACK A
# ============================================================

def load_track_a():

    print("=" * 70)
    print("LOADING TRACK A")
    print("=" * 70)

    print("Dataset:")
    print(DATASET_PATH)

    df = pd.read_csv(
        DATASET_PATH
    )

    print(
        f"\nLoaded {len(df):,} complaints."
    )

    (
        vectorizer,
        category_model,
        subcategory_model,
        category_report,
        subcategory_report,
    ) = classify.train_classifiers(df)

    print(
        "\nTrack A models trained successfully."
    )

    return (
        vectorizer,
        category_model,
        subcategory_model,
    )


# ============================================================
# LOAD TRACK B
# ============================================================

def load_track_b():

    print("\n" + "=" * 70)
    print("LOADING TRACK B")
    print("=" * 70)

    issues = build_issue_index(
        DATASET_PATH
    )

    print(
        f"\nTrack B indexed "
        f"{len(issues)} underlying issues."
    )

    return issues


# ============================================================
# PROCESS COMPLAINT
# ============================================================

def process_complaint(
    description,
    latitude,
    longitude,
    vectorizer,
    category_model,
    subcategory_model,
    issues,
):

    # ========================================================
    # TRACK A
    # ========================================================

    classification = classify.classify_complaint(
        description,
        vectorizer,
        category_model,
        subcategory_model,
    )

    category = classification[
        "predicted_category"
    ]

    subcategory = classification[
        "predicted_subcategory"
    ]

    # ========================================================
    # TRACK B INPUT
    # ========================================================

    timestamp = datetime.now().isoformat()

    complaint = Complaint(
        complaint_id="NEW_COMPLAINT",
        description=description,
        category=category,
        subcategory=subcategory,
        latitude=latitude,
        longitude=longitude,
        timestamp=timestamp,
    )

    # ========================================================
    # TRACK B
    # ========================================================

    issue_result = find_best_issue_match(
        complaint,
        issues,
    )

    # ========================================================
    # DISPLAY
    # ========================================================

    print("\n" + "=" * 70)
    print("CIVICPULSE — TRACK A + TRACK B")
    print("=" * 70)

    print("\nComplaint:")
    print(f"  {description}")

    print("\nLocation:")
    print(
        f"  Latitude  : {latitude}"
    )
    print(
        f"  Longitude : {longitude}"
    )

    # ========================================================
    # TRACK A OUTPUT
    # ========================================================

    print("\n" + "-" * 70)
    print("TRACK A — CLASSIFICATION")
    print("-" * 70)

    print(
        f"Category       : "
        f"{classification['predicted_category']}"
    )

    print(
        f"Category conf. : "
        f"{classification['category_confidence']}"
    )

    print(
        f"Subcategory    : "
        f"{classification['predicted_subcategory']}"
    )

    print(
        f"Subcategory conf.: "
        f"{classification['subcategory_confidence']}"
    )

    print(
        f"Department     : "
        f"{classification['routed_department']}"
    )

    print(
        f"Severity       : "
        f"{classification['severity_score']}/10 — "
        f"{classification['severity_label']}"
    )

    print("\nWhy:")

    for explanation in classification.get(
        "explanation",
        [],
    ):

        print(
            f"  • {explanation}"
        )

    # ========================================================
    # TRACK B OUTPUT
    # ========================================================

    print("\n" + "-" * 70)
    print("TRACK B — ISSUE DETECTION")
    print("-" * 70)

    decision = issue_result.get(
        "decision",
        "NEW_ISSUE",
    )

    similarity = issue_result.get(
        "overall_similarity",
        0.0,
    )

    matched_issue = issue_result.get(
        "matched_issue_id"
    )

    print(
        f"Decision       : "
        f"{decision}"
    )

    print(
        f"Similarity     : "
        f"{similarity}"
    )

    # Only display an issue ID when an
    # existing issue was actually matched.

    if decision == "NEW_ISSUE":

        print(
            "Matched issue  : "
            "None — new civic issue"
        )

    else:

        print(
            f"Matched issue  : "
            f"{matched_issue}"
        )

    if "distance_km" in issue_result:

        print(
            f"Distance       : "
            f"{issue_result['distance_km']} km"
        )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print("\n" + "=" * 70)
    print("FINAL CIVICPULSE RESULT")
    print("=" * 70)

    print(
        f"Category       : "
        f"{classification['predicted_category']}"
    )

    print(
        f"Subcategory    : "
        f"{classification['predicted_subcategory']}"
    )

    print(
        f"Department     : "
        f"{classification['routed_department']}"
    )

    print(
        f"Severity       : "
        f"{classification['severity_score']}/10 "
        f"({classification['severity_label']})"
    )

    print(
        f"Issue decision : "
        f"{decision}"
    )

    if decision == "NEW_ISSUE":

        final_issue_id = (
            "None — new civic issue"
        )

    else:

        final_issue_id = matched_issue

    print(
        f"Issue ID       : "
        f"{final_issue_id}"
    )

    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main():

    (
        vectorizer,
        category_model,
        subcategory_model,
    ) = load_track_a()

    issues = load_track_b()

    print("\n")

    # --------------------------------------------------------
    # Complaint
    # --------------------------------------------------------

    description = input(
        "Enter civic complaint:\n> "
    ).strip()

    if not description:

        print(
            "\nNo complaint entered."
        )

        return

    # --------------------------------------------------------
    # Location
    # --------------------------------------------------------

    print("\nComplaint location:")

    try:

        latitude = float(
            input(
                "Latitude  : "
            ).strip()
        )

        longitude = float(
            input(
                "Longitude : "
            ).strip()
        )

    except ValueError:

        print(
            "\nInvalid latitude/longitude."
        )

        print(
            "Please enter numeric coordinates."
        )

        return

    # --------------------------------------------------------
    # Process
    # --------------------------------------------------------

    process_complaint(
        description,
        latitude,
        longitude,
        vectorizer,
        category_model,
        subcategory_model,
        issues,
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()