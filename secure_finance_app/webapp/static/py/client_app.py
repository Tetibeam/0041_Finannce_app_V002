import sqlite3
import json
import pandas as pd

def get_summary_data():
    """
    Connects to the local (in-memory) SQLite DB and retrieves summary data.
    Returns a JSON string formatted for Plotly.
    """
    try:
        # Pyodideの仮想ファイルシステムにマウントされたDBに接続
        conn = sqlite3.connect('/summary.db')
        
        # データを取得 (pandasを使用すると楽ですが、サイズ削減のため標準ライブラリでも可。
        # ここではPyodideにpandasをロードさせる前提で書きます)
        query = "SELECT month, total_assets FROM monthly_summary ORDER BY month"
        df = pd.read_sql_query(query, conn)
        conn.close()

        # Plotly用のデータ形式に変換
        result = {
            "x": df['month'].tolist(),
            "y": df['total_assets'].tolist(),
            "type": "scatter",
            "mode": "lines+markers",
            "name": "Total Assets",
            "line": {"color": "#38bdf8", "width": 3},
            "marker": {"size": 8}
        }
        
        return json.dumps(result)

    except Exception as e:
        return json.dumps({"error": str(e)})

# この関数をJSから呼び出せるようにする
get_summary_data()
