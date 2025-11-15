import pandas as pd
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_DIR  = os.path.join(BASE_DIR, "database")
FINANCE_DB = os.path.join(DB_DIR, "finance.db")
TARGET_PARAMETER_DB = os.path.join(DB_DIR, "target_parameter.db")

RAW_DATA_DIR = "G:\マイドライブ\AssetManager\Total\output"
RAW_PARAMETER_DIR = "G:\マイドライブ\AssetManager\Total\parameter"


def parquet_to_sqlite(parquet_file, table_name, conn):
    df = pd.read_parquet(parquet_file)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"Table {table_name} created from {os.path.basename(parquet_file)}")

def init_finance_db():
    with sqlite3.connect(FINANCE_DB) as conn:
        parquet_to_sqlite(os.path.join(RAW_DATA_DIR, "asset_detail_test2.parquet"), "asset", conn)
        parquet_to_sqlite(os.path.join(RAW_DATA_DIR, "balance_detail.parquet"), "balance", conn)
        parquet_to_sqlite(os.path.join(RAW_DATA_DIR, "target_asset_profit.parquet"), "target", conn)

    print(f"Finance DB initialized at {FINANCE_DB}")

def init_target_parameter():
    with sqlite3.connect(TARGET_PARAMETER_DB) as conn:
        parquet_to_sqlite(os.path.join(RAW_PARAMETER_DIR, "target_parameter.parquet"), "target_parameter", conn)

    print(f"Target Parameter DB initialized at {TARGET_PARAMETER_DB}")


if __name__ == "__main__":
    init_finance_db()
    init_target_parameter()