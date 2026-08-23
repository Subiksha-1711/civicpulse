"""
CivicPulse — Track B
Basic Issue Detector Tests
"""

from issue_detector import (
    Complaint,
    calculate_issue_similarity,
    find_best_issue_match
)


def main():

    existing = Complaint(
        complaint_id="C001",
        description="A large pothole has formed near the bus stand.",
        category="Road",
        subcategory="Pothole",
        latitude=11.0168,
        longitude=76.9558,
        timestamp="2026-08-20 10:00:00"
    )

    duplicate = Complaint(
        complaint_id="C002",
        description="There is a huge pothole near the bus stand.",
        category="Road",
        subcategory="Pothole",
        latitude=11.0169,
        longitude=76.9559,
        timestamp="2026-08-20 12:00:00"
    )

    different = Complaint(
        complaint_id="C003",
        description="The traffic signal is not working at the junction.",
        category="Road",
        subcategory="Traffic signal",
        latitude=11.0169,
        longitude=76.9559,
        timestamp="2026-08-20 12:00:00"
    )

    print("=" * 70)
    print("CIVICPULSE — TRACK B ISSUE DETECTOR TEST")
    print("=" * 70)

    print("\nTEST 1 — SIMILAR POTHOLE COMPLAINT")
    print("-" * 70)

    result = calculate_issue_similarity(
        duplicate,
        existing
    )

    print(result)

    print("\nTEST 2 — DIFFERENT SUBCATEGORY")
    print("-" * 70)

    result =  find_best_issue_match(
    different,
    {
        "TEST_ISSUE": existing
    }
)
    

    print(result)

    print("\n" + "=" * 70)
    print("TRACK B BASIC TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()