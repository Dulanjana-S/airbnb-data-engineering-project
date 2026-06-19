from pathlib import Path
import logging

import numpy as np
import pandas as pd


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def clean_price(value):
    """Convert price values such as '$1,234.00' into numeric values."""
    if pd.isna(value):
        return np.nan

    cleaned_value = (
        str(value)
        .replace("$", "")
        .replace(",", "")
        .strip()
    )

    return pd.to_numeric(cleaned_value, errors="coerce")


def clean_percentage(value):
    """Convert percentage values such as '95%' into decimal values."""
    if pd.isna(value):
        return np.nan

    cleaned_value = str(value).replace("%", "").strip()
    numeric_value = pd.to_numeric(cleaned_value, errors="coerce")

    if pd.isna(numeric_value):
        return np.nan

    return numeric_value / 100


def clean_text_columns(df, columns):
    """Standardise selected text columns."""
    for column in columns:
        if column in df.columns:
            df[column] = df[column].astype(str).str.strip().str.title()
    return df


def clean_date_columns(df, columns):
    """Convert selected columns into datetime format."""
    for column in columns:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")
    return df


def clean_listings():
    logging.info("Cleaning listings data")

    listings = pd.read_csv(RAW_DIR / "listings.csv.gz", low_memory=False)

    if "price" in listings.columns:
        listings["price_clean"] = listings["price"].apply(clean_price)

    if "price_clean" in listings.columns:
        listings = listings[listings["price_clean"].ge(0) | listings["price_clean"].isna()]

    listings = clean_date_columns(
        listings,
        [
            "host_since",
            "first_review",
            "last_review",
            "calendar_last_scraped",
            "last_scraped",
        ],
    )

    for column in ["host_response_rate", "host_acceptance_rate"]:
        if column in listings.columns:
            listings[f"{column}_clean"] = listings[column].apply(clean_percentage)

    listings = clean_text_columns(
        listings,
        [
            "room_type",
            "property_type",
            "neighbourhood_cleansed",
        ],
    )

    if "latitude" in listings.columns and "longitude" in listings.columns:
        listings = listings[
            listings["latitude"].between(-90, 90)
            & listings["longitude"].between(-180, 180)
        ]

    if "host_since" in listings.columns:
        today = pd.Timestamp.today()
        listings["host_tenure_years"] = (
            (today - listings["host_since"]).dt.days / 365.25
        ).round(2)

    if "bedrooms" in listings.columns and "price_clean" in listings.columns:
        listings["price_per_bedroom"] = (
            listings["price_clean"] / listings["bedrooms"].replace(0, np.nan)
        )

    output_path = PROCESSED_DIR / "clean_listings.csv"
    listings.to_csv(output_path, index=False)

    logging.info("Saved cleaned listings data to %s", output_path)


def clean_calendar():
    logging.info("Cleaning calendar data")

    calendar = pd.read_csv(RAW_DIR / "calendar.csv.gz", low_memory=False)

    if "date" in calendar.columns:
        calendar["date"] = pd.to_datetime(calendar["date"], errors="coerce")
        calendar["day_of_week"] = calendar["date"].dt.day_name()
        calendar["is_weekend"] = calendar["day_of_week"].isin(["Saturday", "Sunday"])

    if "price" in calendar.columns:
        calendar["price_clean"] = calendar["price"].apply(clean_price)

    if "adjusted_price" in calendar.columns:
        calendar["adjusted_price_clean"] = calendar["adjusted_price"].apply(clean_price)

    if "available" in calendar.columns:
        calendar["available_bool"] = calendar["available"].map({"t": True, "f": False})

    output_path = PROCESSED_DIR / "clean_calendar.csv"
    calendar.to_csv(output_path, index=False)

    logging.info("Saved cleaned calendar data to %s", output_path)


def clean_reviews():
    logging.info("Cleaning reviews data")

    reviews = pd.read_csv(RAW_DIR / "reviews.csv.gz", low_memory=False)

    if "date" in reviews.columns:
        reviews["date"] = pd.to_datetime(reviews["date"], errors="coerce")

    output_path = PROCESSED_DIR / "clean_reviews.csv"
    reviews.to_csv(output_path, index=False)

    logging.info("Saved cleaned reviews data to %s", output_path)


def clean_neighbourhoods():
    logging.info("Cleaning neighbourhoods data")

    neighbourhoods = pd.read_csv(RAW_DIR / "neighbourhoods.csv", low_memory=False)

    for column in neighbourhoods.columns:
        if neighbourhoods[column].dtype == "object":
            neighbourhoods[column] = neighbourhoods[column].astype(str).str.strip().str.title()

    output_path = PROCESSED_DIR / "clean_neighbourhoods.csv"
    neighbourhoods.to_csv(output_path, index=False)

    logging.info("Saved cleaned neighbourhoods data to %s", output_path)


def main():
    clean_listings()
    clean_calendar()
    clean_reviews()
    clean_neighbourhoods()
    logging.info("Data cleaning pipeline completed successfully")


if __name__ == "__main__":
    main()