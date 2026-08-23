from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

from integration import (
    load_track_a,
    load_track_b,
)
from issue_detector import Complaint


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


# ============================================================
# LOAD MODELS ONCE
# ============================================================

print("=" * 70)
print("CIVICPULSE API")
print("=" * 70)

(
    vectorizer,
    category_model,
    subcategory_model,
) = load_track_a()

issues = load_track_b()

print("\nCivicPulse API models loaded successfully.")


# ============================================================
# ANALYZE COMPLAINT
# ============================================================
@app.route("/analyze", methods=["POST", "OPTIONS"])
def analyze_complaint():

    # Handle CORS preflight request immediately, before any real logic runs
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required."
        }), 400

    description = data.get(
        "description"
    )

    latitude = data.get(
        "latitude"
    )

    longitude = data.get(
        "longitude"
    )

    if not description:
        return jsonify({
            "error": "description is required."
        }), 400

    if latitude is None or longitude is None:
        return jsonify({
            "error": "latitude and longitude are required."
        }), 400

    try:

        latitude = float(latitude)
        longitude = float(longitude)

    except (TypeError, ValueError):

        return jsonify({
            "error": "latitude and longitude must be numbers."
        }), 400

    # ========================================================
    # TRACK A
    # ========================================================

    classification = __import__(
        "classify"
    ).classify_complaint(
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
    # TRACK B
    # ========================================================

    timestamp = pd.Timestamp.now().isoformat()

    complaint = Complaint(
        complaint_id="API_COMPLAINT",
        description=description,
        category=category,
        subcategory=subcategory,
        latitude=latitude,
        longitude=longitude,
        timestamp=timestamp,
    )

    from issue_detector import find_best_issue_match

    issue_result = find_best_issue_match(
        complaint,
        issues,
    )

    decision = issue_result.get(
        "decision",
        "NEW_ISSUE"
    )

    if decision == "NEW_ISSUE":

        issue_id = None

    else:

        issue_id = issue_result.get(
            "matched_issue_id"
        )

    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    result = {

        "complaint": description,

        "location": {
            "latitude": latitude,
            "longitude": longitude,
        },

        "classification": {

            "category":
                classification[
                    "predicted_category"
                ],

            "category_confidence":
                classification[
                    "category_confidence"
                ],

            "subcategory":
                classification[
                    "predicted_subcategory"
                ],

            "subcategory_confidence":
                classification[
                    "subcategory_confidence"
                ],

            "department":
                classification[
                    "routed_department"
                ],
        },

        "severity": {

            "score":
                classification[
                    "severity_score"
                ],

            "label":
                classification[
                    "severity_label"
                ],

            "explanation":
                classification.get(
                    "explanation",
                    []
                ),
        },

        "issue_detection": {

            "decision": decision,

            "similarity":
                issue_result.get(
                    "overall_similarity",
                    0.0
                ),

            "issue_id":
                issue_id,

            "distance_km":
                issue_result.get(
                    "distance_km"
                ),
        },
    }

    return jsonify(result)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "ok",
        "service": "CivicPulse",
        "track_a": "ready",
        "track_b": "ready",
        "indexed_issues": len(issues),
    })


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
    )