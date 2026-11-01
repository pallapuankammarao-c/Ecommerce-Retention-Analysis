-- ============================================================
-- 03_sales_analysis.sql
-- Executive Revenue, Customer Acquisition, and Sales Trends
-- ============================================================

-- 1. Executive Key Performance Indicators (Delivered Orders Only)
SELECT 
    COUNT(DISTINCT order_id) AS total_delivered_orders,
    COUNT(DISTINCT customer_unique_id) AS total_unique_customers,
    ROUND(SUM(total_order_revenue), 2) AS total_revenue_brl,
    ROUND(AVG(total_order_revenue), 2) AS average_order_value_brl,
    ROUND(AVG(review_score), 2) AS average_review_score
FROM v_master_orders
WHERE order_status = 'delivered';

-- 2. Customer Repeat Purchase Rate
WITH customer_orders AS (
    SELECT 
        customer_unique_id,
        COUNT(DISTINCT order_id) AS total_orders
    FROM v_master_orders
    WHERE order_status = 'delivered'
    GROUP BY customer_unique_id
)
SELECT 
    COUNT(*) AS total_customers,
    SUM(CASE WHEN total_orders = 1 THEN 1 ELSE 0 END) AS one_time_customers,
    SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS repeat_purchase_rate_pct
FROM customer_orders;

-- 3. Monthly Sales & Customer Acquisition Trend
WITH monthly_metrics AS (
    SELECT 
        DATE_TRUNC('month', order_purchase_timestamp) AS order_month,
        COUNT(DISTINCT order_id) AS monthly_orders,
        COUNT(DISTINCT customer_unique_id) AS active_customers,
        ROUND(SUM(total_order_revenue), 2) AS monthly_revenue,
        ROUND(AVG(total_order_revenue), 2) AS monthly_aov
    FROM v_master_orders
    WHERE order_status = 'delivered'
    GROUP BY DATE_TRUNC('month', order_purchase_timestamp)
)
SELECT 
    order_month,
    monthly_orders,
    active_customers,
    monthly_revenue,
    monthly_aov,
    -- Month-over-Month Revenue Growth %
    ROUND((monthly_revenue - LAG(monthly_revenue) OVER(ORDER BY order_month)) * 100.0 / 
          NULLIF(LAG(monthly_revenue) OVER(ORDER BY order_month), 0), 2) AS mom_revenue_growth_pct
FROM monthly_metrics
ORDER BY order_month;

-- 4. Top 10 Product Categories by Revenue
SELECT 
    COALESCE(t.product_category_name_english, p.product_category_name, 'Other') AS category_name,
    COUNT(oi.order_item_id) AS total_units_sold,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    ROUND(SUM(oi.price), 2) AS total_product_revenue,
    ROUND(SUM(oi.price + oi.freight_value), 2) AS total_gross_revenue,
    ROUND(AVG(r.review_score), 2) AS avg_category_review
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN product_category_translation t ON p.product_category_name = t.product_category_name
LEFT JOIN v_clean_order_reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY 1
ORDER BY total_gross_revenue DESC
LIMIT 10;

-- 5. Revenue Contribution by Customer State
SELECT 
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
    ROUND(SUM(oi.price + oi.freight_value), 2) AS total_state_revenue,
    ROUND(SUM(oi.price + oi.freight_value) * 100.0 / 
          SUM(SUM(oi.price + oi.freight_value)) OVER(), 2) AS revenue_share_pct
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY total_state_revenue DESC;

