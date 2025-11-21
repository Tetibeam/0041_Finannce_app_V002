from utils.file_io import load_parquet, load_csv, save_parquet
import utils.reference_data_store as urds
from utils.main_helper import safe_load_master, safe_pipe
from utils.exceptions import DataLoadError

from utils.agg_settings import PATH_ASSET_PROFIT_DETAIL, PATH_OFFSET_UNREALIZED, PATH_BALANCE_RAW_DATA,\
    PATH_ASSET_TYPE_AND_CATEGORY
from utils.agg_profit_cal import set_unrealized_profit, set_realized_deposit, set_realized_mrf,\
    set_realized_interest,set_realized_dividend_and_capital,set_realized_cloud_funds,set_total_returns
from utils.agg_balance_collection import filter_and_clean_raw
from utils.agg_init import load_balance_raw_file, get_latest_date_agg

import pandas as pd

PATHS = {
    "asset_type_and_category": PATH_ASSET_TYPE_AND_CATEGORY,
    "offset_unrealized": PATH_OFFSET_UNREALIZED,
    #"asset_profit": PATH_ASSET_PROFIT_DETAIL
    "asset_profit": "G:/マイドライブ/AssetManager/total/output/asset_detail_test.parquet",
}
#PATH_OUTPUT = PATH_ASSET_PROFIT_DETAIL
PATH_OUTPUT = "G:/マイドライブ/AssetManager/total/output/asset_detail_test2.parquet"

START_DATE = pd.to_datetime("2024/10/01")

def main():
    try:
        # ---- load masters safely ----
        masters = safe_load_master({
            "asset_type_and_category": lambda: load_csv(PATHS["asset_type_and_category"]),
            "offset_unrealized": lambda: load_parquet(PATHS["offset_unrealized"]),
            "asset_profit": lambda: load_parquet(PATHS["asset_profit"]),
        })
        urds.df_asset_type_and_category = masters["asset_type_and_category"]
        urds.df_offset_unrealized = masters["offset_unrealized"]
        df_asset_profit = masters["asset_profit"]

        # ---- date range ----
        end_date = get_latest_date_agg(df_asset_profit)
        if pd.isna(end_date):
            raise DataLoadError("df_asset_profit に有効な日付がありません")

        # ---- raw balance load ----
        df_balance_raw = load_balance_raw_file(start_year=2024, end_year=end_date.year+1, path=PATH_BALANCE_RAW_DATA)
        df_balance_raw_filtered = filter_and_clean_raw(start_date=START_DATE, end_date=end_date, df=df_balance_raw)

        # ---- profit calculation pipeline ----
        df_all_profit = (
            df_asset_profit
            .pipe(safe_pipe(set_unrealized_profit, debug=False))
            .pipe(safe_pipe(set_realized_deposit, df_balance_raw_filtered, debug=False))
            .pipe(safe_pipe(set_realized_mrf, debug=False))
            .pipe(safe_pipe(set_realized_interest, df_balance_raw_filtered, debug=False))
            .pipe(safe_pipe(set_realized_dividend_and_capital, df_balance_raw_filtered, debug=False))
            .pipe(safe_pipe(set_realized_cloud_funds, START_DATE, end_date, df_balance_raw_filtered, debug=False))
            .pipe(safe_pipe(set_total_returns, debug=False))
        )
        df_all_profit.sort_values("date", inplace=True)

        # ---- save ----
        save_parquet(df_all_profit, PATH_OUTPUT)
    except Exception as e:
        print(f"[ERROR] {e}")
        raise

if __name__ == "__main__":
    main()

"""V.001 動作確認版
# ファイルをロード
# df_asset_profit = load_parquet(PATH_ASSET_PROFIT_DETAIL)
df_asset_profit = load_parquet("G:/マイドライブ/AssetManager/total/output/asset_detail_test.parquet")
urds.df_offset_unrealized = load_parquet(PATH_OFFSET_UNREALIZED)
urds.df_asset_type_and_category = load_csv(PATH_ASSET_TYPE_AND_CATEGORY)

# 収支の生データを作成
start_date = pd.to_datetime("2024/10/01")
end_date = get_latest_date_agg(df_asset_profit)

df_balance_raw = load_balance_raw_file(2024, end_date.year+1, PATH_BALANCE_RAW_DATA)
df_balance_raw_filtered = filter_and_clean_raw(start_date, end_date, df_balance_raw)

# 含み損益 - 対象：国内株式、投資信託、確定年金、確定拠出年金、セキュリティートークン
df_asset_profit_unrealized = set_unrealized_profit(df_asset_profit)

# 実現損益（利息等） - 対象：普通預金、定期預金、仕組預金
df_asset_profit_deposit = set_realized_deposit(df_asset_profit_unrealized, df_balance_raw_filtered)

# 実現損益（利金・為替等） - 対象：MRF,外貨普通預金
df_asset_profit_mrf = set_realized_mrf(df_asset_profit_deposit)

# 実現損益（利金）- 対象：日本国債、円建社債
df_asset_profit_interest = set_realized_interest(df_asset_profit_mrf,df_balance_raw_filtered)

# 実現損益（配当、売却） - 対象：国内株式、セキュリティートークン
df_asset_profit_dividend = set_realized_dividend_and_capital(df_asset_profit_interest,df_balance_raw_filtered)

# 実現損益（配当） - 対象：ソーシャルレンディング、セキュリティートークン（ALTANA）
df_asset_profit_cloud_funds = set_realized_cloud_funds(start_date, end_date, df_asset_profit_dividend,df_balance_raw_filtered)

# トータルリターン
df_asset_profit_total_returns = set_total_returns(df_asset_profit_cloud_funds)

# 保存
save_parquet(df_asset_profit_total_returns, "G:/マイドライブ/AssetManager/total/output/asset_detail_test2.parquet")
"""