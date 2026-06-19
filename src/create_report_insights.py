from pathlib import Path
import logging

import pandas as pd


REPORTS_DIR = Path("reports")
SQL_OUTPUTS_DIR = REPORTS_DIR / "sql_outputs"
EDA_OUTPUTS_DIR = REPORTS_DIR / "eda_outputs"
STAT_OUTPUTS_DIR = REPORTS_DIR / "statistical_outputs"

OUTPUT_PATH = REPORTS_DIR / "report_insights.md"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def read_csv_if_exists(path):
    if not path.exists():
        logging.warning("File not found: %s", path)
        return pd.DataFrame()

    return pd.read_csv(path)


def format_number(value, decimals=2):
    if pd.isna(value):
        return "not available"

    try:
        return f"{float(value):,.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)


def get_first_row(df):
    if df.empty:
        return None

    return df.iloc[0].to_dict()


def build_room_type_supply_insight():
    df = read_csv_if_exists(SQL_OUTPUTS_DIR / "query_01_output.csv")
    top_row = get_first_row(df)

    if top_row is None:
        return "Room type supply results were not available."

    room_type = top_row.get("room_type", "not available")
    listing_count = format_number(top_row.get("listing_count"), 0)
    average_availability = format_number(top_row.get("average_availability_365"))
    average_reviews = format_number(top_row.get("average_number_of_reviews"))

    return (
        f"The largest room type category was **{room_type}**, with **{listing_count}** listings. "
        f"This category had an average annual availability of **{average_availability}** days "
        f"and an average of **{average_reviews}** reviews per listing. This indicates that the "
        "Melbourne Airbnb market is strongly shaped by entire-home/apartment supply rather than "
        "shared accommodation."
    )


def build_neighbourhood_supply_insight():
    df = read_csv_if_exists(SQL_OUTPUTS_DIR / "query_02_output.csv")
    top_row = get_first_row(df)

    if top_row is None:
        return "Neighbourhood supply results were not available."

    neighbourhood = top_row.get("neighbourhood_cleansed", "not available")
    listing_count = format_number(top_row.get("listing_count"), 0)
    average_availability = format_number(top_row.get("average_availability_365"))
    average_reviews = format_number(top_row.get("average_number_of_reviews"))

    return (
        f"The neighbourhood with the highest listing count was **{neighbourhood}**, "
        f"with **{listing_count}** listings. Its average annual availability was "
        f"**{average_availability}** days and the average number of reviews was "
        f"**{average_reviews}**. This suggests that neighbourhood-level supply concentration "
        "is important for market monitoring and operational planning."
    )


def build_occupancy_insight():
    df = read_csv_if_exists(SQL_OUTPUTS_DIR / "query_03_output.csv")
    top_row = get_first_row(df)

    if top_row is None:
        return "Estimated occupancy results were not available."

    neighbourhood = top_row.get("neighbourhood_cleansed", "not available")
    listing_count = format_number(top_row.get("listing_count"), 0)
    occupancy = format_number(top_row.get("average_occupancy_rate_estimate"), 4)
    availability = format_number(top_row.get("average_availability_365"))

    return (
        f"The neighbourhood with the highest estimated occupancy-rate proxy was "
        f"**{neighbourhood}**, based on **{listing_count}** listings. Its average "
        f"occupancy-rate estimate was **{occupancy}**, while average annual availability "
        f"was **{availability}** days. This should be treated as a proxy because calendar "
        "unavailability may represent bookings, blocked dates, or host-disabled dates."
    )


def build_weekend_availability_insight():
    df = read_csv_if_exists(SQL_OUTPUTS_DIR / "query_05_output.csv")

    if df.empty or "is_weekend" not in df.columns:
        return "Weekend and weekday availability results were not available."

    return (
        "Weekend and weekday availability was analysed using calendar availability records. "
        "The output is available in `reports/sql_outputs/query_05_output.csv`. This helps "
        "identify whether listings are more or less available on weekends compared with weekdays."
    )


def build_host_concentration_insight():
    df = read_csv_if_exists(SQL_OUTPUTS_DIR / "query_06_output.csv")
    top_row = get_first_row(df)

    if top_row is None:
        return "Host concentration results were not available."

    host_name = top_row.get("host_name", "not available")
    listing_count = format_number(top_row.get("listing_count"), 0)
    average_availability = format_number(top_row.get("average_availability_365"))
    average_reviews = format_number(top_row.get("average_number_of_reviews"))

    return (
        f"The largest host by listing count was **{host_name}**, managing "
        f"**{listing_count}** listings. This host had average annual availability of "
        f"**{average_availability}** days and average reviews per listing of "
        f"**{average_reviews}**. This suggests that host concentration is an important "
        "supply-side feature to monitor."
    )


def build_statistical_summary():
    df = read_csv_if_exists(STAT_OUTPUTS_DIR / "statistical_tests_summary.csv")

    if df.empty:
        return "Statistical test results were not available."

    lines = []

    for _, row in df.iterrows():
        hypothesis = row.get("hypothesis", "Unnamed hypothesis")
        status = row.get("status", "Unknown")
        test_used = row.get("test_used", "Not available")
        p_value = row.get("p_value", "")
        effect_size = row.get("effect_size", "")
        interpretation = row.get("business_interpretation", "")

        if status == "Completed":
            line = (
                f"- **{hypothesis}** was completed using the **{test_used}**. "
                f"The p-value was **{format_number(p_value, 6)}** and the effect size "
                f"was **{format_number(effect_size, 4)}**. {interpretation}"
            )
        else:
            line = f"- **{hypothesis}** was skipped. Reason: {interpretation}"

        lines.append(line)

    return "\n".join(lines)


def build_markdown_report():
    content = f"""# Actual Report Insights

This file summarises the actual generated project outputs and can be used to update `reports/final_report.md`.

## Dataset Limitation: Price Fields

The Melbourne Inside Airbnb files used in this project did not contain usable price values. The `price` field in the detailed listings file, the summary listings file, and the calendar file contained no non-null values. For this reason, the final analysis focuses on supply, availability, host concentration, review behaviour, neighbourhood patterns, and quality signals rather than price or revenue.

## Room Type Supply

{build_room_type_supply_insight()}

## Neighbourhood Supply

{build_neighbourhood_supply_insight()}

## Estimated Occupancy Proxy

{build_occupancy_insight()}

## Weekend vs Weekday Availability

{build_weekend_availability_insight()}

## Host Concentration

{build_host_concentration_insight()}

## Statistical Test Summary

{build_statistical_summary()}

## Output Files Reviewed

- `reports/sql_outputs/query_01_output.csv`
- `reports/sql_outputs/query_02_output.csv`
- `reports/sql_outputs/query_03_output.csv`
- `reports/sql_outputs/query_05_output.csv`
- `reports/sql_outputs/query_06_output.csv`
- `reports/statistical_outputs/statistical_tests_summary.csv`
"""

    OUTPUT_PATH.write_text(content, encoding="utf-8")
    logging.info("Saved report insights to %s", OUTPUT_PATH)


def main():
    build_markdown_report()


if __name__ == "__main__":
    main()