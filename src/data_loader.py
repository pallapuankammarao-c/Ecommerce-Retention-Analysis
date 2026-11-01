"""
Data Loader Module
==================
Loads all Olist Brazilian E-Commerce CSV files from the data/raw/ directory.
Provides functions to load individual datasets or all datasets at once.
"""

import os
import pandas as pd
from pathlib import Path


# -------------------------------------------------------------------
# Path configuration
# -------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

# Expected CSV filenames from the Olist dataset
DATASET_FILES = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}


def load_dataset(name: str, data_dir: Path = RAW_DATA_DIR) -> pd.DataFrame:
    """
    Load a single dataset by its short name.

    Parameters
    ----------
    name : str
        One of: customers, orders, order_items, order_payments,
        order_reviews, products, sellers, geolocation, category_translation
    data_dir : Path
        Directory containing the CSV files. Defaults to data/raw/.

    Returns
    -------
    pd.DataFrame
    """
    if name not in DATASET_FILES:
        raise ValueError(
            f"Unknown dataset '{name}'. "
            f"Choose from: {list(DATASET_FILES.keys())}"
        )

    filepath = data_dir / DATASET_FILES[name]
    if not filepath.exists():
        raise FileNotFoundError(
            f"File not found: {filepath}\n"
            f"Please download the Olist dataset from Kaggle and place "
            f"the CSV files in '{data_dir}'."
        )

    df = pd.read_csv(filepath)
    print(f"[OK] Loaded {name}: {df.shape[0]:,} rows x {df.shape[1]} columns")
    return df


def load_all_datasets(data_dir: Path = RAW_DATA_DIR) -> dict[str, pd.DataFrame]:
    """
    Load all Olist CSV files into a dictionary of DataFrames.

    Parameters
    ----------
    data_dir : Path
        Directory containing the CSV files. Defaults to data/raw/.

    Returns
    -------
    dict[str, pd.DataFrame]
        Keys are the short dataset names, values are DataFrames.
    """
    datasets = {}
    print("=" * 60)
    print("  Loading Olist Brazilian E-Commerce Dataset")
    print("=" * 60)

    for name in DATASET_FILES:
        try:
            datasets[name] = load_dataset(name, data_dir)
        except FileNotFoundError as e:
            print(f"[WARN] Skipped {name}: {e}")

    print("=" * 60)
    total_rows = sum(df.shape[0] for df in datasets.values())
    print(f"Total datasets loaded: {len(datasets)}/{len(DATASET_FILES)}")
    print(f"Total rows across all datasets: {total_rows:,}")
    print("=" * 60)

    return datasets


def dataset_summary(datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Generate a summary table for all loaded datasets.

    Returns a DataFrame with dataset name, rows, columns, 
    missing values count, and duplicate rows count.
    """
    summary_rows = []
    for name, df in datasets.items():
        summary_rows.append({
            "Dataset": name,
            "File": DATASET_FILES[name],
            "Rows": df.shape[0],
            "Columns": df.shape[1],
            "Missing Values": df.isnull().sum().sum(),
            "Duplicate Rows": df.duplicated().sum(),
            "Memory (MB)": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
        })
    return pd.DataFrame(summary_rows)


def check_data_files(data_dir: Path = RAW_DATA_DIR) -> dict[str, bool]:
    """
    Check which expected CSV files exist in the data directory.

    Returns
    -------
    dict[str, bool]
        Keys are dataset names, values are True if the file exists.
    """
    status = {}
    print(f"\nChecking files in: {data_dir}\n")
    for name, filename in DATASET_FILES.items():
        exists = (data_dir / filename).exists()
        status[name] = exists
        icon = "[OK]" if exists else "[MISSING]"
        print(f"  {icon} {filename}")

    found = sum(status.values())
    print(f"\n  {found}/{len(DATASET_FILES)} files found.\n")
    return status


# -------------------------------------------------------------------
# Run directly to verify data availability
# -------------------------------------------------------------------
if __name__ == "__main__":
    check_data_files()
