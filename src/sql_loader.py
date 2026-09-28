"""
GulfMart Retail Inventory Analytics
------------------------------------

Loads fact_inventory into SQL Server via pyodbc, bypassing BULK
INSERT (see README for why: gzip compression, and this avoids the
same category of CRLF/BIT-as-text issues already hit loading the
smaller tables).

Requires the SQL_PASSWORD environment variable to be set before
running (never hardcode a password in this file):

    PowerShell:  $env:SQL_PASSWORD = "your_password"
    then:        python src/sql_loader.py
"""

import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyodbc

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"

SERVER = "."
DATABASE = "GulfMartRetailAnalytics"
USERNAME = "sa"
DRIVER = "ODBC Driver 18 for SQL Server"

CHUNK_SIZE = 50_000

# The exact fact_inventory column order defined in 02_create_tables.sql.
# Matches the pandas column names from generate_fact_inventory() 1:1 --
# no renaming needed.
FACT_INVENTORY_COLUMNS = [
    "date",
    "store_id",
    "product_id",
    "supplier_id",
    "opening_stock",
    "closing_stock",
    "sales_units",
    "receipts",
    "transfers_in",
    "transfers_out",
    "returns_units",
    "damaged_units",
    "inventory_adjustments",
    "demand_rate",
    "safety_stock_units",
    "lead_time_days",
    "minimum_order_qty",
    "replenishment_interval_days",
    "reorder_point",
    "target_stock_level",
    "planned_order_quantity",
    "inventory_status",
    "stockout_event",
    "low_stock_event",
    "inventory_coverage_days",
]


def get_connection():
    """
    Build a pyodbc connection using SQL Server Authentication.
    Password is read from the SQL_PASSWORD environment variable --
    never hardcoded, never committed to Git.
    """

    password = os.environ.get("SQL_PASSWORD")

    if not password:
        print(
            "ERROR: SQL_PASSWORD environment variable is not set.\n"
            "Run this first, in the same terminal session:\n"
            '  $env:SQL_PASSWORD = "your_password"'
        )
        sys.exit(1)

    connection_string = (
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"UID={USERNAME};"
        f"PWD={password};"
        f"TrustServerCertificate=yes;"
    )

    return pyodbc.connect(connection_string)


def prepare_dataframe(fact_inventory):
    """
    Select and clean the analytical subset of fact_inventory columns,
    and convert every value to a native Python type.

    This conversion step matters: pyodbc's fast_executemany does not
    reliably handle numpy scalar types (numpy.int32, numpy.float32,
    numpy.bool_) the way it handles native Python int/float/bool --
    silent type errors or wrong values can result. Converting
    explicitly avoids that entirely rather than hoping it works.

    NaN in inventory_coverage_days (undefined when demand_rate = 0)
    is converted to None, which pyodbc inserts as SQL NULL.
    """

    df = fact_inventory[FACT_INVENTORY_COLUMNS].copy()

    df["date"] = pd.to_datetime(df["date"]).dt.date

    for col in ["stockout_event", "low_stock_event"]:
        df[col] = df[col].astype(int)

    df = df.replace({np.nan: None})

    return df


def dataframe_to_row_tuples(df_chunk):
    """
    Convert a DataFrame chunk into a list of tuples of native Python
    types, ready for pyodbc's executemany().
    """

    records = df_chunk.to_dict("records")

    return [tuple(record[col] for col in FACT_INVENTORY_COLUMNS) for record in records]


def load_fact_inventory():
    print("=" * 60)
    print("Loading fact_inventory into SQL Server")
    print("=" * 60)

    print("\nConnecting to SQL Server...")
    connection = get_connection()
    cursor = connection.cursor()
    cursor.fast_executemany = True

    print("\nReading fact_inventory.csv.gz...")
    start = time.time()
    fact_inventory = pd.read_csv(DATA_RAW_DIR / "fact_inventory.csv.gz")
    print(f"Loaded {len(fact_inventory):,} rows in {time.time() - start:.1f}s")

    df = prepare_dataframe(fact_inventory)

    print("Truncating existing fact_inventory rows...")
    cursor.execute("TRUNCATE TABLE dbo.fact_inventory;")
    connection.commit()

    placeholders = ", ".join(["?"] * len(FACT_INVENTORY_COLUMNS))
    columns_sql = ", ".join(
        f"[{c}]" if c == "date" else c for c in FACT_INVENTORY_COLUMNS
    )
    insert_sql = (
        f"INSERT INTO dbo.fact_inventory ({columns_sql}) VALUES ({placeholders})"
    )

    total_rows = len(df)
    rows_inserted = 0
    start = time.time()

    for chunk_start in range(0, total_rows, CHUNK_SIZE):
        chunk = df.iloc[chunk_start : chunk_start + CHUNK_SIZE]
        rows = dataframe_to_row_tuples(chunk)

        cursor.executemany(insert_sql, rows)
        connection.commit()

        rows_inserted += len(rows)
        elapsed = time.time() - start
        rate = rows_inserted / elapsed if elapsed > 0 else 0

        print(
            f"  Inserted {rows_inserted:,} / {total_rows:,} rows "
            f"({rows_inserted / total_rows:.1%}) — {rate:,.0f} rows/sec"
        )

    print(f"\nInsert complete in {time.time() - start:.1f}s")

    verify_count = cursor.execute("SELECT COUNT(*) FROM dbo.fact_inventory;").fetchval()
    print(f"Verified row count in SQL Server: {verify_count:,}")

    if verify_count != total_rows:
        print(
            f"WARNING: row count mismatch! "
            f"Expected {total_rows:,}, found {verify_count:,}."
        )
    else:
        print("Row count matches expected total. Load successful.")

    cursor.close()
    connection.close()


if __name__ == "__main__":
    load_fact_inventory()
