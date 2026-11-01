-- ============================================================
-- 04_cohort_retention.sql
-- Cohort Retention Analysis (Monthly Cohorts & Retention Matrix)
-- ============================================================

-- Step 1: Identify First Purchase Month for each unique customer
WITH customer_first_purchase AS (
    SELECT 
        c.customer_unique_id,
        MIN(DATE_TRUNC('month', o.order_purchase_timestamp)) AS cohort_month
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
      AND o.order_purchase_timestamp >= '2017-01-01'
      AND o.order_purchase_timestamp <= '2018-08-31'
    GROUP BY c.customer_unique_id
),

-- Step 2: Track all subsequent purchase months
customer_activities AS (
    SELECT 
        c.customer_unique_id,
        fp.cohort_month,
        DATE_TRUNC('month', o.order_purchase_timestamp) AS order_month,
        -- Calculate months elapsed since cohort month
        (EXTRACT(YEAR FROM o.order_purchase_timestamp) - EXTRACT(YEAR FROM fp.cohort_month)) * 12 +
        (EXTRACT(MONTH FROM o.order_purchase_timestamp) - EXTRACT(MONTH FROM fp.cohort_month)) AS cohort_index
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN customer_first_purchase fp ON c.customer_unique_id = fp.customer_unique_id
    WHERE o.order_status = 'delivered'
      AND o.order_purchase_timestamp >= '2017-01-01'
      AND o.order_purchase_timestamp <= '2018-08-31'
),

-- Step 3: Count active customers per cohort month & index
cohort_counts AS (
    SELECT 
        cohort_month,
        cohort_index,
        COUNT(DISTINCT customer_unique_id) AS active_customers
    FROM customer_activities
    GROUP BY cohort_month, cohort_index
),

-- Step 4: Extract base cohort size (Month 0 size)
cohort_sizes AS (
    SELECT 
        cohort_month,
        active_customers AS initial_cohort_size
    FROM cohort_counts
    WHERE cohort_index = 0
)

-- Step 5: Calculate Monthly Retention Percentage Matrix
SELECT 
    TO_CHAR(c.cohort_month, 'YYYY-MM') AS cohort_month,
    s.initial_cohort_size,
    MAX(CASE WHEN c.cohort_index = 0 THEN 100.0 ELSE NULL END) AS month_0_pct,
    MAX(CASE WHEN c.cohort_index = 1 THEN ROUND(c.active_customers * 100.0 / s.initial_cohort_size, 2) ELSE NULL END) AS month_1_pct,
    MAX(CASE WHEN c.cohort_index = 2 THEN ROUND(c.active_customers * 100.0 / s.initial_cohort_size, 2) ELSE NULL END) AS month_2_pct,
    MAX(CASE WHEN c.cohort_index = 3 THEN ROUND(c.active_customers * 100.0 / s.initial_cohort_size, 2) ELSE NULL END) AS month_3_pct,
    MAX(CASE WHEN c.cohort_index = 4 THEN ROUND(c.active_customers * 100.0 / s.initial_cohort_size, 2) ELSE NULL END) AS month_4_pct,
    MAX(CASE WHEN c.cohort_index = 5 THEN ROUND(c.active_customers * 100.0 / s.initial_cohort_size, 2) ELSE NULL END) AS month_5_pct,
    MAX(CASE WHEN c.cohort_index = 6 THEN ROUND(c.active_customers * 100.0 / s.initial_cohort_size, 2) ELSE NULL END) AS month_6_pct,
    MAX(CASE WHEN c.cohort_index = 7 THEN ROUND(c.active_customers * 100.0 / s.initial_cohort_size, 2) ELSE NULL END) AS month_7_pct,
    MAX(CASE WHEN c.cohort_index = 8 THEN ROUND(c.active_customers * 100.0 / s.initial_cohort_size, 2) ELSE NULL END) AS month_8_pct,
    MAX(CASE WHEN c.cohort_index = 9 THEN ROUND(c.active_customers * 100.0 / s.initial_cohort_size, 2) ELSE NULL END) AS month_9_pct,
    MAX(CASE WHEN c.cohort_index = 10 THEN ROUND(c.active_customers * 100.0 / s.initial_cohort_size, 2) ELSE NULL END) AS month_10_pct,
    MAX(CASE WHEN c.cohort_index = 11 THEN ROUND(c.active_customers * 100.0 / s.initial_cohort_size, 2) ELSE NULL END) AS month_11_pct,
    MAX(CASE WHEN c.cohort_index = 12 THEN ROUND(c.active_customers * 100.0 / s.initial_cohort_size, 2) ELSE NULL END) AS month_12_pct
FROM cohort_counts c
JOIN cohort_sizes s ON c.cohort_month = s.cohort_month
GROUP BY c.cohort_month, s.initial_cohort_size
ORDER BY c.cohort_month;

