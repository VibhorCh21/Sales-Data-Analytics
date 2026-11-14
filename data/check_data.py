
from src.data_loader import load_sales_data

# Load the Excel dataset
df = load_sales_data()

# Display first 5 rows
print("\nFirst 5 rows:")
print(df.head())

# Display number of rows and columns
print("\nDataset shape:")
print(df.shape)

# Display column names
print("\nColumn names:")
print(df.columns.tolist())

# Display dataset information
print("\nDataset information:")
df.info()

