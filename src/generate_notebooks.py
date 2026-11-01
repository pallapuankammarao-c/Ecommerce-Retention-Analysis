"""
Notebook Generator
==================
Generates all 5 complete Jupyter Notebooks with markdown explanations,
analysis code, and visualizations.
"""

import json
from pathlib import Path

NOTEBOOKS_DIR = Path("d:/Ecommerce-Retention-Analysis/notebooks")
NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)

def make_notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.10"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }

def md_cell(source):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in source.strip().split("\n")]
    }

def code_cell(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in source.strip().split("\n")]
    }

# ==============================================================================
# NOTEBOOK 1: 01_data_exploration.ipynb
# ==============================================================================
nb1_cells = [
    md_cell("""# 01 - Exploratory Data Analysis & Data Profiling
## E-Commerce Customer Retention & Churn Analysis
### Dataset: Olist Brazilian E-Commerce (~100k Orders)

**Objective:**
Perform an initial survey and statistical profiling across all 9 relational CSV files.
Inspect data types, row counts, unique identifier keys, missing value distributions, and duplicate records."""),
    code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Path setup
DATA_DIR = Path('../data/raw')
sns.set_theme(style='whitegrid')
print('Libraries imported successfully.')"""),
    md_cell("""### 1. Load All 9 Relational Datasets"""),
    code_cell("""customers = pd.read_csv(DATA_DIR / 'olist_customers_dataset.csv')
orders = pd.read_csv(DATA_DIR / 'olist_orders_dataset.csv')
order_items = pd.read_csv(DATA_DIR / 'olist_order_items_dataset.csv')
payments = pd.read_csv(DATA_DIR / 'olist_order_payments_dataset.csv')
reviews = pd.read_csv(DATA_DIR / 'olist_order_reviews_dataset.csv')
products = pd.read_csv(DATA_DIR / 'olist_products_dataset.csv')
sellers = pd.read_csv(DATA_DIR / 'olist_sellers_dataset.csv')
geolocation = pd.read_csv(DATA_DIR / 'olist_geolocation_dataset.csv')
translation = pd.read_csv(DATA_DIR / 'product_category_name_translation.csv')

datasets = {
    'Customers': customers,
    'Orders': orders,
    'Order Items': order_items,
    'Payments': payments,
    'Reviews': reviews,
    'Products': products,
    'Sellers': sellers,
    'Geolocation': geolocation,
    'Category Translation': translation
}

summary = []
for name, df in datasets.items():
    summary.append({
        'Dataset': name,
        'Rows': df.shape[0],
        'Columns': df.shape[1],
        'Missing Values': df.isnull().sum().sum(),
        'Duplicate Rows': df.duplicated().sum()
    })
pd.DataFrame(summary)"""),
    md_cell("""### 2. Inspect Entity Keys and Granularity
Understand the relationship between `customer_id` and `customer_unique_id`."""),
    code_cell("""print(f'Total Customer IDs (Orders): {customers[\"customer_id\"].nunique():,}')
print(f'Total Unique Human Customers: {customers[\"customer_unique_id\"].nunique():,}')
repeat_diff = customers[\"customer_id\"].nunique() - customers[\"customer_unique_id\"].nunique()
print(f'Potential Repeat Customer Events: {repeat_diff:,} ({repeat_diff / customers[\"customer_id\"].nunique() * 100:.2f}%)')"""),
    md_cell("""### 3. Order Status Distribution"""),
    code_cell("""order_status_counts = orders['order_status'].value_counts()
print(order_status_counts)

plt.figure(figsize=(10, 5))
sns.barplot(x=order_status_counts.values, y=order_status_counts.index, palette='Blues_r')
plt.title('Order Status Breakdown in Olist Dataset')
plt.xlabel('Count of Orders')
plt.show()"""),
    md_cell("""### 4. Review Score Distribution"""),
    code_cell("""review_counts = reviews['review_score'].value_counts().sort_index()

plt.figure(figsize=(8, 4))
sns.barplot(x=review_counts.index, y=review_counts.values, palette='RdYlGn')
plt.title('Distribution of Customer Review Scores (1 to 5 Stars)')
plt.xlabel('Review Score')
plt.ylabel('Count')
plt.show()""")
]

with open(NOTEBOOKS_DIR / "01_data_exploration.ipynb", "w") as f:
    json.dump(make_notebook(nb1_cells), f, indent=2)

# ==============================================================================
# NOTEBOOK 2: 02_data_cleaning.ipynb
# ==============================================================================
nb2_cells = [
    md_cell("""# 02 - Data Cleaning & Master Analytical Dataset Creation
## Handling Missing Values, Date Conversions, Status Validations & Merges

**Objective:**
Clean and merge all tables into a cohesive order-level analytical dataset for retention and cohort modeling."""),
    code_cell("""import pandas as pd
import numpy as np
from pathlib import Path

RAW_DIR = Path('../data/raw')
PROCESSED_DIR = Path('../data/processed')
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)"""),
    md_cell("""### 1. Load Raw Tables"""),
    code_cell("""customers = pd.read_csv(RAW_DIR / 'olist_customers_dataset.csv')
orders = pd.read_csv(RAW_DIR / 'olist_orders_dataset.csv')
order_items = pd.read_csv(RAW_DIR / 'olist_order_items_dataset.csv')
payments = pd.read_csv(RAW_DIR / 'olist_order_payments_dataset.csv')
reviews = pd.read_csv(RAW_DIR / 'olist_order_reviews_dataset.csv')
products = pd.read_csv(RAW_DIR / 'olist_products_dataset.csv')
category_translation = pd.read_csv(RAW_DIR / 'product_category_name_translation.csv')
print('Datasets loaded successfully.')"""),
    md_cell("""### 2. Parse Datetime Fields with Dayfirst Parsing"""),
    code_cell("""date_cols = [
    'order_purchase_timestamp',
    'order_approved_at',
    'order_delivered_carrier_date',
    'order_delivered_customer_date',
    'order_estimated_delivery_date'
]
for col in date_cols:
    orders[col] = pd.to_datetime(orders[col], format='mixed', dayfirst=True)
    print(f'Converted {col} to datetime.')"""),
    md_cell("""### 3. Aggregate Order Items, Payments & Reviews per Order"""),
    code_cell("""# 1. Order items aggregation
items_agg = order_items.groupby('order_id').agg(
    item_count=('order_item_id', 'count'),
    total_items_price=('price', 'sum'),
    total_freight_value=('freight_value', 'sum')
).reset_index()
items_agg['order_revenue'] = items_agg['total_items_price'] + items_agg['total_freight_value']

# 2. Payments aggregation
payments_agg = payments.groupby('order_id').agg(
    total_payment_value=('payment_value', 'sum'),
    payment_installments_max=('payment_installments', 'max'),
    primary_payment_type=('payment_type', lambda x: x.mode()[0] if not x.empty else 'unknown')
).reset_index()

# 3. Reviews deduplication (mean score per order)
reviews_agg = reviews.groupby('order_id').agg(
    review_score=('review_score', 'mean'),
    review_count=('review_id', 'count')
).reset_index()

print('Aggregations completed.')"""),
    md_cell("""### 4. Merge Master Order Analytical Dataset"""),
    code_cell("""master = orders.merge(customers, on='customer_id', how='left')
master = master.merge(items_agg, on='order_id', how='left')
master = master.merge(payments_agg, on='order_id', how='left')
master = master.merge(reviews_agg, on='order_id', how='left')

# Add delivery performance features
master['delivery_time_days'] = (master['order_delivered_customer_date'] - master['order_purchase_timestamp']).dt.total_seconds() / 86400.0
master['delivery_delay_days'] = (master['order_delivered_customer_date'] - master['order_estimated_delivery_date']).dt.total_seconds() / 86400.0
master['is_delayed'] = np.where(master['delivery_delay_days'] > 0, 1, 0)
master['delivery_status'] = np.where(
    master['order_delivered_customer_date'].isna(), 'Not Delivered',
    np.where(master['delivery_delay_days'] > 0, 'Late', 'On-Time')
)

master.to_csv(PROCESSED_DIR / 'master_analytical_orders.csv', index=False)
print(f'Master dataset saved: {master.shape[0]:,} rows x {master.shape[1]} columns.')""")
]

with open(NOTEBOOKS_DIR / "02_data_cleaning.ipynb", "w") as f:
    json.dump(make_notebook(nb2_cells), f, indent=2)

# ==============================================================================
# NOTEBOOK 3: 03_customer_analysis.ipynb
# ==============================================================================
nb3_cells = [
    md_cell("""# 03 - Customer & Sales Analysis
## Repeat Purchase Rate, Sales Growth & State Distribution

**Objective:**
Analyze the macro sales trends, customer purchase frequency, and state-level concentration."""),
    code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

PROCESSED_DIR = Path('../data/processed')
master = pd.read_csv(PROCESSED_DIR / 'master_analytical_orders.csv')
delivered = master[master['order_status'] == 'delivered'].copy()
delivered['order_purchase_timestamp'] = pd.to_datetime(delivered['order_purchase_timestamp'])
print(f'Delivered orders loaded: {len(delivered):,}')"""),
    md_cell("""### 1. Repeat Purchase Rate Calculation"""),
    code_cell("""cust_freq = delivered.groupby('customer_unique_id')['order_id'].nunique()
single_cust = (cust_freq == 1).sum()
repeat_cust = (cust_freq > 1).sum()
total_cust = len(cust_freq)

print(f'Total Unique Customers:     {total_cust:,}')
print(f'Single Order Customers:     {single_cust:,} ({single_cust/total_cust*100:.2f}%)')
print(f'Repeat Customers:           {repeat_cust:,} ({repeat_cust/total_cust*100:.2f}%)')"""),
    md_cell("""### 2. Monthly Revenue Trend"""),
    code_cell("""monthly = delivered.groupby(delivered['order_purchase_timestamp'].dt.to_period('M'))['order_revenue'].sum()
monthly.index = monthly.index.astype(str)

plt.figure(figsize=(12, 5))
plt.plot(monthly.index[1:-1], monthly.values[1:-1] / 1e6, marker='o', color='#0284C7', linewidth=2.5)
plt.title('Monthly Sales Revenue (R$ Millions)', fontsize=14, fontweight='bold')
plt.xlabel('Month')
plt.ylabel('Revenue (R$ M)')
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.5)
plt.show()"""),
    md_cell("""### 3. Top Customer States"""),
    code_cell("""state_rev = delivered.groupby('customer_state')['order_revenue'].sum().sort_values(ascending=False).head(10)
plt.figure(figsize=(10, 5))
sns.barplot(x=state_rev.index, y=state_rev.values / 1e6, palette='viridis')
plt.title('Top 10 States by Revenue (R$ Millions)', fontsize=14, fontweight='bold')
plt.xlabel('State')
plt.ylabel('Revenue (R$ M)')
plt.show()""")
]

with open(NOTEBOOKS_DIR / "03_customer_analysis.ipynb", "w") as f:
    json.dump(make_notebook(nb3_cells), f, indent=2)

# ==============================================================================
# NOTEBOOK 4: 04_cohort_analysis.ipynb
# ==============================================================================
nb4_cells = [
    md_cell("""# 04 - Cohort Retention Analysis
## Measuring Customer Retention & Drop-Off Over Time

**Objective:**
Segment customers into monthly acquisition cohorts based on their first purchase date.
Track their retention curve over subsequent months and build the cohort heatmap."""),
    code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

PROCESSED_DIR = Path('../data/processed')
master = pd.read_csv(PROCESSED_DIR / 'master_analytical_orders.csv')
delivered = master[master['order_status'] == 'delivered'].copy()
delivered['order_purchase_timestamp'] = pd.to_datetime(delivered['order_purchase_timestamp'])

# Filter operational period 2017 to mid 2018
cohort_df = delivered[(delivered['order_purchase_timestamp'] >= '2017-01-01') & 
                      (delivered['order_purchase_timestamp'] <= '2018-08-31')].copy()"""),
    md_cell("""### 1. Assign Cohort Month and Order Index"""),
    code_cell("""cohort_df['order_month'] = cohort_df['order_purchase_timestamp'].dt.to_period('M')
cohort_df['cohort_month'] = cohort_df.groupby('customer_unique_id')['order_month'].transform('min')

def get_cohort_index(df):
    return (df['order_month'].dt.year - df['cohort_month'].dt.year) * 12 + (df['order_month'].dt.month - df['cohort_month'].dt.month)

cohort_df['cohort_index'] = get_cohort_index(cohort_df)
print(cohort_df[['customer_unique_id', 'cohort_month', 'order_month', 'cohort_index']].head())"""),
    md_cell("""### 2. Build Cohort Retention Matrix"""),
    code_cell("""cohort_counts = cohort_df.groupby(['cohort_month', 'cohort_index'])['customer_unique_id'].nunique().unstack()
cohort_sizes = cohort_counts.iloc[:, 0]
retention_matrix = cohort_counts.divide(cohort_sizes, axis=0) * 100
retention_matrix.round(2).head(10)"""),
    md_cell("""### 3. Plot Cohort Retention Heatmap"""),
    code_cell("""plt.figure(figsize=(15, 8))
sns.heatmap(
    retention_matrix.iloc[1:18, :12],
    annot=True,
    fmt='.2f',
    cmap='Blues',
    linewidths=0.5,
    cbar_kws={'label': 'Retention Rate (%)'},
    vmin=0.0,
    vmax=1.2
)
plt.title('Customer Cohort Retention Rate (%) Across Operational Months', fontsize=15, fontweight='bold')
plt.xlabel('Months Since Acquisition (Cohort Index)')
plt.ylabel('Cohort Acquisition Month')
plt.show()""")
]

with open(NOTEBOOKS_DIR / "04_cohort_analysis.ipynb", "w") as f:
    json.dump(make_notebook(nb4_cells), f, indent=2)

# ==============================================================================
# NOTEBOOK 5: 05_rfm_analysis.ipynb
# ==============================================================================
nb5_cells = [
    md_cell("""# 05 - RFM Customer Segmentation
## Recency, Frequency, Monetary Scoring & Strategic Prioritization

**Objective:**
Calculate RFM scores (1 to 5 quintiles), segment customers into behavioral groups
(Champions, Loyal Customers, Potential Loyalists, At Risk, etc.), and identify revenue opportunities."""),
    code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

PROCESSED_DIR = Path('../data/processed')
rfm = pd.read_csv(PROCESSED_DIR / 'rfm_customer_segments.csv')
summary = pd.read_csv(PROCESSED_DIR / 'rfm_segment_summary.csv')
print('RFM Customer datasets loaded.')"""),
    md_cell("""### 1. RFM Segment Summary Table"""),
    code_cell("""print(summary.to_string(index=False))"""),
    md_cell("""### 2. Segment Revenue & Customer Share Visualization"""),
    code_cell("""plt.figure(figsize=(12, 6))
sns.barplot(data=summary, x='Segment', y='total_revenue', palette='mako')
plt.title('Total Revenue by RFM Customer Segment (R$)', fontsize=14, fontweight='bold')
plt.xticks(rotation=45)
plt.ylabel('Revenue (R$)')
plt.show()"""),
    md_cell("""### 3. Recency vs Monetary Scatter Plot"""),
    code_cell("""sample_rfm = rfm.sample(n=3000, random_state=42)
plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=sample_rfm,
    x='recency',
    y='monetary',
    hue='Segment',
    alpha=0.6,
    palette='Set2'
)
plt.yscale('log')
plt.title('Recency vs Monetary Spend by Segment (Sample n=3,000)', fontsize=14, fontweight='bold')
plt.xlabel('Recency (Days since last purchase)')
plt.ylabel('Monetary Spend (R$, Log Scale)')
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
plt.show()""")
]

with open(NOTEBOOKS_DIR / "05_rfm_analysis.ipynb", "w") as f:
    json.dump(make_notebook(nb5_cells), f, indent=2)

print("All 5 Jupyter notebooks generated successfully in notebooks/!")

