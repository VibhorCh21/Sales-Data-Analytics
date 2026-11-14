
import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.types import (
    String, BigInteger, DateTime, Numeric, Float
)

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "processed" / "completed_sales.csv"

# Load Neon credentials
load_dotenv(BASE_DIR / ".env")

# Neon database connection
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("NEON_DB_USER"),
    password=os.getenv("NEON_DB_PASSWORD"),
    host=os.getenv("NEON_DB_HOST"),
    port=int(os.getenv("NEON_DB_PORT", "5432")),
    database=os.getenv("NEON_DB_NAME"),
    query={"sslmode": "require"}
)

engine = create_engine(DATABASE_URL)

def migrate_data():
    print("Reading sales CSV...")

    df = pd.read_csv(
        CSV_PATH,
        dtype={"InvoiceNo": str, "StockCode": str},
        low_memory=False
    )

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    df["CustomerID"] = df["CustomerID"].astype("Int64")
    df["CustomerID"] = df["CustomerID"].astype(object)
    df["CustomerID"] = df["CustomerID"].where(
        pd.notna(df["CustomerID"]), None
    )

    print(f"Records found: {len(df):,}")
    print("Uploading data to Neon...")

    column_types = {
        "InvoiceNo": String(20),
        "StockCode": String(20),
        "Description": String(255),
        "Quantity": BigInteger(),
        "InvoiceDate": DateTime(),
        "UnitPrice": Float(),
        "CustomerID": BigInteger(),
        "Country": String(100),
        "Revenue": Numeric(12, 2)
    }

    with engine.begin() as connection:
        df.to_sql(
            name="sales",
            con=connection,
            if_exists="replace",
            index=False,
            chunksize=2000,
            dtype=column_types
        )

    print("Migration completed successfully!")

    with engine.connect() as connection:
        count = connection.exec_driver_sql(
            "SELECT COUNT(*) FROM sales"
        ).scalar()

        print(f"Records in Neon: {count:,}")

    engine.dispose()


if __name__ == "__main__":
    migrate_data()
