from pathlib import Path
import logging

import duckdb


PROCESSED_DIR = Path("data/processed")
DATABASE_DIR = Path("data/database")
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "airbnb_melbourne.duckdb"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def csv_path(filename):
    return (PROCESSED_DIR / filename).as_posix()


def build_database():
    logging.info("Creating DuckDB database at %s", DATABASE_PATH)

    connection = duckdb.connect(str(DATABASE_PATH))

    connection.execute(
        f"""
        CREATE OR REPLACE TABLE listing_master AS
        SELECT *
        FROM read_csv_auto('{csv_path("listing_master.csv")}', header = true);
        """
    )

    connection.execute(
        f"""
        CREATE OR REPLACE TABLE clean_calendar AS
        SELECT *
        FROM read_csv_auto('{csv_path("clean_calendar.csv")}', header = true);
        """
    )

    connection.execute(
        f"""
        CREATE OR REPLACE TABLE clean_reviews AS
        SELECT *
        FROM read_csv_auto('{csv_path("clean_reviews.csv")}', header = true);
        """
    )

    connection.execute(
        """
        CREATE OR REPLACE TABLE dim_host AS
        SELECT DISTINCT
            host_id,
            host_name,
            host_since,
            host_is_superhost,
            host_response_rate_clean,
            host_acceptance_rate_clean,
            host_tenure_years
        FROM listing_master
        WHERE host_id IS NOT NULL;
        """
    )

    connection.execute(
        """
        CREATE OR REPLACE TABLE dim_neighbourhood AS
        SELECT DISTINCT
            neighbourhood_cleansed,
            listing_count_neighbourhood,
            median_price_neighbourhood,
            average_price_neighbourhood,
            average_rating_neighbourhood
        FROM listing_master
        WHERE neighbourhood_cleansed IS NOT NULL;
        """
    )

    connection.execute(
        """
        CREATE OR REPLACE TABLE dim_room_type AS
        SELECT DISTINCT
            room_type
        FROM listing_master
        WHERE room_type IS NOT NULL;
        """
    )

    connection.execute(
        """
        CREATE OR REPLACE TABLE dim_date AS
        SELECT DISTINCT
            date,
            day_of_week,
            is_weekend
        FROM clean_calendar
        WHERE date IS NOT NULL;
        """
    )

    connection.execute(
        """
        CREATE OR REPLACE TABLE fact_listing AS
        SELECT
            id AS listing_id,
            host_id,
            neighbourhood_cleansed,
            room_type,
            analysis_price,
            property_type,
            accommodates,
            bedrooms,
            beds,
            price_clean,
            price_per_bedroom,
            minimum_nights,
            maximum_nights,
            availability_365,
            number_of_reviews,
            review_scores_rating,
            review_scores_cleanliness,
            review_scores_location,
            review_scores_communication,
            reviews_per_month,
            total_calendar_days,
            available_days,
            unavailable_days,
            occupancy_rate_estimate,
            estimated_annual_revenue,
            total_reviews_from_reviews_file,
            review_frequency_per_month
        FROM listing_master;
        """
    )

    connection.execute(
        """
        CREATE OR REPLACE TABLE fact_calendar_daily AS
        SELECT
            listing_id,
            date,
            available_bool,
            price_clean,
            adjusted_price_clean,
            minimum_nights,
            maximum_nights
        FROM clean_calendar;
        """
    )

    connection.execute(
        """
        CREATE OR REPLACE TABLE fact_reviews AS
        SELECT
            listing_id,
            id AS review_id,
            date,
            reviewer_id,
            reviewer_name,
            comments
        FROM clean_reviews;
        """
    )

    tables = connection.execute("SHOW TABLES").fetchdf()
    logging.info("Created database tables:\n%s", tables)

    connection.close()


def main():
    build_database()


if __name__ == "__main__":
    main()