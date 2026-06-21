from pathlib import Path
import logging

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.metrics import silhouette_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


PROCESSED_DIR = Path("data/processed")
REPORTS_DIR = Path("reports")
ML_OUTPUTS_DIR = REPORTS_DIR / "ml_outputs"
FIGURES_DIR = REPORTS_DIR / "figures"

ML_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


NUMERIC_FEATURES = [
    "availability_365",
    "occupancy_rate_estimate",
    "number_of_reviews",
    "reviews_per_month",
    "review_scores_rating",
    "host_tenure_years",
    "calculated_host_listings_count",
]

CATEGORICAL_FEATURES = [
    "room_type",
    "host_is_superhost",
]


def load_listing_master():
    listing_master = pd.read_csv(PROCESSED_DIR / "listing_master.csv", low_memory=False)

    for column in NUMERIC_FEATURES:
        if column in listing_master.columns:
            listing_master[column] = pd.to_numeric(listing_master[column], errors="coerce")

    return listing_master


def select_available_features(df):
    numeric_features = [column for column in NUMERIC_FEATURES if column in df.columns]
    categorical_features = [column for column in CATEGORICAL_FEATURES if column in df.columns]

    if not numeric_features:
        raise ValueError("No numeric features available for clustering")

    return numeric_features, categorical_features


def build_preprocessor(numeric_features, categorical_features):
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    transformers = [
        ("numeric", numeric_pipeline, numeric_features),
    ]

    if categorical_features:
        transformers.append(("categorical", categorical_pipeline, categorical_features))

    return ColumnTransformer(transformers=transformers)


def create_segment_labels(df, transformed_features, cluster_count):
    model = KMeans(
        n_clusters=cluster_count,
        random_state=42,
        n_init=10,
    )

    segment_labels = model.fit_predict(transformed_features)

    output_df = df.copy()
    output_df["segment_id"] = segment_labels

    return output_df, model


def create_segment_profiles(segmented_df):
    profile_columns = {
        "listing_count": ("id", "count"),
    }

    for column in [
        "availability_365",
        "occupancy_rate_estimate",
        "number_of_reviews",
        "reviews_per_month",
        "review_scores_rating",
        "host_tenure_years",
        "calculated_host_listings_count",
    ]:
        if column in segmented_df.columns:
            profile_columns[f"average_{column}"] = (column, "mean")
            profile_columns[f"median_{column}"] = (column, "median")

    segment_profiles = (
        segmented_df
        .groupby("segment_id")
        .agg(**profile_columns)
        .reset_index()
        .sort_values("listing_count", ascending=False)
    )

    return segment_profiles


def create_segment_room_type_summary(segmented_df):
    if "room_type" not in segmented_df.columns:
        return pd.DataFrame()

    return (
        segmented_df
        .groupby(["segment_id", "room_type"])
        .size()
        .reset_index(name="listing_count")
        .sort_values(["segment_id", "listing_count"], ascending=[True, False])
    )


def create_cluster_quality(transformed_features, segment_labels):
    score = silhouette_score(transformed_features, segment_labels)

    return pd.DataFrame(
        [
            {
                "model": "KMeans",
                "cluster_count": len(set(segment_labels)),
                "silhouette_score": round(score, 4),
                "interpretation": (
                    "Silhouette score measures how well listings fit within their assigned segment. "
                    "Higher values indicate clearer separation between segments."
                ),
            }
        ]
    )


def create_pca_figure(transformed_features, segment_labels):
    pca = PCA(n_components=2, random_state=42)
    components = pca.fit_transform(transformed_features)

    plot_df = pd.DataFrame(
        {
            "pca_component_1": components[:, 0],
            "pca_component_2": components[:, 1],
            "segment_id": segment_labels,
        }
    )

    if len(plot_df) > 5000:
        plot_df = plot_df.sample(5000, random_state=42)

    plt.figure(figsize=(10, 6))
    plt.scatter(
        plot_df["pca_component_1"],
        plot_df["pca_component_2"],
        c=plot_df["segment_id"],
        alpha=0.5,
    )
    plt.title("Listing Segments Visualised with PCA")
    plt.xlabel("PCA Component 1")
    plt.ylabel("PCA Component 2")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "listing_segments_pca.png", dpi=300, bbox_inches="tight")
    plt.close()


def create_segment_availability_figure(segment_profiles):
    plt.figure(figsize=(10, 6))
    plt.bar(
        segment_profiles["segment_id"].astype(str),
        segment_profiles["average_availability_365"],
    )
    plt.title("Average Annual Availability by Listing Segment")
    plt.xlabel("Segment ID")
    plt.ylabel("Average Available Days per Year")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "segment_profile_availability.png", dpi=300, bbox_inches="tight")
    plt.close()


def save_outputs(segmented_df, segment_profiles, room_type_summary, cluster_quality):
    selected_columns = [
        column
        for column in [
            "id",
            "name",
            "host_id",
            "host_name",
            "neighbourhood_cleansed",
            "room_type",
            "availability_365",
            "occupancy_rate_estimate",
            "number_of_reviews",
            "reviews_per_month",
            "review_scores_rating",
            "host_tenure_years",
            "calculated_host_listings_count",
            "segment_id",
        ]
        if column in segmented_df.columns
    ]

    segmented_df[selected_columns].to_csv(
        ML_OUTPUTS_DIR / "listing_segments.csv",
        index=False,
    )

    segment_profiles.to_csv(
        ML_OUTPUTS_DIR / "segment_profiles.csv",
        index=False,
    )

    cluster_quality.to_csv(
        ML_OUTPUTS_DIR / "cluster_quality.csv",
        index=False,
    )

    if not room_type_summary.empty:
        room_type_summary.to_csv(
            ML_OUTPUTS_DIR / "segment_room_type_summary.csv",
            index=False,
        )


def main():
    logging.info("Creating ML listing segmentation outputs")

    listing_master = load_listing_master()

    numeric_features, categorical_features = select_available_features(listing_master)
    feature_columns = numeric_features + categorical_features

    modelling_df = listing_master.dropna(how="all", subset=feature_columns).copy()

    preprocessor = build_preprocessor(numeric_features, categorical_features)
    transformed_features = preprocessor.fit_transform(modelling_df)

    segmented_df, _ = create_segment_labels(
        modelling_df,
        transformed_features,
        cluster_count=4,
    )

    segment_profiles = create_segment_profiles(segmented_df)
    room_type_summary = create_segment_room_type_summary(segmented_df)
    cluster_quality = create_cluster_quality(
        transformed_features,
        segmented_df["segment_id"],
    )

    save_outputs(
        segmented_df,
        segment_profiles,
        room_type_summary,
        cluster_quality,
    )

    create_pca_figure(transformed_features, segmented_df["segment_id"])
    create_segment_availability_figure(segment_profiles)

    logging.info("ML listing segmentation outputs created")


if __name__ == "__main__":
    main()