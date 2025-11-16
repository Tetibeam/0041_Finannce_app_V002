from flask import Blueprint, render_template, current_app,jsonify,make_response
from .dashboard_service import build_dashboard_payload
from werkzeug.exceptions import InternalServerError
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR  = os.path.join(BASE_DIR, "database")
FINANCE_DB = os.path.join(DB_DIR, "finance.db")

#dashboard_bp = Blueprint("dashboard", __name__)
dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")

"""@dashboard_bp.route("/")
def index():
    return dashboard()"""

"""@dashboard_bp.route("/dashboard")
def dashboard():
    #db_path = current_app.config["DATABASE_PATH"] + "/" + current_app.config["DATABASE"]["finance"]
    graphs, graphs_info = build_dashboard_graphs(FINANCE_DB)
    return render_template("dashboard.html", graphs=graphs, graphs_info=graphs_info)"""

@dashboard_bp.route("/view")
def view():
    return render_template("dashboard.html")

# API 用ルート
@dashboard_bp.route("/", methods=["GET"])
def index():
    """
    API root: 簡単なメタ情報を返す
    """
    payload = {
        "service": "dashboard",
        "version": "1.0",
        "endpoints": {
            "graphs": "/api/dashboard/graphs",
            "summary": "/api/dashboard/summary"
        }
    }
    return jsonify(payload)

@dashboard_bp.route("/graphs", methods=["GET"])
def graphs():
    """
    グラフ用データを返すエンドポイント。
    フロントはここから時系列データ・メタ情報を受け取り描画する。
    """
    try:
        db_path = os.path.join(
            current_app.config["DATABASE_PATH"],
            current_app.config["DATABASE"]["finance"]
        )
        payload = build_dashboard_payload(db_path, include_graphs=True, include_summary=False)
        # 200 OK
        resp = make_response(jsonify(payload), 200)
        # キャッシュ挙動（必要に応じ調整）
        resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return resp
    except Exception as e:
        # ログはアプリ側で出している想定
        raise InternalServerError(description=str(e))

@dashboard_bp.route("/summary", methods=["GET"])
def summary():
    """
    サマリ（軽量）だけほしいフロントのための簡易エンドポイント。
    """
    try:
        db_path = os.path.join(
            current_app.config["DATABASE_PATH"],
            current_app.config["DATABASE"]["finance"]
        )
        payload = build_dashboard_payload(db_path, include_graphs=False, include_summary=True)
        resp = make_response(jsonify(payload), 200)
        resp.headers["Cache-Control"] = "no-cache"
        return resp
    except Exception as e:
        raise InternalServerError(description=str(e))
