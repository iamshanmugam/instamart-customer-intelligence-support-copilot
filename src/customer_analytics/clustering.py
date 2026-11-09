from __future__ import annotations

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from src.common.paths import MODELS_DIR, OUTPUTS_SEGMENTATION, RANDOM_SEED

FEATURES = ["recency_days", "frequency", "monetary"]


def _interpret_segments(centroids: pd.DataFrame) -> dict[int, str]:
    labels = {}
    for idx, row in centroids.iterrows():
        r, f, m = row["recency_days"], row["frequency"], row["monetary"]
        if f >= centroids["frequency"].median() and m >= centroids["monetary"].median() and r <= centroids["recency_days"].median():
            labels[idx] = "High-value"
        elif r > centroids["recency_days"].quantile(0.75) and f <= centroids["frequency"].quantile(0.5):
            labels[idx] = "At-risk / Low engagement"
        elif f >= centroids["frequency"].quantile(0.5):
            labels[idx] = "Regular"
        else:
            labels[idx] = "New or developing"
    return labels


def run_kmeans_pipeline(rfm: pd.DataFrame) -> dict:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_SEGMENTATION.mkdir(parents=True, exist_ok=True)

    active = rfm[(rfm["frequency"] > 0)].copy()
    X = active[FEATURES].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    joblib.dump(scaler, MODELS_DIR / "rfm_scaler.joblib")

    rows = []
    inertias = []
    silhouettes = []
    k_range = range(2, 9)
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=RANDOM_SEED, n_init=10)
        labels = km.fit_predict(X_scaled)
        inertias.append(km.inertia_)
        sil = silhouette_score(X_scaled, labels)
        silhouettes.append(sil)
        rows.append({"k": k, "inertia": km.inertia_, "silhouette": sil})

    eval_df = pd.DataFrame(rows)
    eval_df.to_csv(OUTPUTS_SEGMENTATION / "kmeans_evaluation.csv", index=False)

    best_k = int(eval_df.loc[eval_df["silhouette"].idxmax(), "k"])
    if best_k < 3:
        best_k = 3

    km_final = KMeans(n_clusters=best_k, random_state=RANDOM_SEED, n_init=10)
    active["cluster"] = km_final.fit_predict(X_scaled)
    joblib.dump(km_final, MODELS_DIR / "kmeans_model.joblib")

    centroids = active.groupby("cluster")[FEATURES].mean()
    interpretations = _interpret_segments(centroids)
    active["segment_name"] = active["cluster"].map(interpretations)

    pca = PCA(n_components=2, random_state=RANDOM_SEED)
    comps = pca.fit_transform(X_scaled)
    active["pca1"] = comps[:, 0]
    active["pca2"] = comps[:, 1]
    var_ratio = pca.explained_variance_ratio_
    pd.Series(
        {
            "pca1_var": var_ratio[0],
            "pca2_var": var_ratio[1],
            "cumulative_var": float(var_ratio.sum()),
        }
    ).to_csv(OUTPUTS_SEGMENTATION / "pca_variance.csv")

    segments_out = active[
        ["customer_id", "recency_days", "frequency", "monetary", "cluster", "segment_name"]
    ]
    segments_out.to_csv(OUTPUTS_SEGMENTATION / "customer_segments.csv", index=False)

    retention = active[
        active["segment_name"].isin(["At-risk / Low engagement"])
        | (
            (active["recency_days"] > active["recency_days"].quantile(0.75))
            & (active["frequency"] <= active["frequency"].median())
        )
    ][["customer_id", "recency_days", "frequency", "monetary", "segment_name"]]
    retention.to_csv(OUTPUTS_SEGMENTATION / "retention_list.csv", index=False)

    inactive = rfm[rfm["frequency"] == 0][["customer_id"]].copy()
    inactive["segment_name"] = "No completed orders"
    inactive.to_csv(OUTPUTS_SEGMENTATION / "inactive_customers.csv", index=False)

    return {
        "best_k": best_k,
        "evaluation": eval_df,
        "active_customers": len(active),
        "retention_count": len(retention),
    }
