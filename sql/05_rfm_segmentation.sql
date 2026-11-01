-- ============================================================
-- 05_rfm_segmentation.sql
-- Recency, Frequency, Monetary (RFM) Customer Segmentation
-- ============================================================

-- Step 1: Calculate raw R, F, M metrics per unique customer
WITH customer_rfm_raw AS (
    SELECT 
        c.customer_unique_id,
        -- Recency: Days between customer's last order and reference date (2018-08-30)
        DATE_PART('day', '2018-08-30 00:00:00'::timestamp - MAX(o.order_purchase_timestamp)) AS recency_days,
        -- Frequency: Count of distinct valid delivered orders
        COUNT(DISTINCT o.order_id) AS frequency_orders,
        -- Monetary: Total gross spend (items + freight)
        ROUND(SUM(oi.price + oi.freight_value), 2) AS monetary_spend,
        ROUND(AVG(r.review_score), 2) AS avg_review_score
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    LEFT JOIN v_clean_order_reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
),

-- Step 2: Assign Quintile Scores (1 to 5)
-- Recency: Lower days = Higher Score (Reverse ranking)
-- Frequency: 1 order = 1, 2 orders = 3, 3+ orders = 5 (due to 97% single purchase skew)
-- Monetary: NTILE(5) higher spending = higher score
rfm_scores AS (
    SELECT 
        customer_unique_id,
        recency_days,
        frequency_orders,
        monetary_spend,
        avg_review_score,
        -- R_Score (1 = oldest, 5 = most recent)
        NTILE(5) OVER(ORDER BY recency_days DESC) AS r_score,
        -- F_Score (robust rule-based binning)
        CASE 
            WHEN frequency_orders = 1 THEN 1
            WHEN frequency_orders = 2 THEN 3
            ELSE 5
        END AS f_score,
        -- M_Score (1 = lowest spend, 5 = highest spend)
        NTILE(5) OVER(ORDER BY monetary_spend ASC) AS m_score
    FROM customer_rfm_raw
),

-- Step 3: Segment Mapping Logic
rfm_segmented AS (
    SELECT 
        customer_unique_id,
        recency_days,
        frequency_orders,
        monetary_spend,
        avg_review_score,
        r_score,
        f_score,
        m_score,
        CONCAT(r_score, f_score, m_score) AS rfm_score_str,
        CASE 
            WHEN r_score >= 4 AND f_score >= 3 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
            WHEN r_score >= 4 AND f_score = 1 AND m_score >= 4 THEN 'Potential Loyalists'
            WHEN r_score >= 4 AND f_score = 1 THEN 'New Customers'
            WHEN r_score = 3 AND f_score = 1 THEN 'Promising Customers'
            WHEN r_score = 2 AND f_score >= 3 THEN 'At Risk'
            WHEN r_score = 1 AND f_score >= 3 THEN 'Cannot Lose Them'
            WHEN r_score = 2 AND f_score = 1 THEN 'Hibernating'
            ELSE 'Lost Customers'
        END AS segment_name
    FROM rfm_scores
)

-- Step 4: RFM Segment Summary & Revenue Contribution
SELECT 
    segment_name,
    COUNT(*) AS total_customers,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS customer_share_pct,
    ROUND(SUM(monetary_spend), 2) AS total_segment_revenue,
    ROUND(SUM(monetary_spend) * 100.0 / SUM(SUM(monetary_spend)) OVER(), 2) AS revenue_share_pct,
    ROUND(AVG(recency_days), 1) AS avg_recency_days,
    ROUND(AVG(frequency_orders), 2) AS avg_frequency,
    ROUND(AVG(monetary_spend), 2) AS avg_monetary_brl,
    ROUND(AVG(avg_review_score), 2) AS avg_segment_review
FROM rfm_segmented
GROUP BY segment_name
ORDER BY total_segment_revenue DESC;

