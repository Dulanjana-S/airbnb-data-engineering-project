# Airbnb Melbourne Data Engineering and Market Analysis Report

## Table of Contents

1. Executive Summary  
2. Objectives and Scope  
3. Dataset Overview  
4. Methodology  
5. Engineering Approach  
6. Data Quality Findings  
7. SQL Analysis Findings  
8. Exploratory Data Analysis Findings  
9. Statistical Findings  
10. Business Recommendations  
11. Assumptions and Decision Log  
12. Limitations and Caveats  
13. Future Improvements  
14. Reflection  
Appendix A. AI Usage Disclosure  
Appendix B. Figure Gallery  
Appendix C. SQL Output Tables  
Appendix D. EDA Output Tables  
Appendix E. Statistical Output Tables  

## 1. Executive Summary

This project analyses the Melbourne, Victoria, Australia Airbnb market using public data from Inside Airbnb.

The objective was to build a reproducible data engineering and analytics workflow that transforms raw Airbnb files into cleaned, profiled, and analytics-ready outputs. The project includes dataset familiarisation, data profiling, cleaning, an enriched listing master table, an analytical DuckDB database, SQL analysis, exploratory data analysis, and statistical testing.

A key dataset limitation was identified during profiling: the Melbourne Inside Airbnb files used in this project did not contain usable price values. The `price` field in the detailed listings file, the summary listings file, and the calendar file contained no non-null values. For this reason, the final analysis focuses on supply, availability, host concentration, review behaviour, neighbourhood patterns, and quality signals rather than price or revenue.

Key findings include:

* Entire homes/apartments dominate Melbourne Airbnb supply, with 17,703 listings.
* Private rooms represent the second-largest room type, with 6,563 listings.
* The Melbourne neighbourhood has the highest listing count, with 7,832 listings.
* Darebin has the highest estimated occupancy-rate proxy, at 0.7066.
* Flexistayz is the largest host by listing count, managing 292 listings.
* Superhost status is statistically associated with different review score distributions.
* Availability patterns differ across room types, neighbourhoods, and weekend/weekday calendar records.

The project intentionally focuses on one city to prioritise depth, code quality, reproducibility, and clear business interpretation.

## 2. Objectives and Scope

### 2.1 Objectives

The main objectives of this project were to:

* Understand the Inside Airbnb Melbourne dataset.
* Profile raw data quality.
* Clean and standardise key fields.
* Create an enriched listing-level analytical dataset.
* Build a simple analytical database model.
* Run SQL-based business analysis.
* Generate EDA outputs and visualisations.
* Apply statistical testing to support analytical findings.
* Document assumptions, limitations, and technical decisions clearly.

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

These items were deprioritised to focus on core data engineering, reproducibility, EDA, statistical analysis, and clear documentation.

## 3. Dataset Overview

### 3.1 Dataset Source

The dataset was sourced from Inside Airbnb.

Files used:

* `listings.csv.gz`
* `listings.csv`
* `calendar.csv.gz`
* `reviews.csv.gz`
* `neighbourhoods.csv`
* `neighbourhoods.geojson`

### 3.2 Main Entities

The main entities in the dataset are:

* **Listings:** Airbnb properties available in the Melbourne market.
* **Hosts:** People or organisations managing one or more listings.
* **Calendar records:** Daily availability records for each listing.
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

### 3.4 Dataset Limitation: Missing Price Values

During profiling, the Melbourne dataset was found to have no usable price data in the relevant files:

* `listings.csv.gz` price values were fully missing.
* `listings.csv` price values were fully missing.
* `calendar.csv.gz` price and adjusted price values were fully missing.

Because of this limitation, price and revenue analysis were excluded from the final analytical findings. This decision avoids producing unsupported or misleading conclusions.

The final analysis therefore focuses on:

* Listing supply
* Annual availability
* Calendar availability
* Review behaviour
* Review scores
* Host concentration
* Neighbourhood-level supply patterns
* Superhost quality signals

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

The full pipeline can be executed with:

```bash
python src/run_pipeline.py
```

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

* Parsing date fields.
* Converting percentage fields into decimal format.
* Standardising text fields.
* Validating latitude and longitude values.
* Creating host tenure fields.
* Creating review frequency fields.
* Creating calendar-based weekend and weekday indicators.
* Preserving missing price values rather than imputing unsupported prices.

### 5.3 Enriched Listing Master Table

The enriched `listing_master` table combines listing attributes with calendar and review summaries.

Derived fields include:

* `available_days`
* `unavailable_days`
* `occupancy_rate_estimate`
* `review_frequency_per_month`
* `listing_count_neighbourhood`
* `average_rating_neighbourhood`

The `occupancy_rate_estimate` field is treated as a proxy because unavailable calendar days may represent bookings, blocked dates, maintenance periods, or host-disabled dates.

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

The raw dataset sizes were:

* Listings: 24,491 rows
* Calendar: 8,939,215 rows
* Reviews: 943,744 rows
* Neighbourhoods: 30 rows

The most important data quality finding was that price fields were not usable. The detailed listings file, summary listings file, and calendar file all had missing price values. This directly affected the analytical scope and required the project to focus on non-price market intelligence.

This is a material limitation, but documenting it clearly strengthens the reliability of the analysis. The project avoids unsupported price or revenue conclusions and instead analyses fields with sufficient data quality.

## 7. SQL Analysis Findings

SQL analysis outputs were generated in:

```text
reports/sql_outputs/
```

### 7.1 Listing Supply by Room Type

The largest room type category was **Entire Home/Apt**, with **17,703** listings. This category had an average annual availability of **151.37** days and an average of **46.39** reviews per listing.

Private rooms were the second-largest category, with **6,563** listings, average annual availability of **139.74** days, and an average of **18.45** reviews per listing.

This indicates that the Melbourne Airbnb market is strongly shaped by entire-home/apartment supply rather than shared accommodation.

### 7.2 Neighbourhood Supply

The neighbourhood with the highest listing count was **Melbourne**, with **7,832** listings. Its average annual availability was **140.12** days and the average number of reviews was **49.14**.

This suggests that neighbourhood-level supply concentration is important for market monitoring and operational planning.

### 7.3 Estimated Occupancy Proxy

The neighbourhood with the highest estimated occupancy-rate proxy was **Darebin**, based on **584** listings. Its average occupancy-rate estimate was **0.7066**, while average annual availability was **106.91** days.

This should be treated as a proxy because calendar unavailability may represent bookings, blocked dates, or host-disabled dates.

### 7.4 Host Concentration

The largest host by listing count was **Flexistayz**, managing **292** listings. This host had average annual availability of **94.66** days and average reviews per listing of **5.80**.

This suggests that host concentration is an important supply-side feature to monitor, especially when distinguishing casual hosts from professional or high-volume operators.

## 8. Exploratory Data Analysis Findings

EDA outputs were generated in:

```text
reports/eda_outputs/
reports/figures/
```

Generated figures include:

* `listing_supply_by_room_type.png`
* `availability_by_room_type.png`
* `top_neighbourhoods_by_listing_count.png`
* `review_score_distribution.png`
* `reviews_by_room_type.png`
* `monthly_availability_rate.png`
* `top_hosts_by_listing_count.png`

### 8.1 Listing Supply by Room Type

Figure: `reports/figures/listing_supply_by_room_type.png`

Business interpretation:

Entire homes/apartments dominate Melbourne Airbnb supply. This suggests the platform is not only serving shared accommodation use cases, but also a large whole-property short-term rental market. Market analysts should therefore evaluate Melbourne Airbnb activity as part of the broader accommodation and housing supply discussion.

### 8.2 Availability by Room Type

Figure: `reports/figures/availability_by_room_type.png`

Business interpretation:

Availability differs by room type, with shared rooms and hotel rooms showing higher average annual availability than entire homes and private rooms. Higher availability may indicate weaker demand, more flexible supply, or listings that are not actively booked throughout the year.

### 8.3 Top Neighbourhoods by Listing Count

Figure: `reports/figures/top_neighbourhoods_by_listing_count.png`

Business interpretation:

The Melbourne neighbourhood has the highest listing concentration. This indicates that Airbnb supply is spatially concentrated rather than evenly distributed across the city. Localised monitoring is therefore more useful than relying only on city-wide averages.

### 8.4 Review Score Distribution

Figure: `reports/figures/review_score_distribution.png`

Business interpretation:

Review score distribution helps assess customer satisfaction patterns. If scores are concentrated near the top end, small differences in rating may still matter commercially because many listings are competing within a narrow high-score band.

### 8.5 Reviews by Room Type

Figure: `reports/figures/reviews_by_room_type.png`

Business interpretation:

Entire homes/apartments have a higher average number of reviews than private rooms. This may indicate stronger guest activity, longer operating history, or greater visibility for entire-home listings.

### 8.6 Monthly Availability

Figure: `reports/figures/monthly_availability_rate.png`

Business interpretation:

Monthly availability patterns help identify potential seasonal or operational changes. Lower availability may suggest stronger demand or more host-blocked dates, while higher availability may indicate weaker demand or excess supply.

### 8.7 Host Concentration

Figure: `reports/figures/top_hosts_by_listing_count.png`

Business interpretation:

The host concentration chart identifies high-volume operators. This is useful for understanding whether supply is driven mainly by many casual hosts or by a smaller group of professional operators.

## 9. Statistical Findings

Statistical outputs were generated at:

```text
reports/statistical_outputs/statistical_tests_summary.csv
```

Non-parametric tests were used because Airbnb marketplace variables such as availability, reviews, and review scores are unlikely to follow ideal normal distributions.

### H1: Entire-home listings have different annual availability than private rooms

Test used: Mann-Whitney U test

* Sample size group 1: 17,703
* Sample size group 2: 6,563
* p-value: 0.000000
* effect size: 0.0659

Interpretation:

The result suggests that entire-home listings and private rooms have statistically different annual availability distributions. The effect size is small, so the practical difference should be interpreted carefully. However, it still indicates that accommodation type is relevant when analysing supply strategy.

### H2: Superhost listings have different review scores than non-superhost listings

Test used: Mann-Whitney U test

* Sample size group 1: 6,781
* Sample size group 2: 12,735
* p-value: 0.000000
* effect size: 0.2590

Interpretation:

The result suggests that superhost status is associated with different review score distributions. The effect size is larger than the other tests in this project, indicating that superhost status may be a meaningful quality signal.

### H3: Annual availability differs across neighbourhoods

Test used: Kruskal-Wallis test

* Total sample size: 24,491
* Neighbourhood groups: 30
* p-value: 0.000000
* effect size: 0.0565

Interpretation:

The result suggests that availability patterns differ across Melbourne neighbourhoods. The effect size is small, but the result supports neighbourhood-level monitoring rather than relying only on city-level averages.

### H4: Weekend availability differs from weekday availability

Test used: Mann-Whitney U test

* Weekend records: 2,547,064
* Weekday records: 6,392,151
* p-value: 0.000000
* effect size: -0.0101

Interpretation:

The result suggests a statistically detectable difference between weekend and weekday availability. However, the effect size is very small, so the practical business impact may be limited. This is an example where statistical significance does not necessarily mean strong practical significance.

## 10. Business Recommendations

### Recommendation 1: Monitor Entire-Home Supply Closely

Entire homes/apartments dominate the Melbourne Airbnb dataset. Stakeholders should monitor this category separately because it represents the largest share of supply and may behave differently from private rooms or shared rooms.

### Recommendation 2: Use Neighbourhood-Level Market Monitoring

The Melbourne neighbourhood has the highest listing concentration, while other areas such as Darebin show strong occupancy-rate proxy patterns. Market analysis should therefore be performed at neighbourhood level rather than relying only on city-wide averages.

### Recommendation 3: Treat Occupancy Estimates Carefully

Occupancy estimates should be used as directional indicators only. Calendar unavailability may include actual bookings, host-blocked dates, maintenance, or inactive dates.

### Recommendation 4: Track High-Volume Hosts

The largest host, Flexistayz, manages 292 listings. Host concentration analysis can help identify professional operators and distinguish them from casual hosts.

### Recommendation 5: Use Superhost Status as a Quality Signal

The statistical analysis suggests that superhost listings have different review score distributions from non-superhost listings. This supports using superhost status as one signal of listing quality, while still considering other review and operational metrics.

### Recommendation 6: Avoid Unsupported Price Conclusions

Because the Melbourne dataset did not contain usable price values, price and revenue conclusions should not be made from this dataset. Future work should use a city or dataset snapshot with valid price data if pricing analysis is required.

## 11. Assumptions and Decision Log

The full assumptions and decision log are documented in:

```text
reports/decision_log.md
```

Major decisions include:

* Selecting one city for depth.
* Using Python for pipeline development.
* Using DuckDB for local analytical modelling.
* Excluding raw data from Git.
* Including report outputs for reviewer evidence.
* Pivoting away from price analysis because the Melbourne price fields were missing.
* Using non-parametric statistical tests.

## 12. Limitations and Caveats

Important limitations include:

* The project analyses only Melbourne.
* The dataset is a public scraped snapshot and may contain missing or inconsistent values.
* Price fields were missing, so price and revenue analysis were not performed.
* Calendar unavailable days are only an occupancy proxy.
* Review frequency is only a proxy for demand.
* Statistical tests do not prove causation.
* Machine learning and AI experiments were not completed due to prioritisation.

## 13. Future Improvements

With more time, the project could be extended by:

* Adding another city with complete price data.
* Building a Streamlit dashboard.
* Adding Docker for reproducibility.
* Implementing dbt models and tests.
* Adding machine learning price prediction using a dataset with valid price fields.
* Running NLP sentiment analysis on review text.
* Deploying the pipeline to a cloud platform.
* Adding automated data quality tests.
* Building a geographic map using `neighbourhoods.geojson`.

## 14. Reflection

This project was scoped to prioritise core data engineering and analytical quality.

The main trade-off was choosing depth over breadth. Instead of attempting every optional section, the project focused on building a reproducible pipeline, clean outputs, SQL analysis, EDA, and statistical testing.

A major learning was that real-world public datasets may not support the original analytical plan. In this case, missing price data required a responsible pivot from price analysis to supply, availability, reviews, host concentration, and quality signals.

The most important professional decision was to avoid inventing or imputing unsupported price values. This improves trust in the final analysis.

## Appendix A. AI Usage Disclosure

The AI usage disclosure is documented in:

```text
reports/ai_usage_disclosure.md
```

AI assistance was used for project planning, code structure guidance, debugging support, README drafting, and report structure guidance. All outputs were reviewed, executed, and validated locally.
