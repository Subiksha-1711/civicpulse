"""
CivicPulse — Track B
Issue Index v2

Builds an index of underlying civic issues from the
CivicPulse ground-truth dataset.

Track B v2 stores the complete complaint cluster so that
issue matching does not depend on a single representative
complaint.

The index provides:
    - category
    - subcategory
    - all complaint descriptions
    - complaint IDs
    - average geographic location
    - geographic spread
    - timestamps
"""

import os
from dataclasses import dataclass, field

import pandas as pd


# ============================================================
# DATASET PATH
# ============================================================

DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "trackA",
    "civicpulse_dataset_v2.csv"
)


# ============================================================
# ISSUE REPRESENTATION
# ============================================================

@dataclass
class IssueRecord:

    issue_id: str

    category: str

    subcategory: str

    complaints: list[str] = field(
        default_factory=list
    )

    complaint_ids: list[str] = field(
        default_factory=list
    )

    latitudes: list[float] = field(
        default_factory=list
    )

    longitudes: list[float] = field(
        default_factory=list
    )

    timestamps: list[str] = field(
        default_factory=list
    )

    @property
    def complaint_count(self) -> int:
        return len(self.complaints)

    # --------------------------------------------------------
    # REPRESENTATIVE DESCRIPTION
    # --------------------------------------------------------

    @property
    def representative_description(self) -> str:

        if not self.complaints:
            return ""

        return self.complaints[0]

    # --------------------------------------------------------
    # COMPLETE CLUSTER TEXT
    # --------------------------------------------------------

    @property
    def cluster_text(self) -> str:

        """
        Combine all complaints belonging to this issue.

        This allows Track B to recognize conceptually similar
        wording even when individual reports use different
        vocabulary.

        Example:

            crater
            pothole
            hole in road
            uneven road surface

        can all contribute evidence to the same issue.
        """

        return " ".join(
            self.complaints
        )

    # --------------------------------------------------------
    # REPRESENTATIVE LOCATION
    # --------------------------------------------------------

    @property
    def average_latitude(self) -> float:

        if not self.latitudes:
            return 0.0

        return sum(
            self.latitudes
        ) / len(self.latitudes)

    @property
    def average_longitude(self) -> float:

        if not self.longitudes:
            return 0.0

        return sum(
            self.longitudes
        ) / len(self.longitudes)

    # --------------------------------------------------------
    # LOCATION RANGE
    # --------------------------------------------------------

    @property
    def min_latitude(self) -> float:

        if not self.latitudes:
            return 0.0

        return min(self.latitudes)

    @property
    def max_latitude(self) -> float:

        if not self.latitudes:
            return 0.0

        return max(self.latitudes)

    @property
    def min_longitude(self) -> float:

        if not self.longitudes:
            return 0.0

        return min(self.longitudes)

    @property
    def max_longitude(self) -> float:

        if not self.longitudes:
            return 0.0

        return max(self.longitudes)


# ============================================================
# COLUMN RESOLUTION
# ============================================================

def find_column(df, candidates):

    normalized = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for candidate in candidates:

        key = candidate.strip().lower()

        if key in normalized:
            return normalized[key]

    return None


# ============================================================
# SAFE FLOAT
# ============================================================

def safe_float(value):

    try:
        return float(value)

    except (TypeError, ValueError):

        return 0.0


# ============================================================
# BUILD ISSUE INDEX
# ============================================================

def build_issue_index(
    dataset_path: str = DATASET_PATH
) -> dict[str, IssueRecord]:

    print(
        "Loading CivicPulse dataset:"
    )

    print(dataset_path)

    df = pd.read_csv(
        dataset_path
    )

    # --------------------------------------------------------
    # Resolve columns
    # --------------------------------------------------------

    issue_column = find_column(
        df,
        [
            "ground_truth_issue_id",
            "issue_id",
            "underlying_issue_id"
        ]
    )

    complaint_id_column = find_column(
        df,
        [
            "complaint_id",
            "id",
            "case_id"
        ]
    )

    description_column = find_column(
        df,
        [
            "description",
            "complaint",
            "complaint_text",
            "text"
        ]
    )

    category_column = find_column(
        df,
        [
            "category"
        ]
    )

    subcategory_column = find_column(
        df,
        [
            "subcategory"
        ]
    )

    latitude_column = find_column(
        df,
        [
            "latitude",
            "lat"
        ]
    )

    longitude_column = find_column(
        df,
        [
            "longitude",
            "lon",
            "lng"
        ]
    )

    timestamp_column = find_column(
        df,
        [
            "timestamp",
            "created_at",
            "date",
            "datetime"
        ]
    )

    required = {
        "issue_id": issue_column,
        "complaint_id": complaint_id_column,
        "description": description_column,
        "category": category_column,
        "subcategory": subcategory_column,
        "latitude": latitude_column,
        "longitude": longitude_column,
        "timestamp": timestamp_column
    }

    missing = [
        name
        for name, column in required.items()
        if column is None
    ]

    if missing:

        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing)
        )

    # --------------------------------------------------------
    # Build index
    # --------------------------------------------------------

    issues: dict[str, IssueRecord] = {}

    for _, row in df.iterrows():

        issue_id = str(
            row[issue_column]
        ).strip()

        if not issue_id:
            continue

        if issue_id not in issues:

            issues[issue_id] = IssueRecord(

                issue_id=issue_id,

                category=str(
                    row[category_column]
                ).strip(),

                subcategory=str(
                    row[subcategory_column]
                ).strip()
            )

        issue = issues[issue_id]

        issue.complaints.append(
            str(
                row[description_column]
            )
        )

        issue.complaint_ids.append(
            str(
                row[complaint_id_column]
            )
        )

        issue.latitudes.append(
            safe_float(
                row[latitude_column]
            )
        )

        issue.longitudes.append(
            safe_float(
                row[longitude_column]
            )
        )

        issue.timestamps.append(
            str(
                row[timestamp_column]
            )
        )

    return issues


# ============================================================
# SUMMARY
# ============================================================

def print_issue_index_summary(
    issues: dict[str, IssueRecord]
):

    counts = [
        issue.complaint_count
        for issue in issues.values()
    ]

    singleton_count = sum(
        count == 1
        for count in counts
    )

    multi_report_count = sum(
        count > 1
        for count in counts
    )

    five_plus_count = sum(
        count >= 5
        for count in counts
    )

    ten_plus_count = sum(
        count >= 10
        for count in counts
    )

    largest = max(
        counts,
        default=0
    )

    print("\n" + "=" * 70)

    print(
        "CIVICPULSE — TRACK B ISSUE INDEX V2"
    )

    print("=" * 70)

    print(
        f"Total underlying issues : "
        f"{len(issues)}"
    )

    print(
        f"Singleton issues        : "
        f"{singleton_count}"
    )

    print(
        f"Multi-report issues     : "
        f"{multi_report_count}"
    )

    print(
        f"Issues with 5+ reports  : "
        f"{five_plus_count}"
    )

    print(
        f"Issues with 10+ reports : "
        f"{ten_plus_count}"
    )

    print(
        f"Largest issue           : "
        f"{largest} reports"
    )

    print("=" * 70)

    print(
        "\nLargest issue clusters:"
    )

    largest_issues = sorted(
        issues.values(),
        key=lambda issue: issue.complaint_count,
        reverse=True
    )[:10]

    for issue in largest_issues:

        print(
            f"\n{issue.issue_id}"
        )

        print(
            f"  Category    : "
            f"{issue.category}"
        )

        print(
            f"  Subcategory : "
            f"{issue.subcategory}"
        )

        print(
            f"  Reports     : "
            f"{issue.complaint_count}"
        )

        print(
            f"  Location    : "
            f"({issue.average_latitude:.6f}, "
            f"{issue.average_longitude:.6f})"
        )

        print(
            f"  Example     : "
            f"{issue.representative_description}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    issues = build_issue_index()

    print(
        f"\nBuilt index for "
        f"{len(issues)} underlying issues."
    )

    print_issue_index_summary(
        issues
    )


if __name__ == "__main__":
    main()