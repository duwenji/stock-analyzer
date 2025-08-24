#!/bin/bash

# 株式分析システム Docker実行スクリプト
# Linux環境用

set -e

echo "=== 株式分析システム Docker環境構築 ==="

# 環境変数ファイルの確認
if [ ! -f "backend/.env.docker" ]; then
    echo "エラー: backend/.env.docker ファイルが見つかりません"
    echo "まず backend/.env.docker ファイルを作成し、必要な環境変数を設定してください"
    exit 1
fi

# Dockerがインストールされているか確認
if ! command -v docker &> /dev/null; then
    echo "エラー: Dockerがインストールされていません"
    echo "Dockerをインストールしてください: https://docs.docker.com/get-docker/"
    exit 1
fi

# Docker Composeが利用可能か確認
if ! command -v docker-compose &> /dev/null; then
    echo "エラー: Docker Composeがインストールされていません"
    echo "Docker Composeをインストールしてください: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "環境変数ファイルを確認しました"
echo "Dockerサービスのビルドを開始します..."

# 環境変数を読み込み
export $(grep -v '^#' backend/.env.docker | xargs)

# Docker Composeでビルドと起動
cd backend
docker-compose up --build -d

echo ""
echo "=== 起動完了 ==="
echo "フロントエンド: http://localhost:3000"
echo "バックエンドAPI: http://localhost:8000"
echo "データベース: localhost:5432"
echo ""
echo "ログを確認: docker-compose logs -f"
echo "停止: docker-compose down"
echo "再起動: docker-compose restart"
