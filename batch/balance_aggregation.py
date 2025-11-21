from utils.file_io import load_parquet, save_parquet
from utils.main_helper import safe_load_master, safe_pipe
import utils.reference_data_store as urds

from utils.agg_init import get_latest_date_agg, load_balance_raw_file
from utils.agg_settings import PATH_BALANCE_TYPE_AND_CATEGORY, PATH_ASSET_PROFIT_DETAIL,\
    PATH_BALANCE_RAW_DATA,PATH_BALANCE_DETAIL
from utils.target_settings import PATH_TARGET_BALANCE

from utils.agg_balance_collection import filter_and_clean_raw, collect_balance,\
    collect_living_adjust, collect_year_end_tax_adjustment, collect_points
from utils.agg_balance_finalize import finalize_data

import pandas as pd
from utils.exceptions import DataLoadError

PATHS = {
    "balance_type_category": PATH_BALANCE_TYPE_AND_CATEGORY,
    #"asset_profit": PATH_ASSET_PROFIT_DETAIL,
    "asset_profit": "G:/マイドライブ/AssetManager/total/output/asset_detail_test.parquet",
    "balance_target": PATH_TARGET_BALANCE
}
PATH_OUTPUT = PATH_BALANCE_DETAIL
START_DATE = pd.to_datetime("2024/10/01")

def main():
    try:
        # ---- load masters safely ----
        masters = safe_load_master({
            "balance_type_category": lambda: load_parquet(PATHS["balance_type_category"]),
            "asset_profit": lambda: load_parquet(PATHS["asset_profit"]),
            "balance_target": lambda: load_parquet(PATHS["balance_target"]),
        })

        urds.df_balance_type_and_category = masters["balance_type_category"]
        df_asset_profit = masters["asset_profit"]
        urds.df_balance_target = masters["balance_target"]

        # ---- date range ----
        end_date = get_latest_date_agg(df_asset_profit)
        if pd.isna(end_date):
            raise DataLoadError("df_asset_profit に有効な日付がありません")

        # ---- raw balance load ----
        df_balance_raw = load_balance_raw_file(start_year=2024, end_year=end_date.year+1, path=PATH_BALANCE_RAW_DATA)
        df_balance_raw_filtered = filter_and_clean_raw(start_date=START_DATE, end_date=end_date, df=df_balance_raw)

        # ---- balance detail calculation ----
        df_balance_detail = pd.DataFrame()
        df_pre = (
            df_balance_detail
            .pipe(safe_pipe(collect_balance, df_balance_raw_filtered))
            .pipe(safe_pipe(collect_living_adjust))
            .pipe(safe_pipe(collect_year_end_tax_adjustment, START_DATE, end_date))
            .pipe(safe_pipe(collect_points, df_asset_profit))
        )
        # ---- finalize & save ----
        df_final = finalize_data(START_DATE, end_date, df_pre)
        df_final.sort_values("date", inplace=True)

        save_parquet(df_final, PATH_OUTPUT)
    except Exception as e:
        print(f"[ERROR] {e}")
        raise

if __name__ == "__main__":
    main()

"""V.001 動作確認版
# ファイルの読み込み / 参照データの登録
urds.df_balance_type_and_category = load_parquet(PATH_BALANCE_TYPE_AND_CATEGORY)
df_asset_profit = load_parquet(PATH_ASSET_PROFIT_DETAIL)
urds.df_balance_target = load_parquet(PATH_TARGET_BALANCE)

# 収支データの日付範囲の設定
start_date = pd.to_datetime("2024/10/01")
end_date = get_latest_date_agg(df_asset_profit)

# 収支の生データを作成
df_balance_raw = load_balance_raw_file(2024, end_date.year+1, PATH_BALANCE_RAW_DATA)
df_balance_raw_filtered = filter_and_clean_raw(start_date, end_date, df_balance_raw)

# データフレームの初期化
df_balance_detail = pd.DataFrame()

# 一般収支
df_balance_detail_general = collect_general_balance(df_balance_raw_filtered, df_balance_detail)

# 特別収支
df_balance_detail_special = collect_special_balance(df_balance_raw_filtered, df_balance_detail_general)

# 生活費調整（二重計算）
df_balance_living_adjust = collect_living_adjust(df_balance_detail_special)

# 年末調整
df_balance_year_end_tax_adjustment = collect_year_end_tax_adjustment(start_date, end_date, df_balance_living_adjust)

# ポイント収支
df_balance_points = collect_points(df_asset_profit, df_balance_year_end_tax_adjustment)

# 収支データ整形
df_finalized = finalize_data(start_date, end_date, df_balance_points)

# 保存
save_parquet(df_finalized, PATH_BALANCE_DETAIL)
"""