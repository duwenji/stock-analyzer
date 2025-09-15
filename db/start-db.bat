@echo off
echo Forcibly removing existing container...
docker rm -f stock-postgres 2> nul

echo Cleaning up unused networks...
docker network prune -f

echo Stopping existing container...
docker compose -f docker-compose-db-only.yml down

echo Starting PostgreSQL container...
docker compose -f docker-compose-db-only.yml up -d --remove-orphans
if %errorlevel% neq 0 exit /b %errorlevel%

echo Waiting for PostgreSQL to start...
timeout /t 30
docker ps --filter "name=stock-postgres" --filter "status=running" | findstr "stock-postgres"
if %errorlevel% neq 0 (
    echo Error: PostgreSQL container not running
    exit /b 1
)

echo Connecting to PostgreSQL...
docker exec -it stock-postgres psql -U stock_user -d stock_analyzer
