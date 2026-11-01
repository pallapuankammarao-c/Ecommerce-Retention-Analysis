# 📊 Business Insights Report: E-Commerce Customer Retention & Churn

**Project Title:** Olist Brazilian E-Commerce Retention & Churn Analysis  
**Analyst:** Data Analytics Team  
**Dataset Timeframe:** 2016 to 2018 (~100,000 Real Customer Orders)  
**Deliverable Scope:** Executive Insights, Cohort Dynamics, RFM Segmentation, Delivery Correlation  

---

## Executive Summary

This report investigates why customers stop purchasing on the Olist e-commerce platform, evaluates customer retention through cohort tracking, analyzes customer lifetime value using RFM segmentation, and quantifies the operational impact of delivery delays on customer ratings and repeat transactions.

### Key Headline Metrics (Delivered Orders)
* **Gross Revenue:** **R$ 15,419,773.75** (15.42 Million BRL)
* **Delivered Orders:** **96,478**
* **Total Unique Human Customers:** **93,358**
* **Average Order Value (AOV):** **R$ 159.83**
* **Average Customer Review Score:** **4.16 / 5.00**
* **Customer Repeat Purchase Rate:** **3.00%** (2,801 customers made 2+ purchases)
* **One-Time Buyers (Drop-off):** **97.00%** (90,557 customers never returned)

---

## 1. Customer Retention Crisis: The 97% Churn Phenomenon

### 1.1 The Baseline Problem
Out of 93,358 unique human buyers who placed a delivered order, only **2,801 customers (3.00%)** returned for a subsequent purchase. 

```
┌─────────────────────────────────────────────────────────────┐
│ Customer Retention Funnel                                   │
├──────────────────────────────────────┬─────────────┬────────┤
│ Total Unique Human Customers         │      93,358 │ 100.0% │
│ Single-Purchase Customers (Churned)  │      90,557 │  97.0% │
│ Repeat Purchase Customers            │       2,801 │   3.0% │
│ 2 Orders                             │       2,572 │  2.75% │
│ 3 Orders                             │         188 │  0.20% │
│ 4+ Orders (Power Buyers)             │          41 │  0.04% │
└──────────────────────────────────────┴─────────────┴────────┘
```

### 1.2 Cohort Retention Analysis Findings
Tracking monthly acquisition cohorts between January 2017 and August 2018 reveals that churn is **immediate**:
* **Month 0 Retention:** 100.0% (Acquisition Month)
* **Month 1 Retention:** **0.18% – 0.62%** (Average: ~0.45%)
* **Month 2 Retention:** **0.22% – 0.46%**
* **Month 3 Retention:** **0.12% – 0.43%**
* **Month 6 Retention:** **0.12% – 0.40%**

**Core Insight:** The sharpest drop-off occurs **between Month 0 and Month 1**. Over 99% of customers do not engage with the platform in the month immediately following their initial purchase. The business is operating almost entirely as an **acquisition-dependent business**, constantly needing paid traffic to replace lost customers.

---

## 2. RFM Customer Segmentation Breakdown

Customers were scored from 1 to 5 across Recency (days since last order), Frequency (order count), and Monetary spend (total value).

| Segment Name | Customer Count | % of Customers | Total Revenue (R$) | % of Total Revenue | Avg Recency | Avg Frequency | Avg Monetary | Avg Review |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Potential Loyalists** | 14,454 | 15.48% | R$ 4,365,470.31 | **28.31%** | 91.6 days | 1.00 | R$ 302.03 | 4.13 |
| **Hibernating** | 18,024 | 19.31% | R$ 2,953,646.52 | **19.15%** | 316.3 days | 1.00 | R$ 163.87 | 4.13 |
| **Lost Customers** | 18,204 | 19.50% | R$ 2,910,416.44 | **18.87%** | 473.6 days | 1.00 | R$ 159.88 | 4.21 |
| **Promising Customers** | 18,105 | 19.39% | R$ 2,738,844.18 | **17.76%** | 220.5 days | 1.00 | R$ 151.28 | 4.01 |
| **New Customers** | 21,770 | 23.32% | R$ 1,587,208.84 | **10.29%** | 90.0 days | 1.00 | R$ 72.91 | 4.25 |
| **Champions** | 1,209 | 1.30% | R$ 389,505.39 | **2.53%** | 89.2 days | 2.15 | R$ 322.17 | 4.28 |
| **Loyal Customers** | 604 | 0.65% | R$ 185,945.01 | **1.21%** | 217.7 days | 2.09 | R$ 307.86 | 4.05 |
| **At Risk** | 553 | 0.59% | R$ 164,484.66 | **1.07%** | 317.5 days | 2.08 | R$ 297.44 | 4.24 |
| **Cannot Lose Them** | 435 | 0.47% | R$ 124,252.40 | **0.81%** | 464.8 days | 2.08 | R$ 285.64 | 4.16 |
| **Total** | **93,358** | **100.0%** | **R$ 15,419,773.75** | **100.0%** | | | | |

### Key RFM Takeaways:
1. **The Most Valuable Segment:** **Potential Loyalists** represents only 15.5% of customers but drives **28.31% of company revenue (R$ 4.37M)**. These customers placed large-basket orders recently (~91 days ago). Converting just 10% of them into repeat buyers would generate over R$ 430K in incremental gross revenue.
2. **The "At Risk" Segment:** 553 proven repeat customers who previously bought multiple times and spent high amounts (R$ 297.44 AOV) have not purchased in ~317 days. They are slipping into hibernation and must be rescued immediately.
3. **The "Cannot Lose Them" Segment:** 435 high-spending repeat buyers have gone cold (>464 days since last purchase).

---

## 3. Delivery Performance vs Customer Satisfaction

Logistics is the primary driver of customer sentiment in the Olist marketplace.

### 3.1 Fulfillment Status & Review Scores
* **On-Time Deliveries:** 88,644 orders (**91.89%**) -> **Average Review: 4.29 / 5.0**
* **Delayed Deliveries:** 7,826 orders (**8.11%**) -> **Average Review: 2.57 / 5.0**
* **Rating Penalty:** A delivery delay causes an average drop of **-1.72 stars (-40.2%)**.

```
Review Rating Breakdown:
                      1-Star     2-Star     3-Star     4-Star     5-Star
On-Time Orders         5.5%       2.6%       7.9%      19.8%      64.2%
Delayed Orders        54.2%       9.8%       9.2%       9.1%      17.7%
```
**Key Finding:** When an order is late, the probability of receiving a **1-star rating skyrockets from 5.5% to 54.2% (nearly a 10x surge)**. 

### 3.2 Geographic Delay Hotspots
States with the highest late delivery percentages:
1. **Alagoas (AL):** 24.1% late delivery rate (Avg transit: 25.2 days)
2. **Maranhão (MA):** 18.9% late delivery rate (Avg transit: 22.8 days)
3. **Ceará (CE):** 16.4% late delivery rate (Avg transit: 21.1 days)
4. **Rio de Janeiro (RJ):** 12.8% late delivery rate (Urban congestion & postal hub bottlenecks)

In contrast, **São Paulo (SP)** maintains a **94.2% on-time delivery rate** with an average delivery window of just 8.7 days.

---

## 4. Answers to Core Business Questions

| Question | Data-Backed Finding |
|:---|:---|
| **What % of customers make repeat purchases?** | **3.00%** (2,801 of 93,358 unique delivered customers). |
| **During which month do customers drop off most?** | **Month 1** (99.4% drop-off from initial acquisition cohort). |
| **Which cohort has the highest retention?** | The **April 2017 cohort** achieved the peak Month 1 retention (**0.62%**). |
| **Which RFM segment contributes the most revenue?** | **Potential Loyalists** (R$ 4.37 Million, 28.31% of total revenue). |
| **Which valuable customers are at risk of leaving?** | **At Risk** (553 customers, R$ 164.5K revenue, 317 days inactive) and **Cannot Lose Them** (435 customers, R$ 124.3K revenue). |
| **Do late deliveries correlate with poor reviews?** | **Yes, strongly.** Ratings drop from 4.29 to 2.57 stars, with 1-star reviews jumping from 5.5% to 54.2%. |
| **Which segment should the business save first?** | **At Risk & Potential Loyalists.** |
