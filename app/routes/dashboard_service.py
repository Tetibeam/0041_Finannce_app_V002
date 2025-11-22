from app.utils.data_loader import get_df_from_db
from typing import Dict, Any
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import json

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
        title = dict(text = x_title, font=dict(size=10)),
        title_standoff=20,
        tickformat="%y/%m/%d",
        tickfont=dict(size=8),
    )
    fig.update_yaxes(
        title = dict(text = y_title, font=dict(size=10)),
        title_standoff=20,
        tickprefix="¥",
        separatethousands=False,  # これを追加すると tickformat が消えない
        tickfont=dict(size=8),
    )
    fig.update_layout(
        # サイズ調整
        autosize=True, margin=dict(l=0,r=10,t=0,b=30),
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
            font=dict(size=10),
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
    x_values = df.index.strftime("%Y-%m-%d").tolist()
    y1_values = df["トータルリターン_実績"].astype(float).tolist()
    y2_values = df["トータルリターン_目標"].astype(float).tolist()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_values, y=y1_values, mode="lines", name="トータルリターン_実績"))
    fig.add_trace(go.Scatter(x=x_values, y=y2_values, mode="lines", name="トータルリターン_目標"))

    fig = graph_common_setting(fig,"日付", "トータルリターン")

    # metaでID付与
    fig.update_layout(meta={"id": "total_returns"})

    fig_dict = fig.to_dict()
    json_str = json.dumps(fig_dict)
    #fig.show()
    #print(json_str)
    return json_str

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
    x_values = df.index.strftime("%Y-%m").tolist()
    y1_values = df["金額_収入"].astype(float).tolist()
    y2_values = df["金額_支出"].astype(float).tolist()
    y3_values = df["目標_収入"].astype(float).tolist()
    y4_values = df["目標_支出"].astype(float).tolist()

    fig = go.Figure()
    fig.add_trace(go.Bar(x=x_values, y=y1_values, name="収入実績"))
    fig.add_trace(go.Bar(x=x_values, y=y2_values, name="支出実績"))
    fig.add_trace(go.Scatter(x=x_values, y=y3_values, mode="lines+markers", name="収入目標"))
    fig.add_trace(go.Scatter(x=x_values, y=y4_values, mode="lines+markers", name="支出目標"))

    fig = graph_common_setting(fig, "日付", "金額")
    # metaでID付与
    fig.update_layout(meta={"id": "general_income_expenditure"})

    fig_dict = fig.to_dict()
    json_str = json.dumps(fig_dict)
    #fig.show()
    return json_str

def build_general_balance(df):
    x_values = df.index.strftime("%Y-%m").tolist()
    y1_values = df["金額_収支"].astype(float).tolist()
    y2_values = df["目標_収支"].astype(float).tolist()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x_values, y=y1_values, name="収支実績"))
    fig.add_trace(go.Scatter(x=x_values, y=y2_values, mode="lines+markers", name="収支目標"))

    fig = graph_common_setting(fig, "日付", "金額")
    # metaでID付与
    fig.update_layout(meta={"id": "general_balance"})

    fig_dict = fig.to_dict()
    json_str = json.dumps(fig_dict)
    #fig.show()
    return json_str

def build_special_income_expenditure(df):
    # PXでグラフ生成
    x_values = df.index.strftime("%Y-%m").tolist()
    y1_values = df["金額_収入"].astype(float).tolist()
    y2_values = df["金額_支出"].astype(float).tolist()
    y3_values = df["目標_収入"].astype(float).tolist()
    y4_values = df["目標_支出"].astype(float).tolist()

    fig = go.Figure()
    fig.add_trace(go.Bar(x=x_values, y=y1_values, name="収入実績"))
    fig.add_trace(go.Bar(x=x_values, y=y2_values, name="支出実績"))
    fig.add_trace(go.Scatter(x=x_values, y=y3_values, mode="lines+markers", name="収入目標"))
    fig.add_trace(go.Scatter(x=x_values, y=y4_values, mode="lines+markers", name="支出目標"))

    fig = graph_common_setting(fig, "日付", "金額")
    # metaでID付与
    fig.update_layout(meta={"id": "special_income_expenditure"})

    fig_dict = fig.to_dict()
    json_str = json.dumps(fig_dict)
    #fig.show()
    return json_str

def build_special_balance(df):
    x_values = df.index.strftime("%Y-%m").tolist()
    y1_values = df["金額_収支"].astype(float).tolist()
    y2_values = df["目標_収支"].astype(float).tolist()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_values, y=y1_values, mode="lines+markers", fill="tozeroy", name="収支累積実績"))
    fig.add_trace(go.Scatter(x=x_values, y=y2_values, mode="lines+markers", name="収支累積目標"))

    fig = graph_common_setting(fig, "日付", "金額")
    # metaでID付与
    fig.update_layout(meta={"id": "special_balance"})

    fig_dict = fig.to_dict()
    json_str = json.dumps(fig_dict)
    #fig.show()
    return json_str

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
    print(BASE_DIR)
    DB_DIR  = os.path.join(BASE_DIR, "..", "database")
    FINANCE_DB = os.path.join(DB_DIR, "finance.db")
    build_dashboard_payload(FINANCE_DB)


