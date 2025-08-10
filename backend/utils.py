import os
import logging
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from matplotlib.font_manager import FontProperties

_env_loaded = False

def initialize_environment():
    """環境変数を初期化する（アプリケーション起動時に1回だけ呼び出す）"""
    global _env_loaded
    if not _env_loaded:
        load_dotenv()
        _env_loaded = True
        logging.info("環境変数を初期化しました")

# 環境変数の読み込みはinitialize_environment()で一元管理

def setup_backend_logger(name=__name__):
    """
    バックエンド全体のロガー設定（1回だけ実行）
    ファイル名、関数名、行番号を含む詳細なログフォーマット
    
    Args:
        name (str): ロガー名 (デフォルトはモジュール名 __name__)
    """
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] - %(message)s',
            handlers=[
                logging.FileHandler(f"logs/stock-analyzer-{__name__}.log"),
                logging.StreamHandler()
            ]
        )
    return logging.getLogger(name)

def get_db_engine():
    """
    標準のPostgreSQLデータベースエンジンを作成（一元化された接続方法）
    接続プールとタイムアウト設定を追加
    
    Returns:
        sqlalchemy.engine.Engine: データベースエンジンオブジェクト
    
    Raises:
        EnvironmentError: 必須の環境変数が設定されていない場合
    """
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    
    if not all([user, password, db_name]):
        raise EnvironmentError("データベース接続に必要な環境変数が設定されていません")
    
    return create_engine(
        f"postgresql://{user}:{password}@{host}:{port}/{db_name}",
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=3600,
        connect_args={
            'connect_timeout': 10,
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5
        }
    )

def process_in_symbol_groups(df, group_size=100):
    """
    銘柄をグループ化して処理 (同じ銘柄のデータは必ず同じグループに)
    
    Args:
        df (pd.DataFrame): 処理対象のDataFrame
        group_size (int): 1グループあたりの銘柄数
        
    Yields:
        pd.DataFrame: グループ化されたDataFrame (symbol, dateでソート済み)
    """
    symbols = df['symbol'].unique()
    for i in range(0, len(symbols), group_size):
        symbol_group = symbols[i:i + group_size]
        group_df = df[df['symbol'].isin(symbol_group)].sort_values(['symbol', 'date'])
        yield group_df

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
