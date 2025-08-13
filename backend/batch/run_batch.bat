@echo on
REM プロジェクトルートに移動
cd /d %~dp0..

REM Pythonのモジュール検索パスを設定
set PYTHONPATH=%cd%

REM 仮想環境のアクティベート（存在する場合）
if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat

REM バッチスクリプトの実行
python batch/stock_symbol_importer.py
python batch/stock_data_importer.py
python batch/technical_indicator_calculator.py --days 7

pause
