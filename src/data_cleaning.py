"""
Data Cleaning Module
====================
Functions for cleaning and preprocessing the Olist dataset.
Handles missing values, duplicates, date conversions, and 
creates the master analytical dataset.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def convert_date_columns(df: pd.DataFrame, date_columns: list[str]) -> pd.DataFrame:
    """Convert specified columns to datetime format."""
    df = df.copy()
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            print(f"  [OK] Converted '{col}' to datetime")
    return df


def remove_duplicates(df: pd.DataFrame, name: str = "DataFrame") -> pd.DataFrame:
    """Remove duplicate rows and report the count."""
    n_before = len(df)
    df = df.drop_duplicates()
    n_removed = n_before - len(df)
    if n_removed > 0:
        print(f"  [REMOVED] Removed {n_removed:,} duplicate rows from {name}")
    else:
        print(f"  [OK] No duplicates found in {name}")
    return df


def handle_missing_values(df: pd.DataFrame, name: str = "DataFrame") -> pd.DataFrame:
    """
    Report and handle missing values. Strategy depends on column type.
    Returns the cleaned DataFrame.
    """
    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if len(missing) == 0:
        print(f"  [OK] No missing values in {name}")
        return df

    print(f"\n  [WARN] Missing values in {name}:")
    for col, count in missing.items():
        pct = count / len(df) * 100
        print(f"      {col}: {count:,} ({pct:.1f}%)")

    return df


def validate_order_statuses(orders_df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate order statuses and report distribution.
    Valid statuses: delivered, shipped, invoiced, processing,
                    created, approved, canceled, unavailable
    """
    valid_statuses = [
        "delivered", "shipped", "invoiced", "processing",
        "created", "approved", "canceled", "unavailable"
    ]

    print("\n  [INFO] Order Status Distribution:")
    status_counts = orders_df["order_status"].value_counts()
    for status, count in status_counts.items():
        pct = count / len(orders_df) * 100
        marker = "[OK]" if status in valid_statuses else "[INVALID]"
        print(f"      {marker} {status}: {count:,} ({pct:.1f}%)")

    invalid = orders_df[~orders_df["order_status"].isin(valid_statuses)]
    if len(invalid) > 0:
        print(f"\n  [WARN] Found {len(invalid):,} orders with invalid status")

    return orders_df


def create_master_dataset(
    orders: pd.DataFrame,
    order_items: pd.DataFrame,
    customers: pd.DataFrame,
    payments: pd.DataFrame,
    reviews: pd.DataFrame,
    products: pd.DataFrame,
    category_translation: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge individual datasets into a single master analytical dataset.

    Joins:
        orders -> order_items -> customers -> payments -> reviews -> products -> category_translation

    Returns
    -------
    pd.DataFrame
        Master dataset with all relevant columns.
    """
    print("\n[BUILD] Building Master Analytical Dataset...")

    # 1. Orders + Order Items
    master = orders.merge(order_items, on="order_id", how="inner")
    print(f"   orders + order_items: {len(master):,} rows")

    # 2. + Customers
    master = master.merge(customers, on="customer_id", how="left")
    print(f"   + customers: {len(master):,} rows")

    # 3. + Payments (aggregated per order)
    payment_agg = payments.groupby("order_id").agg(
        total_payment=("payment_value", "sum"),
        payment_installments=("payment_installments", "max"),
        payment_type=("payment_type", "first"),
    ).reset_index()
    master = master.merge(payment_agg, on="order_id", how="left")
    print(f"   + payments: {len(master):,} rows")

    # 4. + Reviews (first review per order)
    if "review_id" in reviews.columns:
        review_first = reviews.drop_duplicates(subset="order_id", keep="first")
        review_cols = ["order_id", "review_score"]
        if "review_comment_message" in review_first.columns:
            review_cols.append("review_comment_message")
        master = master.merge(review_first[review_cols], on="order_id", how="left")
        print(f"   + reviews: {len(master):,} rows")

    # 5. + Products
    master = master.merge(products, on="product_id", how="left")
    print(f"   + products: {len(master):,} rows")

    # 6. + Category Translation
    if "product_category_name" in master.columns:
        master = master.merge(
            category_translation,
            on="product_category_name",
            how="left"
        )
        print(f"   + category_translation: {len(master):,} rows")

    print(f"\n[OK] Master dataset created: {master.shape[0]:,} rows x {master.shape[1]} columns")
    return master


def save_processed_data(
    df: pd.DataFrame,
    filename: str,
    output_dir: Path,
) -> Path:
    """Save processed DataFrame to CSV in the processed data directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / filename
    df.to_csv(filepath, index=False)
    size_mb = filepath.stat().st_size / 1024 / 1024
    print(f"[SAVED] Saved {filename} ({size_mb:.1f} MB) -> {filepath}")
    return filepath
