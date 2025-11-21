from utils.agg_settings import PATH_ASSET_PROFIT_DETAIL, PATH_ASSET_TYPE_AND_CATEGORY,\
    PATH_ASSET_RAW_DATA
from utils.file_io import load_parquet, load_csv, save_parquet
from utils.agg_init import get_latest_date_agg, get_latest_date_raw
from utils.agg_asset_collection import get_asset_raw_from_table, load_asset_raw_from_pdf
from utils.agg_asset_cleaning import data_cleaning
from utils.agg_asset_finalize import finalize_clean_data, check_not_registered_columns_before_finalize
import pandas as pd
import utils.reference_data_store as urds

def main():
    # ---- settings ----
    MAX_WORKERS = 8

    # ---- load phase ----
    df_asset_profit = load_parquet(PATH_ASSET_PROFIT_DETAIL)
    urds.df_asset_type_and_category = load_csv(PATH_ASSET_TYPE_AND_CATEGORY)

    # for development only
    df_asset_profit = df_asset_profit[df_asset_profit["date"] <= pd.to_datetime("2025-10-28")]

    latest_date_agg = get_latest_date_agg(df_asset_profit)
    latest_date_raw = get_latest_date_raw(PATH_ASSET_RAW_DATA)

    if latest_date_agg > latest_date_raw:
        raise ValueError("最新の集計日が生データ日より新しいです。処理を中止します。")

     # ---- raw data load ----
    all_tables_by_file = load_asset_raw_from_pdf(
        latest_date_agg + pd.Timedelta(days=1),
        latest_date_raw,
        PATH_ASSET_RAW_DATA,
        max_workers=MAX_WORKERS
    )

    df_raw = get_asset_raw_from_table(all_tables_by_file)
    
    # ---- processing ----
    df_pre = data_cleaning(df_raw)

    check_not_registered_columns_before_finalize(df_pre)

    df_final = finalize_clean_data(df_pre, df_asset_profit)
    df_final.sort_values("date", inplace=True)

    # ---- save ----
    save_parquet(df_final, "G:/マイドライブ/AssetManager/total/output/asset_detail_test.parquet")

# -----------------------------------------------------------
# Windows の spawn 問題を防ぐための絶対ルール
# -----------------------------------------------------------
if __name__ == "__main__":
    main()