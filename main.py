from pathlib import Path

from src.data_loader import load_sales_data

from src.data_cleaner import (
    remove_duplicates,
    handle_missing_values,
    calculate_revenue,
    get_completed_sales
)
from src.analysis import (
    get_monthly_revenue,
    get_top_products,
    get_country_sales,
    get_top_customers
)


def main():
    print("Starting Sales Data Analytics Pipeline...")

    # Step 1: Load raw data
    df = load_sales_data()
    print("Raw data loaded:", df.shape)

    # Step 2: Clean data
    df = remove_duplicates(df)
    df = handle_missing_values(df)

    # Step 3: Calculate revenue
    df = calculate_revenue(df)

    # Step 4: Filter completed sales
    completed_sales = get_completed_sales(df)

    print("Completed sales:", completed_sales.shape)
    # Step 5: Perform business analysis

    monthly_revenue = get_monthly_revenue(completed_sales)
    top_products = get_top_products(completed_sales)
    country_sales = get_country_sales(completed_sales)
    top_customers = get_top_customers(completed_sales)

    print("\n--- MONTHLY REVENUE ---")
    print(monthly_revenue.head())

    print("\n--- TOP 10 PRODUCTS ---")
    print(top_products)

    print("\n--- TOP 10 COUNTRIES ---")
    print(country_sales.head(10))

    print("\n--- TOP 10 CUSTOMERS ---")
    print(top_customers)

    # Step 5: Save processed data
    project_root = Path(__file__).resolve().parent

    output_path = (
        project_root
        / "data"
        / "processed"
        / "completed_sales.csv"
    )

    completed_sales.to_csv(output_path, index=False)

    print("Processed data saved:", output_path)
    print("Pipeline completed successfully!")


if __name__ == "__main__":
    main()