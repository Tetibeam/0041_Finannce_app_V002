from .utils.make_target import make_target_main
from .utils.asset_aggregation import make_asset_main
from .utils.balance_aggregation import make_balance_main
from .utils.profit_aggregation import make_profit_main

from .lib.file_io import load_parquet, save_csv, load_csv
from .lib.agg_settings import PATH_ASSET_PROFIT_DETAIL, PATH_BALANCE_DETAIL
PATH_ASSET_PROFIT_DETAIL_DEV = "G:/マイドライブ/AssetManager/total/output/asset_detail_test2.parquet"

import os
import requests
import pandas as pd

API_BASE = os.environ.get("API_BASE_URL", "http://localhost:5000")
PATH_UPDATED_ASSET_PROFIT = "./data/update_diff/diff_asset_profit.csv"
PATH_UPDATED_BALANCE = "./data/update_diff/diff_balance.csv"

def update_master():
    # データ更新しマスターファイルを保存する
    #make_target_main()
    #make_asset_main()
    #make_balance_main()
    #make_profit_main()

    # APIをたたいて、DBの最新日付を取得する
    res = requests.get(f"{API_BASE}/api/dashboard/summary")
    data = res.json()
    latest_date = pd.to_datetime(data["summary"]["latest_date"])# - pd.Timedelta(days=1)
    #print(latest_date,type(latest_date))

    # マスターファイルを開く
    #df_master_asset_profit = load_parquet(PATH_ASSET_PROFIT_DETAIL)
    df_master_asset_profit = load_parquet(PATH_ASSET_PROFIT_DETAIL_DEV)
    df_master_balance = load_parquet(PATH_BALANCE_DETAIL)

    # 更新部分だけを抜き出す
    df_filtered_asset_profit = (
        df_master_asset_profit[df_master_asset_profit["date"] > latest_date]
    )
    df_filtered_balance = (
        df_master_balance[df_master_balance["date"] > latest_date]
    )
    #print(df_filtered_asset_profit)
    #print(df_filtered_balance)

    # 更新部分をファイルに保存する(空の場合も更新>更新部分がないということを知らせる)
    save_csv(df_filtered_asset_profit, PATH_UPDATED_ASSET_PROFIT)
    save_csv(df_filtered_balance, PATH_UPDATED_BALANCE)

if __name__ == "__main__":
    update_master()