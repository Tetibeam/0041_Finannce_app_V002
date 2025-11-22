import pandas as pd
import sqlite3
import os
from typing import Union, List

def get_df_from_db(db_path: str, table_name: str, index_col: str, columns_col, values_col,
                   aggfunc="sum", where_clause=None, set_index: bool=False):
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
    # --- データ読み込み ---
    conn = sqlite3.connect(db_path)
    query = f'SELECT * FROM "{table_name}"'
    if where_clause:
        query += f" WHERE {where_clause}"
    df = pd.read_sql_query(query, conn)
    conn.close()

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