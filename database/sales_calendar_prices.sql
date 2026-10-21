WITH 
sales_long AS (
    SELECT *
    FROM silver.sales_long
    LIMIT 1000
),
sales_calendar AS (
    SELECT *
    FROM sales_long LEFT JOIN silver.calendar
    USING (d)
),
sales_calendar_prices AS (
    SELECT *
    FROM sales_calendar LEFT JOIN silver.sell_prices
    USING (store_id, item_id, wm_yr_wk)
)
SELECT *
FROM sales_calendar_prices;

SELECT *
FROM silver.features_core
LIMIT 1000;