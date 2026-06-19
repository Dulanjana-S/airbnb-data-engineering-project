from pathlib import Path
import logging

import matplotlib.pyplot as plt
import pandas as pd


PROCESSED_DIR = Path("data/processed")
FIGURES_DIR = Path("reports/figures")
EDA_OUTPUTS_DIR = Path("reports/eda_outputs")

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
EDA_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def to_numeric(series):
    return pd.to_numeric(series, errors="coerce")


def save_table(df, filename):
    output_path = EDA_OUTPUTS_DIR / filename
    df.to_csv(output_path, index=False)
    logging.info("Saved table to %s", output_path)


def save_figure(filename):
    output_path = FIGURES_DIR / filename
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    logging.info("Saved figure to %s", output_path)


def load_data():
    listing_master = pd.read_csv(PROCESSED_DIR / "listing_master.csv", low_memory=False)
    calendar = pd.read_csv(PROCESSED_DIR / "clean_calendar.csv", low_memory=False)

    numeric_columns = [
        "availability_365",
        "number_of_reviews",
        "reviews_per_month",
        "review_scores_rating",
        "occupancy_rate_estimate",
    ]

    for column in numeric_columns:
        if column in listing_master.columns:
            listing_master[column] = to_numeric(listing_master[column])

    if "available_bool" in calendar.columns:
        calendar["available_bool"] = calendar["available_bool"].astype(str).str.lower()
        calendar["available_bool"] = calendar["available_bool"].map(
            {
                "true": True,
                "false": False,
                "1": True,
                "0": False,
                "t": True,
                "f": False,
            }
        )

    if "date" in calendar.columns:
        calendar["date"] = pd.to_datetime(calendar["date"], errors="coerce")

    return listing_master, calendar


def create_listing_supply_by_room_type(listing_master):
    summary = (
        listing_master
        .dropna(subset=["room_type"])
        .groupby("room_type")
        .agg(
            listing_count=("id", "count"),
            average_availability_365=("availability_365", "mean"),
            median_availability_365=("availability_365", "median"),
            average_number_of_reviews=("number_of_reviews", "mean"),
        )
        .reset_index()
        .sort_values("listing_count", ascending=False)
    )

    save_table(summary, "listing_supply_by_room_type.csv")

    plt.figure(figsize=(10, 6))
    plt.bar(summary["room_type"], summary["listing_count"])
    plt.title("Melbourne Airbnb Listing Supply by Room Type")
    plt.xlabel("Room Type")
    plt.ylabel("Number of Listings")
    plt.xticks(rotation=30, ha="right")
    save_figure("listing_supply_by_room_type.png")


def create_availability_by_room_type(listing_master):
    summary = (
        listing_master
        .dropna(subset=["room_type", "availability_365"])
        .groupby("room_type")
        .agg(
            listing_count=("id", "count"),
            average_availability_365=("availability_365", "mean"),
            median_availability_365=("availability_365", "median"),
        )
        .reset_index()
        .sort_values("average_availability_365", ascending=False)
    )

    save_table(summary, "availability_by_room_type.csv")

    plt.figure(figsize=(10, 6))
    plt.bar(summary["room_type"], summary["average_availability_365"])
    plt.title("Average Availability by Room Type")
    plt.xlabel("Room Type")
    plt.ylabel("Average Available Days per Year")
    plt.xticks(rotation=30, ha="right")
    save_figure("availability_by_room_type.png")


def create_top_neighbourhoods_by_supply(listing_master):
    summary = (
        listing_master
        .dropna(subset=["neighbourhood_cleansed"])
        .groupby("neighbourhood_cleansed")
        .agg(
            listing_count=("id", "count"),
            average_availability_365=("availability_365", "mean"),
            average_number_of_reviews=("number_of_reviews", "mean"),
            average_review_score=("review_scores_rating", "mean"),
        )
        .reset_index()
        .sort_values("listing_count", ascending=False)
        .head(10)
    )

    save_table(summary, "top_neighbourhoods_by_listing_count.csv")

    plt.figure(figsize=(12, 7))
    plt.barh(summary["neighbourhood_cleansed"], summary["listing_count"])
    plt.title("Top 10 Melbourne Neighbourhoods by Airbnb Listing Count")
    plt.xlabel("Number of Listings")
    plt.ylabel("Neighbourhood")
    plt.gca().invert_yaxis()
    save_figure("top_neighbourhoods_by_listing_count.png")


def create_review_score_distribution(listing_master):
    if "review_scores_rating" not in listing_master.columns:
        logging.warning("review_scores_rating column not found")
        return

    review_scores = listing_master["review_scores_rating"].dropna()

    plt.figure(figsize=(10, 6))
    plt.hist(review_scores, bins=30)
    plt.title("Melbourne Airbnb Review Score Distribution")
    plt.xlabel("Review Score Rating")
    plt.ylabel("Number of Listings")
    save_figure("review_score_distribution.png")


def create_reviews_by_room_type(listing_master):
    summary = (
        listing_master
        .dropna(subset=["room_type"])
        .groupby("room_type")
        .agg(
            listing_count=("id", "count"),
            average_number_of_reviews=("number_of_reviews", "mean"),
            median_number_of_reviews=("number_of_reviews", "median"),
            average_reviews_per_month=("reviews_per_month", "mean"),
        )
        .reset_index()
        .sort_values("average_number_of_reviews", ascending=False)
    )

    save_table(summary, "reviews_by_room_type.csv")

    plt.figure(figsize=(10, 6))
    plt.bar(summary["room_type"], summary["average_number_of_reviews"])
    plt.title("Average Number of Reviews by Room Type")
    plt.xlabel("Room Type")
    plt.ylabel("Average Number of Reviews")
    plt.xticks(rotation=30, ha="right")
    save_figure("reviews_by_room_type.png")


def create_monthly_availability(calendar):
    required_columns = {"date", "available_bool"}

    if not required_columns.issubset(calendar.columns):
        logging.warning("Calendar data does not contain required availability columns")
        return

    monthly_availability = (
        calendar
        .dropna(subset=["date", "available_bool"])
        .assign(month=lambda df: df["date"].dt.to_period("M").astype(str))
        .groupby("month")
        .agg(
            calendar_records=("available_bool", "count"),
            availability_rate=("available_bool", "mean"),
        )
        .reset_index()
    )

    save_table(monthly_availability, "monthly_availability_rate.csv")

    plt.figure(figsize=(12, 6))
    plt.plot(monthly_availability["month"], monthly_availability["availability_rate"])
    plt.title("Monthly Airbnb Availability Rate in Melbourne")
    plt.xlabel("Month")
    plt.ylabel("Availability Rate")
    plt.xticks(rotation=45, ha="right")
    save_figure("monthly_availability_rate.png")


def create_top_hosts_by_listing_count(listing_master):
    if "host_id" not in listing_master.columns:
        logging.warning("host_id column not found")
        return

    host_summary = (
        listing_master
        .dropna(subset=["host_id"])
        .groupby(["host_id", "host_name"], dropna=False)
        .agg(
            listing_count=("id", "count"),
            average_availability_365=("availability_365", "mean"),
            average_number_of_reviews=("number_of_reviews", "mean"),
        )
        .reset_index()
        .sort_values("listing_count", ascending=False)
        .head(20)
    )

    save_table(host_summary, "top_hosts_by_listing_count.csv")

    top_10_hosts = host_summary.head(10).copy()
    top_10_hosts["host_label"] = top_10_hosts["host_name"].fillna(
        top_10_hosts["host_id"].astype(str)
    )

    plt.figure(figsize=(12, 7))
    plt.barh(top_10_hosts["host_label"], top_10_hosts["listing_count"])
    plt.title("Top 10 Hosts by Listing Count")
    plt.xlabel("Number of Listings")
    plt.ylabel("Host")
    plt.gca().invert_yaxis()
    save_figure("top_hosts_by_listing_count.png")


def main():
    logging.info("Creating non-price EDA outputs")

    listing_master, calendar = load_data()

    create_listing_supply_by_room_type(listing_master)
    create_availability_by_room_type(listing_master)
    create_top_neighbourhoods_by_supply(listing_master)
    create_review_score_distribution(listing_master)
    create_reviews_by_room_type(listing_master)
    create_monthly_availability(calendar)
    create_top_hosts_by_listing_count(listing_master)

    logging.info("EDA output generation completed successfully")


if __name__ == "__main__":
    main()