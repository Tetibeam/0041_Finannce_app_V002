from flask import Blueprint, render_template, current_app
from .dashboard_service import build_dashboard_graphs
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR  = os.path.join(BASE_DIR, "database")
FINANCE_DB = os.path.join(DB_DIR, "finance.db")

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def index():
    return dashboard()

@dashboard_bp.route("/dashboard")
def dashboard():
    #db_path = current_app.config["DATABASE_PATH"] + "/" + current_app.config["DATABASE"]["finance"]
    graphs, graphs_info = build_dashboard_graphs(FINANCE_DB)
    return render_template("dashboard.html", graphs=graphs, graphs_info=graphs_info)

