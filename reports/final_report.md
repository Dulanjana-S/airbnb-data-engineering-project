# Airbnb Melbourne Data Engineering and Market Analysis Report

## 1. Executive Summary

This project analyses the Melbourne, Victoria, Australia Airbnb market using public data from Inside Airbnb.

The objective was to build a reproducible data engineering and analytics workflow that transforms raw Airbnb files into cleaned, profiled, and analytics-ready outputs. The project includes dataset familiarisation, data profiling, cleaning, an enriched listing master table, an analytical DuckDB database, SQL analysis, exploratory data analysis, and statistical testing.

The project intentionally focuses on one city to prioritise depth, code quality, reproducibility, and clear business interpretation.

Key outputs include:

* Data quality report
* Cleaned listings, calendar, reviews, and neighbourhood datasets
* Enriched listing master table
* DuckDB analytical database
* SQL analysis outputs
* EDA summary tables and figures
* Statistical testing summary
* Assumptions and decision log
* AI usage disclosure

## 2. Objectives and Scope

### 2.1 Objectives

The main objectives of this project were to:

* Understand the Inside Airbnb Melbourne dataset
* Profile raw data quality
* Clean and standardise key fields
* Create an enriched listing-level analytical dataset
* Build a simple analytical database model
* Run SQL-based business analysis
* Generate EDA outputs and visualisations
* Apply basic statistical testing to support analytical findings
* Document assumptions, limitations, and technical decisions clearly

### 2.2 Scope

This project focuses on one city:

**Melbourne, Victoria, Australia**

A single-city scope was selected because the assignment values depth and quality over attempting every possible task superficially.

### 2.3 Out of Scope

The following items were intentionally not completed:

* Multi-city comparison
* Machine learning price prediction
* LLM-based review analysis
* Cloud deployment
* Dashboard deployment
* Docker containerisation

These items were deprioritised to focus on core data engineering, reproducibility, EDA, and statistical analysis.

## 3. Dataset Overview

### 3.1 Dataset Source

The dataset was sourced from Inside Airbnb.

Files used:

* `listings.csv.gz`
* `calendar.csv.gz`
* `reviews.csv.gz`
* `neighbourhoods.csv`
* `neighbourhoods.geojson`

### 3.2 Main Entities

The main entities in the dataset are:

* **Listings:** Airbnb properties available in the Melbourne market.
* **Hosts:** People or organisations managing one or more listings.
* **Calendar records:** Daily availability and price records for each listing.
* **Reviews:** Guest review records linked to listings.
* **Neighbourhoods:** Geographic groupings used for location-based analysis.

### 3.3 Key Relationships

The main dataset relationships are:

```text
listings.id = calendar.listing_id
listings.id = reviews.listing_id
listings.neighbourhood_cleansed = neighbourhoods.neighbourhood
listings.host_id identifies hosts
```

### 3.4 Dataset Limitations

Important limitations include:

* Public Airbnb data is scraped and may contain missing or inconsistent values.
* Calendar unavailable days may not always represent booked days.
* Estimated revenue is approximate and should not be treated as confirmed host revenue.
* Review frequency is only a proxy for demand.
* The analysis is based on one snapshot of the market, not complete historical market behaviour.

## 4. Methodology

The project followed a structured data engineering workflow:

1. Raw data validation
2. Data profiling
3. Cleaning and standardisation
4. Feature derivation
5. Dataset enrichment
6. Analytical database modelling
7. SQL analysis
8. Exploratory data analysis
9. Statistical testing
10. Documentation and reporting

## 5. Engineering Approach

### 5.1 Pipeline Design

The project uses a repeatable Python pipeline controlled by:

```bash
python src/run_pipeline.py
```

The pipeline runs the following scripts:

1. `check_data.py`
2. `profile_data.py`
3. `clean_data.py`
4. `build_master_table.py`
5. `build_database.py`
6. `run_sql_analysis.py`
7. `create_eda_outputs.py`
8. `create_statistical_analysis.py`

### 5.2 Data Cleaning

Cleaning steps included:

* Converting price values into numeric format
* Parsing date fields
* Converting percentage fields into decimal format
* Standardising text fields
* Validating latitude and longitude values
* Creating calculated fields such as host tenure and price per bedroom
* Creating calendar-based weekend and weekday indicators

### 5.3 Enriched Listing Master Table

The enriched `listing_master` table combines listing attributes with calendar and review summaries.

Derived fields include:

* `average_calendar_price`
* `median_calendar_price`
* `available_days`
* `unavailable_days`
* `occupancy_rate_estimate`
* `estimated_annual_revenue`
* `review_frequency_per_month`
* `median_price_neighbourhood`
* `listing_count_neighbourhood`

### 5.4 Analytical Database

DuckDB was used as the analytical database.

Created tables include:

* `listing_master`
* `clean_calendar`
* `clean_reviews`
* `dim_host`
* `dim_neighbourhood`
* `dim_room_type`
* `dim_date`
* `fact_listing`
* `fact_calendar_daily`
* `fact_reviews`

This provides a simple analytical star-schema style model for querying listing, calendar, and review behaviour.

## 6. Data Quality Findings

A data profiling report was generated at:

```text
reports/data_quality_report.csv
```

The report includes:

* Dataset name
* Row count
* Column count
* Column data type
* Missing value count
* Missing value percentage
* Unique value count
* Sample values

Key data quality observations should be added here after reviewing `reports/data_quality_report.csv`.

## 7. SQL Analysis Findings

SQL analysis outputs were generated in:

```text
reports/sql_outputs/
```

The SQL queries analyse:

* Average and median price by room type
* Top neighbourhoods by median price
* Estimated annual revenue by neighbourhood
* Superhost versus non-superhost review scores
* Weekend versus weekday calendar prices
* Host concentration
* Price and review relationship by room type

Key SQL findings should be added here after reviewing the output CSV files.

## 8. Exploratory Data Analysis Findings

EDA outputs were generated in:

```text
reports/eda_outputs/
reports/figures/
```

Generated figures include:

* Price distribution
* Median price by room type
* Top neighbourhoods by median price
* Review score distribution
* Monthly availability rate
* Price versus number of reviews

### 8.1 Price Distribution

Figure: `reports/figures/price_distribution.png`

Business interpretation:

The price distribution helps identify the typical price range in the Melbourne Airbnb market and highlights the presence of high-price outliers. This is important for pricing strategy because average prices may be distorted by luxury or unusually expensive listings.

### 8.2 Price by Room Type

Figure: `reports/figures/median_price_by_room_type.png`

Business interpretation:

Room type is expected to be a major price driver. Entire homes usually provide more private space and therefore tend to command higher prices than private or shared rooms.

### 8.3 Neighbourhood Price Differences

Figure: `reports/figures/top_neighbourhoods_by_median_price.png`

Business interpretation:

Neighbourhood-level pricing differences suggest that location is important for benchmarking. Hosts, investors, and market analysts should avoid using a single city-wide average price when evaluating listing performance.

### 8.4 Review Score Distribution

Figure: `reports/figures/review_score_distribution.png`

Business interpretation:

Review score distribution helps assess customer satisfaction patterns. If scores are concentrated near the top end, this may indicate rating inflation, where small score differences still matter commercially.

### 8.5 Monthly Availability

Figure: `reports/figures/monthly_availability_rate.png`

Business interpretation:

Monthly availability patterns help identify possible seasonal demand changes. Lower availability may suggest stronger demand or more host-blocked dates, while higher availability may indicate weaker demand or excess supply.

### 8.6 Price Versus Number of Reviews

Figure: `reports/figures/price_vs_number_of_reviews.png`

Business interpretation:

The relationship between price and number of reviews helps evaluate whether lower-priced listings receive more booking activity or whether premium listings can still maintain strong demand.

## 9. Statistical Findings

Statistical outputs were generated at:

```text
reports/statistical_outputs/statistical_tests_summary.csv
```

The statistical analysis tested:

* Whether entire-home listings differ in price from private rooms
* Whether superhost listings differ in review scores from non-superhost listings
* Whether prices differ across neighbourhoods
* Whether weekend prices differ from weekday prices

Non-parametric tests were used because Airbnb price data is commonly skewed and may contain outliers.

The results should be interpreted as evidence of association, not causation.

## 10. Business Recommendations

Based on the completed engineering and analytical workflow, the following recommendations are proposed:

### Recommendation 1: Benchmark Prices by Room Type

Room type should be treated as a core pricing category because different accommodation types serve different customer needs and price points.

### Recommendation 2: Use Neighbourhood-Level Benchmarks

Neighbourhood-level pricing analysis provides more useful market insight than a single city-wide average.

### Recommendation 3: Treat Revenue Estimates Carefully

Estimated revenue should be used as a directional indicator only because calendar unavailable days may not always represent confirmed bookings.

### Recommendation 4: Monitor Host Concentration

Host concentration analysis can help identify professional operators and understand whether supply is controlled by many casual hosts or fewer high-volume hosts.

### Recommendation 5: Combine Quantitative Results with Business Context

Statistical significance should be interpreted alongside effect size, market context, and practical business value.

## 11. Assumptions and Decision Log

The full assumptions and decision log are documented in:

```text
reports/decision_log.md
```

Major decisions include:

* Selecting one city for depth
* Using Python for pipeline development
* Using DuckDB for local analytical modelling
* Excluding raw data from Git
* Including report outputs for reviewer evidence
* Using non-parametric statistical tests

## 12. Limitations and Caveats

Important limitations include:

* The project analyses only Melbourne.
* The dataset is a public scraped snapshot and may contain missing or inconsistent values.
* Calendar unavailable days are only an occupancy proxy.
* Estimated revenue is approximate.
* Statistical tests do not prove causation.
* Machine learning and AI experiments were not completed due to prioritisation.

## 13. Future Improvements

With more time, the project could be extended by:

* Adding multiple cities for cross-market comparison
* Building a Streamlit dashboard
* Adding Docker for reproducibility
* Implementing dbt models and tests
* Adding machine learning price prediction
* Running NLP sentiment analysis on review text
* Deploying the pipeline to a cloud platform
* Adding automated data quality tests

## 14. Reflection

This project was scoped to prioritise core data engineering and analytical quality.

The main trade-off was choosing depth over breadth. Instead of attempting every optional section, the project focused on building a reproducible pipeline, clean outputs, SQL analysis, EDA, and statistical testing.

The most important learning was that real-world public datasets require careful profiling, cleaning, assumptions, and documentation before reliable analysis can be performed.

## Appendix A. AI Usage Disclosure

The AI usage disclosure is documented in:

```text
reports/ai_usage_disclosure.md
```

AI assistance was used for project planning, code structure guidance, debugging support, README drafting, and report structure guidance. All outputs were reviewed, executed, and validated locally.
