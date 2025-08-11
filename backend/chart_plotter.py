import os
import logging
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_finance import candlestick_ohlc
from utils import get_font_config, get_ma_settings  # 相対インポートから絶対インポートに変更

# ロギング設定（バックエンド全体の設定を使用）
logger = logging.getLogger(__name__)

def plot_candlestick(symbol_df, symbol, company_name, output_dir='reports'):
    """
    ローソク足チャートを描画してファイルに保存
    
    Args:
        symbol_df (pd.DataFrame): 銘柄データ (date, open, high, low, close, volume, MA30)
        symbol (str): 銘柄シンボル
        company_name (str): 企業名
        output_dir (str): 出力ディレクトリ
    
    Returns:
        str: 保存された画像ファイルパス
    """
    try:
        # 出力ディレクトリ作成
        os.makedirs(output_dir, exist_ok=True)
        
        # フォント設定取得
        font_prop, title_font = get_font_config()
        
        # チャート設定
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), 
                                       gridspec_kw={'height_ratios': [3, 1]})
        
        # ローソク足データ準備
        plot_df = symbol_df[['open', 'high', 'low', 'close', 'volume']].copy()
        plot_df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        dates = mdates.date2num(symbol_df.index.to_pydatetime())
        
        # ローソク足プロット
        ohlc_data = list(zip(dates, 
                             plot_df['Open'], 
                             plot_df['High'], 
                             plot_df['Low'], 
                             plot_df['Close']))
        
        candlestick_ohlc(ax1, ohlc_data, width=0.6, colorup='r', colordown='g', alpha=1.0)
        
        # 移動平均プロット（NaNは自動スキップ）
        ma_settings = get_ma_settings()
        ax1.plot(dates, symbol_df[f'MA{ma_settings["short"]}'], 
                label=f'{ma_settings["short"]}日移動平均', color='blue')
        ax1.plot(dates, symbol_df[f'MA{ma_settings["long"]}'], 
                label=f'{ma_settings["long"]}日移動平均', color='orange')
        logger.debug(f"移動平均をプロット: {ma_settings}")
        
        # タイトルとラベル設定
        ax1.set_title(f'{company_name} ({symbol}) ローソク足チャート', fontproperties=title_font)
        ax1.set_ylabel('価格', fontproperties=font_prop)
        ax1.legend(prop=font_prop)
        
        # 出来高プロット（Volumeが0の場合はプロットしない）
        volume_mask = plot_df['Volume'] > 0
        non_zero_volumes = plot_df[volume_mask]
        non_zero_dates = dates[volume_mask]  # 直接booleanマスクを使用
        ax2.bar(non_zero_dates, non_zero_volumes['Volume'], color='gray')
        ax2.set_xlabel('日付', fontproperties=font_prop)
        
        # 日付フォーマット設定
        for ax in [ax1, ax2]:
            ax.xaxis_date()
            locator = mdates.AutoDateLocator()
            formatter = mdates.AutoDateFormatter(locator)
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(formatter)
            plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
            for label in ax.get_xticklabels():
                label.set_fontproperties(font_prop)
        
        # レイアウト調整と保存
        plt.tight_layout()
        output_path = os.path.abspath(os.path.join(output_dir, f'{symbol}_candle_chart.png'))
        plt.savefig(output_path)
        plt.close()
        
        return output_path
    
    except Exception as e:
        logger.exception(f"チャート描画エラー ({symbol}): {str(e)}")
        return None
