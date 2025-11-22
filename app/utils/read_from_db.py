from app.utils.data_loader import get_df_from_db
import pandas as pd

def get_asset_and_profit_dashboard(DB_PATH_FINANCE: str):
    """
    指定されたDBパスから資産データと損益データを取得し、ダッシュボード表示用に整形する。

    Args:
        DB_PATH_FINANCE (str): 財務データベースのパス。

    Returns:
        pd.DataFrame: 整形された資産と損益のデータフレーム。

    """
    df_asset = get_df_from_db(
        DB_PATH_FINANCE, "asset", "date", None, ["資産額","トータルリターン"],"sum",set_index=True
        )

    end_date = df_asset.index.max() + pd.DateOffset(months=1)
    where_clause = f"date <= DATE('{end_date}')"
    df_asset_target = get_df_from_db(
        DB_PATH_FINANCE, "target", "date", None, ["資産額", "トータルリターン"], "sum", set_index=True,
        where_clause=where_clause)

    df_merged = pd.merge(
        df_asset, df_asset_target, left_index=True,right_index=True, how="outer", suffixes=("_実績", "_目標"))
    return df_merged

def get_balance_dashboard(DB_PATH_FINANCE: str):
    df = get_df_from_db(
        DB_PATH_FINANCE, "balance", "date", ["収支タイプ", "収支カテゴリー"],["金額", "目標"],
        "sum", set_index=True
    )
    return df