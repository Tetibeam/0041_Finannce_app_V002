import pandas as pd

def cal_total_return_target_dashboard(df: pd.DataFrame):
    df['トータルリターン_目標'] = df['トータルリターン_目標'].cumsum()
    return df

def cal_general_special_balance_dashboard(df: pd.DataFrame, balance_type: str):
    """
    指定されたデータフレームと収支タイプに基づいて、一般収支または特別収支のダッシュボードデータを計算する。

    Args:
        df (pd.DataFrame): 収支データを含むデータフレーム。
        balance_type (str): "一般収支" または "特別収支" のいずれか。

    Returns:
        pd.DataFrame: 計算された収支ダッシュボードデータ。

    Raises:
        ValueError: balance_type が "一般収支" または "特別収支" ではない場合。
    """
    if balance_type not in ["一般収支", "特別収支"]:
        raise ValueError

    df_filtered = df.query('収支タイプ == @balance_type')

    df_filtered = df_filtered.pivot_table(
        index="date", columns="収支カテゴリー",values=["金額", "目標"], aggfunc="sum")
    df_filtered.columns = [f"{val}_{cat}" for val, cat in df_filtered.columns]

    df_filtered = df_filtered.resample('ME').sum()
    if balance_type == "一般収支":
        df_filtered["目標_収支"] = df_filtered["目標_収入"] - df_filtered["目標_支出"]
        df_filtered["金額_収支"] = df_filtered["金額_収入"] - df_filtered["金額_支出"]
    else:
        df_filtered["目標_収支"] = df_filtered["目標_収入"].cumsum() - df_filtered["目標_支出"].cumsum()
        df_filtered["金額_収支"] = df_filtered["金額_収入"].cumsum() - df_filtered["金額_支出"].cumsum()

    return df_filtered
