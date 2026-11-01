# 🖥️ Power BI 5-Page Enterprise Dashboard Implementation Guide

This document provides complete instructions for exploring, maintaining, and presenting the 5-page **E-Commerce Customer Retention & Churn Analysis** Power BI Dashboard (`dashboard/powerbi_dashboard.pbix`).

---

## 🎨 Enterprise Theme & Visual Guidelines
* **Color Palette:**
  * Primary / Dark: `#0F172A` (Navy Blue)
  * Secondary / Accent: `#0EA5E9` (Sky Teal)
  * Success / On-Time: `#10B981` (Emerald Green)
  * Alert / Late Deliveries: `#EF4444` (Crimson Red)
  * Warning / At-Risk: `#F59E0B` (Amber)
  * Background: Clean White `#FFFFFF` with Slate Canvas `#F8FAFC`
* **Typography:** Segoe UI Semibold for titles, Segoe UI for body and data labels.

---

## 📑 5-Page Dashboard Structure

### 📌 Page 1: Executive Overview
* **KPI Cards (Top Banner):**
  1. **Total Revenue:** R$ 15.42M
  2. **Delivered Orders:** 96,478
  3. **Unique Customers:** 93,358
  4. **Average Order Value (AOV):** R$ 159.83
  5. **Repeat Purchase Rate:** 3.00%
  6. **Average Review Score:** 4.16 / 5.0
* **Visuals:**
  * **Line with Shaded Area:** Monthly Gross Revenue (2017 - 2018).
  * **Horizontal Bar Chart:** Top 10 Product Categories by Revenue (Bed Bath Table, Health & Beauty, Computer Accessories).
  * **Column Chart:** Revenue Contribution by State (SP: 37.4%, RJ: 13.2%, MG: 11.9%).
  * **Donut Chart:** New vs Repeat Customer Distribution (97.0% One-Time vs 3.0% Repeat).
* **Interactive Slicers:** Order Date Range (Year/Month), Order Status, Customer State.

---

### 📌 Page 2: Customer Retention & Cohort Analysis
* **Visuals:**
  * **Matrix Visual (Cohort Heatmap):** Rows = Cohort Acquisition Month (2017-01 to 2018-08); Columns = Cohort Index (0 to 18); Values = Retention Rate % with Conditional Formatting (Blues gradient).
  * **Line Chart:** Average Retention Curve across Months 0 to 12.
  * **Clustered Bar Chart:** New Acquired Customers vs Returning Customer Orders per Month.
* **Key Business Takeaway:** Visualizes the sharp first-month retention drop from 100% to 0.45%.

---

### 📌 Page 3: RFM Customer Segmentation
* **Visuals:**
  * **Horizontal Bar Chart:** Customer Count by RFM Segment (Potential Loyalists, New Customers, Champions, At Risk).
  * **Horizontal Bar Chart:** Revenue Contribution by RFM Segment (Potential Loyalists: R$ 4.37M, 28.3%).
  * **Scatter Plot:** Recency (X-Axis, Days) vs Monetary (Y-Axis, Spend, Log Scale) colored by Segment.
  * **Card Callout:** Highlighting the "At Risk" segment (553 valuable repeat customers).

---

### 📌 Page 4: Delivery & Customer Satisfaction
* **Visuals:**
  * **Donut Chart:** On-Time (91.89%) vs Late Deliveries (8.11%).
  * **Column Chart:** Average Customer Rating by Fulfillment (On-Time: 4.29 ⭐ vs Late: 2.57 ⭐).
  * **100% Stacked Bar Chart:** Star Review Distribution (1-Star reviews surge from 5.5% on-time to 54.2% delayed).
  * **Bar Chart:** Repeat Purchase Rate by Delivery Experience.

---

### 📌 Page 5: Strategic Business Recommendations
* **Visuals:**
  * **Executive Strategy Matrix:** Four actionable campaign pillars with target segments, messaging, and expected ROI.
  * **ROI Forecast Gauge:** Projected incremental revenue lift (+R$ 373K ARR at moderate +2.5 pp retention boost).
  * **Operational SLA Targets:** Route optimizations for RJ, BA, and MA regional hubs.

