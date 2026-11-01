"""
E-Commerce Customer Retention & Churn Analysis
Interactive Enterprise Streamlit Web Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json

# Page Configuration
st.set_page_config(
    page_title="Olist E-Commerce Retention & Churn Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Enterprise Styling
st.markdown("""
<style>
    .main { background-color: #F8FAFC; }
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 18px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #E2E8F0;
        text-align: center;
    }
    .metric-title { font-size: 13px; color: #64748B; font-weight: 600; text-transform: uppercase; margin-bottom: 6px; }
    .metric-value { font-size: 26px; color: #0F172A; font-weight: 700; margin-bottom: 4px; }
    .metric-sub { font-size: 12px; color: #10B981; font-weight: 500; }
    .metric-sub-red { font-size: 12px; color: #EF4444; font-weight: 500; }
    h1, h2, h3 { color: #0F172A; font-family: 'Segoe UI', sans-serif; }
    .stTabs [data-baseweb="tab-list"] { gap: 12px; }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: #FFFFFF;
        border-radius: 8px;
        font-weight: 600;
        color: #334155;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0284C7 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# File Paths
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"

@st.cache_data
def load_data():
    kpi = json.load(open(DATA_DIR / "kpi_summary.json"))
    monthly = pd.read_csv(DATA_DIR / "monthly_sales_trend.csv")
    top_cat = pd.read_csv(DATA_DIR / "top_categories.csv")
    states = pd.read_csv(DATA_DIR / "state_distribution.csv")
    cohort = pd.read_csv(DATA_DIR / "cohort_retention_matrix.csv", index_col=0)
    cohort_counts = pd.read_csv(DATA_DIR / "cohort_customer_counts.csv", index_col=0)
    rfm_summary = pd.read_csv(DATA_DIR / "rfm_segment_summary.csv")
    deliv_analysis = pd.read_csv(DATA_DIR / "delivery_delay_analysis.csv")
    deliv_repeat = pd.read_csv(DATA_DIR / "delivery_repeat_summary.csv")
    
    # Load sample of master orders for dynamic filtering
    master_sample = pd.read_csv(DATA_DIR / "master_analytical_orders.csv", nrows=10000)
    return kpi, monthly, top_cat, states, cohort, cohort_counts, rfm_summary, deliv_analysis, deliv_repeat, master_sample

kpi, monthly, top_cat, states, cohort, cohort_counts, rfm_summary, deliv_analysis, deliv_repeat, master_sample = load_data()

# ------------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# ------------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shopping-cart.png", width=64)
    st.title("Olist Retention Analytics")
    st.caption("Brazilian E-Commerce (~100,000 Orders)")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        [
            "📊 Executive Overview",
            "👥 Cohort Retention Heatmap",
            "🎯 RFM Customer Segmentation",
            "🚚 Delivery & Satisfaction",
            "💡 Strategic Recommendations"
        ],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 📌 Quick Business Context")
    st.markdown("""
    - **Timeframe:** 2016 – 2018
    - **Total Orders:** 96,478 Delivered
    - **Unique Customers:** 93,358
    - **Repeat Buyers:** 2,801 (**3.00%**)
    """)
    st.markdown("---")
    st.caption("Data Analytics Portfolio Project")

# ------------------------------------------------------------------------------
# PAGE 1: EXECUTIVE OVERVIEW
# ------------------------------------------------------------------------------
if page == "📊 Executive Overview":
    st.title("📊 Executive Overview & Sales Performance")
    st.markdown("Macro sales performance, customer acquisition dynamics, and retention baseline.")
    
    # Top KPI Banner
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Gross Revenue</div>
            <div class="metric-value">R$ {kpi['total_revenue']/1e6:.2f}M</div>
            <div class="metric-sub">R$ {kpi['total_revenue']:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Delivered Orders</div>
            <div class="metric-value">{kpi['total_orders']:,}</div>
            <div class="metric-sub">97.02% of total orders</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Unique Buyers</div>
            <div class="metric-value">{kpi['unique_customers']:,}</div>
            <div class="metric-sub">Individual Humans</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Avg Order Value</div>
            <div class="metric-value">R$ {kpi['avg_order_value']:.2f}</div>
            <div class="metric-sub">Per Delivered Order</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Repeat Rate</div>
            <div class="metric-value" style="color: #EF4444;">{kpi['repeat_purchase_rate']:.2f}%</div>
            <div class="metric-sub-red">97.00% Churn After 1st Buy</div>
        </div>
        """, unsafe_allow_html=True)
    with col6:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Avg Review</div>
            <div class="metric-value">{kpi['avg_review_score']:.2f} ⭐</div>
            <div class="metric-sub">Out of 5.0 Stars</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Row 1: Monthly Trend & Customer Retention Split
    row1_col1, row1_col2 = st.columns([2, 1])
    
    with row1_col1:
        monthly_filtered = monthly[monthly["purchase_month"] >= "2017-01"].copy()
        fig_monthly = px.area(
            monthly_filtered,
            x="month_str",
            y="revenue",
            title="<b>Monthly Gross Revenue Growth (R$)</b>",
            labels={"month_str": "Month", "revenue": "Revenue (R$)"},
            color_discrete_sequence=["#0284C7"]
        )
        fig_monthly.update_layout(
            hovermode="x unified",
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_monthly, use_container_width=True)
        
    with row1_col2:
        split_df = pd.DataFrame({
            "Customer Type": ["One-Time Buyers (97.0%)", "Repeat Buyers (3.0%)"],
            "Count": [kpi["unique_customers"] - kpi["repeat_customers_count"], kpi["repeat_customers_count"]]
        })
        fig_pie = px.pie(
            split_df,
            names="Customer Type",
            values="Count",
            title="<b>Customer Retention Split</b>",
            color_discrete_sequence=["#CBD5E1", "#10B981"],
            hole=0.45
        )
        fig_pie.update_layout(
            paper_bgcolor="white",
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
    # Row 2: Top Product Categories & Revenue by State
    row2_col1, row2_col2 = st.columns(2)
    
    with row2_col1:
        top10_cat = top_cat.head(10).sort_values("total_revenue", ascending=True)
        fig_cat = px.bar(
            top10_cat,
            x="total_revenue",
            y="product_category_name_english",
            orientation="h",
            title="<b>Top 10 Product Categories by Revenue (R$)</b>",
            labels={"total_revenue": "Revenue (R$)", "product_category_name_english": "Category"},
            color="total_revenue",
            color_continuous_scale="Blues"
        )
        fig_cat.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            coloraxis_showscale=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_cat, use_container_width=True)
        
    with row2_col2:
        top10_states = states.head(10).sort_values("revenue_share_pct", ascending=True)
        fig_states = px.bar(
            top10_states,
            x="revenue_share_pct",
            y="customer_state",
            orientation="h",
            title="<b>Top 10 Brazilian States by Revenue Contribution (%)</b>",
            labels={"revenue_share_pct": "Revenue Share (%)", "customer_state": "State"},
            color="revenue_share_pct",
            color_continuous_scale="Tealgrn"
        )
        fig_states.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            coloraxis_showscale=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_states, use_container_width=True)

# ------------------------------------------------------------------------------
# PAGE 2: COHORT RETENTION HEATMAP
# ------------------------------------------------------------------------------
elif page == "👥 Cohort Retention Heatmap":
    st.title("👥 Customer Cohort Retention Analysis")
    st.markdown("""
    Tracking customer retention by monthly acquisition cohort (Jan 2017 to Aug 2018).
    **Key Finding:** Retention collapses immediately in **Month 1 (averaging 0.45% – 0.62%)**, confirming severe first-purchase churn.
    """)
    
    # Heatmap visual
    cohort_sub = cohort.iloc[1:18, :12]
    fig_heat = px.imshow(
        cohort_sub,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="Blues",
        labels=dict(x="Months Since Acquisition (Cohort Index)", y="Acquisition Cohort Month", color="Retention %"),
        title="<b>Monthly Cohort Retention Rate (%) Matrix</b>",
        zmin=0.0,
        zmax=1.2
    )
    fig_heat.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        height=550,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_heat, use_container_width=True)
    
    st.markdown("### 📉 Cohort Retention Drop-off Curve")
    avg_retention = cohort.iloc[1:18, 1:13].mean()
    retention_curve_df = pd.DataFrame({
        "Month": [f"Month {m}" for m in avg_retention.index],
        "Avg Retention %": avg_retention.values
    })
    fig_curve = px.line(
        retention_curve_df,
        x="Month",
        y="Avg Retention %",
        markers=True,
        title="<b>Average Customer Retention Curve Across All Cohorts</b>",
        color_discrete_sequence=["#EF4444"]
    )
    fig_curve.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_curve, use_container_width=True)

# ------------------------------------------------------------------------------
# PAGE 3: RFM CUSTOMER SEGMENTATION
# ------------------------------------------------------------------------------
elif page == "🎯 RFM Customer Segmentation":
    st.title("🎯 RFM Customer Segmentation & High-Value Priorities")
    st.markdown("Segmenting 93,358 buyers using Recency (R), Frequency (F), and Monetary (M) scores.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        fig_seg_rev = px.bar(
            rfm_summary.sort_values("total_revenue", ascending=True),
            x="total_revenue",
            y="Segment",
            orientation="h",
            title="<b>Total Revenue Contribution by Customer Segment (R$)</b>",
            color="total_revenue",
            color_continuous_scale="Purples",
            text=rfm_summary.sort_values("total_revenue", ascending=True)["revenue_pct"].apply(lambda x: f"{x:.1f}%")
        )
        fig_seg_rev.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            coloraxis_showscale=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_seg_rev, use_container_width=True)
        
    with col2:
        fig_seg_cnt = px.bar(
            rfm_summary.sort_values("customer_count", ascending=True),
            x="customer_count",
            y="Segment",
            orientation="h",
            title="<b>Customer Count by Segment</b>",
            color="customer_count",
            color_continuous_scale="Viridis",
            text=rfm_summary.sort_values("customer_count", ascending=True)["customer_pct"].apply(lambda x: f"{x:.1f}%")
        )
        fig_seg_cnt.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            coloraxis_showscale=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_seg_cnt, use_container_width=True)
        
    st.markdown("### 📋 Segment Metrics Summary Table")
    st.dataframe(
        rfm_summary.style.format({
            "total_revenue": "R$ {:,.2f}",
            "customer_count": "{:,}",
            "avg_recency": "{:.1f} days",
            "avg_frequency": "{:.2f}",
            "avg_monetary": "R$ {:.2f}",
            "avg_review": "{:.2f} ⭐",
            "customer_pct": "{:.2f}%",
            "revenue_pct": "{:.2f}%"
        }),
        use_container_width=True
    )

# ------------------------------------------------------------------------------
# PAGE 4: DELIVERY & SATISFACTION
# ------------------------------------------------------------------------------
elif page == "🚚 Delivery & Satisfaction":
    st.title("🚚 Delivery Fulfillment & Customer Review Analysis")
    st.markdown("Evaluating the direct correlation between shipping delays and review star ratings.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        deliv_split = pd.DataFrame({
            "Delivery Status": ["On-Time Deliveries (91.89%)", "Delayed Deliveries (8.11%)"],
            "Orders": [deliv_analysis.loc[0, "order_count"], deliv_analysis.loc[1, "order_count"]]
        })
        fig_deliv_pie = px.pie(
            deliv_split,
            names="Delivery Status",
            values="Orders",
            title="<b>Delivery Fulfillment Performance</b>",
            color_discrete_sequence=["#10B981", "#EF4444"],
            hole=0.45
        )
        fig_deliv_pie.update_layout(
            paper_bgcolor="white",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_deliv_pie, use_container_width=True)
        
    with col2:
        fig_stars = go.Figure(data=[
            go.Bar(name="On-Time Orders", x=["Average Review Score"], y=[deliv_analysis.loc[0, "avg_review_score"]], marker_color="#10B981", text=[f"{deliv_analysis.loc[0, 'avg_review_score']:.2f} ⭐"], textposition="auto"),
            go.Bar(name="Delayed Orders", x=["Average Review Score"], y=[deliv_analysis.loc[1, "avg_review_score"]], marker_color="#EF4444", text=[f"{deliv_analysis.loc[1, 'avg_review_score']:.2f} ⭐"], textposition="auto")
        ])
        fig_stars.update_layout(
            barmode="group",
            title="<b>Average Customer Rating: On-Time vs Delayed (-1.72 Stars Drop)</b>",
            yaxis=dict(range=[0, 5], title="Rating (1 to 5)"),
            paper_bgcolor="white",
            plot_bgcolor="white",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_stars, use_container_width=True)
        
    st.markdown("### ⚠️ Star Rating Breakdown (1-Star Reviews Surge 10x)")
    star_breakdown = pd.DataFrame({
        "Status": ["On-Time Orders", "Delayed Orders"],
        "1-Star Reviews (%)": [deliv_analysis.loc[0, "1_star_review_pct"], deliv_analysis.loc[1, "1_star_review_pct"]],
        "5-Star Reviews (%)": [deliv_analysis.loc[0, "5_star_review_pct"], deliv_analysis.loc[1, "5_star_review_pct"]]
    })
    st.dataframe(
        star_breakdown.style.format({
            "1-Star Reviews (%)": "{:.1f}%",
            "5-Star Reviews (%)": "{:.1f}%"
        }),
        use_container_width=True
    )

# ------------------------------------------------------------------------------
# PAGE 5: STRATEGIC RECOMMENDATIONS & ROI SIMULATOR
# ------------------------------------------------------------------------------
elif page == "💡 Strategic Recommendations":
    st.title("💡 Strategic Recommendations & Retention ROI Simulator")
    st.markdown("Actionable marketing strategies, operational fixes, and interactive financial model.")
    
    st.markdown("### 🎛️ Interactive Retention Impact Simulator")
    target_lift = st.slider(
        "Select Target Customer Retention Rate Lift (Percentage Points):",
        min_value=0.5,
        max_value=5.0,
        value=2.5,
        step=0.5
    )
    
    base_retention = kpi["repeat_purchase_rate"]
    new_retention = base_retention + target_lift
    incremental_repeat_orders = int(kpi["unique_customers"] * (target_lift / 100))
    incremental_revenue = incremental_repeat_orders * kpi["avg_order_value"]
    
    sim_col1, sim_col2, sim_col3 = st.columns(3)
    with sim_col1:
        st.metric(
            label="Simulated Retention Rate",
            value=f"{new_retention:.2f}%",
            delta=f"+{target_lift:.1f} pp"
        )
    with sim_col2:
        st.metric(
            label="Additional Repeat Orders",
            value=f"+{incremental_repeat_orders:,}",
            delta="New Orders"
        )
    with sim_col3:
        st.metric(
            label="Estimated Incremental Gross Revenue",
            value=f"R$ {incremental_revenue:,.2f}",
            delta="Annualized Run-Rate"
        )
        
    st.markdown("---")
    st.markdown("""
    ### 🚀 4 Concrete Retention Action Pillars
    
    1. **Target Potential Loyalists (14,454 customers | R$ 4.37M Revenue):**
       - High-value single buyers with R$ 302 average spend.
       - Deploy an automated **21-day post-delivery cross-sell email** with an expiring **R$ 25 loyalty voucher**.
    
    2. **VIP Win-Back Blitz (553 'At Risk' Multi-Buyers):**
       - Multi-order buyers who have been inactive for ~300+ days.
       - Send a personalized **Free Freight + 15% discount campaign**.
       
    3. **Proactive Delivery Delay Credits (Carrier Telemetry):**
       - Because late delivery causes an immediate 40.2% drop in review ratings, automatically credit **R$ 20 store credit** when telemetry detects an in-transit breach >48 hours *before* complaints arrive.
       
    4. **SLA Penalties for Dispatch Hubs:**
       - Route optimizations in high-delay regions: Alagoas (24.1% late), Maranhão (18.9% late), and Rio de Janeiro (12.8% late).
    """)

st.markdown("---")
st.caption("Olist E-Commerce Retention & Churn Analysis — Live Interactive Dashboard")

