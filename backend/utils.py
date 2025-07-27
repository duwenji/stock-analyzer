import os
import logging
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from matplotlib.font_manager import FontProperties

# 環境変数の読み込み
load_dotenv()

def db_connector():
    """データベース接続を返す"""
    return {
        "query": lambda q: print(f"Query executed: {q}")
    }

def setup_backend_logger():
    """
    バックエンド全体のロガー設定（1回だけ実行）
    ファイル名、関数名、行番号を含む詳細なログフォーマット
    """
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] - %(message)s',
            handlers=[
                logging.FileHandler("logs/stock-analyzer-backend.log"),
                logging.StreamHandler()
            ]
        )
    return logging.getLogger(__name__)

def get_db_engine():
    """
    PostgreSQLデータベースエンジンを作成
    
    Returns:
        sqlalchemy.engine.Engine: データベースエンジンオブジェクト
    
    Raises:
        EnvironmentError: 必須の環境変数が設定されていない場合
    """
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')
    
    if not all([user, password, db_name]):
        raise EnvironmentError("データベース接続に必要な環境変数が設定されていません")
    
    return create_engine(f"postgresql://{user}:{password}@localhost:5432/{db_name}")

def get_font_config():
    """日本語フォント設定を返す"""
    font_prop = FontProperties(fname=r'C:\Windows\Fonts\msgothic.ttc', size=9)
    title_font = FontProperties(fname=r'C:\Windows\Fonts\msgothic.ttc', size=12)
    return font_prop, title_font

def get_company_names(engine):
    """
    銘柄シンボルと企業名のマッピングを取得
    
    Args:
        engine (sqlalchemy.engine.Engine): データベースエンジン
    
    Returns:
        dict: {シンボル: 企業名} の辞書
    """
    try:
        company_names_df = pd.read_sql_query("SELECT symbol, name FROM stocks", engine)
        return dict(zip(company_names_df['symbol'], company_names_df['name']))
    except Exception as e:
        print(f"銘柄情報の取得中にエラー: {str(e)}")
        return {}
