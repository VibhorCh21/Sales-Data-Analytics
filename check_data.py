from src.data_loader import load_sales_data

df = load_sales_data()

print("\nFirst 5 rows:")
print(df.head())

print("\nDataset shape:")
print(df.shape)

print("\nColumn names:")
print(df.columns.tolist())

print("\nDataset information:")
df.info()


print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate rows:")
print(df.duplicated().sum())

print("\nNegative quantities:")
print((df["Quantity"] < 0).sum())

print("\nZero or negative prices:")
print((df["UnitPrice"] <= 0).sum())

print("\nCancelled invoices:")
print(df["InvoiceNo"].astype(str).str.startswith("C").sum())


print("\nSample cancelled invoices:")
print(
    df[df["InvoiceNo"].astype(str).str.startswith("C")]
    .head(5)
)

print("\nSample negative quantity records:")
print(
    df[df["Quantity"] < 0]
    .head(5)
)

print("\nSample zero/negative price records:")
print(
    df[df["UnitPrice"] <= 0]
    .head(5)
)


from src.data_cleaner import (
    remove_duplicates,
    handle_missing_values,
    calculate_revenue,
    separate_sales_and_returns,
    separate_cancelled_invoices,
    filter_valid_prices,
    get_completed_sales
)
print("\n--- DATA CLEANING ---")

# Step 1: Remove duplicate records
df_cleaned = remove_duplicates(df)

# Step 2: Handle missing values
df_cleaned = handle_missing_values(df_cleaned)

# Check final dataset
print("\nOriginal dataset shape:", df.shape)
print("Cleaned dataset shape:", df_cleaned.shape)

print("\nFinal missing values:")
print(df_cleaned.isnull().sum())

print("\n--- REVENUE CALCULATION ---")

df_cleaned = calculate_revenue(df_cleaned)

print("\nRevenue column:")
print(df_cleaned[["Quantity", "UnitPrice", "Revenue"]].head())

print("\nTotal revenue including returns:")
print(df_cleaned["Revenue"].sum())

print("\n--- SALES DATA FILTERING ---")

sales, returns = separate_sales_and_returns(df_cleaned)

regular, cancelled = separate_cancelled_invoices(df_cleaned)

valid_prices, invalid_prices = filter_valid_prices(df_cleaned)

completed_sales = get_completed_sales(df_cleaned)

print("\nNormal sales records:", len(sales))
print("Return records:", len(returns))

print("\nRegular invoice records:", len(regular))
print("Cancelled invoice records:", len(cancelled))

print("\nValid price records:", len(valid_prices))
print("Invalid price records:", len(invalid_prices))

print("\nCompleted sales records:", len(completed_sales))

print("\nCompleted sales revenue:")
print(completed_sales["Revenue"].sum())

from pathlib import Path

project_root = Path(__file__).resolve().parent
output_path = project_root / "data" / "processed" / "completed_sales.csv"

completed_sales.to_csv(output_path, index=False)

print("\nProcessed data saved successfully!")
print("File location:", output_path)