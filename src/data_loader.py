
import pandas as pd
from pathlib import Path


def load_sales_data():
    """Load sales data from the Excel file."""

    project_root = Path(__file__).resolve().parent.parent
    file_path = project_root / "data" / "raw" / "online_retail.xlsx"

    df = pd.read_excel(file_path)

    return df
