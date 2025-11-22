import pandas as pd
import sqlite3
import os
from typing import Union, List
from pathlib import Path

# DBアクセスは with 文を使うことにします
# 1. commit/rollback/close を自動化して安全
# 2. コードが短く、読みやすい
# 3. 例外発生時も DB が壊れない

def get_df_from_db(
    db_path: str, table_name: str, index_col: str, columns_col, values_col,
    aggfunc="sum", where_clause=None, set_index: bool=False
):
    """
    指定されたデータベースからデータを読み込み、DataFrameを返す。

    Args:
        db_path (str): SQLiteデータベースのパス。
        table_name (str): データを取得するテーブル名。
        index_col (str): DataFrameのインデックス（またはgroupbyの第一引数）として使用する列名。
        columns_col (str or list, optional): groupbyの第二引数として使用する列名。
                                            Noneの場合、index_colとvalues_colのみでgroupbyを行う。
        values_col (str or list): 集計対象の列名。
        aggfunc (str, optional): 集計関数。デフォルトは"sum"。
        where_clause (str, optional): データをフィルタリングするためのWHERE句。デフォルトはNone。
        set_index (bool, optional): index_col をDataFrameのインデックスとして設定するかどうか。デフォルトはFalse。

    Returns:
        pd.DataFrame: 処理されたDataFrame。
    """
    query = f'SELECT * FROM "{table_name}"'
    if where_clause:
        query += f" WHERE {where_clause}"
    # --- with を使って接続管理 ---
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(query, conn)

    # --- 日付列があれば変換 ---
    if isinstance(index_col, str):
        if any(key in index_col.lower() for key in ["date", "日", "年月", "timestamp"]):
            df[index_col] = pd.to_datetime(df[index_col], errors="coerce")

    # --- 列の指定がない場合のデフォルト動作 ---
    if columns_col is None:
        # index_col でグループ化して values_col を集計
        values = [values_col] if isinstance(values_col, str) else values_col
        grouped = df.groupby(index_col, as_index=False)[values].agg(aggfunc)
        return grouped.set_index(index_col) if set_index else grouped

    # --- 通常のgroupby処理 ---
    group_keys = [index_col] + ([columns_col] if isinstance(columns_col, str) else columns_col)
    values = [values_col] if isinstance(values_col, str) else values_col

    grouped = df.groupby(group_keys, as_index=False)[values].agg(aggfunc)

    return grouped.set_index(index_col) if set_index else grouped

def append_to_table(db_path: str, df: pd.DataFrame, table_name: str) -> int:
    """
    DataFrame の内容を指定テーブルに追記して、追加件数を返す。

    Args:
        db_path (str): SQLite データベースのパス
        df (pd.DataFrame): 追記する DataFrame
        table_name (str): 追記先テーブル名

    Returns:
        int: 追加した行数
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df must be a pandas DataFrame, got {type(df)}")
    if df.empty:
        return 0
    if not isinstance(table_name, str) or not table_name.isidentifier():
        raise ValueError(f"Invalid table name: {table_name}")

    db_file = Path(db_path)
    if not db_file.exists():
        raise FileNotFoundError(f"DBファイルが存在しません: {db_path}")

    # --- DB接続、withで管理 ---
    try:
        with sqlite3.connect(db_path) as conn:
            df.to_sql(table_name, conn, if_exists="append", index=False)
            return len(df)
    except Exception as e:
        raise InternalServerError(f"DB追加に失敗しました: {e}")

def update_from_csv(db_path: str, csv_path: str, table_name: str) -> int:
    """
    CSV ファイルを読み込んで指定テーブルに追記する。

    Args:
        db_path (str): SQLite データベースのパス
        csv_path (str): CSV ファイルのパス
        table_name (str): 追記先テーブル名

    Returns:
        int: 追加した行数
    """
    df = pd.read_csv(csv_path)
    return append_to_table(db_path, df, table_name)