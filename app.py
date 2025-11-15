from flask import Flask
from utils.config import load_settings
from modules.routes_dashboard import dashboard_bp
from modules.routes_graph import graph_bp

def create_app():
    app = Flask(__name__)

    # YAML設定を読み込み
    settings = load_settings("setting.yaml")

    # まとめて Flask に登録
    for key, value in settings.items():
        app.config[key.upper()] = value  # 大文字にしておくのが慣例
    #app.config[key.upper()] = value  # 大文字にしておくのが慣例app.config["DB_PATH_FINANCE"] = settings["database_path"] + "/" + settings["database"]["finance"]

    # Blueprint登録
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(graph_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

"""
from flask import Flask, render_template
from utils.read_from_db import get_asset_and_profit_dashboard, get_balance_dashboard
from utils.config import load_settings
import utils.visualize_dashboard as viz
from utils.calculation import cal_general_special_balance_dashboard,cal_total_return_target_dashboard
import os


settings = load_settings("setting.yaml")
DB_PATH_FINANCE = os.path.join(    settings["database_path"],"",settings["database"]["finance"])

graphs = {}

app = Flask(__name__)

@app.route("/")
def index():
    # ダッシュボードがトップ
    return dashboard()

@app.route("/dashboard")
def dashboard():
    global graphs

    df_asset_profit = get_asset_and_profit_dashboard(DB_PATH_FINANCE) # DBから資産データを取得、整形
    df_asset_profit = cal_total_return_target_dashboard(df_asset_profit)

    # 1. 総資産推移
    fig = viz.display_total_assets(df_asset_profit)
    graphs["assets"] = viz.write_html(fig,"assets")

    # 2. トータルリターン推移
    fig = viz.display_total_returns(df_asset_profit)
    graphs["returns"]  = viz.write_html(fig,"returns")

    df_balance = get_balance_dashboard(DB_PATH_FINANCE)
    df_general = cal_general_special_balance_dashboard(df_balance, "一般収支")
    df_special = cal_general_special_balance_dashboard(df_balance, "特別収支")

    # 3. 一般収入・支出
    fig = viz.display_general_income_expenditure(df_general)
    graphs["general_income_expenditure"] = viz.write_html(fig,"general_income_expenditure")

    # 4. 一般収支
    fig = viz.display_general_balance(df_general)
    graphs["general_balance"]  = viz.write_html(fig,"general_balance")

    # 5. 特別収入・支出
    fig = viz.display_special_income_expenditure(df_special)
    graphs["special_income_expenditure"]  = viz.write_html(fig,"special_income_expenditure")

    # 6. 特別収支
    fig = viz.display_special_balance(df_special)
    #graphs["special_balance"] = fig.to_html(full_html=False)
    graphs["special_balance"]  = viz.write_html(fig,"special_balance")


    # グラフタイトルとキーを辞書で管理
    graphs_info = {
        "assets": "🤑 総資産推移",
        "general_income_expenditure": "🤑 一般収入・支出",
        "special_income_expenditure": "🤑 特別収入・支出",
        "returns": "🤑 トータルリターン",
        "general_balance": "🤑 一般収支",
        "special_balance": "🤑 特別収支"
    }
    return render_template("dashboard.html", graphs=graphs, graphs_info=graphs_info)

@app.route("/graph/<key>")
def show_graph(key):
    graphs_info = {
        "assets": "🤑 総資産推移",
        "general_income_expenditure": "🤑 一般収入・支出",
        "special_income_expenditure": "🤑 特別収入・支出",
        "returns": "🤑 トータルリターン",
        "general_balance": "🤑 一般収支",
        "special_balance": "🤑 特別収支"
    }

    # key が存在しない場合は404
    if key not in graphs_info:
        abort(404)

    title = graphs_info[key]
    fig_html = graphs[key]  # すでに生成済みのHTMLを取得する想定

    return render_template("graph_detail.html", title=title, fig_html=fig_html)

if __name__ == "__main__":
    app.run(debug=True)
"""