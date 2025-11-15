import sys
from pathlib import Path

# このファイルの親フォルダ(= modules の親)をパスに追加
sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils.read_from_db import get_asset_and_profit_dashboard, get_balance_dashboard
from utils.calculation import cal_general_special_balance_dashboard, cal_total_return_target_dashboard
import utils.visualize_dashboard as viz

graphs_cache = {}
graphs_info = {
    "assets": "🤑 総資産推移",
    "general_income_expenditure": "🤑 一般収入・支出",
    "special_income_expenditure": "🤑 特別収入・支出",
    "returns": "🤑 トータルリターン",
    "general_balance": "🤑 一般収支",
    "special_balance": "🤑 特別収支"
}

def build_dashboard_graphs(db_path):
    global graphs_cache

    # データ取得
    df_asset_profit = get_asset_and_profit_dashboard(db_path)
    df_asset_profit = cal_total_return_target_dashboard(df_asset_profit)
    df_balance = get_balance_dashboard(db_path)
    df_general = cal_general_special_balance_dashboard(df_balance, "一般収支")
    df_special = cal_general_special_balance_dashboard(df_balance, "特別収支")

    # グラフ化
    graphs_cache.clear()

    graphs_cache["assets"] = viz.write_html(viz.display_total_assets(df_asset_profit), "assets")
    graphs_cache["returns"] = viz.write_html(viz.display_total_returns(df_asset_profit), "returns")
    graphs_cache["general_income_expenditure"] = viz.write_html(viz.display_general_income_expenditure(df_general), "general_income_expenditure")
    graphs_cache["general_balance"] = viz.write_html(viz.display_general_balance(df_general), "general_balance")
    graphs_cache["special_income_expenditure"] = viz.write_html(viz.display_special_income_expenditure(df_special), "special_income_expenditure")
    graphs_cache["special_balance"] = viz.write_html(viz.display_special_balance(df_special), "special_balance")

    return graphs_cache, graphs_info
