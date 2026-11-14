
def remove_duplicates(df):
    """
    Remove exact duplicate records.
    """

    before = len(df)

    df = df.drop_duplicates()

    after = len(df)

    removed = before - after

    print(f"Duplicate records removed: {removed}")

    return df


def handle_missing_values(df):
    """
    Handle missing values in the dataset.
    """

    df = df.copy()

    # Fill missing product descriptions
    df["Description"] = df["Description"].fillna("Unknown Product")

    print("Missing values handled.")
    print("\nRemaining missing values:")
    print(df.isnull().sum())

    return df
def calculate_revenue(df):
    """
    Calculate revenue for each transaction row.
    """

    df = df.copy()

    df["Revenue"] = df["Quantity"] * df["UnitPrice"]

    return df

def separate_sales_and_returns(df):
    """
    Separate normal sales and returned transactions.
    """

    sales = df[df["Quantity"] > 0].copy()
    returns = df[df["Quantity"] < 0].copy()

    return sales, returns


def separate_cancelled_invoices(df):
    """
    Separate cancelled invoices from regular invoices.
    """

    cancelled = df[
        df["InvoiceNo"].astype(str).str.startswith("C")
    ].copy()

    regular = df[
        ~df["InvoiceNo"].astype(str).str.startswith("C")
    ].copy()

    return regular, cancelled


def filter_valid_prices(df):
    """
    Keep transactions with positive unit prices.
    """

    valid = df[df["UnitPrice"] > 0].copy()
    invalid = df[df["UnitPrice"] <= 0].copy()

    return valid, invalid


def get_completed_sales(df):
    """
    Get valid completed sales transactions.
    """

    completed_sales = df[
        (df["Quantity"] > 0) &
        (df["UnitPrice"] > 0) &
        (~df["InvoiceNo"].astype(str).str.startswith("C"))
    ].copy()

    return completed_sales
