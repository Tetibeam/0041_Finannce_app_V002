from flask import Blueprint, request, jsonify, current_app
import os
import pandas as pd
import sqlite3
from werkzeug.exceptions import BadRequest, InternalServerError

data_bp = Blueprint("data", __name__, url_prefix="/api/data")

@data_bp.route("/upload", methods=["POST"])
def upload_update():
    """
    CSVファイル(diff_asset_profit.csv, diff_balance.csv)を受け取り、
    finance.db の asset, balance テーブルに追記する。
    """
    try:
        # ファイルの取得
        file_asset = request.files.get("file_asset")
        file_balance = request.files.get("file_balance")

        if not file_asset and not file_balance:
            raise BadRequest("No files provided. 'file_asset' or 'file_balance' is required.")

        db_path = os.path.join(
            current_app.config["DATABASE_PATH"],
            current_app.config["DATABASE"]["finance"]
        )

        updated_counts = {}

        # DB接続
        with sqlite3.connect(db_path) as conn:
            # Asset Profit Update
            if file_asset:
                df_asset = pd.read_csv(file_asset)
                if not df_asset.empty:
                    # 必要なカラムがあるかチェックなどは省略（信頼できるソース前提）
                    df_asset.to_sql("asset", conn, if_exists="append", index=False)
                    updated_counts["asset"] = len(df_asset)
                else:
                    updated_counts["asset"] = 0

            # Balance Update
            if file_balance:
                df_balance = pd.read_csv(file_balance)
                if not df_balance.empty:
                    df_balance.to_sql("balance", conn, if_exists="append", index=False)
                    updated_counts["balance"] = len(df_balance)
                else:
                    updated_counts["balance"] = 0

        return jsonify({
            "status": "success",
            "message": "Database updated successfully.",
            "updated_counts": updated_counts
        })

    except BadRequest as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Database update failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
