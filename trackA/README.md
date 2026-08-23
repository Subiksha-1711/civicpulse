# CivicPulse — Track A: Complaint Understanding & Priority Engine

## What's here

- `data/civicpulse_trackb_dataset.csv` — the dataset your teammate pushed (Track B's, has category/subcategory + duplicate labels), rebuilt cleanly so it parses without CSV errors (a few descriptions had commas that broke the raw file).
- `classify.py` — text classification (TF-IDF + Logistic Regression) for **category** and **subcategory**, a **category → department routing table**, and a transparent keyword-based **severity scorer** (0–10) with an explanation of which words drove it.
- `priority_engine.py` — combines six weighted factors into the **Civic Priority Score** (0–100): Severity, Safety Risk, People Affected, Duration, Complaint Density, Vulnerability. Every score comes with a plain-English "why" — this is your demo moment for judges.

## Run it

```bash
pip install pandas scikit-learn
python3 classify.py          # trains + demos the classifier
python3 priority_engine.py   # demos the priority score with explainability
```

## Design decisions worth knowing (so you can defend them if judges ask)

1. **Severity/Safety/Duration/Vulnerability are rule-based, not ML.** The dataset has no severity labels — only category/subcategory. Rather than training on fabricated labels, these factors use transparent keyword + regex signals. This is a *feature*, not a shortcut: it's what makes the "why this score" moment legible live on stage, instead of a black box.
2. **Category/Subcategory ARE a real trained classifier** (TF-IDF + LogReg) since those labels genuinely exist in the data.
3. **Weights** (Severity 0.25, Safety 0.25, People Affected 0.20, Duration 0.15, Complaint Density 0.10, Vulnerability 0.05) are a starting point — tune them once you see real demo complaints. They sum to 1.0 and scale to a 0–100 score.

## Integration contract with Track B (duplicate detection / clustering)

`compute_priority(description, cluster_size=None)` in `priority_engine.py` takes an optional `cluster_size` — the number of duplicate complaints Track B's clustering found for that issue. When Track B's script produces its `ISSUE_CLUSTER_N` groups, just pass `len(component)` as `cluster_size` here. Without it, People Affected and Complaint Density fall back to text-only estimates (still functional for solo testing, just less accurate) — nothing breaks if Track B isn't wired up yet.

## Integration contract with Track C (portal / dashboard)

Call `classify_complaint(description, vectorizer, category_model, subcategory_model)` then `compute_priority(description, cluster_size)` per incoming complaint. Both return plain dicts — easy to serialize to JSON for an API endpoint. Suggested single endpoint:

```
POST /analyze-complaint
{ "description": "...", "cluster_size": 12 }
->
{ category, subcategory, routed_department, severity_score, severity_label,
  priority_score, priority_label, breakdown: [...] }
```

## Known limitations (flag these proactively, don't let judges find them first)

- Keyword lists are small and English-only — a complaint phrased unusually could get 0 severity. Good pothole/streetlight/garbage/drain/water/electricity phrasing works; edge cases won't.
- "college" is currently tagged as a mild vulnerability term, which double-counts for location names like "PSG College Gate" — worth trimming before the live demo if that complaint is in your script.
- Category classifier reports 100% held-out accuracy — expected for this dataset (many near-duplicate phrasings per issue), not a claim of production-grade generalization. Worth saying this yourself if asked.
