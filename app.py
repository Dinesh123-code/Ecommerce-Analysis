import os
import sys
from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from src.analytics import (
    best_selling_products,
    load_and_prepare_sales_data,
    monthly_sales_trends,
    profit_analysis,
    regional_performance,
    revenue_by_category,
    summary_metrics,
    top_customers,
)
from src.db import fetch_sales_data_from_mysql

from streamlit.runtime.scriptrunner import get_script_run_ctx

if get_script_run_ctx() is None:
    print("Run this dashboard with: streamlit run app.py")
    raise SystemExit(0)

load_dotenv()

st.set_page_config(
    page_title="E-Commerce Sales Analysis Dashboard",
    page_icon="📈",
    layout="wide",
)

st.title("E-Commerce Sales Analysis Dashboard")
st.caption("Analyze best sellers, top customers, monthly trends, category revenue, profit, and regional performance.")

with st.sidebar:
    st.header("Data Source")
    data_source = st.radio("Choose input source", ["MySQL", "CSV Upload"], index=0)

    st.subheader("MySQL Settings")
    mysql_host = st.text_input("Host", value=os.getenv("MYSQL_HOST", "localhost"))
    mysql_port = st.number_input("Port", min_value=1, max_value=65535, value=int(os.getenv("MYSQL_PORT", "3306")))
    mysql_user = st.text_input("User", value=os.getenv("MYSQL_USER", "root"))
    mysql_password = st.text_input("Password", value=os.getenv("MYSQL_PASSWORD", ""), type="password")
    mysql_database = st.text_input("Database", value=os.getenv("MYSQL_DATABASE", "ecommerce_db"))
    mysql_table = st.text_input("Table", value=os.getenv("MYSQL_TABLE", "ecommerce_sales"))

    st.subheader("Display")
    top_n = st.slider("Top N items", min_value=5, max_value=25, value=10)


def load_csv(uploaded_file: BytesIO) -> pd.DataFrame:
    raw_df = pd.read_csv(uploaded_file)
    return load_and_prepare_sales_data(raw_df)


@st.cache_data(show_spinner=False)
def load_mysql(host: str, port: int, user: str, password: str, database: str, table: str) -> pd.DataFrame:
    return load_and_prepare_sales_data(
        fetch_sales_data_from_mysql(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            table=table,
        )
    )


def show_metric_row(df: pd.DataFrame) -> None:
    metrics = summary_metrics(df)
    cols = st.columns(6)
    cols[0].metric("Revenue", f"${metrics['revenue']:,.2f}")
    cols[1].metric("Profit", f"${metrics['profit']:,.2f}")
    cols[2].metric("Orders", f"{metrics['orders']:,}")
    cols[3].metric("Customers", f"{metrics['customers']:,}")
    cols[4].metric("Products", f"{metrics['products']:,}")
    cols[5].metric("Avg Order Value", f"${metrics['avg_order_value']:,.2f}")


uploaded_file = None
sales_df = None

if data_source == "CSV Upload":
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file is not None:
        try:
            sales_df = load_csv(uploaded_file)
        except Exception as exc:
            st.error(f"Unable to read CSV data: {exc}")
else:
    if st.button("Load data from MySQL", type="primary"):
        try:
            sales_df = load_mysql(mysql_host, int(mysql_port), mysql_user, mysql_password, mysql_database, mysql_table)
        except Exception as exc:
            st.error(f"Unable to read MySQL data: {exc}")

if sales_df is None:
    st.info("Provide a CSV file or connect to MySQL to start the analysis.")
    st.markdown(
        """
        ### Expected columns
        `order_id`, `order_date`, `customer_id`, `customer_name`, `product_name`,
        `category`, `region`, `quantity`, `unit_price`, `cost`, `revenue`, `profit`

        The app will compute missing `revenue` and `profit` values when possible.
        """
    )
    st.stop()

show_metric_row(sales_df)

st.divider()

left, right = st.columns([2, 1])
with left:
    st.subheader("Sample Data")
    st.dataframe(sales_df.head(20), use_container_width=True)
with right:
    st.subheader("Data Health")
    st.write(f"Rows: {len(sales_df):,}")
    st.write(f"Date range: {sales_df['order_date'].min().date()} to {sales_df['order_date'].max().date()}")
    st.write(f"Regions: {sales_df['region'].nunique():,}")
    st.write(f"Categories: {sales_df['category'].nunique():,}")

st.divider()

product_df = best_selling_products(sales_df, top_n=top_n)
customer_df = top_customers(sales_df, top_n=top_n)
monthly_df = monthly_sales_trends(sales_df)
category_df = revenue_by_category(sales_df)
profit_df = profit_analysis(sales_df)
regional_df = regional_performance(sales_df)

chart_tabs = st.tabs([
    "Best Sellers",
    "Top Customers",
    "Monthly Trends",
    "Category Revenue",
    "Profit Analysis",
    "Regional Performance",
])

with chart_tabs[0]:
    st.subheader("Best-Selling Products")
    fig = px.bar(
        product_df,
        x="product_name",
        y="revenue",
        color="quantity",
        title="Revenue by Product",
        labels={"product_name": "Product", "revenue": "Revenue", "quantity": "Units Sold"},
    )
    fig.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(product_df, use_container_width=True)

with chart_tabs[1]:
    st.subheader("Top Customers")
    fig = px.bar(
        customer_df,
        x="customer_label",
        y="revenue",
        color="orders",
        title="Revenue by Customer",
        labels={"customer_label": "Customer", "revenue": "Revenue", "orders": "Orders"},
    )
    fig.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(customer_df, use_container_width=True)

with chart_tabs[2]:
    st.subheader("Monthly Sales Trends")
    line_fig = px.line(
        monthly_df,
        x="month",
        y=["revenue", "profit"],
        markers=True,
        title="Revenue and Profit Over Time",
        labels={"value": "Amount", "month": "Month", "variable": "Metric"},
    )
    st.plotly_chart(line_fig, use_container_width=True)
    st.dataframe(monthly_df, use_container_width=True)

with chart_tabs[3]:
    st.subheader("Revenue by Category")
    fig = px.pie(category_df, names="category", values="revenue", hole=0.4, title="Category Revenue Share")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(category_df, use_container_width=True)

with chart_tabs[4]:
    st.subheader("Profit Analysis")
    fig = px.bar(
        profit_df,
        x="product_name",
        y="profit",
        color="margin_pct",
        title="Profit by Product",
        labels={"product_name": "Product", "profit": "Profit", "margin_pct": "Margin %"},
    )
    fig.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(profit_df, use_container_width=True)

with chart_tabs[5]:
    st.subheader("Regional Performance")
    fig = px.bar(
        regional_df,
        x="region",
        y="revenue",
        color="profit",
        title="Regional Revenue and Profit",
        labels={"region": "Region", "revenue": "Revenue", "profit": "Profit"},
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(regional_df, use_container_width=True)

with st.expander("View full cleaned dataset"):
    st.dataframe(sales_df, use_container_width=True)
