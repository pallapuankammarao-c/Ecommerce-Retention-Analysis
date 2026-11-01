-- ============================================================
-- 06_delivery_review_analysis.sql
-- Logistics Performance, Delivery Delay, and Review Sentiment
-- ============================================================

-- 1. Overall Delivery On-Time vs Late Fulfillment
SELECT 
    delivery_status,
    COUNT(*) AS total_orders,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS percentage_share,
    ROUND(AVG(review_score), 2) AS average_review_score,
    ROUND(AVG(delay_days), 1) AS average_delay_days
FROM v_master_orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL
GROUP BY delivery_status;

-- 2. Star Review Breakdown: On-Time vs Late Deliveries
SELECT 
    delivery_status,
    ROUND(SUM(CASE WHEN review_score = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS star_1_pct,
    ROUND(SUM(CASE WHEN review_score = 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS star_2_pct,
    ROUND(SUM(CASE WHEN review_score = 3 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS star_3_pct,
    ROUND(SUM(CASE WHEN review_score = 4 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS star_4_pct,
    ROUND(SUM(CASE WHEN review_score = 5 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS star_5_pct
FROM v_master_orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL
  AND review_score IS NOT NULL
GROUP BY delivery_status;

-- 3. Delivery Performance by Brazilian State
SELECT 
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 ELSE 0 END) AS late_deliveries,
    ROUND(SUM(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 ELSE 0 END) * 100.0 / 
          COUNT(DISTINCT o.order_id), 2) AS late_delivery_rate_pct,
    ROUND(AVG(r.review_score), 2) AS avg_state_review_score,
    ROUND(AVG(EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_purchase_timestamp)) / 86400), 1) AS avg_transit_days
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN v_clean_order_reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
GROUP BY c.customer_state
HAVING COUNT(DISTINCT o.order_id) >= 100
ORDER BY late_delivery_rate_pct DESC;

-- 4. Impact of Experiencing a Delivery Delay on Repeat Purchase Rate
WITH customer_delivery_summary AS (
    SELECT 
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 ELSE 0 END) AS late_order_count
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
    GROUP BY c.customer_unique_id
)
SELECT 
    CASE 
        WHEN late_order_count > 0 THEN 'Experienced Late Delivery'
        ELSE 'Always On-Time'
    END AS customer_experience,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS repeat_rate_pct
FROM customer_delivery_summary
GROUP BY 1;

