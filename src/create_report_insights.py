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


def build_room_type_insight():
    df = read_csv_if_exists(SQL_OUTPUTS_DIR / "query_01_output.csv")
    top_row = get_first_row(df)

    if top_row is None:
        return "Room type pricing results were not available."

    room_type = top_row.get("room_type", "not available")
    median_price = format_number(top_row.get("median_price"))
    average_price = format_number(top_row.get("average_price"))
    listing_count = format_number(top_row.get("listing_count"), 0)

    return (
        f"The highest median price room type was **{room_type}**, "
        f"with a median price of **{median_price}** and an average price of "
        f"**{average_price}** across **{listing_count}** listings. "
        "This supports the view that room type is a major pricing driver and "
        "should be used as a core benchmark category."
    )


def build_neighbourhood_price_insight():
    df = read_csv_if_exists(SQL_OUTPUTS_DIR / "query_02_output.csv")
    top_row = get_first_row(df)

    if top_row is None:
        return "Neighbourhood price results were not available."

    neighbourhood = top_row.get("neighbourhood_cleansed", "not available")
    median_price = format_number(top_row.get("median_price"))
    listing_count = format_number(top_row.get("listing_count"), 0)

    return (
        f"The neighbourhood with the highest median price among neighbourhoods "
        f"with sufficient listing volume was **{neighbourhood}**, with a median "
        f"price of **{median_price}** across **{listing_count}** listings. "
        "This indicates that location has a strong relationship with pricing, "
        "and city-wide averages may hide important local market differences."
    )


def build_revenue_insight():
    df = read_csv_if_exists(SQL_OUTPUTS_DIR / "query_03_output.csv")
    top_row = get_first_row(df)

    if top_row is None:
        return "Estimated revenue results were not available."

    neighbourhood = top_row.get("neighbourhood_cleansed", "not available")
    revenue = format_number(top_row.get("total_estimated_revenue"))
    occupancy = format_number(top_row.get("average_occupancy_rate"), 4)

    return (
        f"The neighbourhood with the highest estimated annual revenue contribution "
        f"was **{neighbourhood}**, with estimated annual revenue of **{revenue}** "
        f"and an average occupancy-rate proxy of **{occupancy}**. "
        "This should be interpreted as a directional market signal because calendar "
        "unavailable days may include bookings, blocked dates, or host-disabled dates."
    )


def build_weekend_price_insight():
    df = read_csv_if_exists(SQL_OUTPUTS_DIR / "query_05_output.csv")

    if df.empty or "is_weekend" not in df.columns:
        return "Weekend and weekday pricing results were not available."

    return (
        "Weekend and weekday calendar pricing was analysed to identify whether "
        "hosts use day-of-week pricing strategies. The output is available in "
        "`reports/sql_outputs/query_05_output.csv` and should be interpreted "
        "alongside the statistical test results."
    )


def build_host_concentration_insight():
    df = read_csv_if_exists(SQL_OUTPUTS_DIR / "query_06_output.csv")
    top_row = get_first_row(df)

    if top_row is None:
        return "Host concentration results were not available."

    host_name = top_row.get("host_name", "not available")
    listing_count = format_number(top_row.get("listing_count"), 0)
    revenue = format_number(top_row.get("total_estimated_revenue"))

    return (
        f"The largest host by listing count was **{host_name}**, managing "
        f"**{listing_count}** listings in the analysed dataset. The same host had "
        f"estimated annual revenue of **{revenue}**. This suggests that host "
        "concentration is an important supply-side feature to monitor."
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
                f"The p-value was **{format_number(p_value, 6)}** and the effect "
                f"size was **{format_number(effect_size, 4)}**. {interpretation}"
            )
        else:
            line = (
                f"- **{hypothesis}** was skipped. Reason: {interpretation}"
            )

        lines.append(line)

    return "\n".join(lines)


def build_markdown_report():
    content = f"""# Actual Report Insights

This file summarises the actual generated project outputs and can be used to update `reports/final_report.md`.

## Room Type Pricing

{build_room_type_insight()}

## Neighbourhood Pricing

{build_neighbourhood_price_insight()}

## Estimated Revenue

{build_revenue_insight()}

## Weekend vs Weekday Pricing

{build_weekend_price_insight()}

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