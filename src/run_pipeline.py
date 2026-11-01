"""
End-to-End Analytics Pipeline
=============================
Executes full data cleaning, master dataset construction, EDA,
Cohort Retention, RFM Segmentation, Delivery vs Review Analysis,
exports processed datasets, and generates dashboard visualizations.
"""

import sys
import os
import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mticker

# Ensure local src is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DASHBOARD_IMG_DIR = PROJECT_ROOT / "dashboard" / "dashboard_screenshots"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
DASHBOARD_IMG_DIR.mkdir(parents=True, exist_ok=True)

# Styling
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "#F8FAFC",
    "axes.edgecolor": "#CBD5E1",
    "axes.labelcolor": "#1E293B",
    "xtick.color": "#334155",
    "ytick.color": "#334155",
    "font.sans-serif": ["Segoe UI", "Arial", "sans-serif"],
    "font.family": "sans-serif"
})

def run_pipeline():
    print("=" * 70)
    print("STEP 2: DATA CLEANING & PREPROCESSING")
    print("=" * 70)

    # 1. Load raw files
    print("[1/7] Loading raw CSV files...")
    customers = pd.read_csv(RAW_DIR / "olist_customers_dataset.csv")
    orders = pd.read_csv(RAW_DIR / "olist_orders_dataset.csv")
    order_items = pd.read_csv(RAW_DIR / "olist_order_items_dataset.csv")
    payments = pd.read_csv(RAW_DIR / "olist_order_payments_dataset.csv")
    reviews = pd.read_csv(RAW_DIR / "olist_order_reviews_dataset.csv")
    products = pd.read_csv(RAW_DIR / "olist_products_dataset.csv")
    sellers = pd.read_csv(RAW_DIR / "olist_sellers_dataset.csv")
    category_translation = pd.read_csv(RAW_DIR / "product_category_name_translation.csv")

    # 2. Convert date columns
    date_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
    for col in date_cols:
        orders[col] = pd.to_datetime(orders[col], format="mixed", dayfirst=True)
        print(f"  [OK] Converted {col} to datetime")

    reviews["review_creation_date"] = pd.to_datetime(reviews["review_creation_date"], format="mixed", dayfirst=True)
    reviews["review_answer_timestamp"] = pd.to_datetime(reviews["review_answer_timestamp"], format="mixed", dayfirst=True)

    # 3. Handle duplicates
    initial_orders = len(orders)
    orders = orders.drop_duplicates(subset=["order_id"])
    print(f"  [OK] Orders deduplicated: {initial_orders} -> {len(orders)}")

    # 4. Status validation
    print("\nOrder Status Counts:")
    print(orders["order_status"].value_counts().to_string())

    # We filter for delivered orders for revenue & retention core calculations, but keep full orders for funnel analysis
    valid_orders = orders[orders["order_status"] == "delivered"].copy()
    print(f"\nDelivered valid orders: {len(valid_orders):,} ({len(valid_orders)/len(orders)*100:.2f}%)")

    # 5. Product Translation Merge
    products_clean = products.merge(category_translation, on="product_category_name", how="left")
    products_clean["product_category_name_english"] = products_clean["product_category_name_english"].fillna("other")

    # 6. Order Items aggregate
    items_agg = order_items.groupby("order_id").agg(
        item_count=("order_item_id", "count"),
        total_items_price=("price", "sum"),
        total_freight_value=("freight_value", "sum")
    ).reset_index()
    items_agg["order_revenue"] = items_agg["total_items_price"] + items_agg["total_freight_value"]

    # 7. Payments aggregate
    payments_agg = payments.groupby("order_id").agg(
        total_payment_value=("payment_value", "sum"),
        payment_installments_max=("payment_installments", "max"),
        primary_payment_type=("payment_type", lambda x: x.mode()[0] if not x.empty else "unknown")
    ).reset_index()

    # 8. Reviews aggregate (mean score & first review comment)
    reviews_agg = reviews.groupby("order_id").agg(
        review_score=("review_score", "mean"),
        review_count=("review_id", "count"),
        has_review_comment=("review_comment_message", lambda x: int(x.dropna().count() > 0))
    ).reset_index()

    # 9. Master Analytical Dataset (Order Level)
    print("\n[2/7] Constructing Master Analytical Dataset...")
    master = orders.merge(customers, on="customer_id", how="left")
    master = master.merge(items_agg, on="order_id", how="left")
    master = master.merge(payments_agg, on="order_id", how="left")
    master = master.merge(reviews_agg, on="order_id", how="left")

    # Calculate Delivery Metrics
    master["delivery_time_days"] = (master["order_delivered_customer_date"] - master["order_purchase_timestamp"]).dt.total_seconds() / 86400.0
    master["estimated_time_days"] = (master["order_estimated_delivery_date"] - master["order_purchase_timestamp"]).dt.total_seconds() / 86400.0
    master["delivery_delay_days"] = (master["order_delivered_customer_date"] - master["order_estimated_delivery_date"]).dt.total_seconds() / 86400.0
    master["is_delayed"] = np.where(master["delivery_delay_days"] > 0, 1, 0)
    master["delivery_status"] = np.where(
        master["order_delivered_customer_date"].isna(),
        "Not Delivered",
        np.where(master["delivery_delay_days"] > 0, "Late", "On-Time")
    )

    # Master Order Items Detailed (Item Level for product category breakdowns)
    master_items = order_items.merge(orders, on="order_id", how="left")
    master_items = master_items.merge(customers, on="customer_id", how="left")
    master_items = master_items.merge(products_clean[["product_id", "product_category_name_english"]], on="product_id", how="left")
    master_items = master_items.merge(reviews_agg[["order_id", "review_score"]], on="order_id", how="left")

    # Save processed master files
    master.to_csv(PROCESSED_DIR / "master_analytical_orders.csv", index=False)
    master_items.to_csv(PROCESSED_DIR / "master_order_items.csv", index=False)
    print(f"  [SAVED] master_analytical_orders.csv: {master.shape[0]:,} rows x {master.shape[1]} cols")
    print(f"  [SAVED] master_order_items.csv: {master_items.shape[0]:,} rows x {master_items.shape[1]} cols")

    # =========================================================================
    # STEP 3: EXPLORATORY DATA ANALYSIS (EDA) & CORE METRICS
    # =========================================================================
    print("\n" + "=" * 70)
    print("STEP 3: EXPLORATORY DATA ANALYSIS & CORE METRICS")
    print("=" * 70)

    delivered_master = master[master["order_status"] == "delivered"].copy()
    
    total_revenue = delivered_master["order_revenue"].sum()
    total_orders = len(delivered_master)
    total_customers_unique = delivered_master["customer_unique_id"].nunique()
    total_customers_raw = len(customers)
    avg_order_value = total_revenue / total_orders
    avg_review_score = delivered_master["review_score"].mean()

    # Repeat purchase calculation
    customer_order_counts = delivered_master.groupby("customer_unique_id")["order_id"].nunique()
    repeat_customers_count = (customer_order_counts > 1).sum()
    single_order_customers_count = (customer_order_counts == 1).sum()
    repeat_purchase_rate = (repeat_customers_count / total_customers_unique) * 100

    print(f"Total Revenue:              R$ {total_revenue:,.2f}")
    print(f"Total Delivered Orders:     {total_orders:,}")
    print(f"Unique Customers:          {total_customers_unique:,}")
    print(f"Average Order Value (AOV):  R$ {avg_order_value:,.2f}")
    print(f"Average Review Score:       {avg_review_score:.2f} / 5.0")
    print(f"Repeat Customers:           {repeat_customers_count:,} ({repeat_purchase_rate:.2f}%)")
    print(f"Single Purchase Customers:  {single_order_customers_count:,} ({100 - repeat_purchase_rate:.2f}%)")

    # Monthly revenue & order trend
    delivered_master["purchase_month"] = delivered_master["order_purchase_timestamp"].dt.to_period("M")
    monthly_trend = delivered_master.groupby("purchase_month").agg(
        revenue=("order_revenue", "sum"),
        orders=("order_id", "nunique"),
        unique_customers=("customer_unique_id", "nunique"),
        avg_order_value=("order_revenue", "mean"),
        avg_review_score=("review_score", "mean")
    ).reset_index()
    monthly_trend["month_str"] = monthly_trend["purchase_month"].astype(str)
    monthly_trend.to_csv(PROCESSED_DIR / "monthly_sales_trend.csv", index=False)
    print("  [SAVED] monthly_sales_trend.csv")

    # Top product categories by revenue and order volume
    top_categories = master_items[master_items["order_status"] == "delivered"].groupby("product_category_name_english").agg(
        total_revenue=("price", "sum"),
        items_sold=("order_item_id", "count"),
        avg_item_price=("price", "mean"),
        avg_review=("review_score", "mean")
    ).reset_index().sort_values("total_revenue", ascending=False)
    top_categories.to_csv(PROCESSED_DIR / "top_categories.csv", index=False)
    print("  [SAVED] top_categories.csv")

    # State distribution
    state_dist = delivered_master.groupby("customer_state").agg(
        total_revenue=("order_revenue", "sum"),
        orders=("order_id", "count"),
        unique_customers=("customer_unique_id", "nunique"),
        avg_delay_days=("delivery_delay_days", "mean")
    ).reset_index().sort_values("total_revenue", ascending=False)
    state_dist["revenue_share_pct"] = (state_dist["total_revenue"] / total_revenue) * 100
    state_dist.to_csv(PROCESSED_DIR / "state_distribution.csv", index=False)
    print("  [SAVED] state_distribution.csv")

    # Save KPI JSON
    kpi_dict = {
        "total_revenue": round(float(total_revenue), 2),
        "total_orders": int(total_orders),
        "unique_customers": int(total_customers_unique),
        "avg_order_value": round(float(avg_order_value), 2),
        "avg_review_score": round(float(avg_review_score), 2),
        "repeat_customers_count": int(repeat_customers_count),
        "repeat_purchase_rate": round(float(repeat_purchase_rate), 2),
        "on_time_delivery_pct": round(float((delivered_master["delivery_delay_days"] <= 0).mean() * 100), 2),
        "late_delivery_pct": round(float((delivered_master["delivery_delay_days"] > 0).mean() * 100), 2)
    }
    with open(PROCESSED_DIR / "kpi_summary.json", "w") as f:
        json.dump(kpi_dict, f, indent=4)
    print("  [SAVED] kpi_summary.json")

    # =========================================================================
    # STEP 5: COHORT RETENTION ANALYSIS
    # =========================================================================
    print("\n" + "=" * 70)
    print("STEP 5: COHORT RETENTION ANALYSIS")
    print("=" * 70)

    # Filter to orders between 2017-01 and 2018-08 (representative operational period)
    cohort_data = delivered_master[
        (delivered_master["order_purchase_timestamp"] >= "2017-01-01") &
        (delivered_master["order_purchase_timestamp"] <= "2018-08-31")
    ].copy()

    cohort_data["order_month"] = cohort_data["order_purchase_timestamp"].dt.to_period("M")
    cohort_data["cohort_month"] = cohort_data.groupby("customer_unique_id")["order_month"].transform("min")

    def get_month_diff(x):
        return (x["order_month"].dt.year - x["cohort_month"].dt.year) * 12 + (x["order_month"].dt.month - x["cohort_month"].dt.month)

    cohort_data["cohort_index"] = get_month_diff(cohort_data)

    # Pivot customer counts
    cohort_pivot_counts = cohort_data.groupby(["cohort_month", "cohort_index"])["customer_unique_id"].nunique().unstack()
    cohort_sizes = cohort_pivot_counts.iloc[:, 0]
    retention_matrix = cohort_pivot_counts.divide(cohort_sizes, axis=0) * 100

    # Format cohort matrix for export
    retention_matrix_clean = retention_matrix.round(2)
    retention_matrix_clean.index = retention_matrix_clean.index.astype(str)
    retention_matrix_clean.to_csv(PROCESSED_DIR / "cohort_retention_matrix.csv")
    cohort_pivot_counts.to_csv(PROCESSED_DIR / "cohort_customer_counts.csv")
    print(f"  [SAVED] cohort_retention_matrix.csv ({retention_matrix_clean.shape[0]} cohorts x {retention_matrix_clean.shape[1]} months)")
    print("\nSample Cohort Retention Matrix (%):")
    print(retention_matrix_clean.iloc[:6, :6].to_string())

    # =========================================================================
    # STEP 6: RFM CUSTOMER SEGMENTATION
    # =========================================================================
    print("\n" + "=" * 70)
    print("STEP 6: RFM CUSTOMER SEGMENTATION")
    print("=" * 70)

    analysis_date = delivered_master["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
    print(f"Reference Analysis Date: {analysis_date.strftime('%Y-%m-%d')}")

    rfm = delivered_master.groupby("customer_unique_id").agg(
        recency=("order_purchase_timestamp", lambda x: (analysis_date - x.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("order_revenue", "sum"),
        avg_review_score=("review_score", "mean"),
        first_purchase_date=("order_purchase_timestamp", "min"),
        last_purchase_date=("order_purchase_timestamp", "max"),
        customer_city=("customer_city", "first"),
        customer_state=("customer_state", "first")
    ).reset_index()

    # Quintile scoring
    # Recency: lower is better (5 = most recent, 1 = least recent)
    rfm["R_Score"] = pd.qcut(rfm["recency"], q=5, labels=[5, 4, 3, 2, 1]).astype(int)

    # Frequency: heavily skewed (97% single purchase)
    # Custom robust binning for frequency: 1 order = score 1; 2 orders = score 3; 3+ orders = score 5
    rfm["F_Score"] = np.where(
        rfm["frequency"] == 1, 1,
        np.where(rfm["frequency"] == 2, 3, 5)
    )

    # Monetary: higher spending is better (1 to 5)
    rfm["M_Score"] = pd.qcut(rfm["monetary"], q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["RFM_Score"] = rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str) + rfm["M_Score"].astype(str)

    # Business Segment Assignment Function
    def assign_segment(row):
        r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]
        if r >= 4 and f >= 3:
            return "Champions"
        elif r >= 3 and f >= 3:
            return "Loyal Customers"
        elif r >= 4 and f == 1 and m >= 4:
            return "Potential Loyalists"
        elif r >= 4 and f == 1:
            return "New Customers"
        elif r == 3 and f == 1:
            return "Promising Customers"
        elif r == 2 and f >= 3:
            return "At Risk"
        elif r == 1 and f >= 3:
            return "Cannot Lose Them"
        elif r == 2 and f == 1:
            return "Hibernating"
        else:
            return "Lost Customers"

    rfm["Segment"] = rfm.apply(assign_segment, axis=1)

    # RFM Segment Summary
    segment_summary = rfm.groupby("Segment").agg(
        customer_count=("customer_unique_id", "count"),
        total_revenue=("monetary", "sum"),
        avg_recency=("recency", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
        avg_review=("avg_review_score", "mean")
    ).reset_index()

    segment_summary["customer_pct"] = (segment_summary["customer_count"] / len(rfm)) * 100
    segment_summary["revenue_pct"] = (segment_summary["total_revenue"] / rfm["monetary"].sum()) * 100
    segment_summary = segment_summary.sort_values("total_revenue", ascending=False).round(2)

    rfm.to_csv(PROCESSED_DIR / "rfm_customer_segments.csv", index=False)
    segment_summary.to_csv(PROCESSED_DIR / "rfm_segment_summary.csv", index=False)
    print("  [SAVED] rfm_customer_segments.csv")
    print("  [SAVED] rfm_segment_summary.csv")
    print("\nRFM Segment Summary Table:")
    print(segment_summary.to_string(index=False))

    # =========================================================================
    # STEP 7: DELIVERY DELAY AND REVIEW ANALYSIS
    # =========================================================================
    print("\n" + "=" * 70)
    print("STEP 7: DELIVERY DELAY & REVIEW ANALYSIS")
    print("=" * 70)

    delivered_orders = delivered_master[delivered_master["order_delivered_customer_date"].notna()].copy()
    on_time = delivered_orders[delivered_orders["delivery_delay_days"] <= 0]
    delayed = delivered_orders[delivered_orders["delivery_delay_days"] > 0]

    on_time_pct = (len(on_time) / len(delivered_orders)) * 100
    late_pct = (len(delayed) / len(delivered_orders)) * 100
    avg_review_ontime = on_time["review_score"].mean()
    avg_review_late = delayed["review_score"].mean()

    # Repeat purchase by delivery performance
    # Customer experienced at least one late delivery vs exclusively on-time
    customer_deliv_exp = delivered_orders.groupby("customer_unique_id").agg(
        total_orders=("order_id", "nunique"),
        late_orders=("is_delayed", "sum")
    ).reset_index()
    customer_deliv_exp["experienced_delay"] = np.where(customer_deliv_exp["late_orders"] > 0, "Experienced Late Delivery", "Always On-Time")
    customer_deliv_exp["is_repeat"] = customer_deliv_exp["total_orders"] > 1

    deliv_repeat_summary = customer_deliv_exp.groupby("experienced_delay").agg(
        total_customers=("customer_unique_id", "count"),
        repeat_customers=("is_repeat", "sum"),
        repeat_rate=("is_repeat", "mean")
    ).reset_index()
    deliv_repeat_summary["repeat_rate_pct"] = deliv_repeat_summary["repeat_rate"] * 100

    print(f"On-time Deliveries:        {len(on_time):,} ({on_time_pct:.2f}%) | Avg Review: {avg_review_ontime:.2f} *")
    print(f"Late Deliveries:           {len(delayed):,} ({late_pct:.2f}%)  | Avg Review: {avg_review_late:.2f} *")
    print(f"Review Drop for Late Deliveries: -{avg_review_ontime - avg_review_late:.2f} stars ({((avg_review_ontime - avg_review_late)/avg_review_ontime)*100:.1f}% reduction)")
    print("\nRepeat Purchase by Delivery Experience:")
    print(deliv_repeat_summary.to_string(index=False))

    deliv_analysis_df = pd.DataFrame({
        "delivery_category": ["On-Time Orders", "Delayed Orders"],
        "order_count": [len(on_time), len(delayed)],
        "percentage": [round(on_time_pct, 2), round(late_pct, 2)],
        "avg_review_score": [round(avg_review_ontime, 2), round(avg_review_late, 2)],
        "1_star_review_pct": [round((on_time["review_score"] == 1).mean() * 100, 2), round((delayed["review_score"] == 1).mean() * 100, 2)],
        "5_star_review_pct": [round((on_time["review_score"] == 5).mean() * 100, 2), round((delayed["review_score"] == 5).mean() * 100, 2)]
    })
    deliv_analysis_df.to_csv(PROCESSED_DIR / "delivery_delay_analysis.csv", index=False)
    deliv_repeat_summary.to_csv(PROCESSED_DIR / "delivery_repeat_summary.csv", index=False)
    print("  [SAVED] delivery_delay_analysis.csv & delivery_repeat_summary.csv")

    # =========================================================================
    # GENERATE PUBLICATION-QUALITY DASHBOARD CHARTS (5 PAGES)
    # =========================================================================
    print("\n" + "=" * 70)
    print("GENERATING DASHBOARD VISUALIZATIONS (PAGES 1 - 5)")
    print("=" * 70)

    NAVY = "#0F172A"
    TEAL = "#0EA5E9"
    ACCENT_GREEN = "#10B981"
    ACCENT_RED = "#EF4444"
    AMBER = "#F59E0B"

    # --- PAGE 1: EXECUTIVE OVERVIEW ---
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.patch.set_facecolor("white")
    fig.suptitle("PAGE 1: Executive Overview Dashboard\nTotal Revenue: R$ 15.42M | Orders: 96,478 | AOV: R$ 159.85 | Repeat Rate: 3.12%",
                 fontsize=18, fontweight="bold", color=NAVY, y=0.98)

    # 1.1 Monthly Revenue Trend
    ax1 = axes[0, 0]
    monthly_trend_filtered = monthly_trend[monthly_trend["purchase_month"] >= "2017-01"].copy()
    ax1.plot(monthly_trend_filtered["month_str"], monthly_trend_filtered["revenue"] / 1e6,
             color=TEAL, marker="o", linewidth=2.5, markersize=6)
    ax1.fill_between(monthly_trend_filtered["month_str"], monthly_trend_filtered["revenue"] / 1e6,
                     alpha=0.15, color=TEAL)
    ax1.set_title("Monthly Revenue Trend (R$ Millions)", fontsize=13, fontweight="bold", color=NAVY)
    ax1.set_ylabel("Revenue (R$ M)")
    ax1.tick_params(axis="x", rotation=45)
    ax1.grid(True, linestyle="--", alpha=0.5)

    # 1.2 Top 10 Product Categories by Revenue
    ax2 = axes[0, 1]
    top10_cat = top_categories.head(10).sort_values("total_revenue", ascending=True)
    bars = ax2.barh(top10_cat["product_category_name_english"], top10_cat["total_revenue"] / 1e3, color="#38BDF8")
    ax2.set_title("Top 10 Product Categories by Revenue (R$ Thousands)", fontsize=13, fontweight="bold", color=NAVY)
    ax2.set_xlabel("Revenue (R$ K)")
    for bar in bars:
        w = bar.get_width()
        ax2.text(w + 10, bar.get_y() + bar.get_height()/2, f"R${w:,.0f}K", va="center", fontsize=9, color=NAVY)

    # 1.3 Revenue by Top 10 Brazilian States
    ax3 = axes[1, 0]
    top10_states = state_dist.head(10).sort_values("total_revenue", ascending=False)
    ax3.bar(top10_states["customer_state"], top10_states["revenue_share_pct"], color="#6366F1")
    ax3.set_title("Revenue Contribution by Top 10 States (%)", fontsize=13, fontweight="bold", color=NAVY)
    ax3.set_ylabel("Share of Revenue (%)")
    for i, v in enumerate(top10_states["revenue_share_pct"]):
        ax3.text(i, v + 0.8, f"{v:.1f}%", ha="center", fontsize=9, fontweight="bold", color=NAVY)

    # 1.4 New vs Repeat Customer Orders
    ax4 = axes[1, 1]
    repeat_labels = ["Single Order Customers", "Repeat Customers"]
    repeat_vals = [single_order_customers_count, repeat_customers_count]
    ax4.pie(repeat_vals, labels=repeat_labels, autopct="%1.2f%%", startangle=140,
            colors=["#CBD5E1", ACCENT_GREEN], explode=(0, 0.15),
            textprops={"fontsize": 11, "fontweight": "bold", "color": NAVY})
    ax4.set_title("Customer Retention Split\n(96.88% One-Time vs 3.12% Repeat)", fontsize=13, fontweight="bold", color=NAVY)

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(DASHBOARD_IMG_DIR / "page1_executive_overview.png", dpi=160, bbox_inches="tight")
    plt.close()
    print("  [SAVED] page1_executive_overview.png")

    # --- PAGE 2: COHORT RETENTION HEATMAP ---
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor("white")
    heatmap_data = retention_matrix_clean.iloc[1:18, :13] # Jan 2017 to mid 2018
    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt=".2f",
        cmap="Blues",
        linewidths=0.8,
        linecolor="white",
        cbar_kws={"label": "Retention Rate (%)"},
        vmin=0.0,
        vmax=1.5,
        ax=ax
    )
    ax.set_title("PAGE 2: Customer Retention Cohort Analysis (Monthly % Retention)\nKey Finding: Month 1 Retention Averages 0.45% - 0.70%, revealing sharp first-purchase churn",
                 fontsize=15, fontweight="bold", color=NAVY, pad=18)
    ax.set_xlabel("Months Since First Purchase (Cohort Index)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Cohort Month (First Purchase)", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(DASHBOARD_IMG_DIR / "page2_cohort_analysis.png", dpi=160, bbox_inches="tight")
    plt.close()
    print("  [SAVED] page2_cohort_analysis.png")

    # --- PAGE 3: RFM CUSTOMER SEGMENTATION ---
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    fig.patch.set_facecolor("white")
    fig.suptitle("PAGE 3: RFM Customer Segmentation & Revenue Contribution\nPrioritizing High-Value Customer Retention",
                 fontsize=16, fontweight="bold", color=NAVY)

    # 3.1 Customer Count by Segment
    ax1 = axes[0]
    seg_sort_count = segment_summary.sort_values("customer_count", ascending=True)
    palette_counts = sns.color_palette("viridis", len(seg_sort_count))
    bars1 = ax1.barh(seg_sort_count["Segment"], seg_sort_count["customer_count"], color=palette_counts)
    ax1.set_title("Customer Count by RFM Segment", fontsize=13, fontweight="bold", color=NAVY)
    ax1.set_xlabel("Number of Customers")
    for b in bars1:
        w = b.get_width()
        ax1.text(w + 300, b.get_y() + b.get_height()/2, f"{w:,} ({w/len(rfm)*100:.1f}%)", va="center", fontsize=9)

    # 3.2 Revenue by Segment
    ax2 = axes[1]
    seg_sort_rev = segment_summary.sort_values("total_revenue", ascending=True)
    palette_rev = sns.color_palette("mako", len(seg_sort_rev))
    bars2 = ax2.barh(seg_sort_rev["Segment"], seg_sort_rev["total_revenue"] / 1e6, color=palette_rev)
    ax2.set_title("Total Revenue by RFM Segment (R$ Millions)", fontsize=13, fontweight="bold", color=NAVY)
    ax2.set_xlabel("Revenue (R$ Millions)")
    for b in bars2:
        w = b.get_width()
        ax2.text(w + 0.05, b.get_y() + b.get_height()/2, f"R${w:.2f}M ({w/(rfm['monetary'].sum()/1e6)*100:.1f}%)", va="center", fontsize=9)

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(DASHBOARD_IMG_DIR / "page3_rfm_segmentation.png", dpi=160, bbox_inches="tight")
    plt.close()
    print("  [SAVED] page3_rfm_segmentation.png")

    # --- PAGE 4: DELIVERY PERFORMANCE & CUSTOMER SATISFACTION ---
    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    fig.patch.set_facecolor("white")
    fig.suptitle("PAGE 4: Delivery Delay & Review Satisfaction Analysis\nDirect Impact of Logistics Performance on Customer Sentiment",
                 fontsize=16, fontweight="bold", color=NAVY, y=0.98)

    # 4.1 On-time vs Late Delivery Split
    ax1 = axes[0, 0]
    ax1.pie([on_time_pct, late_pct], labels=["On-Time Orders", "Delayed Orders"], autopct="%1.1f%%",
            colors=[ACCENT_GREEN, ACCENT_RED], startangle=140, explode=(0, 0.1),
            textprops={"fontsize": 11, "fontweight": "bold"})
    ax1.set_title(f"Delivery Fulfillment Performance\n({len(on_time):,} On-Time vs {len(delayed):,} Delayed)", fontsize=12, fontweight="bold")

    # 4.2 Average Review Score by Status
    ax2 = axes[0, 1]
    statuses = ["On-Time Orders", "Delayed Orders"]
    scores = [avg_review_ontime, avg_review_late]
    bars = ax2.bar(statuses, scores, color=[ACCENT_GREEN, ACCENT_RED], width=0.5)
    ax2.set_ylim(0, 5)
    ax2.set_ylabel("Average Review Score (1 - 5)")
    ax2.set_title(f"Customer Rating Drop: {avg_review_ontime:.2f} * -> {avg_review_late:.2f} * (-{avg_review_ontime - avg_review_late:.2f} stars)", fontsize=12, fontweight="bold")
    for b in bars:
        ax2.text(b.get_x() + b.get_width()/2, b.get_height() + 0.15, f"{b.get_height():.2f} / 5.0", ha="center", fontsize=11, fontweight="bold")

    # 4.3 Review Score Distribution (On-Time vs Late)
    ax3 = axes[1, 0]
    review_dist = pd.crosstab(delivered_orders["delivery_status"], delivered_orders["review_score"], normalize="index") * 100
    review_dist.loc[["On-Time", "Late"]].plot(kind="bar", stacked=True, ax=ax3, colormap="RdYlGn", edgecolor="white")
    ax3.set_title("Review Star Breakdown: On-Time vs Late (%)", fontsize=12, fontweight="bold")
    ax3.set_ylabel("Percentage of Reviews (%)")
    ax3.tick_params(axis="x", rotation=0)
    ax3.legend(title="Review Stars", bbox_to_anchor=(1.02, 1), loc="upper left")

    # 4.4 Repeat Purchase Rate by Delivery Experience
    ax4 = axes[1, 1]
    exp_labels = deliv_repeat_summary["experienced_delay"]
    exp_rates = deliv_repeat_summary["repeat_rate_pct"]
    bars_exp = ax4.bar(exp_labels, exp_rates, color=[ACCENT_GREEN, AMBER], width=0.5)
    ax4.set_title("Customer Repeat Purchase Rate by Delivery Experience", fontsize=12, fontweight="bold")
    ax4.set_ylabel("Repeat Purchase Rate (%)")
    for b in bars_exp:
        ax4.text(b.get_x() + b.get_width()/2, b.get_height() + 0.1, f"{b.get_height():.2f}%", ha="center", fontsize=11, fontweight="bold")

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(DASHBOARD_IMG_DIR / "page4_delivery_satisfaction.png", dpi=160, bbox_inches="tight")
    plt.close()
    print("  [SAVED] page4_delivery_satisfaction.png")

    # --- PAGE 5: BUSINESS RECOMMENDATIONS & STRATEGY ---
    fig, ax = plt.subplots(figsize=(15, 9))
    fig.patch.set_facecolor("white")
    ax.axis("off")

    recommendations_text = """
========================================================================================
PAGE 5: STRATEGIC BUSINESS RECOMMENDATIONS & RETENTION ACTION PLAN
========================================================================================

1. CRITICAL DIAGNOSIS
   * Overall Retention Crisis: Only 3.12% of customers return for a second purchase.
   * Month 1 Cohort Drop-off: 99.4% drop-off in Month 1 across all cohorts.
   * Delivery Experience Gap: Late delivery orders suffer a catastrophic drop from 4.29 to 2.27 stars
     and increase 1-star reviews by 6x (from 5.5% to 54.2%).

2. TARGET SEGMENTS TO RESCUE FIRST
   [Priority 1] 'At Risk' Customers (300+ customers, R$ 70K+ revenue)
                Action: Targeted VIP win-back email sequence offering free freight + 15% discount.
   [Priority 2] 'Champions' & 'Loyal Customers' (500+ customers, R$ 130K+ revenue)
                Action: Exclusive loyalty reward program, early access to new releases, priority shipping.
   [Priority 3] 'Potential Loyalists' (18,000+ customers, R$ 5.8M revenue)
                Action: Automated second-purchase trigger (sent 21 days post-delivery) with cross-sell items.

3. LOGISTICS SLA & OPERATIONAL FIXES
   * Implement automated proactive delay notification with compensatory R$ 20 coupon before customer complains.
   * Audit shipping routes in high-delay states (RJ, BA, MA) with regional 3PL partners.
   * Tighten seller fulfillment SLA: penalize sellers with dispatch delay > 48 hours.

4. ESTIMATED REVENUE IMPACT (PROJECTED)
   * Increasing customer retention from 3.12% to 6.00% (+2.88 pp) creates ~2,760 additional repeat orders.
   * At an Average Order Value of R$ 159.85, this yields an estimated R$ 441,000+ incremental ARR.
========================================================================================
"""
    ax.text(0.05, 0.95, recommendations_text, fontsize=12, family="monospace",
            va="top", ha="left", color=NAVY, bbox=dict(boxstyle="round,pad=1", facecolor="#F1F5F9", edgecolor="#CBD5E1", linewidth=1.5))
    plt.tight_layout()
    plt.savefig(DASHBOARD_IMG_DIR / "page5_recommendations_action_plan.png", dpi=160, bbox_inches="tight")
    plt.close()
    print("  [SAVED] page5_recommendations_action_plan.png")

    print("\n" + "=" * 70)
    print("PIPELINE EXECUTION COMPLETE! ALL ARTIFACTS AND DATASETS SAVED.")
    print("=" * 70)

if __name__ == "__main__":
    run_pipeline()

