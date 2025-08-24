@echo off
chcp 65001 >nul
echo === 株式分析システム Docker環境構築 ===
echo Windows環境用

REM 環境変数ファイルの確認
if not exist "backend\.env.docker" (
    echo エラー: backend\.env.docker ファイルが見つかりません
    echo まず backend\.env.example を backend\.env.docker にコピーし、
    echo 必要な環境変数を設定してください
    pause
    exit /b 1
)

REM Dockerがインストールされているか確認
docker --version >nul 2>&1
if errorlevel 1 (
    echo エラー: Dockerがインストールされていません
    echo Dockerをインストールしてください: https://docs.docker.com/get-docker/
    pause
    exit /b 1
)

REM Docker Composeが利用可能か確認
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo エラー: Docker Composeがインストールされていません
    echo Docker Composeをインストールしてください: https://docs.docker.com/compose/install/
    pause
    exit /b 1
)

echo 環境変数ファイルを確認しました
echo Dockerサービスのビルドを開始します...

REM Docker Composeでビルドと起動
cd backend
docker-compose up --build -d

echo.
echo === 起動完了 ===
echo フロントエンド: http://localhost:3000
echo バックエンドAPI: http://localhost:8000
echo データベース: localhost:5432
echo.
echo ログを確認: docker-compose logs -f
echo 停止: docker-compose down
echo 再起動: docker-compose restart
echo.
pause
