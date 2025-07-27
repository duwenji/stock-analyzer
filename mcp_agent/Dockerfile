# 軽量なPythonイメージをベースに使用
FROM python:3.10-slim

# 作業ディレクトリ設定
WORKDIR /app

# 依存関係インストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ソースコードコピー
COPY . .

# MCPサーバーポート公開
EXPOSE 8080

# エントリーポイント設定
CMD ["python", "main.py"]
