-- Average listing price by room type
SELECT
    room_type,
    COUNT(*) AS listing_count,
    ROUND(AVG(TRY_CAST(price_clean AS DOUBLE)), 2) AS average_price,
    ROUND(MEDIAN(TRY_CAST(price_clean AS DOUBLE)), 2) AS median_price
FROM fact_listing
WHERE TRY_CAST(price_clean AS DOUBLE) IS NOT NULL
GROUP BY room_type
ORDER BY median_price DESC;


-- Top 10 neighbourhoods by median price
SELECT
    neighbourhood_cleansed,
    COUNT(*) AS listing_count,
    ROUND(MEDIAN(TRY_CAST(price_clean AS DOUBLE)), 2) AS median_price,
    ROUND(AVG(TRY_CAST(price_clean AS DOUBLE)), 2) AS average_price
FROM fact_listing
WHERE TRY_CAST(price_clean AS DOUBLE) IS NOT NULL
GROUP BY neighbourhood_cleansed
HAVING COUNT(*) >= 10
ORDER BY median_price DESC
LIMIT 10;


-- Estimated annual revenue by neighbourhood
SELECT
    neighbourhood_cleansed,
    COUNT(*) AS listing_count,
    ROUND(SUM(TRY_CAST(estimated_annual_revenue AS DOUBLE)), 2) AS total_estimated_revenue,
    ROUND(AVG(TRY_CAST(occupancy_rate_estimate AS DOUBLE)), 4) AS average_occupancy_rate
FROM fact_listing
WHERE TRY_CAST(estimated_annual_revenue AS DOUBLE) IS NOT NULL
GROUP BY neighbourhood_cleansed
ORDER BY total_estimated_revenue DESC
LIMIT 10;


-- Superhost vs non-superhost review scores
SELECT
    dh.host_is_superhost,
    COUNT(*) AS listing_count,
    ROUND(AVG(TRY_CAST(fl.review_scores_rating AS DOUBLE)), 2) AS average_review_score,
    ROUND(MEDIAN(TRY_CAST(fl.review_scores_rating AS DOUBLE)), 2) AS median_review_score
FROM fact_listing fl
LEFT JOIN dim_host dh
    ON fl.host_id = dh.host_id
WHERE TRY_CAST(fl.review_scores_rating AS DOUBLE) IS NOT NULL
GROUP BY dh.host_is_superhost
ORDER BY average_review_score DESC;


-- Weekend vs weekday calendar prices
SELECT
    dd.is_weekend,
    COUNT(*) AS calendar_records,
    ROUND(AVG(TRY_CAST(fcd.price_clean AS DOUBLE)), 2) AS average_price,
    ROUND(MEDIAN(TRY_CAST(fcd.price_clean AS DOUBLE)), 2) AS median_price
FROM fact_calendar_daily fcd
LEFT JOIN dim_date dd
    ON fcd.date = dd.date
WHERE TRY_CAST(fcd.price_clean AS DOUBLE) IS NOT NULL
GROUP BY dd.is_weekend
ORDER BY dd.is_weekend DESC;


-- Host concentration: hosts with the most listings
SELECT
    dh.host_id,
    dh.host_name,
    COUNT(fl.listing_id) AS listing_count,
    ROUND(AVG(TRY_CAST(fl.price_clean AS DOUBLE)), 2) AS average_price,
    ROUND(SUM(TRY_CAST(fl.estimated_annual_revenue AS DOUBLE)), 2) AS total_estimated_revenue
FROM fact_listing fl
LEFT JOIN dim_host dh
    ON fl.host_id = dh.host_id
GROUP BY dh.host_id, dh.host_name
ORDER BY listing_count DESC
LIMIT 10;


-- Price and review relationship by room type
SELECT
    room_type,
    COUNT(*) AS listing_count,
    ROUND(AVG(TRY_CAST(price_clean AS DOUBLE)), 2) AS average_price,
    ROUND(AVG(TRY_CAST(number_of_reviews AS DOUBLE)), 2) AS average_number_of_reviews,
    ROUND(AVG(TRY_CAST(review_scores_rating AS DOUBLE)), 2) AS average_review_score
FROM fact_listing
WHERE TRY_CAST(price_clean AS DOUBLE) IS NOT NULL
GROUP BY room_type
ORDER BY average_price DESC;