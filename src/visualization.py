"""
Visualization Module
====================
Professional charting functions for the E-Commerce Retention project.
Uses Matplotlib and Seaborn with a consistent, publication-quality style.
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path


# -------------------------------------------------------------------
# Global style settings
# -------------------------------------------------------------------
COLORS = {
    "primary": "#1B2838",      # Dark navy
    "secondary": "#2196F3",    # Blue
    "accent": "#00BCD4",       # Teal
    "success": "#4CAF50",      # Green
    "warning": "#FF9800",      # Orange
    "danger": "#F44336",       # Red
    "light_bg": "#F5F7FA",     # Light background
    "text": "#333333",         # Dark text
}

PALETTE = ["#2196F3", "#00BCD4", "#4CAF50", "#FF9800", "#F44336",
           "#9C27B0", "#3F51B5", "#009688", "#FFC107", "#795548"]


def set_style():
    """Apply consistent plot styling across all charts."""
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({
        "figure.figsize": (12, 6),
        "figure.dpi": 100,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#CCCCCC",
        "axes.labelcolor": COLORS["text"],
        "axes.titlesize": 14,
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "font.family": "sans-serif",
        "grid.alpha": 0.3,
    })


def plot_monthly_revenue(df: pd.DataFrame, date_col: str, revenue_col: str,
                         title: str = "Monthly Revenue Trend",
                         save_path: str | None = None):
    """Line chart of monthly revenue."""
    set_style()
    monthly = df.groupby(df[date_col].dt.to_period("M"))[revenue_col].sum()
    monthly.index = monthly.index.to_timestamp()

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(monthly.index, monthly.values, color=COLORS["secondary"],
            linewidth=2.5, marker="o", markersize=5)
    ax.fill_between(monthly.index, monthly.values, alpha=0.1, color=COLORS["secondary"])
    ax.set_title(title, fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel("Month", fontsize=12)
    ax.set_ylabel("Revenue (R$)", fontsize=12)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R${x:,.0f}"))
    plt.xticks(rotation=45)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()


def plot_cohort_heatmap(retention_df: pd.DataFrame,
                        title: str = "Customer Cohort Retention Heatmap",
                        save_path: str | None = None):
    """Heatmap of cohort retention percentages."""
    set_style()
    fig, ax = plt.subplots(figsize=(16, 10))

    sns.heatmap(
        retention_df,
        annot=True,
        fmt=".1f",
        cmap="YlGnBu",
        linewidths=0.5,
        linecolor="white",
        ax=ax,
        vmin=0,
        vmax=100,
        cbar_kws={"label": "Retention Rate (%)"},
    )

    ax.set_title(title, fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel("Months Since First Purchase", fontsize=12)
    ax.set_ylabel("Cohort Month", fontsize=12)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()


def plot_rfm_segments(segment_df: pd.DataFrame,
                      title: str = "Customer Segments by Count",
                      save_path: str | None = None):
    """Horizontal bar chart of customer segment distribution."""
    set_style()
    fig, ax = plt.subplots(figsize=(12, 7))

    segment_counts = segment_df["Segment"].value_counts().sort_values()
    colors = sns.color_palette("viridis", len(segment_counts))

    bars = ax.barh(segment_counts.index, segment_counts.values, color=colors)
    ax.set_title(title, fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel("Number of Customers", fontsize=12)

    for bar, val in zip(bars, segment_counts.values):
        ax.text(val + 50, bar.get_y() + bar.get_height() / 2,
                f"{val:,}", va="center", fontsize=10)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()


def plot_delivery_vs_reviews(df: pd.DataFrame,
                             delay_col: str = "delivery_delay_days",
                             review_col: str = "review_score",
                             save_path: str | None = None):
    """Box plot of review scores by delivery status (on-time vs late)."""
    set_style()
    fig, ax = plt.subplots(figsize=(10, 6))

    df = df.copy()
    df["delivery_status"] = np.where(df[delay_col] > 0, "Late", "On Time")

    sns.boxplot(
        data=df, x="delivery_status", y=review_col,
        palette=[COLORS["success"], COLORS["danger"]],
        ax=ax,
    )

    ax.set_title("Review Scores: On-Time vs Late Deliveries",
                 fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel("Delivery Status", fontsize=12)
    ax.set_ylabel("Review Score", fontsize=12)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()


def plot_top_categories(df: pd.DataFrame, category_col: str, revenue_col: str,
                        top_n: int = 10, save_path: str | None = None):
    """Horizontal bar chart of top product categories by revenue."""
    set_style()
    fig, ax = plt.subplots(figsize=(12, 7))

    top = (
        df.groupby(category_col)[revenue_col]
        .sum()
        .nlargest(top_n)
        .sort_values()
    )

    colors = sns.color_palette("Blues_r", len(top))
    ax.barh(top.index, top.values, color=colors)
    ax.set_title(f"Top {top_n} Product Categories by Revenue",
                 fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel("Revenue (R$)", fontsize=12)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R${x:,.0f}"))
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()


def plot_kpi_cards(kpis: dict, save_path: str | None = None):
    """
    Create a KPI summary card visual.

    Parameters
    ----------
    kpis : dict
        Keys are KPI names, values are (value_string, subtitle) tuples.
    """
    set_style()
    n = len(kpis)
    fig, axes = plt.subplots(1, n, figsize=(4 * n, 3))

    if n == 1:
        axes = [axes]

    for ax, (name, (value, subtitle)) in zip(axes, kpis.items()):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.text(0.5, 0.65, str(value), ha="center", va="center",
                fontsize=28, fontweight="bold", color=COLORS["primary"])
        ax.text(0.5, 0.35, name, ha="center", va="center",
                fontsize=12, color=COLORS["text"])
        ax.text(0.5, 0.15, subtitle, ha="center", va="center",
                fontsize=9, color="#888888")
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color("#E0E0E0")
            spine.set_linewidth(1.5)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()
