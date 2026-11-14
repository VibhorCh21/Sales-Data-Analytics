import pandas as pd

from src.data_cleaner import (
    remove_duplicates,
    handle_missing_values,
    calculate_revenue,
    get_completed_sales
)


def test_remove_duplicates():
    data = {
        "Product": ["A", "B", "A"],
        "Quantity": [2, 3, 2]
    }

    df = pd.DataFrame(data)

    result = remove_duplicates(df)

    assert len(result) == 2


def test_handle_missing_values():
    data = {
        "Description": ["Product A", None],
        "CustomerID": [1001, None]
    }

    df = pd.DataFrame(data)

    result = handle_missing_values(df)

    assert result["Description"].isnull().sum() == 0
    assert result["Description"].iloc[1] == "Unknown Product"

    # CustomerID missing values should remain unchanged
    assert result["CustomerID"].isnull().sum() == 1


def test_calculate_revenue():
    data = {
        "Quantity": [2, 3],
        "UnitPrice": [100, 50]
    }

    df = pd.DataFrame(data)

    result = calculate_revenue(df)

    assert result["Revenue"].tolist() == [200, 150]


def test_get_completed_sales():
    data = {
        "InvoiceNo": ["1001", "1002", "C1003", "1004"],
        "Quantity": [2, -1, 3, 1],
        "UnitPrice": [100, 50, 20, 0]
    }

    df = pd.DataFrame(data)

    result = get_completed_sales(df)

    assert len(result) == 1
    assert result.iloc[0]["InvoiceNo"] == "1001"