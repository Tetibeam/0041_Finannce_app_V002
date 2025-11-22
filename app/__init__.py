from flask import Flask
from app.utils.config import load_settings
import os

def create_app():
    app = Flask(__name__)

    # YAML設定を読み込み
    # setting.yaml is at the root, so we need to go up one level from app/
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    setting_path = os.path.join(base_dir, "setting.yaml")
    
    settings = load_settings(setting_path)

    # まとめて Flask に登録
    for key, value in settings.items():
        app.config[key.upper()] = value

    # Blueprint登録
    from app.routes.routes_dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    from app.routes.routes_data import data_bp
    app.register_blueprint(data_bp)

    return app
