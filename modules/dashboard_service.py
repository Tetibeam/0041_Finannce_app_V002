from utils.data_loader import get_df_from_db
from typing import Dict, Any
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import json


# このファイルの親フォルダ(= modules の親)をパスに追加
sys.path.append(str(Path(__file__).resolve().parent.parent))
"""
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
"""
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
    latest = latest.strftime("%Y/%m/%d")
    return {
        "latest_date": latest,
        "total_assets": int(df_asset_profit.loc[latest, "資産額"]),
        "total_target_assets": int(df_target.loc[latest, "資産額"]),
        "total_returns": int(df_asset_profit.loc[latest, "トータルリターン"]),
        "total_target_returns": int(df_target.loc[latest, "トータルリターン"]),
    }

def graph_common_setting(fig, x_title, y_title):
    fig.update_xaxes(
        title = dict(text = x_title, font=dict(size=14)),
        title_standoff=20,
        tickformat="%y/%m/%d",
        tickfont=dict(size=10),
    )
    fig.update_yaxes(
        title = dict(text = y_title, font=dict(size=14)),
        title_standoff=20,
        tickprefix="¥",
        tickformat=",~s",
        tickfont=dict(size=10),
    )
    fig.update_layout(
        # サイズ調整
        autosize=True, margin=dict(l=0,r=10,t=0,b=30),
        title_font=dict(size=14), font=dict(size=8),
        # template
        template="plotly_dark",
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
            font=dict(size=12),
        )
    )

    return fig

def build_total_assets(df_asset_profit, df_target):
    # データフレーム生成
    df = pd.merge(df_asset_profit["資産額"], df_target["資産額"],
                  left_index=True, right_index=True,suffixes=("_実績", "_目標"))
    #print(df)
    # PXでグラフ生成
    x_values = df.index.strftime("%Y-%m-%d").tolist()
    y1_values = df["資産額_実績"].astype(float).tolist()
    y2_values = df["資産額_目標"].astype(float).tolist()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_values, y=y1_values, mode="lines", name="資産額_実績"))
    fig.add_trace(go.Scatter(x=x_values, y=y2_values, mode="lines", name="資産額_目標"))
    fig = graph_common_setting(fig, "日付", "資産額")
    # metaでID付与
    fig.update_layout(meta={"id": "total_assets"})

    fig_dict = fig.to_dict()
    json_str = json.dumps(fig_dict)
    #fig.show()
    return json_str

def build_total_returns(df_asset_profit, df_target):
    # データフレーム生成
    df_cumsum_target = df_target["トータルリターン"]
    df = pd.merge(df_asset_profit["トータルリターン"], df_cumsum_target,
                  left_index=True, right_index=True,suffixes=("_実績", "_目標"))
    # PXでグラフ生成
    fig = px.line(df, x=df.index, y=["トータルリターン_実績", "トータルリターン_目標"],template="plotly_dark",
            labels={"index": "日付", "value":"トータルリターン","variable":""})
    fig = graph_common_setting(fig,"日付", "トータルリターン")
    # metaでID付与
    fig.update_layout(meta={"id": "total_returns"})
    #fig.show()

    # JSONに変換
    return fig.to_json()

def make_general_and_special_balance(df, balance_type: str):
    if balance_type not in ["一般収支", "特別収支"]:
        raise ValueError

    df_filtered = df.query('収支タイプ == @balance_type')

    df_filtered = df_filtered.pivot_table(
        index="date", columns="収支カテゴリー",values=["金額", "目標"], aggfunc="sum")
    df_filtered.columns = [f"{val}_{cat}" for val, cat in df_filtered.columns]

    df_filtered = df_filtered.resample('ME').sum()
    if balance_type == "一般収支":
        df_filtered["目標_収支"] = df_filtered["目標_収入"] + df_filtered["目標_支出"]
        df_filtered["金額_収支"] = df_filtered["金額_収入"] + df_filtered["金額_支出"]
    else:
        df_filtered["目標_収支"] = df_filtered["目標_収入"].cumsum() + df_filtered["目標_支出"].cumsum()
        df_filtered["金額_収支"] = df_filtered["金額_収入"].cumsum() + df_filtered["金額_支出"].cumsum()

    return df_filtered

def build_general_income_expenditure(df):
    # PXでグラフ生成
    fig = px.bar(
        df, x=df.index, y=["金額_収入", "金額_支出"], barmode='group',
        template='plotly_dark',labels={'value':'金額', 'date':'年月', 'variable':''}
    )
    fig.add_scatter(
        x=df.index,
        y=df['目標_収入'],
        mode='lines+markers',
        name='目標_収入',
        line=dict(color='blue', width=2)
    )
    fig.add_scatter(
        x=df.index,
        y=df['目標_支出'],
        mode='lines+markers',
        name='目標_支出',
        line=dict(color='orange', width=2)
    )
    fig = graph_common_setting(fig, "日付", "金額")
    # metaでID付与
    fig.update_layout(meta={"id": "general_income_expenditure"})
    #fig.show()

    # JSONに変換
    return fig.to_json()

def build_general_balance(df):
    fig = px.bar(
        df, x=df.index, y=["金額_収支"],  template='plotly_dark',
            labels={'value':'金額', 'date':'年月', 'variable':''},
    )
    fig.add_scatter(
        x=df.index,
        y=df['目標_収支'],
        mode='lines+markers',
        name='目標_収支',
        line=dict(color='orange', width=2)
    )
    fig = graph_common_setting(fig, "日付", "金額")
    # metaでID付与
    fig.update_layout(meta={"id": "general_balance"})
    #fig.show()

    # JSONに変換
    return fig.to_json()

def build_special_income_expenditure(df):
    fig = px.bar(
    df, x=df.index, y=["金額_収入", "金額_支出"],barmode='group', template='plotly_dark',
        labels={'value':'金額', 'date':'年月', 'variable':''})

    fig.add_scatter(
        x=df.index,
        y=df['目標_収入'],
        mode='lines+markers',
        name='目標_収入',
        line=dict(color='blue', width=2)
    )
    fig.add_scatter(
        x=df.index,
        y=df['目標_支出'],
        mode='lines+markers',
        name='目標_支出',
        line=dict(color='orange', width=2)
    )
    fig = graph_common_setting(fig, "日付", "金額")
    # metaでID付与
    fig.update_layout(meta={"id": "special_income_expenditure"})
    #fig.show()

    # JSONに変換
    return fig.to_json()

def build_special_balance(df):
    fig = px.line(
        df, x=df.index, y=["金額_収支","目標_収支"], template='plotly_dark', markers=True,
            labels={'value':'金額', 'date':'年月', 'variable':''}
    )
    fig = graph_common_setting(fig, "日付", "金額")
    # metaでID付与
    fig.update_layout(meta={"id": "special_balance"})
    #fig.show()

    # JSONに変換
    return fig.to_json()

def build_dashboard_payload(db_path: str, include_graphs: bool = True, include_summary: bool = True) -> Dict[str, Any]:
    # DBから必要データを読み込みます
    df_asset_profit, df_balance, df_target = read_table_from_db(db_path)
    #print(df_target)

    result = {"ok":True, "summary": {}, "graphs": {}}

    if include_summary:
        result["summary"] = build_summary(df_asset_profit, df_target)
        #print(result)
    if include_graphs:
        df_general = make_general_and_special_balance(df_balance, "一般収支")
        df_special = make_general_and_special_balance(df_balance, "特別収支")

        result["graphs"] = {
            "assets": build_total_assets(df_asset_profit, df_target),
            "returns": build_total_returns(df_asset_profit, df_target),
            "general_income_expenditure": build_general_income_expenditure(df_general),
            "general_balance": build_general_balance(df_general),
            "special_income_expenditure": build_special_income_expenditure(df_special),
            "special_balance": build_special_balance(df_special)
        }
    return result

if __name__ == "__main__":
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_DIR  = os.path.join(BASE_DIR, "database")
    FINANCE_DB = os.path.join(DB_DIR, "finance.db")
    build_dashboard_payload(FINANCE_DB)


