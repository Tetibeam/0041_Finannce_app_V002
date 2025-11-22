from flask import Blueprint, render_template, abort
#from .dashboard_service import graphs_cache, graphs_info
"""
graph_bp = Blueprint("graph", __name__)

@graph_bp.route("/graph/<key>")
def show_graph(key):
    if key not in graphs_info:
        abort(404)
    fig_html = graphs_cache.get(key, "<p>グラフが見つかりません</p>")
    title = graphs_info[key]
    return render_template("graph_detail.html", title=title, fig_html=fig_html)
"""