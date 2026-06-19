-- Listing supply by room type
SELECT
    room_type,
    COUNT(*) AS listing_count,
    ROUND(AVG(TRY_CAST(availability_365 AS DOUBLE)), 2) AS average_availability_365,
    ROUND(MEDIAN(TRY_CAST(availability_365 AS DOUBLE)), 2) AS median_availability_365,
    ROUND(AVG(TRY_CAST(number_of_reviews AS DOUBLE)), 2) AS average_number_of_reviews
FROM fact_listing
GROUP BY room_type
ORDER BY listing_count DESC;


-- Top neighbourhoods by listing count
SELECT
    neighbourhood_cleansed,
    COUNT(*) AS listing_count,
    ROUND(AVG(TRY_CAST(availability_365 AS DOUBLE)), 2) AS average_availability_365,
    ROUND(AVG(TRY_CAST(number_of_reviews AS DOUBLE)), 2) AS average_number_of_reviews,
    ROUND(AVG(TRY_CAST(review_scores_rating AS DOUBLE)), 2) AS average_review_score
FROM fact_listing
GROUP BY neighbourhood_cleansed
ORDER BY listing_count DESC
LIMIT 10;


-- Neighbourhoods with highest estimated occupancy
SELECT
    neighbourhood_cleansed,
    COUNT(*) AS listing_count,
    ROUND(AVG(TRY_CAST(occupancy_rate_estimate AS DOUBLE)), 4) AS average_occupancy_rate_estimate,
    ROUND(AVG(TRY_CAST(availability_365 AS DOUBLE)), 2) AS average_availability_365,
    ROUND(AVG(TRY_CAST(number_of_reviews AS DOUBLE)), 2) AS average_number_of_reviews
FROM fact_listing
WHERE occupancy_rate_estimate IS NOT NULL
GROUP BY neighbourhood_cleansed
ORDER BY average_occupancy_rate_estimate DESC
LIMIT 10;


-- Superhost vs non-superhost review scores
SELECT
    dh.host_is_superhost,
    COUNT(*) AS listing_count,
    ROUND(AVG(TRY_CAST(fl.review_scores_rating AS DOUBLE)), 2) AS average_review_score,
    ROUND(MEDIAN(TRY_CAST(fl.review_scores_rating AS DOUBLE)), 2) AS median_review_score,
    ROUND(AVG(TRY_CAST(fl.number_of_reviews AS DOUBLE)), 2) AS average_number_of_reviews
FROM fact_listing fl
LEFT JOIN dim_host dh
    ON fl.host_id = dh.host_id
WHERE fl.review_scores_rating IS NOT NULL
GROUP BY dh.host_is_superhost
ORDER BY average_review_score DESC;


-- Weekend vs weekday availability from calendar
SELECT
    dd.is_weekend,
    COUNT(*) AS calendar_records,
    ROUND(AVG(CASE WHEN fcd.available_bool = true THEN 1 ELSE 0 END), 4) AS availability_rate
FROM fact_calendar_daily fcd
LEFT JOIN dim_date dd
    ON fcd.date = dd.date
GROUP BY dd.is_weekend
ORDER BY dd.is_weekend DESC;


-- Host concentration: hosts with the most listings
SELECT
    dh.host_id,
    dh.host_name,
    COUNT(fl.listing_id) AS listing_count,
    ROUND(AVG(TRY_CAST(fl.availability_365 AS DOUBLE)), 2) AS average_availability_365,
    ROUND(AVG(TRY_CAST(fl.number_of_reviews AS DOUBLE)), 2) AS average_number_of_reviews
FROM fact_listing fl
LEFT JOIN dim_host dh
    ON fl.host_id = dh.host_id
GROUP BY dh.host_id, dh.host_name
ORDER BY listing_count DESC
LIMIT 10;


-- Review and availability relationship by room type
SELECT
    room_type,
    COUNT(*) AS listing_count,
    ROUND(AVG(TRY_CAST(number_of_reviews AS DOUBLE)), 2) AS average_number_of_reviews,
    ROUND(AVG(TRY_CAST(reviews_per_month AS DOUBLE)), 2) AS average_reviews_per_month,
    ROUND(AVG(TRY_CAST(availability_365 AS DOUBLE)), 2) AS average_availability_365,
    ROUND(AVG(TRY_CAST(review_scores_rating AS DOUBLE)), 2) AS average_review_score
FROM fact_listing
GROUP BY room_type
ORDER BY listing_count DESC;