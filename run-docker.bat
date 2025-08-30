@echo off
setlocal enabledelayedexpansion
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

REM 全コンテナの状態をチェック
echo コンテナ状態を確認中...
for /f "tokens=*" %%i in ('docker ps -a --filter "name=stock-postgres" --format "{{.Status}}"') do (
    set "postgres_status=%%i"
)

REM 状態に応じた処理
if "!postgres_status!"=="" (
    echo コンテナが存在しません。全サービスを新規作成します...
    docker-compose up --build -d
) else if "!postgres_status:~0,2!"=="Up" (
    echo PostgreSQLコンテナは既に実行中です: !postgres_status!
    echo 他のサービスを起動します...
    docker-compose up --no-recreate -d
) else (
    echo PostgreSQLコンテナは停止中です: !postgres_status!
    echo 全サービスを起動します...
    docker-compose up --no-recreate -d
)

echo.
echo === 処理完了 ===
echo フロントエンド: http://localhost:3000
echo バックエンドAPI: http://localhost:8000
echo データベース: localhost:5432
echo.
echo ログを確認: docker-compose logs -f
echo 停止: docker-compose down
echo 再起動: docker-compose restart
echo.
pause
