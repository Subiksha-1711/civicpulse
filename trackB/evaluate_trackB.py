"""
CivicPulse — Track B
FAST Issue-Level Evaluation V4

Concept preserved:
    Complaint
        ↓
    Candidate issues
        ↓
    Category + subcategory filtering
        ↓
    Compare against reports in each candidate issue
        ↓
    Best text + geographic match
        ↓
    Cluster bonus
        ↓
    NEW / RELATED / DUPLICATE

Optimization:
    - TF-IDF calculated once
    - cosine similarity calculated once
    - category/subcategory candidates pre-indexed
    - geographic distances calculated only for candidates
    - no repeated dataframe filtering
"""

import os
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from issue_index import build_issue_index
from issue_detector import (
    haversine_distance_km,
    DUPLICATE_THRESHOLD,
    RELATED_THRESHOLD,
)


# ============================================================
# DATASET
# ============================================================

DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "trackA",
    "civicpulse_dataset_v2.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

GEO_MAX_DISTANCE_KM = 1.0

TEXT_WEIGHT = 0.45
CATEGORY_WEIGHT = 0.15
SUBCATEGORY_WEIGHT = 0.15
GEO_WEIGHT = 0.20
TIME_WEIGHT = 0.05


# ============================================================
# LOAD DATA
# ============================================================

def load_dataset():

    print("=" * 80)
    print("CIVICPULSE — TRACK B FAST ISSUE-LEVEL EVALUATION V4")
    print("=" * 80)

    print("\nLoading dataset:")
    print(DATASET_PATH)

    df = pd.read_csv(DATASET_PATH)

    print(f"\nLoaded {len(df):,} complaints.")

    return df


# ============================================================
# BUILD TF-IDF
# ============================================================

def build_tfidf(df):

    print("\nBuilding global TF-IDF matrix...")

    descriptions = (
        df["description"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True
    )

    matrix = vectorizer.fit_transform(
        descriptions
    )

    print(
        f"TF-IDF matrix: {matrix.shape}"
    )

    print(
        "\nCalculating cosine similarity matrix..."
    )

    similarities = cosine_similarity(matrix)

    print("Similarity matrix ready.")

    return similarities


# ============================================================
# BUILD ISSUE MEMBERS
# ============================================================

def build_issue_members(df):

    issue_members = {}

    for index, issue_id in enumerate(
        df["ground_truth_issue_id"].astype(str)
    ):

        issue_members.setdefault(
            issue_id,
            []
        ).append(index)

    return issue_members


# ============================================================
# BUILD CANDIDATE INDEX
# ============================================================

def build_candidate_index(df):

    """
    Maps:

        (category, subcategory)
                ↓
        candidate issue IDs

    This removes unrelated issues before
    any expensive similarity calculation.
    """

    candidate_index = {}

    grouped = df.groupby(
        [
            df["category"].astype(str).str.strip().str.lower(),
            df["subcategory"].astype(str).str.strip().str.lower(),
        ]
    )

    for (category, subcategory), group in grouped:

        issue_ids = set(
            group["ground_truth_issue_id"]
            .astype(str)
        )

        candidate_index[
            (category, subcategory)
        ] = list(issue_ids)

    return candidate_index


# ============================================================
# PRECOMPUTE ISSUE DATA
# ============================================================

def build_issue_data(df, issue_members):

    issue_data = {}

    for issue_id, members in issue_members.items():

        latitudes = df.iloc[members]["latitude"].astype(float).to_numpy()
        longitudes = df.iloc[members]["longitude"].astype(float).to_numpy()

        issue_data[issue_id] = {
            "members": np.array(
                members,
                dtype=np.int32
            ),

            "latitudes": latitudes,

            "longitudes": longitudes,

            "avg_latitude": float(
                latitudes.mean()
            ),

            "avg_longitude": float(
                longitudes.mean()
            ),
        }

    return issue_data


# ============================================================
# FAST GEO DISTANCE
# ============================================================

def haversine_vectorized(
    lat1,
    lon1,
    lat2,
    lon2
):

    earth_radius_km = 6371.0

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)

    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2.0) ** 2
        +
        np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon / 2.0) ** 2
    )

    c = 2.0 * np.arctan2(
        np.sqrt(a),
        np.sqrt(1.0 - a)
    )

    return earth_radius_km * c


# ============================================================
# MATCH ONE COMPLAINT
# ============================================================

def match_complaint(
    index,
    df,
    similarities,
    candidate_index,
    issue_data
):

    row = df.iloc[index]

    category = (
        str(row["category"])
        .strip()
        .lower()
    )

    subcategory = (
        str(row["subcategory"])
        .strip()
        .lower()
    )

    latitude = float(
        row["latitude"]
    )

    longitude = float(
        row["longitude"]
    )

    candidate_key = (
        category,
        subcategory
    )

    candidate_issues = candidate_index.get(
        candidate_key,
        []
    )

    best_issue = None
    best_score = -1.0
    best_report_index = None

    # --------------------------------------------------------
    # Only examine issues with same category/subcategory.
    # --------------------------------------------------------

    for issue_id in candidate_issues:

        data = issue_data[issue_id]

        members = data["members"]

        # Remove current complaint itself.
        members = members[
            members != index
        ]

        if len(members) == 0:
            continue

        # ----------------------------------------------------
        # Geographic filtering FIRST.
        #
        # If an issue is more than 1 km away, don't calculate
        # expensive text scoring for it.
        # ----------------------------------------------------

        member_latitudes = data["latitudes"]

        member_longitudes = data["longitudes"]

        # Original arrays correspond to original members.
        original_members = issue_data[
            issue_id
        ]["members"]

        mask = original_members != index

        member_latitudes = member_latitudes[mask]
        member_longitudes = member_longitudes[mask]

        distances = haversine_vectorized(
            latitude,
            longitude,
            member_latitudes,
            member_longitudes
        )

        nearby_mask = (
            distances < GEO_MAX_DISTANCE_KM
        )

        if not np.any(nearby_mask):
            continue

        nearby_members = members[
            nearby_mask
        ]

        nearby_distances = distances[
            nearby_mask
        ]

        # ----------------------------------------------------
        # Find best text similarity among nearby reports.
        # ----------------------------------------------------

        text_scores = similarities[
            index,
            nearby_members
        ]

        best_position = int(
            np.argmax(text_scores)
        )

        best_text_score = float(
            text_scores[best_position]
        )

        best_member = int(
            nearby_members[best_position]
        )

        best_distance = float(
            nearby_distances[best_position]
        )

        # ----------------------------------------------------
        # Geographic similarity.
        # ----------------------------------------------------

        geo_score = max(
            0.0,
            1.0
            - (
                best_distance
                / GEO_MAX_DISTANCE_KM
            )
        )

        # ----------------------------------------------------
        # Count nearby reports.
        # ----------------------------------------------------

        nearby_count = int(
            np.sum(
                nearby_distances <= 0.25
            )
        )

        cluster_bonus = min(
            0.04,
            nearby_count * 0.01
        )

        # ----------------------------------------------------
        # Weighted score.
        # ----------------------------------------------------

        score = (
            TEXT_WEIGHT * best_text_score
            + CATEGORY_WEIGHT * 1.0
            + SUBCATEGORY_WEIGHT * 1.0
            + GEO_WEIGHT * geo_score
            + TIME_WEIGHT * 1.0
        )

        score = min(
            1.0,
            score + cluster_bonus
        )

        if score > best_score:

            best_score = score

            best_issue = issue_id

            best_report_index = best_member

    # ========================================================
    # DECISION
    # ========================================================

    if best_issue is None:

        decision = "NEW_ISSUE"

    elif best_score >= DUPLICATE_THRESHOLD:

        decision = "DUPLICATE_ISSUE"

    elif best_score >= RELATED_THRESHOLD:

        decision = "RELATED_ISSUE"

    else:

        decision = "NEW_ISSUE"

    return {
        "decision": decision,

        "predicted_issue_id": best_issue,

        "score": round(
            max(0.0, best_score),
            4
        ),

        "matched_report_index":
            best_report_index
    }


# ============================================================
# EVALUATION
# ============================================================

def evaluate():

    df = load_dataset()

    required = [
        "complaint_id",
        "description",
        "category",
        "subcategory",
        "latitude",
        "longitude",
        "timestamp",
        "ground_truth_issue_id"
    ]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            "Missing columns: "
            + ", ".join(missing)
        )

    # --------------------------------------------------------
    # Issue index
    # --------------------------------------------------------

    print(
        "\nBuilding underlying issue index..."
    )

    issues = build_issue_index(
        DATASET_PATH
    )

    print(
        f"Indexed {len(issues)} underlying issues."
    )

    # --------------------------------------------------------
    # TF-IDF
    # --------------------------------------------------------

    similarities = build_tfidf(
        df
    )

    # --------------------------------------------------------
    # Issue members
    # --------------------------------------------------------

    print(
        "\nBuilding issue member index..."
    )

    issue_members = build_issue_members(
        df
    )

    print(
        f"Issue clusters: "
        f"{len(issue_members)}"
    )

    # --------------------------------------------------------
    # Candidate index
    # --------------------------------------------------------

    print(
        "Building category/subcategory candidate index..."
    )

    candidate_index = build_candidate_index(
        df
    )

    # --------------------------------------------------------
    # Issue data
    # --------------------------------------------------------

    print(
        "Precomputing issue geographic data..."
    )

    issue_data = build_issue_data(
        df,
        issue_members
    )

    print(
        "\n" + "=" * 80
    )

    print(
        "ISSUE-LEVEL MATCHING EVALUATION"
    )

    print(
        "=" * 80
    )

    total = len(df)

    correct = 0
    wrong = 0
    new_predictions = 0
    correct_duplicate = 0

    repeat_total = 0
    repeat_correct = 0

    correct_examples = []
    wrong_examples = []
    new_examples = []

    # ========================================================
    # EVALUATE
    # ========================================================

    for i in range(total):

        actual_issue = str(
            df.iloc[i][
                "ground_truth_issue_id"
            ]
        )

        issue_indices = issue_members[
            actual_issue
        ]

        is_repeat = any(
            x != i
            for x in issue_indices
        )

        if is_repeat:
            repeat_total += 1

        result = match_complaint(
            i,
            df,
            similarities,
            candidate_index,
            issue_data
        )

        predicted_issue = (
            result[
                "predicted_issue_id"
            ]
        )

        # ----------------------------------------------------
        # Correct
        # ----------------------------------------------------

        if predicted_issue == actual_issue:

            correct += 1

            if is_repeat:
                repeat_correct += 1

            if (
                result["decision"]
                == "DUPLICATE_ISSUE"
            ):
                correct_duplicate += 1

            if len(correct_examples) < 5:

                correct_examples.append(
                    (
                        i,
                        result
                    )
                )

        # ----------------------------------------------------
        # Singleton correctly NEW
        # ----------------------------------------------------

        elif (
            not is_repeat
            and
            result["decision"]
            == "NEW_ISSUE"
        ):

            new_predictions += 1

            if len(new_examples) < 5:

                new_examples.append(
                    (
                        i,
                        result
                    )
                )

        # ----------------------------------------------------
        # Wrong
        # ----------------------------------------------------

        else:

            wrong += 1

            if len(wrong_examples) < 5:

                wrong_examples.append(
                    (
                        i,
                        result
                    )
                )

        if (
            (i + 1) % 100 == 0
        ):

            print(
                f"Processed "
                f"{i + 1:,}/{total:,} complaints..."
            )

    # ========================================================
    # METRICS
    # ========================================================

    accuracy = (
        correct / total
        if total
        else 0.0
    )

    repeat_recall = (
        repeat_correct / repeat_total
        if repeat_total
        else 0.0
    )

    singleton_total = (
        total - repeat_total
    )

    print(
        "\n" + "-" * 80
    )

    print(
        "ISSUE-LEVEL METRICS"
    )

    print(
        "-" * 80
    )

    print(
        f"Total complaints          : "
        f"{total:,}"
    )

    print(
        f"Underlying issues         : "
        f"{len(issues):,}"
    )

    print(
        f"Singleton complaints      : "
        f"{singleton_total:,}"
    )

    print(
        f"Repeat complaints         : "
        f"{repeat_total:,}"
    )

    print(
        f"Correct issue matches     : "
        f"{correct:,}"
    )

    print(
        f"Wrong issue matches       : "
        f"{wrong:,}"
    )

    print(
        f"NEW_ISSUE predictions     : "
        f"{new_predictions:,}"
    )

    print(
        f"DUPLICATE correct matches : "
        f"{correct_duplicate:,}"
    )

    print(
        f"\nOverall accuracy          : "
        f"{accuracy:.3f} "
        f"({accuracy * 100:.1f}%)"
    )

    print(
        f"Repeat-issue recall       : "
        f"{repeat_recall:.3f} "
        f"({repeat_recall * 100:.1f}%)"
    )

    # ========================================================
    # EXAMPLES
    # ========================================================

    print(
        "\n" + "-" * 80
    )

    print(
        "CORRECT ISSUE MATCHES"
    )

    print(
        "-" * 80
    )

    for number, (i, result) in enumerate(
        correct_examples,
        start=1
    ):

        row = df.iloc[i]

        print(
            f"\nExample {number}"
        )

        print(
            f"Complaint [{row['complaint_id']}]"
        )

        print(
            f"   {row['description']}"
        )

        print(
            f"Actual issue : "
            f"{row['ground_truth_issue_id']}"
        )

        print(
            f"Predicted    : "
            f"{result['predicted_issue_id']}"
        )

        print(
            f"Decision     : "
            f"{result['decision']}"
        )

        print(
            f"Score        : "
            f"{result['score']}"
        )

    print(
        "\n" + "-" * 80
    )

    print(
        "WRONG / MISSED ISSUE MATCHES"
    )

    print(
        "-" * 80
    )

    for number, (i, result) in enumerate(
        wrong_examples,
        start=1
    ):

        row = df.iloc[i]

        print(
            f"\nExample {number}"
        )

        print(
            f"Complaint [{row['complaint_id']}]"
        )

        print(
            f"   {row['description']}"
        )

        print(
            f"Actual issue : "
            f"{row['ground_truth_issue_id']}"
        )

        print(
            f"Predicted    : "
            f"{result['predicted_issue_id']}"
        )

        print(
            f"Decision     : "
            f"{result['decision']}"
        )

        print(
            f"Score        : "
            f"{result['score']}"
        )

    print(
        "\n" + "=" * 80
    )

    print(
        "TRACK B FAST EVALUATION V4 COMPLETE"
    )

    print(
        "=" * 80
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    evaluate()