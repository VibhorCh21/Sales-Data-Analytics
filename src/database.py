
import os
import pandas as pd
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text, MetaData, Table, Column
from sqlalchemy import String, BigInteger, DateTime, Numeric, Float
from sqlalchemy.engine import URL

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

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
metadata = MetaData()

sales_table = Table(
    "sales",
    metadata,
    Column("InvoiceNo", String(20)),
    Column("StockCode", String(20)),
    Column("Description", String(255)),
    Column("Quantity", BigInteger),
    Column("InvoiceDate", DateTime),
    Column("UnitPrice", Float),
    Column("CustomerID", Float),
    Column("Country", String(100)),
    Column("Revenue", Numeric(12, 2))
)
def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            print("Database connected successfully!")
            print(result.scalar())
    except Exception as error:
        print("Database connection failed:", error)

def test_neon_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            print("Neon database connected successfully!")
            print(result.scalar())
    except Exception as error:
        print("Neon connection failed:", error)



def load_sales_to_database():
    """Load completed sales data into PostgreSQL."""

    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / "data" / "processed" / "completed_sales.csv"

    df = pd.read_csv(
        csv_path,
        dtype={"InvoiceNo": str},
        low_memory=False
    )

    # Convert data types
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["CustomerID"] = df["CustomerID"].astype("Int64")
    df["CustomerID"] = df["CustomerID"].astype(object)
    df["CustomerID"] = df["CustomerID"].where(
        pd.notna(df["CustomerID"]), None
    )

    # Insert records in batches
    with engine.begin() as connection:
        sales_table.drop(connection, checkfirst=True)
        sales_table.create(connection)

        df.to_sql(
            name="sales",
            con=connection,
            if_exists="append",
            index=False,
            chunksize=2000,
            method=None
        )

    print(f"Successfully loaded {len(df)} records into PostgreSQL!")
