
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
def load_data(query, params=None):
    with engine.connect() as connection:
        return pd.read_sql(
            text(query),
            connection,
            params=params
        )


try:
    # Date range filter
    st.sidebar.header("📅 Date Filter")

    date_query = """
        SELECT
            MIN("InvoiceDate") AS min_date,
            MAX("InvoiceDate") AS max_date
        FROM sales;
    """

    date_limits = load_data(date_query).iloc[0]

    start_date = st.sidebar.date_input(
        "Start Date",
        value=date_limits["min_date"].date(),
        min_value=date_limits["min_date"].date(),
        max_value=date_limits["max_date"].date()
    )

    end_date = st.sidebar.date_input(
        "End Date",
        value=date_limits["max_date"].date(),
        min_value=date_limits["min_date"].date(),
        max_value=date_limits["max_date"].date()
    )

    if start_date > end_date:
        st.error("Start Date cannot be after End Date.")
        st.stop()

    # Common date parameters
    date_params = {
        "start_date": start_date,
        "end_date": end_date
    }

    # Business overview
    summary_query = """
        SELECT
            COALESCE(SUM("Revenue"), 0) AS total_revenue,
            COUNT(DISTINCT "InvoiceNo") AS total_orders,
            COUNT(DISTINCT "CustomerID") AS total_customers,
            COUNT(DISTINCT "StockCode") AS total_products
        FROM sales
        WHERE "InvoiceDate" >= :start_date
          AND "InvoiceDate" < (:end_date + INTERVAL '1 day');
    """

    summary = load_data(summary_query, date_params).iloc[0]

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
        WHERE "InvoiceDate" >= :start_date
          AND "InvoiceDate" < (:end_date + INTERVAL '1 day')
        GROUP BY month
        ORDER BY month;
    """

    monthly_data = load_data(monthly_query, date_params)

    if not monthly_data.empty:
        monthly_data = monthly_data.set_index("month")
        st.line_chart(monthly_data["revenue"])
    else:
        st.info("No sales data available for the selected dates.")

    st.divider()

    # Top 10 products
    st.subheader("🏆 Top 10 Products by Revenue")

    products_query = """
        SELECT
            "Description",
            SUM("Revenue") AS revenue
        FROM sales
        WHERE "InvoiceDate" >= :start_date
          AND "InvoiceDate" < (:end_date + INTERVAL '1 day')
        GROUP BY "Description"
        ORDER BY revenue DESC
        LIMIT 10;
    """

    products_data = load_data(products_query, date_params)

    if not products_data.empty:
        st.bar_chart(
            products_data.set_index("Description")["revenue"]
        )
    else:
        st.info("No product data available for the selected dates.")

    st.divider()

    # Top 10 countries
    st.subheader("🌍 Top 10 Countries by Revenue")

    countries_query = """
        SELECT
            "Country",
            SUM("Revenue") AS revenue
        FROM sales
        WHERE "InvoiceDate" >= :start_date
          AND "InvoiceDate" < (:end_date + INTERVAL '1 day')
        GROUP BY "Country"
        ORDER BY revenue DESC
        LIMIT 10;
    """

    countries_data = load_data(countries_query, date_params)

    if not countries_data.empty:
        st.bar_chart(
            countries_data.set_index("Country")["revenue"]
        )
    else:
        st.info("No country data available for the selected dates.")

    st.success("Dashboard connected to PostgreSQL successfully!")

except Exception as error:
    st.error(f"Unable to load dashboard data: {error}")
