import sqlite3
import os
import pandas as pd
import random
from datetime import datetime, timedelta

# パス設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DB_PATH = os.path.join(BASE_DIR, 'raw_data', 'finance_master.db')
PUBLIC_DB_DIR = os.path.join(BASE_DIR, '..', 'webapp', 'static', 'db')
PUBLIC_DB_PATH = os.path.join(PUBLIC_DB_DIR, 'summary.db')

def create_dummy_raw_data():
    """
    デモ用に生データDBを作成します。
    本来はここにあなたの実際の資産データが存在する想定です。
    """
    if os.path.exists(RAW_DB_PATH):
        print(f"Raw DB already exists at: {RAW_DB_PATH}")
        return

    print("Creating dummy raw data...")
    conn = sqlite3.connect(RAW_DB_PATH)
    cursor = conn.cursor()

    # 生データテーブル: 詳細な取引履歴を含む想定
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            date TEXT,
            category TEXT,
            amount INTEGER,
            description TEXT
        )
    ''')

    # サンプルデータの投入 (過去1年分)
    data = []
    start_date = datetime.now() - timedelta(days=365)
    base_asset = 1000000 # 初期資産 100万円

    current_asset = base_asset
    for i in range(365):
        date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        
        # 収入 (給料など)
        if i % 30 == 0:
            amount = 300000
            data.append((date, 'Income', amount, 'Salary'))
            current_asset += amount
        
        # 支出 (ランダム)
        if random.random() > 0.3:
            amount = -random.randint(1000, 10000)
            data.append((date, 'Expense', amount, 'Daily shopping'))
            current_asset += amount

    cursor.executemany('INSERT INTO transactions (date, category, amount, description) VALUES (?, ?, ?, ?)', 
                       [(d[0], d[1], d[2], d[3]) for d in data])
    
    conn.commit()
    conn.close()
    print("Dummy raw data created.")

def build_summary_db():
    """
    生データ(Raw DB)を読み込み、集計して公開用DB(Summary DB)を作成します。
    """
    print(f"Building summary DB from {RAW_DB_PATH}...")
    
    # 1. 生データの読み込み
    raw_conn = sqlite3.connect(RAW_DB_PATH)
    
    # ここで必要な集計処理を行います (例: 月ごとの総資産推移)
    # 実際にはもっと複雑なSQLやPandas処理が入ります
    query = """
        SELECT 
            strftime('%Y-%m', date) as month,
            SUM(amount) as monthly_change
        FROM transactions
        GROUP BY month
        ORDER BY month
    """
    df = pd.read_sql_query(query, raw_conn)
    raw_conn.close()

    # 累積和を計算して「総資産」にする (初期資産100万スタートと仮定)
    df['total_assets'] = df['monthly_change'].cumsum() + 1000000

    # 2. 公開用DBの作成
    if not os.path.exists(PUBLIC_DB_DIR):
        os.makedirs(PUBLIC_DB_DIR)
        
    # 既存のDBがあれば削除 (完全リフレッシュ)
    if os.path.exists(PUBLIC_DB_PATH):
        os.remove(PUBLIC_DB_PATH)

    public_conn = sqlite3.connect(PUBLIC_DB_PATH)
    
    # 集計結果のみを書き込む
    df[['month', 'total_assets']].to_sql('monthly_summary', public_conn, index=False)
    
    public_conn.close()
    print(f"Summary DB created successfully at: {PUBLIC_DB_PATH}")

if __name__ == '__main__':
    create_dummy_raw_data()
    build_summary_db()
