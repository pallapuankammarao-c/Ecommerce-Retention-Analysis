"""
Cohort Analysis Module
======================
Functions for creating customer cohorts based on first purchase month
and calculating monthly retention rates.
"""

import pandas as pd
import numpy as np


def assign_cohort(orders_df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign each customer to a cohort based on their first purchase month.

    Parameters
    ----------
    orders_df : pd.DataFrame
        Must contain 'customer_unique_id' and 'order_purchase_timestamp'.

    Returns
    -------
    pd.DataFrame
        Original DataFrame with added 'cohort_month' and 'order_month' columns.
    """
    df = orders_df.copy()

    # Ensure datetime
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])

    # Order month (truncated to first day of month)
    df["order_month"] = df["order_purchase_timestamp"].dt.to_period("M")

    # Cohort month = first purchase month per customer
    df["cohort_month"] = df.groupby("customer_unique_id")[
        "order_month"
    ].transform("min")

    return df


def build_cohort_matrix(cohort_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a cohort retention matrix.

    Rows = cohort month, Columns = months since first purchase (0, 1, 2, ...).
    Values = number of unique customers active in each period.

    Parameters
    ----------
    cohort_df : pd.DataFrame
        Must contain 'customer_unique_id', 'cohort_month', 'order_month'.

    Returns
    -------
    pd.DataFrame
        Cohort matrix with cohort months as rows and period offsets as columns.
    """
    df = cohort_df.copy()

    # Calculate months since cohort month
    df["cohort_index"] = (
        df["order_month"].astype(int) - df["cohort_month"].astype(int)
    )

    # Count unique customers per cohort-period combination
    cohort_data = (
        df.groupby(["cohort_month", "cohort_index"])["customer_unique_id"]
        .nunique()
        .reset_index()
        .rename(columns={"customer_unique_id": "customer_count"})
    )

    # Pivot to matrix form
    cohort_matrix = cohort_data.pivot(
        index="cohort_month",
        columns="cohort_index",
        values="customer_count"
    )

    return cohort_matrix


def calculate_retention_rates(cohort_matrix: pd.DataFrame) -> pd.DataFrame:
    """
    Convert raw cohort counts to retention percentages.

    Each row is divided by the cohort size (Month 0 value).

    Parameters
    ----------
    cohort_matrix : pd.DataFrame
        Raw cohort matrix from build_cohort_matrix().

    Returns
    -------
    pd.DataFrame
        Retention rates as percentages (0–100).
    """
    cohort_sizes = cohort_matrix.iloc[:, 0]
    retention = cohort_matrix.divide(cohort_sizes, axis=0) * 100
    return retention.round(2)


def cohort_summary(retention_df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize retention metrics across cohorts.

    Returns
    -------
    pd.DataFrame
        Summary with cohort size, avg retention at Month 1/3/6, etc.
    """
    summary = pd.DataFrame({
        "cohort_month": retention_df.index,
        "cohort_size": retention_df.iloc[:, 0] if 0 in retention_df.columns else None,
    })

    for month in [1, 2, 3, 6]:
        col_name = f"month_{month}_retention"
        if month in retention_df.columns:
            summary[col_name] = retention_df[month].values
        else:
            summary[col_name] = np.nan

    return summary.reset_index(drop=True)
