"""
CivicPulse — Track B
Issue Detection & Duplicate Intelligence V3

Purpose:
    Determine whether a new complaint refers to an existing
    underlying civic issue.

V3 improvement:
    Instead of comparing against only one representative
    complaint, an existing issue is evaluated using ALL
    complaints belonging to that issue.

    This makes the detector robust to different wording such as:

        "large crater"
        "pothole"
        "nearly lost control"
        "hole in road"

    when they all belong to the same underlying issue.

Output:
    NEW_ISSUE
    RELATED_ISSUE
    DUPLICATE_ISSUE
"""

import re
from dataclasses import dataclass
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# CONFIGURATION
# ============================================================

TEXT_WEIGHT = 0.45
CATEGORY_WEIGHT = 0.15
SUBCATEGORY_WEIGHT = 0.15
GEO_WEIGHT = 0.20
TIME_WEIGHT = 0.05

DUPLICATE_THRESHOLD = 0.75
RELATED_THRESHOLD = 0.50

GEO_MAX_DISTANCE_KM = 1.0
TIME_MAX_HOURS = 72


# ============================================================
# DATA STRUCTURE
# ============================================================

@dataclass
class Complaint:
    complaint_id: str
    description: str
    category: str
    subcategory: str
    latitude: float
    longitude: float
    timestamp: str
    ground_truth_issue_id: str | None = None


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text: str) -> str:

    text = str(text).lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# ============================================================
# TEXT SIMILARITY
# ============================================================

def calculate_text_similarity(
    text1: str,
    text2: str
) -> float:

    text1 = normalize_text(text1)
    text2 = normalize_text(text2)

    if not text1 or not text2:
        return 0.0

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True
    )

    matrix = vectorizer.fit_transform(
        [text1, text2]
    )

    return float(
        cosine_similarity(
            matrix[0:1],
            matrix[1:2]
        )[0][0]
    )


# ============================================================
# CATEGORY
# ============================================================

def calculate_category_similarity(
    category1: str,
    category2: str
) -> float:

    return 1.0 if (
        str(category1).strip().lower()
        ==
        str(category2).strip().lower()
    ) else 0.0


# ============================================================
# SUBCATEGORY
# ============================================================

def calculate_subcategory_similarity(
    subcategory1: str,
    subcategory2: str
) -> float:

    return 1.0 if (
        str(subcategory1).strip().lower()
        ==
        str(subcategory2).strip().lower()
    ) else 0.0


# ============================================================
# GEOGRAPHIC DISTANCE
# ============================================================

def haversine_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:

    earth_radius_km = 6371.0

    lat1 = radians(float(lat1))
    lon1 = radians(float(lon1))
    lat2 = radians(float(lat2))
    lon2 = radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        +
        cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return earth_radius_km * c


def calculate_geo_similarity(
    complaint1: Complaint,
    complaint2: Complaint
) -> float:

    distance = haversine_distance_km(
        complaint1.latitude,
        complaint1.longitude,
        complaint2.latitude,
        complaint2.longitude
    )

    if distance >= GEO_MAX_DISTANCE_KM:
        return 0.0

    return max(
        0.0,
        1.0 - (
            distance /
            GEO_MAX_DISTANCE_KM
        )
    )


# ============================================================
# TEMPORAL SIMILARITY
# ============================================================

def parse_timestamp(
    timestamp: str
) -> datetime:

    return datetime.fromisoformat(
        str(timestamp).replace(
            "Z",
            ""
        )
    )


def calculate_time_similarity(
    timestamp1: str,
    timestamp2: str
) -> float:

    try:

        dt1 = parse_timestamp(
            timestamp1
        )

        dt2 = parse_timestamp(
            timestamp2
        )

    except Exception:
        return 0.0

    difference_hours = abs(
        (
            dt1 - dt2
        ).total_seconds()
    ) / 3600.0

    if difference_hours >= TIME_MAX_HOURS:
        return 0.0

    return max(
        0.0,
        1.0 - (
            difference_hours /
            TIME_MAX_HOURS
        )
    )


# ============================================================
# SINGLE REPORT SIMILARITY
# ============================================================

def calculate_issue_similarity(
    new_complaint: Complaint,
    existing_complaint: Complaint
) -> dict:

    text_score = calculate_text_similarity(
        new_complaint.description,
        existing_complaint.description
    )

    category_score = calculate_category_similarity(
        new_complaint.category,
        existing_complaint.category
    )

    subcategory_score = calculate_subcategory_similarity(
        new_complaint.subcategory,
        existing_complaint.subcategory
    )

    geo_score = calculate_geo_similarity(
        new_complaint,
        existing_complaint
    )

    time_score = calculate_time_similarity(
        new_complaint.timestamp,
        existing_complaint.timestamp
    )

    overall_score = (
        TEXT_WEIGHT * text_score
        + CATEGORY_WEIGHT * category_score
        + SUBCATEGORY_WEIGHT * subcategory_score
        + GEO_WEIGHT * geo_score
        + TIME_WEIGHT * time_score
    )

    if overall_score >= DUPLICATE_THRESHOLD:

        decision = "DUPLICATE_ISSUE"

    elif overall_score >= RELATED_THRESHOLD:

        decision = "RELATED_ISSUE"

    else:

        decision = "NEW_ISSUE"

    distance = haversine_distance_km(
        new_complaint.latitude,
        new_complaint.longitude,
        existing_complaint.latitude,
        existing_complaint.longitude
    )

    return {
        "decision": decision,
        "overall_similarity": round(
            overall_score,
            4
        ),
        "text_similarity": round(
            text_score,
            4
        ),
        "category_similarity": round(
            category_score,
            4
        ),
        "subcategory_similarity": round(
            subcategory_score,
            4
        ),
        "geographic_similarity": round(
            geo_score,
            4
        ),
        "temporal_similarity": round(
            time_score,
            4
        ),
        "distance_km": round(
            distance,
            4
        ),
        "matched_complaint_id":
            existing_complaint.complaint_id
    }


# ============================================================
# ISSUE CLUSTER MATCHING
# ============================================================

def find_best_issue_match(
    new_complaint: Complaint,
    existing_issues: dict
) -> dict:

    if not existing_issues:
        return {
            "decision": "NEW_ISSUE",
            "overall_similarity": 0.0,
            "matched_issue_id": None
        }

    best_result = None

    for issue_id, issue in existing_issues.items():

        # Category must agree.
        if (
            new_complaint.category.strip().lower()
            != issue.category.strip().lower()
        ):
            continue

        # Subcategory mismatch is a strong negative signal.
        subcategory_score = (
            1.0
            if (
                new_complaint.subcategory.strip().lower()
                == issue.subcategory.strip().lower()
            )
            else 0.0
        )

        if subcategory_score == 0.0:
            continue

        # ----------------------------------------------------
        # Compare against ALL complaints belonging to issue.
        # Keep the strongest text match.
        # ----------------------------------------------------

        best_text_score = 0.0
        best_complaint_index = 0

        for index, description in enumerate(issue.complaints):

            text_score = calculate_text_similarity(
                new_complaint.description,
                description
            )

            if text_score > best_text_score:
                best_text_score = text_score
                best_complaint_index = index

        # ----------------------------------------------------
        # Geographic similarity against issue cluster.
        # ----------------------------------------------------

        issue_lat = issue.average_latitude
        issue_lon = issue.average_longitude

        distance = haversine_distance_km(
            new_complaint.latitude,
            new_complaint.longitude,
            issue_lat,
            issue_lon
        )

        if distance >= GEO_MAX_DISTANCE_KM:
            geo_score = 0.0
        else:
            geo_score = max(
                0.0,
                1.0 - (
                    distance / GEO_MAX_DISTANCE_KM
                )
            )

        # ----------------------------------------------------
        # Temporal similarity against closest report.
        # ----------------------------------------------------

        best_time_score = 0.0

        for timestamp in issue.timestamps:

            time_score = calculate_time_similarity(
                new_complaint.timestamp,
                timestamp
            )

            if time_score > best_time_score:
                best_time_score = time_score

        # ----------------------------------------------------
        # Overall score
        # ----------------------------------------------------

        overall_score = (
            TEXT_WEIGHT * best_text_score
            + CATEGORY_WEIGHT * 1.0
            + SUBCATEGORY_WEIGHT * subcategory_score
            + GEO_WEIGHT * geo_score
            + TIME_WEIGHT * best_time_score
        )

        if overall_score >= DUPLICATE_THRESHOLD:
            decision = "DUPLICATE_ISSUE"

        elif overall_score >= RELATED_THRESHOLD:
            decision = "RELATED_ISSUE"

        else:
            decision = "NEW_ISSUE"

        result = {
            "decision": decision,
            "overall_similarity": round(
                overall_score,
                4
            ),
            "text_similarity": round(
                best_text_score,
                4
            ),
            "category_similarity": 1.0,
            "subcategory_similarity": 1.0,
            "geographic_similarity": round(
                geo_score,
                4
            ),
            "temporal_similarity": round(
                best_time_score,
                4
            ),
            "distance_km": round(
                distance,
                4
            ),
            "matched_issue_id": issue_id,
            "matched_complaint_id": (
                issue.complaint_ids[
                    best_complaint_index
                ]
            )
        }

        if (
            best_result is None
            or result["overall_similarity"]
            > best_result["overall_similarity"]
        ):
            best_result = result

    if best_result is None:
        return {
            "decision": "NEW_ISSUE",
            "overall_similarity": 0.0,
            "matched_issue_id": None
        }

    return best_result
    """
    Find the best existing issue.

    Supports both:

    1. Issue index:
           dict[str, IssueRecord]

    2. Legacy/basic test input:
           list[Complaint]

    The production path uses all reports belonging to
    each issue cluster.
    """

    if not existing_issues:
        return {
            "decision": "NEW_ISSUE",
            "overall_similarity": 0.0,
            "matched_issue_id": None,
            "matched_complaint_id": None
        }

    # ========================================================
    # BACKWARD COMPATIBILITY
    # ========================================================
    #
    # test_issue_detector.py currently passes:
    #
    #     [existing]
    #
    # Keep that test working.
    #
    if isinstance(existing_issues, list):

        results = []

        for complaint in existing_issues:

            if (
                str(new_complaint.category).strip().lower()
                !=
                str(complaint.category).strip().lower()
            ):
                continue

            result = calculate_issue_similarity(
                new_complaint,
                complaint
            )

            results.append(result)

        if not results:
            return {
                "decision": "NEW_ISSUE",
                "overall_similarity": 0.0,
                "matched_issue_id": None,
                "matched_complaint_id": None
            }

        return max(
            results,
            key=lambda x: x["overall_similarity"]
        )

    # ========================================================
    # PRODUCTION ISSUE-INDEX PATH
    # ========================================================

    best_result = None
    best_issue_id = None

    for issue_id, issue in existing_issues.items():

        # Category must match.
        if (
            str(new_complaint.category).strip().lower()
            !=
            str(issue.category).strip().lower()
        ):
            continue

        # Subcategory mismatch is a strong indication that
        # this is a different underlying issue.
        if (
            str(new_complaint.subcategory).strip().lower()
            !=
            str(issue.subcategory).strip().lower()
        ):
            continue

        issue_best = None

        # ----------------------------------------------------
        # Compare against EVERY report in this issue.
        # ----------------------------------------------------

        for index, description in enumerate(
            issue.complaints
        ):

            existing = Complaint(
                complaint_id=str(
                    issue.complaint_ids[index]
                ),
                description=description,
                category=issue.category,
                subcategory=issue.subcategory,
                latitude=issue.latitudes[index],
                longitude=issue.longitudes[index],
                timestamp=issue.timestamps[index],
                ground_truth_issue_id=issue_id
            )

            result = calculate_issue_similarity(
                new_complaint,
                existing
            )

            if (
                issue_best is None
                or
                result["overall_similarity"]
                >
                issue_best["overall_similarity"]
            ):
                issue_best = result

        if issue_best is None:
            continue

        # ----------------------------------------------------
        # Cluster consistency
        # ----------------------------------------------------

        nearby_count = 0

        for index in range(
            len(issue.complaints)
        ):

            distance = haversine_distance_km(
                new_complaint.latitude,
                new_complaint.longitude,
                issue.latitudes[index],
                issue.longitudes[index]
            )

            if distance <= 0.25:
                nearby_count += 1

        # Maximum 0.04 bonus.
        cluster_bonus = min(
            0.04,
            nearby_count * 0.01
        )

        issue_score = min(
            1.0,
            issue_best["overall_similarity"]
            + cluster_bonus
        )

        issue_best["overall_similarity"] = round(
            issue_score,
            4
        )

        if issue_score >= DUPLICATE_THRESHOLD:

            issue_best["decision"] = (
                "DUPLICATE_ISSUE"
            )

        elif issue_score >= RELATED_THRESHOLD:

            issue_best["decision"] = (
                "RELATED_ISSUE"
            )

        else:

            issue_best["decision"] = (
                "NEW_ISSUE"
            )

        issue_best["matched_issue_id"] = issue_id

        if (
            best_result is None
            or
            issue_score
            >
            best_result["overall_similarity"]
        ):

            best_result = issue_best
            best_issue_id = issue_id

    # ========================================================
    # NO MATCH
    # ========================================================

    if best_result is None:

        return {
            "decision": "NEW_ISSUE",
            "overall_similarity": 0.0,
            "matched_issue_id": None,
            "matched_complaint_id": None
        }

    best_result["matched_issue_id"] = best_issue_id

    return best_result