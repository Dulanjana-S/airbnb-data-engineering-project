from pathlib import Path
import pandas as pd


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")


def show_column_summary(df, column):
    print("-" * 80)
    print(f"Column: {column}")

    if column not in df.columns:
        print("Status: MISSING")
        return

    non_null_count = df[column].notna().sum()
    null_count = df[column].isna().sum()

    print(f"Data type: {df[column].dtype}")
    print(f"Non-null count: {non_null_count}")
    print(f"Null count: {null_count}")

    sample_values = df[column].dropna().head(10).to_list()
    print(f"Sample values: {sample_values}")

    numeric_values = pd.to_numeric(df[column], errors="coerce")
    valid_numeric_count = numeric_values.notna().sum()

    print(f"Valid numeric count: {valid_numeric_count}")

    if valid_numeric_count > 0:
        print(f"Minimum: {numeric_values.min()}")
        print(f"Median: {numeric_values.median()}")
        print(f"Mean: {numeric_values.mean()}")
        print(f"Maximum: {numeric_values.max()}")


def inspect_listings():
    print("=" * 80)
    print("RAW LISTINGS PRICE / REVENUE FIELDS")

    listings = pd.read_csv(RAW_DIR / "listings.csv.gz", low_memory=False)

    columns = [
        "price",
        "estimated_occupancy_l365d",
        "estimated_revenue_l365d",
        "availability_365",
        "room_type",
        "neighbourhood_cleansed",
    ]

    for column in columns:
        show_column_summary(listings, column)


def inspect_calendar():
    print("=" * 80)
    print("RAW CALENDAR PRICE FIELDS")

    calendar = pd.read_csv(RAW_DIR / "calendar.csv.gz", low_memory=False)

    columns = [
        "price",
        "adjusted_price",
        "available",
    ]

    for column in columns:
        show_column_summary(calendar, column)


def inspect_listing_master():
    print("=" * 80)
    print("PROCESSED LISTING MASTER FIELDS")

    listing_master = pd.read_csv(PROCESSED_DIR / "listing_master.csv", low_memory=False)

    columns = [
        "price_clean",
        "average_calendar_price",
        "median_calendar_price",
        "analysis_price",
        "estimated_annual_revenue",
        "room_type",
        "neighbourhood_cleansed",
    ]

    for column in columns:
        show_column_summary(listing_master, column)


def main():
    inspect_listings()
    inspect_calendar()
    inspect_listing_master()


if __name__ == "__main__":
    main()
