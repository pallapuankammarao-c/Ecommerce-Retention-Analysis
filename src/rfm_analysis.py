"""
RFM Analysis Module
====================
Functions for Recency-Frequency-Monetary customer segmentation.
Scores customers from 1–5 on each dimension and assigns named segments.
"""

import pandas as pd
import numpy as np
from datetime import datetime


# -------------------------------------------------------------------
# RFM Segment naming rules
# -------------------------------------------------------------------
SEGMENT_MAP = {
    (5, 5, 5): "Champions",
    (5, 5, 4): "Champions",
    (5, 4, 5): "Champions",
    (5, 4, 4): "Champions",
    (4, 5, 5): "Champions",
    (4, 5, 4): "Loyal Customers",
    (4, 4, 5): "Loyal Customers",
    (4, 4, 4): "Loyal Customers",
    (4, 4, 3): "Loyal Customers",
    (3, 5, 5): "Loyal Customers",
    (3, 5, 4): "Loyal Customers",
    (3, 4, 5): "Loyal Customers",
    (3, 4, 4): "Loyal Customers",
    (5, 3, 5): "Potential Loyalists",
    (5, 3, 4): "Potential Loyalists",
    (5, 3, 3): "Potential Loyalists",
    (5, 2, 3): "Potential Loyalists",
    (4, 3, 5): "Potential Loyalists",
    (4, 3, 4): "Potential Loyalists",
    (4, 3, 3): "Potential Loyalists",
    (4, 2, 3): "Potential Loyalists",
    (5, 1, 5): "New Customers",
    (5, 1, 4): "New Customers",
    (5, 1, 3): "New Customers",
    (5, 1, 2): "New Customers",
    (5, 1, 1): "New Customers",
    (4, 1, 4): "New Customers",
    (4, 1, 3): "New Customers",
    (4, 1, 2): "New Customers",
    (4, 1, 1): "New Customers",
    (5, 2, 5): "Promising Customers",
    (5, 2, 4): "Promising Customers",
    (5, 2, 2): "Promising Customers",
    (5, 2, 1): "Promising Customers",
    (4, 2, 5): "Promising Customers",
    (4, 2, 4): "Promising Customers",
    (4, 2, 2): "Promising Customers",
    (4, 2, 1): "Promising Customers",
    (3, 3, 5): "Promising Customers",
    (3, 3, 4): "Promising Customers",
    (3, 3, 3): "Promising Customers",
    (3, 2, 5): "Promising Customers",
    (3, 2, 4): "Promising Customers",
    (3, 2, 3): "Promising Customers",
    (3, 2, 2): "Promising Customers",
    (3, 2, 1): "Promising Customers",
    (3, 1, 5): "Promising Customers",
    (3, 1, 4): "Promising Customers",
    (3, 1, 3): "Promising Customers",
    (3, 1, 2): "Promising Customers",
    (3, 1, 1): "Promising Customers",
    (2, 5, 5): "At Risk",
    (2, 5, 4): "At Risk",
    (2, 5, 3): "At Risk",
    (2, 4, 5): "At Risk",
    (2, 4, 4): "At Risk",
    (2, 4, 3): "At Risk",
    (2, 3, 5): "At Risk",
    (2, 3, 4): "At Risk",
    (2, 3, 3): "At Risk",
    (2, 3, 2): "At Risk",
    (2, 2, 5): "At Risk",
    (2, 2, 4): "At Risk",
    (2, 2, 3): "At Risk",
    (2, 2, 2): "At Risk",
    (2, 2, 1): "At Risk",
    (2, 1, 5): "At Risk",
    (2, 1, 4): "At Risk",
    (2, 1, 3): "At Risk",
    (2, 1, 2): "At Risk",
    (2, 1, 1): "At Risk",
    (1, 5, 5): "Cannot Lose Them",
    (1, 5, 4): "Cannot Lose Them",
    (1, 5, 3): "Cannot Lose Them",
    (1, 5, 2): "Cannot Lose Them",
    (1, 5, 1): "Cannot Lose Them",
    (1, 4, 5): "Cannot Lose Them",
    (1, 4, 4): "Cannot Lose Them",
    (1, 4, 3): "Cannot Lose Them",
    (1, 4, 2): "Cannot Lose Them",
    (1, 4, 1): "Cannot Lose Them",
    (1, 3, 5): "Hibernating",
    (1, 3, 4): "Hibernating",
    (1, 3, 3): "Hibernating",
    (1, 3, 2): "Hibernating",
    (1, 3, 1): "Hibernating",
    (1, 2, 5): "Hibernating",
    (1, 2, 4): "Hibernating",
    (1, 2, 3): "Hibernating",
    (1, 2, 2): "Hibernating",
    (1, 2, 1): "Hibernating",
    (1, 1, 5): "Lost Customers",
    (1, 1, 4): "Lost Customers",
    (1, 1, 3): "Lost Customers",
    (1, 1, 2): "Lost Customers",
    (1, 1, 1): "Lost Customers",
    (2, 1, 1): "Lost Customers",
    (3, 3, 1): "Promising Customers",
    (3, 3, 2): "Promising Customers",
    (3, 4, 3): "Loyal Customers",
    (3, 4, 2): "Loyal Customers",
    (3, 4, 1): "Loyal Customers",
    (3, 5, 3): "Loyal Customers",
    (3, 5, 2): "Loyal Customers",
    (3, 5, 1): "Loyal Customers",
    (2, 5, 2): "At Risk",
    (2, 5, 1): "At Risk",
    (2, 4, 2): "At Risk",
    (2, 4, 1): "At Risk",
    (2, 3, 1): "At Risk",
}


def calculate_rfm(
    orders_df: pd.DataFrame,
    order_items_df: pd.DataFrame,
    analysis_date: str | None = None,
) -> pd.DataFrame:
    """
    Calculate RFM metrics for each customer.

    Parameters
    ----------
    orders_df : pd.DataFrame
        Must contain: customer_unique_id, order_id, order_purchase_timestamp,
        order_status
    order_items_df : pd.DataFrame
        Must contain: order_id, price, freight_value
    analysis_date : str, optional
        Reference date for recency calculation (YYYY-MM-DD).
        Defaults to the day after the most recent order.

    Returns
    -------
    pd.DataFrame
        Customer-level RFM table with columns:
        customer_unique_id, recency, frequency, monetary
    """
    # Filter to delivered orders only
    delivered = orders_df[orders_df["order_status"] == "delivered"].copy()
    delivered["order_purchase_timestamp"] = pd.to_datetime(
        delivered["order_purchase_timestamp"]
    )

    # Set analysis date
    if analysis_date is None:
        analysis_date = delivered["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
    else:
        analysis_date = pd.to_datetime(analysis_date)

    # Merge with order items for monetary values
    order_revenue = order_items_df.groupby("order_id").agg(
        order_value=("price", "sum"),
        freight=("freight_value", "sum"),
    ).reset_index()
    order_revenue["total_value"] = order_revenue["order_value"] + order_revenue["freight"]

    merged = delivered.merge(order_revenue, on="order_id", how="inner")

    # Calculate RFM
    rfm = merged.groupby("customer_unique_id").agg(
        recency=("order_purchase_timestamp", lambda x: (analysis_date - x.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("total_value", "sum"),
    ).reset_index()

    rfm["monetary"] = rfm["monetary"].round(2)

    print(f"[OK] RFM calculated for {len(rfm):,} customers")
    print(f"   Analysis date: {analysis_date.strftime('%Y-%m-%d')}")
    print(f"   Recency range: {rfm['recency'].min()} - {rfm['recency'].max()} days")
    print(f"   Frequency range: {rfm['frequency'].min()} - {rfm['frequency'].max()} orders")
    print(f"   Monetary range: R${rfm['monetary'].min():.2f} - R${rfm['monetary'].max():.2f}")

    return rfm


def assign_rfm_scores(rfm_df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign R, F, M scores from 1 (worst) to 5 (best) using quintiles.

    Recency: Lower days = better = higher score (reversed).
    Frequency: Higher = better = higher score.
    Monetary: Higher = better = higher score.
    """
    df = rfm_df.copy()

    # R score (reverse: low recency = high score)
    df["R"] = pd.qcut(df["recency"], q=5, labels=[5, 4, 3, 2, 1], duplicates="drop").astype(int)

    # F score
    df["F"] = pd.qcut(df["frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5], duplicates="drop").astype(int)

    # M score
    df["M"] = pd.qcut(df["monetary"], q=5, labels=[1, 2, 3, 4, 5], duplicates="drop").astype(int)

    # Combined RFM score
    df["RFM_Score"] = df["R"].astype(str) + df["F"].astype(str) + df["M"].astype(str)

    print(f"\n[INFO] RFM Score Distribution:")
    print(f"   R scores: {df['R'].value_counts().sort_index().to_dict()}")
    print(f"   F scores: {df['F'].value_counts().sort_index().to_dict()}")
    print(f"   M scores: {df['M'].value_counts().sort_index().to_dict()}")

    return df


def assign_segments(rfm_scored: pd.DataFrame) -> pd.DataFrame:
    """
    Map RFM score combinations to named customer segments.

    Uses the SEGMENT_MAP lookup. Unmapped combinations default
    to a rule-based fallback.
    """
    df = rfm_scored.copy()

    def get_segment(row):
        key = (row["R"], row["F"], row["M"])
        if key in SEGMENT_MAP:
            return SEGMENT_MAP[key]
        # Fallback rules for any unmapped combinations
        r, f, m = key
        if r >= 4 and f >= 4:
            return "Champions"
        elif r >= 3 and f >= 3:
            return "Loyal Customers"
        elif r >= 4 and f == 1:
            return "New Customers"
        elif r >= 3:
            return "Promising Customers"
        elif r == 2:
            return "At Risk"
        elif r == 1 and f >= 4:
            return "Cannot Lose Them"
        elif r == 1 and f >= 2:
            return "Hibernating"
        else:
            return "Lost Customers"

    df["Segment"] = df.apply(get_segment, axis=1)

    print(f"\n[SEGMENTS] Customer Segments:")
    segment_counts = df["Segment"].value_counts()
    for seg, count in segment_counts.items():
        pct = count / len(df) * 100
        print(f"   {seg}: {count:,} ({pct:.1f}%)")

    return df


def segment_summary(rfm_segmented: pd.DataFrame) -> pd.DataFrame:
    """
    Create a summary report by RFM segment.

    Returns
    -------
    pd.DataFrame
        Segment-level metrics: count, avg R/F/M, total revenue, revenue share.
    """
    summary = rfm_segmented.groupby("Segment").agg(
        customer_count=("customer_unique_id", "count"),
        avg_recency=("recency", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
        total_revenue=("monetary", "sum"),
    ).round(2)

    summary["revenue_pct"] = (
        summary["total_revenue"] / summary["total_revenue"].sum() * 100
    ).round(1)

    summary = summary.sort_values("total_revenue", ascending=False)
    return summary.reset_index()
