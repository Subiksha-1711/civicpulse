import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.cluster import DBSCAN


# ============================================================
# 1. LOAD DATASET
# ============================================================

df = pd.read_csv("civicpulse_trackb_dataset.csv")

print(df.head())
print("Number of complaints:", len(df))


# ============================================================
# 2. GENERATE SENTENCE EMBEDDINGS
# ============================================================

model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = model.encode(
    df["description"].tolist(),
    show_progress_bar=True
)

print("\nNumber of embeddings:", len(embeddings))
print("Embedding size:", embeddings.shape)


# ============================================================
# 3. COSINE SIMILARITY
# ============================================================

similarity_matrix = cosine_similarity(embeddings)

print("Similarity matrix shape:", similarity_matrix.shape)


# Compare first complaint with next 5 complaints
print("\nSimilarity examples:")

for i in range(1, 6):
    print(
        f"Complaint 1 <-> Complaint {i + 1}: "
        f"{similarity_matrix[0][i]:.4f}"
    )


# ============================================================
# 4. REMOVE SELF-SIMILARITY
# ============================================================

np.fill_diagonal(similarity_matrix, -1)


# ============================================================
# 5. FIND MOST SIMILAR COMPLAINT FOR EACH COMPLAINT
# ============================================================

most_similar_index = np.argmax(
    similarity_matrix,
    axis=1
)

most_similar_score = np.max(
    similarity_matrix,
    axis=1
)


print("\n===== MOST SIMILAR COMPLAINTS =====")

for i in range(min(10, len(df))):

    j = most_similar_index[i]

    print("\nComplaint:", i + 1)

    print(
        "Text:",
        df.iloc[i]["description"]
    )

    print(
        "Most similar:",
        j + 1
    )

    print(
        "Text:",
        df.iloc[j]["description"]
    )

    print(
        "Similarity:",
        round(most_similar_score[i], 4)
    )


# ============================================================
# 6. TEST DUPLICATE DETECTION THRESHOLDS
# ============================================================

thresholds = [0.70, 0.75, 0.80, 0.85, 0.90]

print("\n===== DUPLICATE DETECTION EVALUATION =====")

for threshold in thresholds:

    y_true = []
    y_pred = []

    for i in range(len(df)):

        j = most_similar_index[i]

        # Ground truth
        true_duplicate = (
            df.iloc[i]["ground_truth_issue_id"]
            == df.iloc[j]["ground_truth_issue_id"]
        )

        # Model prediction
        predicted_duplicate = (
            most_similar_score[i] >= threshold
        )

        y_true.append(true_duplicate)
        y_pred.append(predicted_duplicate)

    precision = precision_score(
        y_true,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_true,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_true,
        y_pred,
        zero_division=0
    )

    print(f"\nThreshold: {threshold}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall:    {recall:.3f}")
    print(f"F1 Score:  {f1:.3f}")


# ============================================================
# 7. SIMILARITY HEATMAP
# ============================================================

plt.figure(figsize=(10, 8))

plt.imshow(
    similarity_matrix,
    cmap="viridis"
)

plt.colorbar(
    label="Cosine Similarity"
)

plt.xlabel("Complaint Index")
plt.ylabel("Complaint Index")

plt.title(
    "Complaint Semantic Similarity Matrix"
)

plt.savefig("similarity_heatmap.png")


# ============================================================
# 8. CONVERT SIMILARITY TO DISTANCE
# ============================================================

distance_matrix = 1 - similarity_matrix

# Prevent tiny floating-point negative values
distance_matrix = np.clip(
    distance_matrix,
    0,
    None
)


# ============================================================
# 9. TEST DIFFERENT DBSCAN EPS VALUES
# ============================================================

print("\n===== DBSCAN PARAMETER TESTING =====")

eps_values = [
    0.20,
    0.25,
    0.30,
    0.35,
    0.40
]

for eps in eps_values:

    dbscan = DBSCAN(
        eps=eps,
        min_samples=2,
        metric="precomputed"
    )

    labels = dbscan.fit_predict(
        distance_matrix
    )

    number_of_clusters = (
        len(set(labels))
        - (1 if -1 in labels else 0)
    )

    noise_complaints = list(labels).count(-1)

    print(
        f"eps={eps:.2f} | "
        f"clusters={number_of_clusters} | "
        f"noise={noise_complaints}"
    )


# ============================================================
# 10. RUN FINAL DBSCAN
# ============================================================

# Temporary value.
# We will change this after seeing the eps results.

best_eps = 0.30

dbscan = DBSCAN(
    eps=best_eps,
    min_samples=2,
    metric="precomputed"
)

labels = dbscan.fit_predict(
    distance_matrix
)


# ============================================================
# 11. ADD CLUSTER ID TO DATASET
# ============================================================

df["cluster_id"] = labels


# ============================================================
# 12. CLUSTER SUMMARY
# ============================================================

number_of_clusters = (
    len(set(labels))
    - (1 if -1 in labels else 0)
)

noise_complaints = list(labels).count(-1)

print("\n===== FINAL DBSCAN RESULT =====")

print(
    "Number of clusters:",
    number_of_clusters
)

print(
    "Noise complaints:",
    noise_complaints
)


# ============================================================
# 13. CLUSTER SIZES
# ============================================================

print("\n===== CLUSTER SIZES =====")

print(
    df["cluster_id"]
    .value_counts()
    .sort_index()
)


# ============================================================
# 14. SHOW CLUSTERED COMPLAINTS
# ============================================================

print("\n===== CLUSTER RESULTS =====")

print(
    df[
        [
            "complaint_id",
            "ground_truth_issue_id",
            "cluster_id",
            "description"
        ]
    ].to_string(index=False)
)
print("\n===== GROUND TRUTH vs DBSCAN =====")

cluster_comparison = pd.crosstab(
    df["ground_truth_issue_id"],
    df["cluster_id"]
)

print(cluster_comparison)
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

# Evaluate all complaints, including noise
ari = adjusted_rand_score(
    df["ground_truth_issue_id"],
    df["cluster_id"]
)

nmi = normalized_mutual_info_score(
    df["ground_truth_issue_id"],
    df["cluster_id"]
)

print("\n===== CLUSTERING QUALITY =====")
print("Adjusted Rand Index (ARI):", round(ari, 3))
print("Normalized Mutual Information (NMI):", round(nmi, 3))
print(df.columns.tolist())
print("\n===== LOCATION INFORMATION =====")

print("Latitude range:")
print(df["latitude"].min(), "to", df["latitude"].max())

print("\nLongitude range:")
print(df["longitude"].min(), "to", df["longitude"].max())

print("\nMissing latitude:", df["latitude"].isna().sum())
print("Missing longitude:", df["longitude"].isna().sum())
print("\n===== ISSUE LOCATION CHECK =====")

location_summary = df.groupby("ground_truth_issue_id").agg(
    complaints=("complaint_id", "count"),
    min_lat=("latitude", "min"),
    max_lat=("latitude", "max"),
    min_lon=("longitude", "min"),
    max_lon=("longitude", "max")
)

print(location_summary.to_string())
from sklearn.metrics import pairwise_distances

# Convert latitude and longitude to radians
coords = np.radians(
    df[["latitude", "longitude"]].values
)

# Calculate geographic distance using haversine metric
geo_distance = pairwise_distances(
    coords,
    metric="haversine"
)

# Convert radians to kilometers
geo_distance_km = geo_distance * 6371

print("\n===== GEOGRAPHIC DISTANCE =====")

print(
    "Minimum distance:",
    round(geo_distance_km[geo_distance_km > 0].min(), 3),
    "km"
)

print(
    "Maximum distance:",
    round(geo_distance_km.max(), 3),
    "km"
)
same_issue_distances = []

for i in range(len(df)):
    for j in range(i + 1, len(df)):

        if (
            df.iloc[i]["ground_truth_issue_id"]
            == df.iloc[j]["ground_truth_issue_id"]
        ):
            same_issue_distances.append(
                geo_distance_km[i][j]
            )

print("\n===== SAME ISSUE DISTANCE =====")

print(
    "Average distance:",
    round(np.mean(same_issue_distances), 3),
    "km"
)

print(
    "Maximum distance:",
    round(np.max(same_issue_distances), 3),
    "km"
)

print(
    "95th percentile:",
    round(np.percentile(same_issue_distances, 95), 3),
    "km"
)
# ============================================================
# GEO-AWARE DUPLICATE DETECTION
# ============================================================

TEXT_THRESHOLD = 0.75
LOCATION_THRESHOLD_KM = 0.50

duplicate_pairs = []

for i in range(len(df)):
    for j in range(i + 1, len(df)):

        text_similarity = similarity_matrix[i][j]
        distance_km = geo_distance_km[i][j]

        if (
            text_similarity >= TEXT_THRESHOLD
            and distance_km <= LOCATION_THRESHOLD_KM
        ):
            duplicate_pairs.append({
                "complaint_1": df.iloc[i]["complaint_id"],
                "complaint_2": df.iloc[j]["complaint_id"],
                "similarity": round(text_similarity, 3),
                "distance_km": round(distance_km, 3)
            })

pairs_df = pd.DataFrame(duplicate_pairs)

print("\n===== GEO-AWARE DUPLICATE PAIRS =====")

print(
    "Number of duplicate pairs:",
    len(pairs_df)
)

if len(pairs_df) > 0:
    print("\nSample duplicate pairs:")
    print(
        pairs_df.head(20).to_string(index=False)
    )
else:
    print("No duplicate pairs found.")

import networkx as nx

# ============================================================
# CREATE ISSUE CLUSTERS FROM DUPLICATE PAIRS
# ============================================================

G = nx.Graph()

# Add every complaint as a node
G.add_nodes_from(df["complaint_id"])

# Add duplicate relationships as edges
for _, row in pairs_df.iterrows():

    G.add_edge(
        row["complaint_1"],
        row["complaint_2"]
    )

# Find connected groups
components = list(nx.connected_components(G))

print("\n===== ISSUE CLUSTERS =====")

cluster_number = 1

for component in components:

    if len(component) > 1:

        print(
            f"\nISSUE_CLUSTER_{cluster_number}"
        )

        print(
    "Complaints:",
    [int(x) for x in sorted(component)]
)
        

        print(
            "Number of complaints:",
            len(component)
        )

        cluster_number += 1