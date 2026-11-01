-- ============================================================
-- 02_data_cleaning.sql
-- Data Profiling, Validation, and Cleaning Logic
-- ============================================================

-- 1. Check Missing Values in Orders
SELECT 
    COUNT(*) AS total_orders,
    SUM(CASE WHEN order_approved_at IS NULL THEN 1 ELSE 0 END) AS missing_approval,
    SUM(CASE WHEN order_delivered_carrier_date IS NULL THEN 1 ELSE 0 END) AS missing_carrier_date,
    SUM(CASE WHEN order_delivered_customer_date IS NULL THEN 1 ELSE 0 END) AS missing_customer_delivered_date,
    SUM(CASE WHEN order_status = 'delivered' AND order_delivered_customer_date IS NULL THEN 1 ELSE 0 END) AS delivered_missing_timestamp
FROM orders;

-- 2. Validate Order Status Distribution
SELECT 
    order_status,
    COUNT(*) AS order_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS percentage_share
FROM orders
GROUP BY order_status
ORDER BY order_count DESC;

-- 3. Identify and Inspect Cancelled and Unavailable Orders
SELECT 
    order_status,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT oi.order_id) AS orders_with_items,
    ROUND(SUM(oi.price), 2) AS lost_items_revenue,
    ROUND(SUM(oi.freight_value), 2) AS lost_freight_value
FROM orders o
LEFT JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status IN ('canceled', 'unavailable')
GROUP BY order_status;

-- 4. Deduplicate Review Records (Keep latest review per order)
CREATE OR REPLACE VIEW v_clean_order_reviews AS
WITH ranked_reviews AS (
    SELECT 
        review_id,
        order_id,
        review_score,
        review_comment_message,
        review_creation_date,
        ROW_NUMBER() OVER(PARTITION BY order_id ORDER BY review_creation_date DESC) AS rn
    FROM order_reviews
)
SELECT 
    review_id,
    order_id,
    review_score,
    review_comment_message,
    review_creation_date
FROM ranked_reviews
WHERE rn = 1;

-- 5. Create Clean Order-Level Master View
CREATE OR REPLACE VIEW v_master_orders AS
SELECT 
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    -- Revenue aggregations
    COALESCE(i.total_items_price, 0) AS items_price,
    COALESCE(i.total_freight, 0) AS freight_value,
    COALESCE(i.total_items_price, 0) + COALESCE(i.total_freight, 0) AS total_order_revenue,
    -- Review
    r.review_score,
    -- Delivery Performance Flags
    CASE 
        WHEN o.order_delivered_customer_date IS NULL THEN 'Not Delivered'
        WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 'Late'
        ELSE 'On-Time'
    END AS delivery_status,
    CASE 
        WHEN o.order_delivered_customer_date IS NOT NULL 
        THEN ROUND(EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_estimated_delivery_date)) / 86400, 1)
        ELSE NULL 
    END AS delay_days
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN (
    SELECT 
        order_id,
        SUM(price) AS total_items_price,
        SUM(freight_value) AS total_freight
    FROM order_items
    GROUP BY order_id
) i ON o.order_id = i.order_id
LEFT JOIN v_clean_order_reviews r ON o.order_id = r.order_id;

