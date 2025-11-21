from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

# ルート: アプリケーションのメインページを表示
@app.route('/')
def index():
    return render_template('index.html')

# 静的ファイル（DBやPythonスクリプト）へのアクセスを明示的に許可
# 通常の static フォルダ運用でも可能ですが、セキュリティ意識として明示します
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
