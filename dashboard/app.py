
import sys
from pathlib import Path
from datetime import timedelta

import streamlit as st
import pandas as pd
from sqlalchemy import text

# Configure Streamlit page
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom Dashboard Styling
st.markdown("""
<style>
    .stApp {
        background-color: #101820;
    }

    h1, h2, h3 {
        color: #F1F5F9;
        font-weight: 700;
    }

    [data-testid="stMetric"] {
        background-color: #1B2836;
        border: 1px solid #2D3D4F;
        padding: 20px;
        border-radius: 12px;
    }

    [data-testid="stMetricLabel"] {
        color: #AAB8C5;
    }

    [data-testid="stMetricValue"] {
        color: #00A86B;
        font-weight: 700;
    }

    .stButton button,
    .stDownloadButton button {
        background-color: #00A86B;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #2D3D4F;
        border-radius: 10px;
    }

    hr {
        border-color: #2D3D4F;
    }

    [data-testid="stSidebar"] {
        background-color: #17232F;
        border-right: 1px solid #2D3D4F;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #F1F5F9;
    }

    [data-testid="stSidebar"] p {
        color: #AAB8C5;
    }

    [data-testid="stDateInput"] input {
        border-radius: 8px;
    }

</style>
""", unsafe_allow_html=True)

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

    st.sidebar.title("📊 Sales Analytics")

    st.sidebar.markdown(
        "Explore business performance and customer insights."
    )

    st.sidebar.divider()

    st.sidebar.subheader("📅 Date Filter")


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

    # Dashboard navigation
    overview_tab, customer_tab, sales_tab = st.tabs([
        "📊 Overview",
        "👥 Customer Analytics",
        "📈 Sales Insights"
    ])

    with overview_tab:
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

        # Calculate previous period dates
        period_days = (end_date - start_date).days + 1
        previous_start = start_date - timedelta(days=period_days)
        previous_end = start_date - timedelta(days=1)

        # Fetch previous period revenue
        previous_query = """
            SELECT
                COALESCE(SUM("Revenue"), 0) AS previous_revenue
            FROM sales
            WHERE "InvoiceDate" >= :previous_start
              AND "InvoiceDate" < (:previous_end + INTERVAL '1 day');
        """

        previous_data = load_data(
            previous_query,
            {
                "previous_start": previous_start,
                "previous_end": previous_end
            }
        )

        previous_revenue = previous_data.iloc[0]["previous_revenue"]

        # Calculate revenue growth
        revenue_growth = (
            ((summary["total_revenue"] - previous_revenue) / previous_revenue) * 100
            if previous_revenue > 0
            else None
        )

        # KPI section
        st.markdown("### 📌 Key Performance Indicators")
        st.subheader("Business Overview")

        # Calculate Average Order Value
        average_order_value = (
            summary["total_revenue"] / summary["total_orders"]
            if summary["total_orders"] > 0
            else 0
        )

        # Display KPI metrics
        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric(
            "Total Revenue",
            f"£{summary['total_revenue']:,.2f}",
            delta=f"{revenue_growth:+.2f}%" if revenue_growth is not None else "N/A"
        )

        col2.metric("Total Orders", f"{int(summary['total_orders']):,}")
        col3.metric("Total Customers", f"{int(summary['total_customers']):,}")
        col4.metric("Total Products", f"{int(summary['total_products']):,}")
        col5.metric("Average Order Value", f"£{average_order_value:,.2f}")

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

            st.line_chart(
                monthly_data["revenue"],
                x_label="Month",
                y_label="Revenue (£)",
                color="#00A86B"
            )
        else:
            st.info("No sales data available for the selected dates.")

        st.divider()

    

        # Executive Business Highlights
        st.divider()
        st.subheader("💡 Executive Business Highlights")

        highlights_query = """
            SELECT
                (
                    SELECT "Description"
                    FROM sales
                    WHERE "InvoiceDate" >= :start_date
                      AND "InvoiceDate" < (:end_date + INTERVAL '1 day')
                      AND "Description" IS NOT NULL
                    GROUP BY "Description"
                    ORDER BY SUM("Revenue") DESC
                    LIMIT 1
                ) AS top_product,
                (
                    SELECT "Country"
                    FROM sales
                    WHERE "InvoiceDate" >= :start_date
                      AND "InvoiceDate" < (:end_date + INTERVAL '1 day')
                    GROUP BY "Country"
                    ORDER BY SUM("Revenue") DESC
                    LIMIT 1
                ) AS top_country,
                (
                    SELECT TO_CHAR("InvoiceDate", 'FMDay')
                    FROM sales
                    WHERE "InvoiceDate" >= :start_date
                      AND "InvoiceDate" < (:end_date + INTERVAL '1 day')
                    GROUP BY
                        EXTRACT(DOW FROM "InvoiceDate"),
                        TO_CHAR("InvoiceDate", 'FMDay')
                    ORDER BY SUM("Revenue") DESC
                    LIMIT 1
                ) AS best_sales_day
        """

        highlights_data = load_data(
            highlights_query,
            date_params
        )

        if not highlights_data.empty:
            highlights = highlights_data.iloc[0]

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "🏆 Top Product",
                highlights["top_product"] or "N/A"
            )

            col2.metric(
                "🌍 Leading Country",
                highlights["top_country"] or "N/A"
            )

            col3.metric(
                "📅 Best Sales Day",
                highlights["best_sales_day"] or "N/A"
            )


    with customer_tab:
        # Top 10 customers
        st.subheader("👥 Top 10 Customers by Revenue")

        customers_query = """
            SELECT
                "CustomerID",
                SUM("Revenue") AS revenue,
                COUNT(DISTINCT "InvoiceNo") AS total_orders
            FROM sales
            WHERE "InvoiceDate" >= :start_date
              AND "InvoiceDate" < (:end_date + INTERVAL '1 day')
              AND "CustomerID" IS NOT NULL
            GROUP BY "CustomerID"
            ORDER BY revenue DESC
            LIMIT 10;
        """

        customers_data = load_data(customers_query, date_params)

        if not customers_data.empty:
            st.dataframe(
                customers_data,
                width="stretch",
                hide_index=True
    )
        else:
            st.info("No customer data available for the selected dates.")



        st.divider()

        # Customer segmentation
        st.subheader("🎯 Customer Segmentation")


        segmentation_query = """
            WITH customer_spending AS (
                SELECT
                    "CustomerID",
                    SUM("Revenue") AS total_revenue
                FROM sales
                WHERE "InvoiceDate" >= :start_date
                  AND "InvoiceDate" < (:end_date + INTERVAL '1 day')
                  AND "CustomerID" IS NOT NULL
                GROUP BY "CustomerID"
            ),
            thresholds AS (
                SELECT
                    PERCENTILE_CONT(0.80)
                        WITHIN GROUP (ORDER BY total_revenue) AS high_threshold,
                    PERCENTILE_CONT(0.50)
                        WITHIN GROUP (ORDER BY total_revenue) AS medium_threshold
                FROM customer_spending
            ),
            segmented_customers AS (
                SELECT
                    cs."CustomerID",
                    cs.total_revenue,
                    CASE
                        WHEN cs.total_revenue >= t.high_threshold
                            THEN 'High Value'
                        WHEN cs.total_revenue >= t.medium_threshold
                            THEN 'Medium Value'
                        ELSE 'Low Value'
                    END AS segment
                FROM customer_spending cs
                CROSS JOIN thresholds t
            )
            SELECT
                segment,
                COUNT(*) AS customer_count,
                ROUND(SUM(total_revenue), 2) AS total_revenue
            FROM segmented_customers
            GROUP BY segment
            ORDER BY
                CASE
                    WHEN segment = 'High Value' THEN 1
                    WHEN segment = 'Medium Value' THEN 2
                    ELSE 3
                END
        """




        segmentation_data = load_data(
            segmentation_query,
            date_params
        )

        if not segmentation_data.empty:
            st.dataframe(
                segmentation_data,
                width="stretch",
                hide_index=True
            )

            st.bar_chart(
                segmentation_data.set_index("segment")["customer_count"],
                x_label="Customer Segment",
                y_label="Number of Customers"
            )
        else:
            st.info("No customer data available for segmentation.")


        st.subheader("Customer Purchase Frequency")

        frequency_query = """
            SELECT
                "CustomerID",
                COUNT(DISTINCT "InvoiceNo") AS total_orders,
                SUM("Revenue") AS total_revenue
            FROM sales
            WHERE "InvoiceDate" >= :start_date
              AND "InvoiceDate" < (:end_date + INTERVAL '1 day')
              AND "CustomerID" IS NOT NULL
            GROUP BY "CustomerID"
        """

        frequency_data = load_data(
            frequency_query,
            date_params
        )

        if not frequency_data.empty:
            frequency_data["Purchase Frequency"] = frequency_data["total_orders"].apply(
                lambda x: "One-time" if x == 1 else "Repeat"
            )

            frequency_summary = (
                frequency_data["Purchase Frequency"]
                .value_counts()
                .reset_index()
            )

            frequency_summary.columns = [
                "Customer Type",
                "Number of Customers"
            ]

            st.bar_chart(
                frequency_summary.set_index("Customer Type"),
                y="Number of Customers",
                color="#00A86B"
            )
        else:
            st.info("No customer purchase data available.")

        st.subheader("RFM Customer Analysis")

        rfm_query = """
            WITH customer_metrics AS (
                SELECT
                    "CustomerID",
                    CAST(:end_date AS DATE) - MAX("InvoiceDate")::DATE
                        AS recency_days,
                    COUNT(DISTINCT "InvoiceNo") AS frequency,
                    SUM("Revenue") AS monetary
                FROM sales
                WHERE "InvoiceDate" < (:end_date + INTERVAL '1 day')
                AND "CustomerID" IS NOT NULL
                GROUP BY "CustomerID"
            ),
            rfm_scores AS (
                SELECT
                    "CustomerID",
                    recency_days,
                    frequency,
                    monetary,
                    6 - NTILE(5) OVER (
                        ORDER BY recency_days ASC
                    ) AS r_score,
                    NTILE(5) OVER (
                        ORDER BY frequency ASC
                    ) AS f_score,
                    NTILE(5) OVER (
                        ORDER BY monetary ASC
                    ) AS m_score
                FROM customer_metrics
            ),
            customer_segments AS (
                SELECT *,
                    CASE
                        WHEN r_score >= 4 AND f_score >= 4
                             AND m_score >= 4
                            THEN 'Champions'
                        WHEN f_score >= 4
                            THEN 'Loyal Customers'
                        WHEN r_score >= 4 AND f_score >= 3
                            THEN 'Potential Loyalists'
                        WHEN r_score <= 2 AND f_score >= 3
                            THEN 'At Risk'
                        WHEN r_score <= 2 AND f_score <= 2
                            THEN 'Hibernating'
                        ELSE 'Others'
                    END AS segment
                FROM rfm_scores
            )
            SELECT
                segment,
                COUNT(*) AS customer_count,
                ROUND(SUM(monetary), 2) AS total_revenue
            FROM customer_segments
            GROUP BY segment
            ORDER BY customer_count DESC
        """


        rfm_data = load_data(
        rfm_query,
        {"end_date": end_date}
            )  

        if not rfm_data.empty:
            st.dataframe(
                rfm_data,
                width="stretch",
                hide_index=True
            )

            # Customer Count Chart
            st.bar_chart(
                rfm_data.set_index("segment")["customer_count"],
                y="customer_count",
                color="#00A86B"
            )

            # Revenue Contribution Chart
            st.subheader("Revenue Contribution by Customer Segment")

            st.bar_chart(
                rfm_data.set_index("segment")["total_revenue"],
                y="total_revenue",
                color="#00A86B"
            )

        else:
            st.info("No customer data available for RFM analysis.")

        st.divider()

    with sales_tab:
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
                products_data.set_index("Description")["revenue"],
                x_label="Product",
                y_label="Revenue (£)",
                horizontal=True
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
                countries_data.set_index("Country")["revenue"],
                x_label="Country",
                y_label="Revenue (£)",
                horizontal=True
            )
        else:
            st.info("No country data available for the selected dates.")


        st.divider()

        st.divider()

        # Geographical Sales Analysis
        st.subheader("🌍 Geographical Sales Contribution")

        geography_query = """
            SELECT
                "Country",
                COUNT(DISTINCT "InvoiceNo") AS total_orders,
                COUNT(DISTINCT "CustomerID") AS total_customers,
                ROUND(SUM("Revenue"), 2) AS revenue
            FROM sales
            WHERE "InvoiceDate" >= :start_date
              AND "InvoiceDate" < (:end_date + INTERVAL '1 day')
            GROUP BY "Country"
            ORDER BY revenue DESC
        """

        geography_data = load_data(
            geography_query,
            date_params
        )

        if not geography_data.empty:
            total_geo_revenue = geography_data["revenue"].sum()

            geography_data["Revenue Contribution (%)"] = (
                geography_data["revenue"] / total_geo_revenue * 100
            ).round(2)

            st.dataframe(
                geography_data,
                width="stretch",
                hide_index=True
            )

            st.bar_chart(
                geography_data.head(10).set_index("Country")["Revenue Contribution (%)"],
                y="Revenue Contribution (%)",
                color="#00A86B"
            )
        else:
            st.info("No geographical sales data available.")

        # Day-wise Sales Analysis
        st.subheader("📅 Day-wise Sales Performance")

        weekday_query = """
            SELECT
                EXTRACT(DOW FROM "InvoiceDate") AS day_number,
                TO_CHAR("InvoiceDate", 'FMDay') AS day_name,
                COUNT(DISTINCT "InvoiceNo") AS total_orders,
                ROUND(SUM("Revenue"), 2) AS revenue
            FROM sales
            WHERE "InvoiceDate" >= :start_date
              AND "InvoiceDate" < (:end_date + INTERVAL '1 day')
            GROUP BY day_number, day_name
            ORDER BY day_number
        """

        weekday_data = load_data(
            weekday_query,
            date_params
        )

        if not weekday_data.empty:
            st.bar_chart(
                weekday_data.set_index("day_name")["revenue"],
                x_label="Day of Week",
                y_label="Revenue (£)",
                color="#00A86B"
            )

            st.dataframe(
                weekday_data[["day_name", "total_orders", "revenue"]],
                width="stretch",
                hide_index=True
            )
        else:
            st.info("No weekday sales data available.")

        st.divider()

        st.divider()

        # Hourly Sales Analysis
        st.subheader("🕒 Hourly Sales Performance")

        hourly_query = """
            SELECT
                EXTRACT(HOUR FROM "InvoiceDate") AS sales_hour,
                COUNT(DISTINCT "InvoiceNo") AS total_orders,
                ROUND(SUM("Revenue"), 2) AS revenue
            FROM sales
            WHERE "InvoiceDate" >= :start_date
              AND "InvoiceDate" < (:end_date + INTERVAL '1 day')
            GROUP BY sales_hour
            ORDER BY sales_hour
        """

        hourly_data = load_data(
            hourly_query,
            date_params
        )

        if not hourly_data.empty:
            hourly_data["sales_hour"] = (
                hourly_data["sales_hour"].astype(int).astype(str)
                + ":00"
            )

            st.line_chart(
                hourly_data.set_index("sales_hour")["revenue"],
                x_label="Hour of Day",
                y_label="Revenue (£)",
                color="#00A86B"
            )

            st.dataframe(
                hourly_data,
                width="stretch",
                hide_index=True
            )
        else:
            st.info("No hourly sales data available.")

        # Order Value Distribution
        st.subheader("💰 Order Value Distribution")

        order_value_query = """
            WITH order_totals AS (
                SELECT
                    "InvoiceNo",
                    SUM("Revenue") AS order_value
                FROM sales
                WHERE "InvoiceDate" >= :start_date
                  AND "InvoiceDate" < (:end_date + INTERVAL '1 day')
                GROUP BY "InvoiceNo"
            ),
            order_groups AS (
                SELECT
                    order_value,
                    NTILE(4) OVER (
                        ORDER BY order_value
                    ) AS quartile
                FROM order_totals
            )
            SELECT
                CASE
                    WHEN quartile = 1 THEN 'Q1 - Lower Value'
                    WHEN quartile = 2 THEN 'Q2 - Medium-Low'
                    WHEN quartile = 3 THEN 'Q3 - Medium-High'
                    ELSE 'Q4 - Higher Value'
                END AS order_segment,
                COUNT(*) AS total_orders,
                ROUND(AVG(order_value), 2) AS average_order_value
            FROM order_groups
            GROUP BY quartile
            ORDER BY quartile
        """

        order_value_data = load_data(
            order_value_query,
            date_params
        )

        if not order_value_data.empty:
            st.bar_chart(
                order_value_data.set_index("order_segment")["total_orders"],
                y="total_orders",
                color="#00A86B"
            )

            st.dataframe(
                order_value_data,
                width="stretch",
                hide_index=True
            )
        else:
            st.info("No order value data available.")


        # Download Sales Report
        st.subheader("Download Sales Report")

        download_query = """
            SELECT
                "InvoiceNo",
                "StockCode",
                "Description",
                "Quantity",
                "InvoiceDate",
                "UnitPrice",
                "CustomerID",
                "Country",
                "Revenue"
            FROM sales
            WHERE "InvoiceDate" >= :start_date
              AND "InvoiceDate" < (:end_date + INTERVAL '1 day')
            ORDER BY "InvoiceDate"
        """

        download_data = load_data(
            download_query,
            date_params
        )

        csv_data = download_data.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            label="Download Sales Data (CSV)",
            data=csv_data,
            file_name="sales_report.csv",
            mime="text/csv",
            width="stretch"
        )


    st.success("Dashboard connected to PostgreSQL successfully!")

except Exception as error:
    st.error(f"Unable to load dashboard data: {error}")
