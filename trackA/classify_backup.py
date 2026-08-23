"""
CivicPulse — Track A: Complaint Understanding
================================================

Production classifier for CivicPulse.

Pipeline:
    Complaint text
        ↓
    TF-IDF
        ↓
    Calibrated Linear SVM
        ↓
    Category + Subcategory
        ↓
    Department routing
        ↓
    Explainable severity analysis

The severity layer is intentionally rule-based and transparent because
the dataset has no human-labeled severity target. It is designed to
explain which civic-risk signals caused a higher severity score.
"""

import re
import json
from pathlib import Path

import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


# ============================================================
# 1. PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "civicpulse_dataset_v2.csv"


# ============================================================
# 2. CATEGORY → DEPARTMENT ROUTING
# ============================================================

CATEGORY_TO_DEPARTMENT = {
    "Road": "Roads & Infrastructure Department",
    "Streetlight": "Electricity Department (Street Lighting Wing)",
    "Sanitation": "Sanitation & Solid Waste Management Department",
    "Drainage": "Stormwater & Drainage Department",
    "Water": "Water Supply Department",
    "Electricity": "Electricity Department",
}


# ============================================================
# 3. EXPLAINABLE SEVERITY SIGNALS
# ============================================================

# Strong, direct safety hazards.
SAFETY_RISK_TERMS = {
    "live wire": 5,
    "exposed wire": 5,
    "exposed electrical": 4,
    "exposed electrical wire": 5,
    "sparking": 5,
    "spark": 4,
    "electric shock": 5,
    "electrical hazard": 5,
    "burning wire": 5,
    "dangerous": 4,
    "danger": 4,
    "unsafe": 4,
    "risky": 3,
    "accident": 5,
    "collision": 5,
    "crash": 5,
    "injury": 5,
    "injured": 5,
    "almost fell": 4,
    "nearly fell": 4,
    "contaminated": 5,
    "unsafe to drink": 5,
    "not fit for drinking": 5,
    "unfit for drinking": 5,
    "stomach upset": 4,
    "fell sick": 4,
}


ROAD_IMPACT_TERMS = {
    "deep pothole": 3,
    "large pothole": 3,
    "huge pothole": 4,
    "deep crater": 4,
    "large crater": 3,
    "road crater": 3,
    "vehicles swerving": 4,
    "vehicle swerving": 4,
    "bike nearly fell": 4,
    "bike struggled": 3,
    "bikes struggling": 3,
    "bikes are struggling": 3,
    "bikes struggle": 3,
    "struggling to pass": 3,
    "hard to cross": 3,
    "difficult to cross": 3,
    "road blocked": 5,
    "road completely blocked": 6,
    "completely blocked": 5,
    "cannot pass": 4,
    "cannot cross": 4,
    "vehicles cannot pass": 5,
    "traffic completely blocked": 6,
    "traffic getting stuck": 4,
    "vehicles getting stuck": 4,
    "vehicles are getting stuck": 4,
    "traffic is getting stuck": 4,
    "traffic jam": 3,
    "signal failure": 4,
    "signal stopped": 4,
    "signal is not working": 4,
    "signal not working": 4,
    "traffic signal stopped": 4,
    "traffic signal failure": 4,
    "stopped changing": 3,
}


WATER_IMPACT_TERMS = {
    "no water": 4,
    "no water supply": 5,
    "water supply stopped": 5,
    "water supply cut": 5,
    "water supply unavailable": 5,
    "water unavailable": 5,
    "water supply interrupted": 4,
    "water interruption": 4,
    "no drinking water": 5,
    "water shortage": 4,
    "irregular water supply": 3,
    "brown water": 4,
    "dirty water": 4,
    "bad smelling water": 4,
    "strange smell": 3,
    "bad smell in water": 4,
    "water appears contaminated": 5,
    "water looks brown": 4,
    "looks brown": 4,
    "strange smell and looks brown": 5,
    "worried about using it": 3,
}


SANITATION_IMPACT_TERMS = {
    "garbage piling up": 3,
    "garbage has accumulated": 3,
    "garbage accumulating": 3,
    "waste accumulating": 3,
    "trash piling up": 3,
    "rotting waste": 4,
    "waste has accumulated": 3,
    "bad smell": 3,
    "foul smell": 3,
    "flies": 3,
    "mosquitoes": 3,
    "vermin": 4,
}


INFRASTRUCTURE_IMPACT_TERMS = {
    "not functioning": 2,
    "not working": 2,
    "stopped working": 3,
    "completely stopped": 4,
    "shut down": 3,
    "blocked": 3,
    "overflowing": 3,
    "overflow": 3,
    "flooded": 5,
    "flooding": 5,
    "waterlogged": 5,
    "flood water": 5,
    "entered houses": 6,
    "entered homes": 6,
    "houses flooded": 6,
    "homes flooded": 6,
    "road flooded": 5,
    "not responding": 3,
    "failed": 2,
    "power outage": 4,
    "power has gone out": 4,
    "electricity unavailable": 4,
    "no electricity": 4,
    "electricity outage": 4,
    "drain is blocked": 4,
    "drain blocked": 4,
    "drain is overflowing": 5,
    "drain overflowing": 5,
    "streetlight is off": 3,
    "streetlight is not working": 3,
    "streetlights are off": 4,
    "streetlights have been off": 4,
    "street is completely dark": 4,
    "completely dark": 4,
}


SCALE_TERMS = {
    "many houses": 4,
    "many households": 4,
    "many families": 4,
    "multiple households": 4,
    "entire street": 4,
    "whole street": 4,
    "entire area": 4,
    "whole area": 4,
    "many residents": 4,
    "residents": 2,
    "families": 3,
    "households": 3,
    "several residents": 3,
    "multiple residents": 3,
    "everyone": 5,
    "public": 2,
    "commuters": 3,
    "vehicles": 2,
    "pedestrians": 2,
    "several houses": 3,
    "several homes": 3,
    "multiple houses": 4,
}


VULNERABILITY_TERMS = {
    "children": 5,
    "child": 5,
    "school": 5,
    "students": 3,
    "elderly": 5,
    "senior citizens": 5,
    "hospital": 6,
    "clinic": 5,
    "patients": 5,
    "pregnant": 5,
}


URGENCY_TERMS = {
    "urgent": 4,
    "urgently": 4,
    "emergency": 5,
    "immediately": 5,
    "as soon as possible": 4,
    "right away": 4,
    "needs immediate attention": 5,
    "please act immediately": 5,
}


# ============================================================
# 4. TERM MATCHING
# ============================================================

def score_terms(text_lower, term_dict):
    """
    Score matching terms while avoiding substring double-counting.

    Example:
        'child' does not match 'children' accidentally.
    Multi-word phrases are matched as phrases.
    """

    total = 0
    hits = []

    for term, weight in term_dict.items():

        if " " in term:
            matched = term in text_lower
        else:
            matched = bool(
                re.search(
                    rf"\b{re.escape(term)}\b",
                    text_lower
                )
            )

        if matched:
            total += weight
            hits.append(term)

    return total, hits


# ============================================================
# 5. DURATION SCORING
# ============================================================

def score_duration(text_lower):

    score = 0
    hits = []

    day_matches = re.findall(
        r"\b(\d+)\s*days?\b",
        text_lower
    )

    for value in day_matches:
        days = int(value)

        if days >= 14:
            points = 6
        elif days >= 7:
            points = 5
        elif days >= 4:
            points = 4
        elif days >= 2:
            points = 2
        else:
            points = 1

        score += points
        hits.append(f"{days} day(s)")

    week_matches = re.findall(
        r"\b(\d+)\s*weeks?\b",
        text_lower
    )

    for value in week_matches:
        weeks = int(value)
        points = min(7, 3 + weeks)
        score += points
        hits.append(f"{weeks} week(s)")

    month_matches = re.findall(
        r"\b(\d+)\s*months?\b",
        text_lower
    )

    for value in month_matches:
        months = int(value)
        score += 7
        hits.append(f"{months} month(s)")

    natural_duration = {
        "since yesterday": 2,
        "since morning": 1,
        "since last night": 2,
        "since last week": 5,
        "for many days": 4,
        "for several days": 4,
        "for weeks": 5,
        "for many weeks": 6,
        "for several weeks": 6,
        "for months": 7,
        "for many months": 8,
        "for two days": 2,
        "for three days": 3,
        "for four days": 4,
        "for five days": 4,
        "for six days": 4,
        "for a week": 5,
        "for two weeks": 6,
        "for three weeks": 6,
        "for a month": 7,
        "two days": 2,
        "three days": 3,
        "four days": 4,
        "five days": 4,
        "six days": 4,
        "a week": 5,
        "two weeks": 6,
        "three weeks": 6,
        "a month": 7,
    }

    for phrase, points in natural_duration.items():
        if phrase in text_lower:
            score += points
            hits.append(phrase)

    return min(score, 10), hits


# ============================================================
# 6. SEVERITY ENGINE
# ============================================================

def compute_severity(description: str):

    text_lower = description.lower()

    safety_raw, safety_hits = score_terms(
        text_lower, SAFETY_RISK_TERMS
    )

    road_raw, road_hits = score_terms(
        text_lower, ROAD_IMPACT_TERMS
    )

    water_raw, water_hits = score_terms(
        text_lower, WATER_IMPACT_TERMS
    )

    sanitation_raw, sanitation_hits = score_terms(
        text_lower, SANITATION_IMPACT_TERMS
    )

    infrastructure_raw, infrastructure_hits = score_terms(
        text_lower, INFRASTRUCTURE_IMPACT_TERMS
    )

    scale_raw, scale_hits = score_terms(
        text_lower, SCALE_TERMS
    )

    vulnerability_raw, vulnerability_hits = score_terms(
        text_lower, VULNERABILITY_TERMS
    )

    urgency_raw, urgency_hits = score_terms(
        text_lower, URGENCY_TERMS
    )

    duration_score, duration_hits = score_duration(
        text_lower
    )

    # --------------------------------------------------------
    # Component scores
    # --------------------------------------------------------

    safety_score = min(10, safety_raw)

    impact_raw = (
        road_raw
        + water_raw
        + sanitation_raw
        + infrastructure_raw
    )

    impact_score = min(10, impact_raw)

    people_score = min(10, scale_raw)

    vulnerability_score = min(10, vulnerability_raw)

    urgency_score = min(10, urgency_raw)

    # --------------------------------------------------------
    # Base weighted score
    # --------------------------------------------------------

    weighted_score = (
        safety_score * 0.30
        + impact_score * 0.25
        + people_score * 0.15
        + duration_score * 0.15
        + vulnerability_score * 0.10
        + urgency_score * 0.05
    )

    # --------------------------------------------------------
    # Compound civic-risk rules
    #
    # These are deliberately explicit and explainable.
    # They capture situations where several moderate signals
    # together represent a materially higher civic risk.
    # --------------------------------------------------------

    risk_boost = 0
    boost_reasons = []

    # Electrical hazard + vulnerable location
    if safety_score >= 4 and vulnerability_score >= 5:
        risk_boost += 4
        boost_reasons.append(
            "serious hazard near a vulnerable population"
        )

    # Direct electrical hazard + vulnerable population
    if (
        safety_score >= 5
        and vulnerability_score >= 5
        and any(
            term in text_lower
            for term in [
                "live wire",
                "exposed wire",
                "exposed electrical",
                "sparking",
                "electrical hazard",
            ]
        )
    ):
        risk_boost += 3
        boost_reasons.append(
            "direct electrical hazard + vulnerable population"
        )

    # Major transport obstruction
    if (
        any(
            phrase in text_lower
            for phrase in [
                "completely blocked",
                "cannot pass",
                "vehicles cannot pass",
                "traffic completely blocked",
                "road completely blocked",
            ]
        )
        and people_score >= 2
    ):
        risk_boost += 3
        boost_reasons.append(
            "major transportation obstruction"
        )

    # Severe flooding/property impact
    if (
        any(
            phrase in text_lower
            for phrase in [
                "flood water",
                "entered houses",
                "entered homes",
                "houses flooded",
                "homes flooded",
            ]
        )
    ):
        risk_boost += 4
        boost_reasons.append(
            "flooding/property impact"
        )

    # Flooding + multiple people/locations
    if (
        any(
            phrase in text_lower
            for phrase in [
                "entered houses",
                "entered homes",
                "houses flooded",
                "homes flooded",
            ]
        )
        and people_score >= 3
    ):
        risk_boost += 2
        boost_reasons.append(
            "flooding affecting multiple households"
        )

    # Water quality + health/safety concern
    if (
        water_score := min(10, water_raw)
    ) >= 4 and (
        safety_score >= 5
        or vulnerability_score >= 5
        or any(
            phrase in text_lower
            for phrase in [
                "contaminated",
                "not fit for drinking",
                "unsafe to drink",
                "stomach upset",
                "fell sick",
            ]
        )
    ):
        risk_boost += 3
        boost_reasons.append(
            "water-quality concern with health-risk indicators"
        )

    # Visible drinking-water quality concern should not remain LOW.
    if (
        water_raw >= 4
        and any(
            phrase in text_lower
            for phrase in [
                "brown water",
                "looks brown",
                "strange smell",
                "dirty water",
                "bad smelling water",
            ]
        )
    ):
        risk_boost += 2
        boost_reasons.append(
            "visible drinking-water quality concern"
        )

    # Drain blockage + overflow is a meaningful public-disruption event.
    if (
        any(phrase in text_lower for phrase in [
            "drain is blocked",
            "drain blocked",
            "drain is overflowing",
            "drain overflowing",
            "overflowing",
        ])
        and any(phrase in text_lower for phrase in [
            "street",
            "road",
            "houses",
            "homes",
        ])
    ):
        risk_boost += 2
        boost_reasons.append(
            "blocked/overflowing drainage affecting public space"
        )

    # Prolonged sanitation + health indicators.
    if (
        sanitation_raw >= 4
        and duration_score >= 4
        and any(phrase in text_lower for phrase in [
            "flies", "mosquitoes", "vermin", "school"
        ])
    ):
        risk_boost += 3
        boost_reasons.append(
            "prolonged sanitation issue with health-risk indicators"
        )

    # Streetlight outage + darkness/pedestrian safety.
    if (
        infrastructure_raw >= 3
        and any(phrase in text_lower for phrase in [
            "streetlight", "streetlights", "street is completely dark",
            "completely dark"
        ])
        and (
            duration_score >= 3
            or any(phrase in text_lower for phrase in [
                "unsafe", "pedestrians", "women", "children"
            ])
        )
    ):
        risk_boost += 2
        boost_reasons.append(
            "prolonged/dangerous streetlight outage"
        )

    # Large service outage
    if (
        any(
            phrase in text_lower
            for phrase in [
                "power outage",
                "power has gone out",
                "electricity unavailable",
                "no electricity",
                "electricity outage",
                "no water supply",
                "water supply unavailable",
                "water unavailable",
                "water supply interrupted",
            ]
        )
        and people_score >= 4
    ):
        risk_boost += 2
        boost_reasons.append(
            "large-scale service outage"
        )

    # Long-running large-scale service issue
    if (
        duration_score >= 4
        and people_score >= 4
    ):
        risk_boost += 2
        boost_reasons.append(
            "long duration + large affected population"
        )

    # Urgent request combined with an actual hazard
    if (
        urgency_score >= 4
        and (
            safety_score >= 4
            or impact_score >= 6
        )
    ):
        risk_boost += 2
        boost_reasons.append(
            "urgent request combined with a serious civic hazard"
        )

    # Severe road hazard + vulnerable population
    if (
        road_raw >= 4
        and vulnerability_score >= 5
    ):
        risk_boost += 2
        boost_reasons.append(
            "road hazard near vulnerable population"
        )

    # Severe road hazard + traffic disruption
    if (
        road_raw >= 4
        and any(
            phrase in text_lower
            for phrase in [
                "vehicles",
                "bikes",
                "traffic",
                "commuters",
                "pedestrians",
                "struggling to pass",
            ]
        )
    ):
        risk_boost += 3
        boost_reasons.append(
            "significant road hazard affecting movement"
        )

    # Sanitation issue + prolonged duration
    if (
        sanitation_raw >= 3
        and duration_score >= 4
    ):
        risk_boost += 1
        boost_reasons.append(
            "sanitation problem persisting for multiple days"
        )

    # --------------------------------------------------------
    # Final score
    # --------------------------------------------------------

    severity_score = round(
        weighted_score + risk_boost
    )

    severity_score = min(
        10,
        max(
            0,
            severity_score
        )
    )

    if severity_score >= 8:
        label = "CRITICAL"
    elif severity_score >= 6:
        label = "HIGH"
    elif severity_score >= 3:
        label = "MEDIUM"
    else:
        label = "LOW"

    # --------------------------------------------------------
    # Explainability
    # --------------------------------------------------------

    explanation = []

    if safety_hits:
        explanation.append(
            "Safety risk: "
            + ", ".join(safety_hits)
            + f" (+{safety_score})"
        )

    if road_hits:
        explanation.append(
            "Road/traffic impact: "
            + ", ".join(road_hits)
            + f" (+{min(10, road_raw)})"
        )

    if water_hits:
        explanation.append(
            "Water impact: "
            + ", ".join(water_hits)
            + f" (+{min(10, water_raw)})"
        )

    if sanitation_hits:
        explanation.append(
            "Sanitation impact: "
            + ", ".join(sanitation_hits)
            + f" (+{min(10, sanitation_raw)})"
        )

    if infrastructure_hits:
        explanation.append(
            "Infrastructure disruption: "
            + ", ".join(infrastructure_hits)
            + f" (+{min(10, infrastructure_raw)})"
        )

    if scale_hits:
        explanation.append(
            "People affected: "
            + ", ".join(scale_hits)
            + f" (+{people_score})"
        )

    if duration_hits:
        explanation.append(
            "Duration: "
            + ", ".join(duration_hits)
            + f" (+{duration_score})"
        )

    if vulnerability_hits:
        explanation.append(
            "Vulnerable population: "
            + ", ".join(vulnerability_hits)
            + f" (+{vulnerability_score})"
        )

    if urgency_hits:
        explanation.append(
            "Urgency: "
            + ", ".join(urgency_hits)
            + f" (+{urgency_score})"
        )

    for reason in boost_reasons:
        explanation.append(
            "Compound-risk boost: " + reason
        )

    if not explanation:
        explanation.append(
            "No strong severity signals detected."
        )

    return {
        "severity_score": severity_score,
        "severity_label": label,
        "explanation": explanation,
    }


# ============================================================
# 7. MODEL CREATION
# ============================================================

def create_classifier():

    base_model = LinearSVC(
        C=1.0
    )

    return CalibratedClassifierCV(
        estimator=base_model,
        method="sigmoid",
        cv=3
    )


# ============================================================
# 8. TRAIN CLASSIFIERS
# ============================================================

def train_classifiers(df):

    X_train, X_test, y_category_train, y_category_test = (
        train_test_split(
            df["description"],
            df["category"],
            test_size=0.2,
            random_state=42,
            stratify=df["category"]
        )
    )

    train_indices = X_train.index
    test_indices = X_test.index

    y_subcategory_train = df.loc[
        train_indices,
        "subcategory"
    ]

    y_subcategory_test = df.loc[
        test_indices,
        "subcategory"
    ]

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.9,
        sublinear_tf=True
    )

    Xtr = vectorizer.fit_transform(
        X_train
    )

    Xte = vectorizer.transform(
        X_test
    )

    category_model = create_classifier()

    category_model.fit(
        Xtr,
        y_category_train
    )

    category_predictions = category_model.predict(
        Xte
    )

    category_report = classification_report(
        y_category_test,
        category_predictions,
        zero_division=0
    )

    subcategory_model = create_classifier()

    subcategory_model.fit(
        Xtr,
        y_subcategory_train
    )

    subcategory_predictions = (
        subcategory_model.predict(Xte)
    )

    subcategory_report = classification_report(
        y_subcategory_test,
        subcategory_predictions,
        zero_division=0
    )

    return (
        vectorizer,
        category_model,
        subcategory_model,
        category_report,
        subcategory_report,
    )


# ============================================================
# 9. CLASSIFY A NEW COMPLAINT
# ============================================================

def classify_complaint(
    description,
    vectorizer,
    category_model,
    subcategory_model
):

    vec = vectorizer.transform(
        [description]
    )

    category_pred = category_model.predict(
        vec
    )[0]

    category_probabilities = (
        category_model.predict_proba(vec)[0]
    )

    category_confidence = max(
        category_probabilities
    )

    subcategory_pred = (
        subcategory_model.predict(vec)[0]
    )

    subcategory_probabilities = (
        subcategory_model.predict_proba(vec)[0]
    )

    subcategory_confidence = max(
        subcategory_probabilities
    )

    department = CATEGORY_TO_DEPARTMENT.get(
        category_pred,
        "General Municipal Office"
    )

    severity = compute_severity(
        description
    )

    return {
        "description": description,
        "predicted_category": category_pred,
        "category_confidence": round(
            float(category_confidence),
            3
        ),
        "predicted_subcategory": subcategory_pred,
        "subcategory_confidence": round(
            float(subcategory_confidence),
            3
        ),
        "routed_department": department,
        **severity,
    }


# ============================================================
# 10. DEMO
# ============================================================

if __name__ == "__main__":

    print(
        f"Loading dataset:\n{DATASET_PATH}\n"
    )

    df = pd.read_csv(
        DATASET_PATH
    )

    print(
        f"Loaded {len(df)} complaints.\n"
    )

    (
        vectorizer,
        category_model,
        subcategory_model,
        category_report,
        subcategory_report,
    ) = train_classifiers(df)

    print("=" * 70)
    print("CATEGORY CLASSIFIER — HELD-OUT REPORT")
    print("=" * 70)
    print(category_report)

    print("=" * 70)
    print("SUBCATEGORY CLASSIFIER — HELD-OUT REPORT")
    print("=" * 70)
    print(subcategory_report)

    demo_complaints = [

        (
            "A deep crater has formed on the road near "
            "the market and bikes are struggling to pass."
        ),

        (
            "The traffic signal at the junction has stopped "
            "changing and vehicles are getting stuck."
        ),

        (
            "The drinking water has a strange smell and "
            "looks brown. Residents are worried about using it."
        ),

        (
            "A live wire is hanging close to the road and "
            "children are playing nearby."
        ),

        (
            "Garbage has not been collected for many days "
            "and there is a bad smell near the houses."
        ),
    ]

    print("\n" + "=" * 70)
    print("CIVICPULSE CLASSIFICATION DEMO")
    print("=" * 70)

    results = []

    for complaint in demo_complaints:

        result = classify_complaint(
            complaint,
            vectorizer,
            category_model,
            subcategory_model
        )

        results.append(result)

        print(
            f"\n📝 {complaint}"
        )

        print(
            f"   Category: "
            f"{result['predicted_category']} "
            f"(confidence "
            f"{result['category_confidence']})"
        )

        print(
            f"   Subcategory: "
            f"{result['predicted_subcategory']} "
            f"(confidence "
            f"{result['subcategory_confidence']})"
        )

        print(
            f"   Department: "
            f"{result['routed_department']}"
        )

        print(
            f"   Severity: "
            f"{result['severity_score']}/10 — "
            f"{result['severity_label']}"
        )

        print("   Why:")

        for explanation in result["explanation"]:
            print(
                f"      • {explanation}"
            )

    output_path = (
        BASE_DIR /
        "classification_demo_output.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=2
        )

    print(
        f"\nSaved demo output → "
        f"{output_path}"
    )