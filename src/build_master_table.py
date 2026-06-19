from pathlib import Path
import logging

import numpy as np
import pandas as pd


PROCESSED_DIR = Path("data/processed")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_processed_data():
    listings = pd.read_csv(PROCESSED_DIR / "clean_listings.csv", low_memory=False)
    calendar = pd.read_csv(PROCESSED_DIR / "clean_calendar.csv", low_memory=False)
    reviews = pd.read_csv(PROCESSED_DIR / "clean_reviews.csv", low_memory=False)

    return listings, calendar, reviews


def build_calendar_summary(calendar):
    required_columns = {"listing_id", "available_bool", "price_clean"}

    if not required_columns.issubset(calendar.columns):
        missing = required_columns - set(calendar.columns)
        raise ValueError(f"Calendar data is missing required columns: {missing}")

    calendar_summary = (
        calendar
        .groupby("listing_id")
        .agg(
            total_calendar_days=("available_bool", "count"),
            available_days=("available_bool", "sum"),
            average_calendar_price=("price_clean", "mean"),
            median_calendar_price=("price_clean", "median"),
        )
        .reset_index()
    )

    calendar_summary["unavailable_days"] = (
        calendar_summary["total_calendar_days"] - calendar_summary["available_days"]
    )

    calendar_summary["occupancy_rate_estimate"] = (
        calendar_summary["unavailable_days"] / calendar_summary["total_calendar_days"]
    ).round(4)

    calendar_summary["estimated_annual_revenue"] = (
        calendar_summary["unavailable_days"] * calendar_summary["average_calendar_price"]
    ).round(2)

    return calendar_summary


def build_review_summary(reviews):
    if "listing_id" not in reviews.columns:
        raise ValueError("Reviews data is missing listing_id column")

    if "date" in reviews.columns:
        reviews["date"] = pd.to_datetime(reviews["date"], errors="coerce")

        review_summary = (
            reviews
            .groupby("listing_id")
            .agg(
                total_reviews_from_reviews_file=("listing_id", "count"),
                first_review_date=("date", "min"),
                last_review_date=("date", "max"),
            )
            .reset_index()
        )

        review_summary["review_period_days"] = (
            review_summary["last_review_date"] - review_summary["first_review_date"]
        ).dt.days

        review_summary["review_frequency_per_month"] = (
            review_summary["total_reviews_from_reviews_file"]
            / (review_summary["review_period_days"].replace(0, np.nan) / 30.44)
        ).round(2)

    else:
        review_summary = (
            reviews
            .groupby("listing_id")
            .size()
            .reset_index(name="total_reviews_from_reviews_file")
        )

    return review_summary


def select_listing_columns(listings):
    preferred_columns = [
        "id",
        "name",
        "host_id",
        "host_name",
        "host_since",
        "host_is_superhost",
        "host_response_rate_clean",
        "host_acceptance_rate_clean",
        "host_tenure_years",
        "neighbourhood_cleansed",
        "latitude",
        "longitude",
        "property_type",
        "room_type",
        "accommodates",
        "bedrooms",
        "beds",
        "price",
        "price_clean",
        "price_per_bedroom",
        "minimum_nights",
        "maximum_nights",
        "availability_365",
        "number_of_reviews",
        "review_scores_rating",
        "review_scores_cleanliness",
        "review_scores_location",
        "review_scores_communication",
        "reviews_per_month",
    ]

    available_columns = [column for column in preferred_columns if column in listings.columns]
    return listings[available_columns].copy()


def add_neighbourhood_metrics(master):
    if "neighbourhood_cleansed" not in master.columns:
        return master

    aggregation_rules = {
        "listing_count_neighbourhood": ("id", "count"),
    }

    if "price_clean" in master.columns:
        aggregation_rules["median_price_neighbourhood"] = ("price_clean", "median")
        aggregation_rules["average_price_neighbourhood"] = ("price_clean", "mean")

    if "review_scores_rating" in master.columns:
        aggregation_rules["average_rating_neighbourhood"] = ("review_scores_rating", "mean")

    neighbourhood_metrics = (
        master
        .groupby("neighbourhood_cleansed")
        .agg(**aggregation_rules)
        .reset_index()
    )

    return master.merge(neighbourhood_metrics, on="neighbourhood_cleansed", how="left")


def build_listing_master():
    logging.info("Loading processed datasets")
    listings, calendar, reviews = load_processed_data()

    logging.info("Building calendar summary")
    calendar_summary = build_calendar_summary(calendar)

    logging.info("Building review summary")
    review_summary = build_review_summary(reviews)

    logging.info("Building enriched listing master table")
    listing_master = select_listing_columns(listings)

    if "id" not in listing_master.columns:
        raise ValueError("Listings data is missing id column")

    listing_master = listing_master.merge(
        calendar_summary,
        left_on="id",
        right_on="listing_id",
        how="left",
    )

    listing_master = listing_master.merge(
        review_summary,
        left_on="id",
        right_on="listing_id",
        how="left",
        suffixes=("", "_reviews"),
    )

    listing_master = add_neighbourhood_metrics(listing_master)

    listing_master.drop(
        columns=[column for column in ["listing_id", "listing_id_reviews"] if column in listing_master.columns],
        inplace=True,
    )

    output_path = PROCESSED_DIR / "listing_master.csv"
    listing_master.to_csv(output_path, index=False)

    logging.info("Saved listing master table to %s", output_path)
    logging.info("Listing master rows: %s", len(listing_master))
    logging.info("Listing master columns: %s", len(listing_master.columns))


def main():
    build_listing_master()


if __name__ == "__main__":
    main()