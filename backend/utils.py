import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from matplotlib.font_manager import FontProperties

# 環境変数の読み込み
load_dotenv()

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
