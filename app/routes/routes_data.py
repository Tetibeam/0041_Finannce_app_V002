from flask import Blueprint, request, jsonify, current_app
import os
import pandas as pd
import sqlite3
from werkzeug.exceptions import BadRequest, InternalServerError
from app.utils.data_loader import update_from_csv

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
        # --- CSV → DB ---
        asset_added = 0
        balance_added = 0

        if file_asset:
            asset_added = update_from_csv(db_path, file_asset, "asset")
        if file_balance:
            balance_added = update_from_csv(db_path, file_balance, "balance")

        return jsonify({
            "status": "success",
            "updated_counts": {"asset": asset_added, "balance": balance_added}
        })

    except BadRequest as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Database update failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
