"""
CivicPulse — Track A: Civic Priority Score Engine
====================================================
Combines six weighted factors into a single 0-100 Civic Priority
Score, and — critically for the demo — returns a plain-English
breakdown of exactly why a complaint scored the way it did.

Formula (weights sum to 1.0, chosen for the hackathon demo — tune freely):

    Priority = 0.25*Severity + 0.25*SafetyRisk + 0.20*PeopleAffected
             + 0.15*Duration + 0.10*ComplaintDensity + 0.05*Vulnerability

All six sub-factors are scored 0-10, then the weighted sum is scaled to 0-100.

Integration point with Track B: pass `cluster_size` (number of duplicate
complaints Track B's clustering found for this issue) to drive
PeopleAffected and ComplaintDensity properly. Without it, this module
falls back to text-only estimates so it still works standalone.

Usage:
    python3 priority_engine.py
"""

import re
from classify import compute_severity, SAFETY_RISK_TERMS, score_terms, score_duration


VULNERABILITY_TERMS = {
    "school": 4, "children": 4, "hospital": 5, "elderly": 4,
    "clinic": 4, "college": 2, "park": 1,
}

WEIGHTS = {
    "severity": 0.25,
    "safety_risk": 0.25,
    "people_affected": 0.20,
    "duration": 0.15,
    "complaint_density": 0.10,
    "vulnerability": 0.05,
}


def _score_people_affected(text_lower, cluster_size):
    """0-10. Prefers real cluster_size from Track B; falls back to text cues."""
    if cluster_size is not None:
        # log-ish scale: 1 complaint -> ~1, 10 -> ~6, 50+ -> 10
        score = min(10, round(2.5 * (cluster_size ** 0.5)))
        return score, [f"{cluster_size} linked complaints (from Track B clustering)"]

    scale_score, scale_hits = score_terms(text_lower, {
        "many houses": 6, "families": 5, "residents": 4, "several": 3,
        "multiple": 3, "everyone": 5, "nobody": 2,
    })
    score = min(10, scale_score)
    explanation = [f"text mentions: {', '.join(scale_hits)}"] if scale_hits else \
        ["no explicit scale language — assuming single-household impact"]
    return score, explanation


def _score_duration(text_lower):
    raw, hits = score_duration(text_lower)
    score = min(10, round(raw * 10 / 6))
    explanation = [f"'{h}'" for h in hits] if hits else ["no duration mentioned"]
    return score, explanation


def _score_safety(text_lower):
    raw, hits = score_terms(text_lower, SAFETY_RISK_TERMS)
    score = min(10, raw * 2)
    explanation = [f"'{h}'" for h in hits] if hits else ["no safety-risk language detected"]
    return score, explanation


def _score_vulnerability(text_lower):
    raw, hits = score_terms(text_lower, VULNERABILITY_TERMS)
    score = min(10, raw)
    explanation = [f"'{h}'" for h in hits] if hits else \
        ["no vulnerable-population indicators (school/hospital/elderly) detected"]
    return score, explanation


def _score_density(cluster_size):
    """0-10. Requires Track B's cluster output; degrades gracefully without it."""
    if cluster_size is None:
        return 2, ["no clustering data available yet — default low-density assumption"]
    score = min(10, round(2.5 * (cluster_size ** 0.5)))
    return score, [f"{cluster_size} similar reports clustered in this area (Track B)"]


def compute_priority(description: str, cluster_size: int = None):
    """
    description: complaint text
    cluster_size: optional int — number of duplicate complaints Track B
                  found for this same underlying issue. Pass this in once
                  Track B's output is wired up for a much sharper score.

    Returns a dict with the final score, label, per-factor breakdown,
    and a ready-to-print explanation for the demo.
    """
    text_lower = description.lower()

    severity_info = compute_severity(description)
    severity_score = severity_info["severity_score"]

    safety_score, safety_expl = _score_safety(text_lower)
    people_score, people_expl = _score_people_affected(text_lower, cluster_size)
    duration_score, duration_expl = _score_duration(text_lower)
    density_score, density_expl = _score_density(cluster_size)
    vulnerability_score, vulnerability_expl = _score_vulnerability(text_lower)

    factors = {
        "severity": severity_score,
        "safety_risk": safety_score,
        "people_affected": people_score,
        "duration": duration_score,
        "complaint_density": density_score,
        "vulnerability": vulnerability_score,
    }

    weighted_sum = sum(factors[k] * WEIGHTS[k] for k in factors)
    final_score = round(weighted_sum * 10)  # scale 0-10 weighted avg -> 0-100
    final_score = max(0, min(100, final_score))

    if final_score >= 80:
        label = "CRITICAL"
    elif final_score >= 60:
        label = "HIGH"
    elif final_score >= 35:
        label = "MEDIUM"
    else:
        label = "LOW"

    breakdown = [
        {
            "factor": "Severity", "score": severity_score, "weight": WEIGHTS["severity"],
            "contribution": round(severity_score * WEIGHTS["severity"] * 10, 1),
            "why": severity_info["explanation"],
        },
        {
            "factor": "Safety Risk", "score": safety_score, "weight": WEIGHTS["safety_risk"],
            "contribution": round(safety_score * WEIGHTS["safety_risk"] * 10, 1),
            "why": safety_expl,
        },
        {
            "factor": "People Affected", "score": people_score, "weight": WEIGHTS["people_affected"],
            "contribution": round(people_score * WEIGHTS["people_affected"] * 10, 1),
            "why": people_expl,
        },
        {
            "factor": "Duration", "score": duration_score, "weight": WEIGHTS["duration"],
            "contribution": round(duration_score * WEIGHTS["duration"] * 10, 1),
            "why": duration_expl,
        },
        {
            "factor": "Complaint Density", "score": density_score, "weight": WEIGHTS["complaint_density"],
            "contribution": round(density_score * WEIGHTS["complaint_density"] * 10, 1),
            "why": density_expl,
        },
        {
            "factor": "Vulnerability", "score": vulnerability_score, "weight": WEIGHTS["vulnerability"],
            "contribution": round(vulnerability_score * WEIGHTS["vulnerability"] * 10, 1),
            "why": vulnerability_expl,
        },
    ]

    return {
        "description": description,
        "priority_score": final_score,
        "priority_label": label,
        "breakdown": breakdown,
    }


def print_priority_report(result):
    print(f"\n📝 \"{result['description']}\"")
    print(f"   🔴 PRIORITY SCORE: {result['priority_score']}/100 — {result['priority_label']}")
    print(f"   {'Factor':<20}{'Score':<8}{'Weight':<8}{'Contribution':<14}Why")
    for f in result["breakdown"]:
        why = "; ".join(f["why"])
        print(f"   {f['factor']:<20}{f['score']}/10{'':<3}{f['weight']:<8}{f['contribution']:<14}{why}")


if __name__ == "__main__":
    demo_cases = [
        # (description, cluster_size)
        ("Streetlight opposite PSG College Gate is not functioning for many days, "
         "women feel unsafe walking here after dark.", 50),
        ("Sparks were seen coming from a wire near Town Hall, children play nearby "
         "and it's very dangerous.", 6),
        ("Small pothole near my house, not too big but should be fixed.", None),
        ("Garbage has not been collected near our street for 4 days, very bad smell now.", None),
    ]

    print("===== CIVIC PRIORITY SCORE — DEMO REPORTS =====")
    for description, cluster_size in demo_cases:
        result = compute_priority(description, cluster_size=cluster_size)
        print_priority_report(result)
