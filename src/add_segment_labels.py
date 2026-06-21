from pathlib import Path
import logging

import pandas as pd


ML_OUTPUTS_DIR = Path("reports/ml_outputs")

SEGMENT_LABELS = {
    0: "Low-availability active supply",
    1: "High-availability casual or idle supply",
    2: "Established high-review listings",
    3: "Low-rating low-activity listings",
}

SEGMENT_BUSINESS_INTERPRETATIONS = {
    0: (
        "Listings in this segment have low annual availability and a high occupancy-rate proxy. "
        "They appear to represent active supply with stronger utilisation patterns."
    ),
    1: (
        "Listings in this segment have high annual availability and a lower occupancy-rate proxy. "
        "They may represent casual, idle, seasonal, or lower-utilisation supply."
    ),
    2: (
        "Listings in this segment have very high review counts and strong review scores. "
        "They appear to represent established, review-rich listings with stronger demand signals."
    ),
    3: (
        "Listings in this segment have lower review scores, low review counts, and relatively high availability. "
        "They may require host-quality improvement, listing optimisation, or operational review."
    ),
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def add_labels_to_segment_profiles():
    segment_profiles_path = ML_OUTPUTS_DIR / "segment_profiles.csv"

    if not segment_profiles_path.exists():
        raise FileNotFoundError(f"Missing file: {segment_profiles_path}")

    segment_profiles = pd.read_csv(segment_profiles_path)

    segment_profiles["segment_name"] = segment_profiles["segment_id"].map(SEGMENT_LABELS)
    segment_profiles["business_interpretation"] = segment_profiles["segment_id"].map(
        SEGMENT_BUSINESS_INTERPRETATIONS
    )

    ordered_columns = [
        "segment_id",
        "segment_name",
        "listing_count",
        "average_availability_365",
        "average_occupancy_rate_estimate",
        "average_number_of_reviews",
        "average_reviews_per_month",
        "average_review_scores_rating",
        "average_host_tenure_years",
        "business_interpretation",
    ]

    available_columns = [column for column in ordered_columns if column in segment_profiles.columns]

    segment_profiles[available_columns].to_csv(
        ML_OUTPUTS_DIR / "segment_profiles_labelled.csv",
        index=False,
    )

    logging.info("Saved labelled segment profiles")


def add_labels_to_listing_segments():
    listing_segments_path = ML_OUTPUTS_DIR / "listing_segments.csv"

    if not listing_segments_path.exists():
        raise FileNotFoundError(f"Missing file: {listing_segments_path}")

    listing_segments = pd.read_csv(listing_segments_path)
    listing_segments["segment_name"] = listing_segments["segment_id"].map(SEGMENT_LABELS)

    listing_segments.to_csv(
        ML_OUTPUTS_DIR / "listing_segments_labelled.csv",
        index=False,
    )

    logging.info("Saved labelled listing segments")


def main():
    add_labels_to_segment_profiles()
    add_labels_to_listing_segments()


if __name__ == "__main__":
    main()