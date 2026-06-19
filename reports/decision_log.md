# Assumptions and Engineering Decision Log

## Assumptions

### A1. City Scope

This project uses only the Melbourne, Victoria, Australia dataset from Inside Airbnb.

The assignment allows candidates to choose their own city scope. A single-city approach was selected to prioritise depth, reproducibility, code quality, and clear business interpretation.

### A2. Calendar Availability as Occupancy Proxy

Calendar records where a listing is unavailable are treated as an approximate occupancy signal.

This is an assumption because unavailable days may represent actual bookings, host-blocked dates, maintenance periods, or other non-booking reasons.

### A3. Estimated Revenue

Estimated annual revenue is calculated as:

```text
unavailable_days * average_calendar_price
```

This is not a confirmed revenue figure. It is an analytical estimate based on public calendar data.

### A4. Statistical Interpretation

Statistical test results are interpreted as evidence of association, not causation.

For example, if entire-home listings have higher prices than private rooms, this does not prove that room type alone causes the price difference. Other factors such as location, amenities, property size, and host strategy may also influence price.

### A5. Missing and Incomplete Data

Missing values are kept as nulls where possible rather than being aggressively imputed.

This approach preserves transparency and avoids introducing unsupported assumptions into the analysis.

---

## Engineering Decision Log

### Decision 1: Use One City Instead of Multiple Cities

Options considered:

* Analyse one city in depth
* Analyse multiple cities with a broader comparison

Decision:

Melbourne was selected as the single city for this project.

Rationale:

A one-city scope supports stronger data cleaning, profiling, modelling, EDA, and statistical analysis within the available time.

Trade-off:

This limits cross-city comparison, but improves project depth and reproducibility.

---

### Decision 2: Use Python for Pipeline Development

Options considered:

* Python
* R
* SQL-only workflow

Decision:

Python was selected for data ingestion, profiling, cleaning, analysis, and output generation.

Rationale:

Python provides strong support for data engineering workflows through pandas, DuckDB, scipy, and matplotlib.

Trade-off:

A SQL-only pipeline may be simpler for database modelling, but Python provides more flexibility for file handling, chart generation, and statistical testing.

---

### Decision 3: Use DuckDB as the Analytical Database

Options considered:

* SQLite
* PostgreSQL
* DuckDB

Decision:

DuckDB was selected as the analytical database.

Rationale:

DuckDB is lightweight, fast for analytical queries, easy to reproduce locally, and does not require a separate database server.

Trade-off:

DuckDB is not a full production data warehouse, but it is suitable for a take-home assessment and local analytical engineering workflow.

---

### Decision 4: Exclude Raw Data from Git

Options considered:

* Commit raw data files
* Exclude raw data files and provide download instructions

Decision:

Raw dataset files are excluded from Git.

Rationale:

The files can be large and are publicly available from Inside Airbnb. The README explains where to download them and where to place them.

Trade-off:

Reviewers must download the raw files to rerun the pipeline, but the repository remains lightweight and clean.

---

### Decision 5: Commit Report Outputs

Options considered:

* Exclude all generated outputs
* Include selected report outputs for reviewer evidence

Decision:

Report outputs such as CSV summaries and figures are included.

Decision: Pivot away from price analysis

During profiling, the Melbourne listings and calendar files were found to contain no usable price values. Instead of imputing or inventing prices, the project scope was adjusted to focus on supply, availability, review behaviour, host concentration, neighbourhood patterns, and quality signals.

Trade-off:
This reduced the ability to analyse pricing and revenue, but improved the trustworthiness of the final analysis.

Rationale:

This allows reviewers to inspect outputs quickly without rerunning the full pipeline first.

Trade-off:

The repository contains some generated files, but they are useful evidence for assessment review.

---

### Decision 6: Use Non-Parametric Statistical Tests

Options considered:

* Parametric tests such as t-tests and ANOVA
* Non-parametric tests such as Mann-Whitney U and Kruskal-Wallis

Decision:

Non-parametric tests were used for the main statistical comparisons.

Rationale:

Airbnb price data is usually skewed, contains outliers, and may not satisfy normality assumptions.

Trade-off:

Non-parametric tests are less focused on mean differences, but they are more robust for skewed distributions.
