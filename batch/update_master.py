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
import logging

API_BASE = os.environ.get("API_BASE_URL", "http://localhost:5000")
PATH_UPDATED_ASSET_PROFIT = "./data/update_diff/diff_asset_profit.csv"
PATH_UPDATED_BALANCE = "./data/update_diff/diff_balance.csv"

# ロガーの設定
logger = logging.getLogger(__name__)

def update_master():
    """
    データを更新し、APIから最新日付を取得して差分ファイルを生成する。
    """
    logger.info("Master update started.")
    try:
        # データ更新しマスターファイルを保存する
        make_target_main()
        make_asset_main()
        make_balance_main()
        make_profit_main()
        logger.info("Master update finished.")

        # APIをたたいて、DBの最新日付を取得する
        res = requests.get(f"{API_BASE}/api/dashboard/summary", timeout=10)
        res.raise_for_status() # エラーチェック
        data = res.json()
        latest_date = pd.to_datetime(data["summary"]["latest_date"])# - pd.Timedelta(days=1)
        logger.info(f"Latest date from API: {latest_date}")

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

        # 更新部分をファイルに保存する(空の場合も更新>更新部分がないということを知らせる)
        save_csv(df_filtered_asset_profit, PATH_UPDATED_ASSET_PROFIT)
        save_csv(df_filtered_balance, PATH_UPDATED_BALANCE)
        logger.info("Master update completed successfully.")

        # ---------------------------------------------------------
        # APIへデータをアップロードしてDBを更新する
        # ---------------------------------------------------------
        upload_url = f"{API_BASE}/api/data/upload"
        logger.info(f"Uploading data to {upload_url}...")

        files = {
            "file_asset": open(PATH_UPDATED_ASSET_PROFIT, "rb"),
            "file_balance": open(PATH_UPDATED_BALANCE, "rb")
        }
        
        try:
            resp = requests.post(upload_url, files=files, timeout=30)
            resp.raise_for_status()
            py
            logger.info(f"Upload successful: {result}")
        except Exception as e:
            logger.error(f"Failed to upload data: {e}")
        finally:
            # ファイルハンドルを閉じる
            for f in files.values():
                f.close()

    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise

if __name__ == "__main__":
    # ロガーの設定を追加
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    update_master()