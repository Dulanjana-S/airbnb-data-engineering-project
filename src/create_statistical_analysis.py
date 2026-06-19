from pathlib import Path
import logging

import numpy as np
import pandas as pd
from scipy import stats


PROCESSED_DIR = Path("data/processed")
OUTPUT_DIR = Path("reports/statistical_outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def to_numeric(series):
    return pd.to_numeric(series, errors="coerce")


def rank_biserial_effect_size(u_statistic, n1, n2):
    if n1 == 0 or n2 == 0:
        return np.nan
    return round((2 * u_statistic) / (n1 * n2) - 1, 4)


def create_skipped_result(hypothesis, reason):
    return {
        "hypothesis": hypothesis,
        "test_used": "Not run",
        "status": "Skipped",
        "null_hypothesis": "",
        "alternative_hypothesis": "",
        "sample_size_group_1": 0,
        "sample_size_group_2": 0,
        "test_statistic": np.nan,
        "p_value": np.nan,
        "effect_size": np.nan,
        "business_interpretation": reason,
    }


def mann_whitney_test(group_a, group_b):
    group_a = group_a.dropna()
    group_b = group_b.dropna()

    if len(group_a) < 2 or len(group_b) < 2:
        return None

    statistic, p_value = stats.mannwhitneyu(
        group_a,
        group_b,
        alternative="two-sided",
    )

    effect_size = rank_biserial_effect_size(
        statistic,
        len(group_a),
        len(group_b),
    )

    return statistic, p_value, effect_size, len(group_a), len(group_b)


def test_entire_home_vs_private_room_availability(listing_master):
    hypothesis = "H1: Entire-home listings have different annual availability than private rooms"

    required_columns = {"room_type", "availability_365"}
    if not required_columns.issubset(listing_master.columns):
        return create_skipped_result(
            hypothesis,
            "Required columns were not available for this test.",
        )

    room_type_normalised = listing_master["room_type"].astype(str).str.lower().str.strip()

    entire_home = listing_master.loc[
        room_type_normalised.str.contains("entire home", na=False),
        "availability_365",
    ]

    private_room = listing_master.loc[
        room_type_normalised.str.contains("private room", na=False),
        "availability_365",
    ]

    result = mann_whitney_test(entire_home, private_room)

    if result is None:
        return create_skipped_result(
            hypothesis,
            "The test was skipped because one or both room-type groups had fewer than two valid availability records.",
        )

    statistic, p_value, effect_size, n1, n2 = result

    return {
        "hypothesis": hypothesis,
        "test_used": "Mann-Whitney U test",
        "status": "Completed",
        "null_hypothesis": "There is no annual availability distribution difference between entire-home listings and private rooms.",
        "alternative_hypothesis": "There is an annual availability distribution difference between entire-home listings and private rooms.",
        "sample_size_group_1": n1,
        "sample_size_group_2": n2,
        "test_statistic": round(statistic, 4),
        "p_value": round(p_value, 6),
        "effect_size": effect_size,
        "business_interpretation": "This tests whether different accommodation types behave differently in terms of yearly availability. A significant result suggests supply strategy differs by room type.",
    }


def test_superhost_vs_non_superhost_review_scores(listing_master):
    hypothesis = "H2: Superhost listings have different review scores than non-superhost listings"

    required_columns = {"host_is_superhost", "review_scores_rating"}
    if not required_columns.issubset(listing_master.columns):
        return create_skipped_result(
            hypothesis,
            "Required columns were not available for this test.",
        )

    superhost_flag = listing_master["host_is_superhost"].astype(str).str.lower().str.strip()

    superhost = listing_master.loc[
        superhost_flag.isin(["t", "true", "1", "yes"]),
        "review_scores_rating",
    ]

    non_superhost = listing_master.loc[
        superhost_flag.isin(["f", "false", "0", "no"]),
        "review_scores_rating",
    ]

    result = mann_whitney_test(superhost, non_superhost)

    if result is None:
        return create_skipped_result(
            hypothesis,
            "The test was skipped because one or both superhost groups had fewer than two valid review score records.",
        )

    statistic, p_value, effect_size, n1, n2 = result

    return {
        "hypothesis": hypothesis,
        "test_used": "Mann-Whitney U test",
        "status": "Completed",
        "null_hypothesis": "There is no review score distribution difference between superhost and non-superhost listings.",
        "alternative_hypothesis": "There is a review score distribution difference between superhost and non-superhost listings.",
        "sample_size_group_1": n1,
        "sample_size_group_2": n2,
        "test_statistic": round(statistic, 4),
        "p_value": round(p_value, 6),
        "effect_size": effect_size,
        "business_interpretation": "This tests whether superhost status is associated with guest satisfaction. A significant result suggests superhost status may be a useful quality signal.",
    }


def test_neighbourhood_availability_differences(listing_master):
    hypothesis = "H3: Annual availability differs across neighbourhoods"

    required_columns = {"neighbourhood_cleansed", "availability_365"}
    if not required_columns.issubset(listing_master.columns):
        return create_skipped_result(
            hypothesis,
            "Required columns were not available for this test.",
        )

    filtered_data = listing_master.dropna(
        subset=["neighbourhood_cleansed", "availability_365"]
    ).copy()

    neighbourhood_counts = filtered_data["neighbourhood_cleansed"].value_counts()
    eligible_neighbourhoods = neighbourhood_counts[neighbourhood_counts >= 30].index

    neighbourhood_groups = []

    for _, group in filtered_data[
        filtered_data["neighbourhood_cleansed"].isin(eligible_neighbourhoods)
    ].groupby("neighbourhood_cleansed"):
        values = group["availability_365"].dropna()
        if len(values) >= 30:
            neighbourhood_groups.append(values)

    if len(neighbourhood_groups) < 2:
        return create_skipped_result(
            hypothesis,
            "The test was skipped because fewer than two neighbourhoods had enough valid availability records.",
        )

    statistic, p_value = stats.kruskal(*neighbourhood_groups)

    n = sum(len(group) for group in neighbourhood_groups)
    k = len(neighbourhood_groups)
    effect_size = round((statistic - k + 1) / (n - k), 4) if n > k else np.nan

    return {
        "hypothesis": hypothesis,
        "test_used": "Kruskal-Wallis test",
        "status": "Completed",
        "null_hypothesis": "Annual availability distributions are the same across neighbourhoods.",
        "alternative_hypothesis": "At least one neighbourhood has a different annual availability distribution.",
        "sample_size_group_1": n,
        "sample_size_group_2": k,
        "test_statistic": round(statistic, 4),
        "p_value": round(p_value, 6),
        "effect_size": effect_size,
        "business_interpretation": "This tests whether supply availability patterns differ by location. A significant result suggests neighbourhood-level market monitoring is needed.",
    }


def test_weekend_vs_weekday_availability(calendar):
    hypothesis = "H4: Weekend availability differs from weekday availability"

    required_columns = {"is_weekend", "available_bool"}
    if not required_columns.issubset(calendar.columns):
        return create_skipped_result(
            hypothesis,
            "Required columns were not available for this test.",
        )

    weekend_flag = calendar["is_weekend"].astype(str).str.lower().str.strip()
    available_numeric = calendar["available_bool"].astype(str).str.lower().map(
        {
            "true": 1,
            "false": 0,
            "1": 1,
            "0": 0,
            "t": 1,
            "f": 0,
        }
    )

    weekend_values = available_numeric[weekend_flag.isin(["true", "1", "yes"])]
    weekday_values = available_numeric[weekend_flag.isin(["false", "0", "no"])]

    result = mann_whitney_test(weekend_values, weekday_values)

    if result is None:
        return create_skipped_result(
            hypothesis,
            "The test was skipped because weekend or weekday records had insufficient valid availability values.",
        )

    statistic, p_value, effect_size, n1, n2 = result

    return {
        "hypothesis": hypothesis,
        "test_used": "Mann-Whitney U test",
        "status": "Completed",
        "null_hypothesis": "Weekend and weekday availability distributions are the same.",
        "alternative_hypothesis": "Weekend and weekday availability distributions are different.",
        "sample_size_group_1": n1,
        "sample_size_group_2": n2,
        "test_statistic": round(statistic, 4),
        "p_value": round(p_value, 6),
        "effect_size": effect_size,
        "business_interpretation": "This tests whether availability patterns differ between weekends and weekdays. A significant result may indicate seasonal or demand-driven booking behaviour.",
    }


def save_results(results):
    output_path = OUTPUT_DIR / "statistical_tests_summary.csv"
    pd.DataFrame(results).to_csv(output_path, index=False)
    logging.info("Saved statistical results to %s", output_path)


def main():
    logging.info("Loading processed datasets")

    listing_master = pd.read_csv(PROCESSED_DIR / "listing_master.csv", low_memory=False)
    calendar = pd.read_csv(PROCESSED_DIR / "clean_calendar.csv", low_memory=False)

    for column in [
        "availability_365",
        "review_scores_rating",
        "number_of_reviews",
        "reviews_per_month",
    ]:
        if column in listing_master.columns:
            listing_master[column] = to_numeric(listing_master[column])

    results = [
        test_entire_home_vs_private_room_availability(listing_master),
        test_superhost_vs_non_superhost_review_scores(listing_master),
        test_neighbourhood_availability_differences(listing_master),
        test_weekend_vs_weekday_availability(calendar),
    ]

    save_results(results)
    logging.info("Statistical analysis outputs created")


if __name__ == "__main__":
    main()