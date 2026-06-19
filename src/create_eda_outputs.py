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

    listing_master["price_clean"] = to_numeric(listing_master["price_clean"])

    if "review_scores_rating" in listing_master.columns:
        listing_master["review_scores_rating"] = to_numeric(
            listing_master["review_scores_rating"]
        )

    if "number_of_reviews" in listing_master.columns:
        listing_master["number_of_reviews"] = to_numeric(
            listing_master["number_of_reviews"]
        )

    if "price_clean" in calendar.columns:
        calendar["price_clean"] = to_numeric(calendar["price_clean"])

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


def create_price_distribution(listing_master):
    price_data = listing_master["price_clean"].dropna()
    price_data = price_data[price_data > 0]
    price_data = price_data[price_data <= price_data.quantile(0.99)]

    plt.figure(figsize=(10, 6))
    plt.hist(price_data, bins=50)
    plt.title("Melbourne Airbnb Listing Price Distribution")
    plt.xlabel("Price")
    plt.ylabel("Number of Listings")
    save_figure("price_distribution.png")


def create_price_by_room_type(listing_master):
    summary = (
        listing_master
        .dropna(subset=["room_type", "price_clean"])
        .groupby("room_type")
        .agg(
            listing_count=("id", "count"),
            median_price=("price_clean", "median"),
            average_price=("price_clean", "mean"),
        )
        .reset_index()
        .sort_values("median_price", ascending=False)
    )

    save_table(summary, "price_by_room_type.csv")

    plt.figure(figsize=(10, 6))
    plt.bar(summary["room_type"], summary["median_price"])
    plt.title("Median Price by Room Type")
    plt.xlabel("Room Type")
    plt.ylabel("Median Price")
    plt.xticks(rotation=30, ha="right")
    save_figure("median_price_by_room_type.png")


def create_top_neighbourhood_prices(listing_master):
    summary = (
        listing_master
        .dropna(subset=["neighbourhood_cleansed", "price_clean"])
        .groupby("neighbourhood_cleansed")
        .agg(
            listing_count=("id", "count"),
            median_price=("price_clean", "median"),
            average_price=("price_clean", "mean"),
        )
        .reset_index()
    )

    summary = summary[summary["listing_count"] >= 10]
    summary = summary.sort_values("median_price", ascending=False).head(10)

    save_table(summary, "top_neighbourhoods_by_median_price.csv")

    plt.figure(figsize=(12, 7))
    plt.barh(summary["neighbourhood_cleansed"], summary["median_price"])
    plt.title("Top 10 Neighbourhoods by Median Price")
    plt.xlabel("Median Price")
    plt.ylabel("Neighbourhood")
    plt.gca().invert_yaxis()
    save_figure("top_neighbourhoods_by_median_price.png")


def create_review_score_distribution(listing_master):
    if "review_scores_rating" not in listing_master.columns:
        logging.warning("review_scores_rating column not found")
        return

    review_scores = listing_master["review_scores_rating"].dropna()

    plt.figure(figsize=(10, 6))
    plt.hist(review_scores, bins=30)
    plt.title("Review Score Distribution")
    plt.xlabel("Review Score Rating")
    plt.ylabel("Number of Listings")
    save_figure("review_score_distribution.png")


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
    plt.title("Monthly Availability Rate")
    plt.xlabel("Month")
    plt.ylabel("Availability Rate")
    plt.xticks(rotation=45, ha="right")
    save_figure("monthly_availability_rate.png")


def create_host_concentration_table(listing_master):
    if "host_id" not in listing_master.columns:
        logging.warning("host_id column not found")
        return

    host_summary = (
        listing_master
        .dropna(subset=["host_id"])
        .groupby(["host_id", "host_name"], dropna=False)
        .agg(
            listing_count=("id", "count"),
            average_price=("price_clean", "mean"),
            total_estimated_revenue=("estimated_annual_revenue", "sum"),
        )
        .reset_index()
        .sort_values("listing_count", ascending=False)
        .head(20)
    )

    save_table(host_summary, "top_hosts_by_listing_count.csv")


def create_price_vs_reviews(listing_master):
    required_columns = {"price_clean", "number_of_reviews"}

    if not required_columns.issubset(listing_master.columns):
        logging.warning("Required columns for price vs reviews chart not found")
        return

    chart_data = listing_master.dropna(subset=["price_clean", "number_of_reviews"])
    chart_data = chart_data[chart_data["price_clean"] > 0]
    chart_data = chart_data[chart_data["price_clean"] <= chart_data["price_clean"].quantile(0.99)]

    if len(chart_data) > 5000:
        chart_data = chart_data.sample(5000, random_state=42)

    plt.figure(figsize=(10, 6))
    plt.scatter(chart_data["number_of_reviews"], chart_data["price_clean"], alpha=0.4)
    plt.title("Price vs Number of Reviews")
    plt.xlabel("Number of Reviews")
    plt.ylabel("Price")
    save_figure("price_vs_number_of_reviews.png")


def main():
    logging.info("Creating EDA outputs")

    listing_master, calendar = load_data()

    create_price_distribution(listing_master)
    create_price_by_room_type(listing_master)
    create_top_neighbourhood_prices(listing_master)
    create_review_score_distribution(listing_master)
    create_monthly_availability(calendar)
    create_host_concentration_table(listing_master)
    create_price_vs_reviews(listing_master)

    logging.info("EDA output generation completed successfully")


if __name__ == "__main__":
    main()
    