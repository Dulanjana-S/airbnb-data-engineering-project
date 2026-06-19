# Actual Report Insights

This file summarises the actual generated project outputs and can be used to update `reports/final_report.md`.

## Dataset Limitation: Price Fields

The Melbourne Inside Airbnb files used in this project did not contain usable price values. The `price` field in the detailed listings file, the summary listings file, and the calendar file contained no non-null values. For this reason, the final analysis focuses on supply, availability, host concentration, review behaviour, neighbourhood patterns, and quality signals rather than price or revenue.

## Room Type Supply

The largest room type category was **Entire Home/Apt**, with **17,703** listings. This category had an average annual availability of **151.37** days and an average of **46.39** reviews per listing. This indicates that the Melbourne Airbnb market is strongly shaped by entire-home/apartment supply rather than shared accommodation.

## Neighbourhood Supply

The neighbourhood with the highest listing count was **Melbourne**, with **7,832** listings. Its average annual availability was **140.12** days and the average number of reviews was **49.14**. This suggests that neighbourhood-level supply concentration is important for market monitoring and operational planning.

## Estimated Occupancy Proxy

The neighbourhood with the highest estimated occupancy-rate proxy was **Darebin**, based on **584** listings. Its average occupancy-rate estimate was **0.7066**, while average annual availability was **106.91** days. This should be treated as a proxy because calendar unavailability may represent bookings, blocked dates, or host-disabled dates.

## Weekend vs Weekday Availability

Weekend and weekday availability was analysed using calendar availability records. The output is available in `reports/sql_outputs/query_05_output.csv`. This helps identify whether listings are more or less available on weekends compared with weekdays.

## Host Concentration

The largest host by listing count was **Flexistayz**, managing **292** listings. This host had average annual availability of **94.66** days and average reviews per listing of **5.80**. This suggests that host concentration is an important supply-side feature to monitor.

## Statistical Test Summary

- **H1: Entire-home listings have different annual availability than private rooms** was completed using the **Mann-Whitney U test**. The p-value was **0.000000** and the effect size was **0.0659**. This tests whether different accommodation types behave differently in terms of yearly availability. A significant result suggests supply strategy differs by room type.
- **H2: Superhost listings have different review scores than non-superhost listings** was completed using the **Mann-Whitney U test**. The p-value was **0.000000** and the effect size was **0.2590**. This tests whether superhost status is associated with guest satisfaction. A significant result suggests superhost status may be a useful quality signal.
- **H3: Annual availability differs across neighbourhoods** was completed using the **Kruskal-Wallis test**. The p-value was **0.000000** and the effect size was **0.0565**. This tests whether supply availability patterns differ by location. A significant result suggests neighbourhood-level market monitoring is needed.
- **H4: Weekend availability differs from weekday availability** was completed using the **Mann-Whitney U test**. The p-value was **0.000000** and the effect size was **-0.0101**. This tests whether availability patterns differ between weekends and weekdays. A significant result may indicate seasonal or demand-driven booking behaviour.

## Output Files Reviewed

- `reports/sql_outputs/query_01_output.csv`
- `reports/sql_outputs/query_02_output.csv`
- `reports/sql_outputs/query_03_output.csv`
- `reports/sql_outputs/query_05_output.csv`
- `reports/sql_outputs/query_06_output.csv`
- `reports/statistical_outputs/statistical_tests_summary.csv`
