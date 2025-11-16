from utils.data_loader import get_df_from_db
from typing import Dict, Any
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import plotly.express as px

# このファイルの親フォルダ(= modules の親)をパスに追加
sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils.calculation import cal_general_special_balance_dashboard, cal_total_return_target_dashboard
from utils.read_from_db import get_asset_and_profit_dashboard, get_balance_dashboard
from typing import Dict, Any
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


def read_table_from_db(db_path):
    df_asset_profit = get_df_from_db(
        db_path=db_path, table_name="asset", index_col="date", columns_col=None, 
        values_col=["資産額", "トータルリターン"], aggfunc="sum", set_index=True
    )
    df_balance = get_df_from_db(
        db_path=db_path, table_name="balance", index_col="date", columns_col= ["収支タイプ", "収支カテゴリー"],
        values_col=["金額", "目標"],aggfunc="sum", set_index=True
    )
    df_target = get_df_from_db(
        db_path=db_path, table_name="target", index_col="date", columns_col= None,
        values_col=["資産額", "トータルリターン"],aggfunc="sum", set_index=True,
    )
    return df_asset_profit, df_balance, df_target

def build_summary(df_asset_profit, df_target) -> Dict[str, float]:
    latest = df_asset_profit.index.max()
    return {
        "latest_date": latest,
        "total_assets": df_asset_profit.loc[latest, "資産額"],
        "total_target_assets": df_target.loc[latest, "資産額"],
        "total_returns": df_asset_profit.loc[latest, "トータルリターン"],
        "total_target_returns": df_target.loc[latest, "トータルリターン"],
    }

def graph_common_setting(fig):
    fig.update_xaxes(tickformat="%y/%m/%d")
    fig.update_layout(
        # サイズ調整
        autosize=True, margin=dict(l=0,r=10,t=0,b=30),
        title_font=dict(size=14), font=dict(size=8),
    )

    for trace in fig.data:
        trace.name = trace.name  # 再設定して凡例マッピングを維持

    fig.update_layout(
        legend=dict(
            visible=True,
            orientation="h",
            yanchor="top",
            y=1.2,
            xanchor="right",
            x=1,
        )
    )

    return fig

def build_total_assets(df_asset_profit, df_target):
    # データフレーム生成
    df = pd.merge(df_asset_profit["資産額"], df_target["資産額"],
                  left_index=True, right_index=True,suffixes=("_実績", "_目標"))
    # PXでグラフ生成
    fig = px.line(df, x=df.index, y=["資産額_実績", "資産額_目標"],template="plotly_dark",
            labels={"index": "日付", "value":"資産額","variable":""})
    fig = graph_common_setting(fig)

    # metaでID付与
    fig.update_layout(meta={"id": "total_assets"})

    # JSONに変換
    return fig.to_json()

def build_total_returns(df_asset_profit, df_target):
    # データフレーム生成
    df_cumsum_target = df_target["トータルリターン"].cumsum()
    df = pd.merge(df_asset_profit["トータルリターン"], df_cumsum_target,
                  left_index=True, right_index=True,suffixes=("_実績", "_目標"))
    # PXでグラフ生成
    fig = px.line(df, x=df.index, y=["トータルリターン_実績", "トータルリターン_目標"],template="plotly_dark",
            labels={"index": "日付", "value":"トータルリターン","variable":""})
    fig = graph_common_setting(fig)
    # metaでID付与
    fig.update_layout(meta={"id": "total_returns"})
    #fig.show()

    # JSONに変換
    return fig.to_json()

def make_df_general(df_balance):
    df_general = df_balance.query('収支タイプ == "一般収支"')
    df_general = df_general.pivot_table(
        index="date", columns="収支カテゴリー",values=["金額", "目標"], aggfunc="sum")
    df_general.columns = [f"{val}_{cat}" for val, cat in df_general.columns]
    df_general = df_general.resample('ME').sum()
    #print(df_general)
    return df_general

def build_general_income_expenditure(df_general):
    # PXでグラフ生成
    fig = px.bar(
        df_general, x=df_general.index, y=["金額_収入", "金額_支出"], barmode='group',
        template='plotly_dark',labels={'value':'金額', 'date':'年月', 'variable':''}
    )
    fig.add_scatter(
        x=df_general.index,
        y=df_general['目標_収入'],
        mode='lines+markers',
        name='目標_収入',
        line=dict(color='blue', width=2)
    )
    fig.add_scatter(
        x=df_general.index,
        y=df_general['目標_支出'],
        mode='lines+markers',
        name='目標_支出',
        line=dict(color='orange', width=2)
    )
    fig = graph_common_setting(fig)
    # metaでID付与
    fig.update_layout(meta={"id": "general_income_expenditure"})
    #fig.show()

    # JSONに変換
    return fig.to_json()

def build_general_balance(df_general):
    fig = px.bar(
        df_general, x=df_general.index, y=["金額_収支"],  template='plotly_dark',
            labels={'value':'金額', 'date':'年月', 'variable':''},
    )
    fig.add_scatter(
        x=df_general.index,
        y=df_general['目標_収支'],
        mode='lines+markers',
        name='目標_収支',
        line=dict(color='orange', width=2)
    )
    fig = graph_common_setting(fig)
    # metaでID付与
    fig.update_layout(meta={"id": "general_balance"})
    fig.show()

    # JSONに変換
    return fig.to_json()
def build_special_income_expenditure(df_special):
    pass
def build_special_balance(df_special):
    pass

def build_dashboard_payload(db_path: str, include_graphs: bool = True, include_summary: bool = True) -> Dict[str, Any]:
    # DBから必要データを読み込みます
    df_asset_profit, df_balance, df_target = read_table_from_db(db_path)
    #print(df_target)

    result = {"ok":True, "summary": {}, "graphs": {}}

    if include_summary:
        result["summary"] = build_summary(df_asset_profit, df_target)
        #print(result)
    if include_graphs:
        # データフレーム生成
        df_general_balance = make_df_general(df_balance)

        result["graphs"] = {
            "assets": build_total_assets(df_asset_profit, df_target),
            "returns": build_total_returns(df_asset_profit, df_target),
            "general_income_expenditure": build_general_income_expenditure(df_general_balance),
            "general_balance": build_general_balance(df_general_balance),
            "special_income_expenditure": build_special_income_expenditure(df_special_balance),
            "special_balance": build_special_balance(df_special_balance)
        }
    return result

if __name__ == "__main__":
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_DIR  = os.path.join(BASE_DIR, "database")
    FINANCE_DB = os.path.join(DB_DIR, "finance.db")
    build_dashboard_payload(FINANCE_DB)


