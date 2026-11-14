
import sys
from pathlib import Path

import streamlit as st
import pandas as pd
from sqlalchemy import text

# Configure Streamlit page
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.database import engine


# Dashboard heading
st.title("📊 Sales Analytics Dashboard")
st.caption("Online Retail Sales Performance | 2010–2011")

st.divider()


# Fetch data from PostgreSQL
@st.cache_data(ttl=300)
def load_data(query):
    with engine.connect() as connection:
        return pd.read_sql(text(query), connection)


try:
    # Business overview
    summary_query = """
        SELECT
            COALESCE(SUM("Revenue"), 0) AS total_revenue,
            COUNT(DISTINCT "InvoiceNo") AS total_orders,
            COUNT(DISTINCT "CustomerID") AS total_customers,
            COUNT(DISTINCT "StockCode") AS total_products
        FROM sales;
    """

    summary = load_data(summary_query).iloc[0]

    st.subheader("Business Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Revenue", f"£{summary['total_revenue']:,.2f}")
    col2.metric("Total Orders", f"{summary['total_orders']:,}")
    col3.metric("Total Customers", f"{summary['total_customers']:,}")
    col4.metric("Total Products", f"{summary['total_products']:,}")

    st.divider()

    # Monthly revenue trend
    st.subheader("📈 Monthly Revenue Trend")

    monthly_query = """
        SELECT
            DATE_TRUNC('month', "InvoiceDate") AS month,
            SUM("Revenue") AS revenue
        FROM sales
        GROUP BY month
        ORDER BY month;
    """

    monthly_data = load_data(monthly_query)

    if not monthly_data.empty:
        monthly_data = monthly_data.set_index("month")
        st.line_chart(monthly_data["revenue"])

    st.divider()

    # Top 10 products
    st.subheader("🏆 Top 10 Products by Revenue")

    products_query = """
        SELECT
            "Description",
            SUM("Revenue") AS revenue
        FROM sales
        GROUP BY "Description"
        ORDER BY revenue DESC
        LIMIT 10;
    """

    products_data = load_data(products_query)

    if not products_data.empty:
        st.bar_chart(
            products_data.set_index("Description")["revenue"]
        )

    st.divider()

    # Top 10 countries
    st.subheader("🌍 Top 10 Countries by Revenue")

    countries_query = """
        SELECT
            "Country",
            SUM("Revenue") AS revenue
        FROM sales
        GROUP BY "Country"
        ORDER BY revenue DESC
        LIMIT 10;
    """

    countries_data = load_data(countries_query)

    if not countries_data.empty:
        st.bar_chart(
            countries_data.set_index("Country")["revenue"]
        )

    st.success("Dashboard connected to PostgreSQL successfully!")

except Exception:
    st.error(
        "Unable to load dashboard data. "
        "Please check your database connection and table structure."
    )
