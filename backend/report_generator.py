import xml.etree.ElementTree as ET
import os

def init_xml_report(file_path):
    """XMLレポートファイルを初期化してヘッダーを書き込む"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n')
            f.write('<StockAnalysisReport>\n')
        return True
    except Exception as e:
        print(f"レポート初期化エラー: {str(e)}")
        return False

def finalize_xml_report(file_path):
    """XMLレポートにフッターを書き込んで完了"""
    try:
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write('</StockAnalysisReport>')
        return True
    except Exception as e:
        print(f"レポート終了処理エラー: {str(e)}")
        return False

def generate_stock_entry(symbol_df, symbol, company_name, chart_path, ai_recommendation=None):
    """
    銘柄ごとのXML要素を生成
    
    Args:
        symbol_df (pd.DataFrame): 銘柄データ
        symbol (str): 銘柄シンボル
        company_name (str): 企業名
        chart_path (str): チャート画像パス
        ai_recommendation (dict): AI分析結果
    
    Returns:
        str: XML文字列
    """
    try:
        # XML要素の作成
        stock_elem = ET.Element("Stock")
        stock_elem.set("symbol", symbol)
        stock_elem.set("name", company_name)
        
        # チャート画像要素（チャートが生成された場合のみ）
        if chart_path is not None:
            ET.SubElement(stock_elem, "ChartImage").text = chart_path
        
        # 指標要素
        indicators_elem = ET.SubElement(stock_elem, "Indicators")
        ET.SubElement(indicators_elem, "Close").text = f"{symbol_df['close'].iloc[-1]:.2f}"
        ET.SubElement(indicators_elem, "MA30").text = f"{symbol_df['MA30'].iloc[-1]:.2f}"
        ET.SubElement(indicators_elem, "Volume").text = f"{symbol_df['volume'].iloc[-1]:,}"
        ET.SubElement(indicators_elem, "PriceRange").text = f"{symbol_df['high'].iloc[-1] - symbol_df['low'].iloc[-1]:.2f}"
        
        # RSI状態判定
        rsi_value = symbol_df['rsi'].iloc[-1]
        rsi_state = '買われすぎ' if rsi_value > 70 else '売られすぎ' if rsi_value < 30 else '中立'
        rsi_elem = ET.SubElement(indicators_elem, "RSI")
        rsi_elem.set("value", f"{rsi_value:.2f}")
        rsi_elem.set("state", rsi_state)
        
        # MACD状態判定
        macd_elem = ET.SubElement(indicators_elem, "MACD")
        macd_elem.set("value", f"{symbol_df['macd'].iloc[-1]:.4f}")
        macd_elem.set("signal", f"{symbol_df['signal_line'].iloc[-1]:.4f}")
        macd_trend = '強気' if symbol_df['macd'].iloc[-1] > symbol_df['signal_line'].iloc[-1] else '弱気'
        macd_elem.set("trend", macd_trend)
        
        # クロス判定
        ET.SubElement(indicators_elem, "GoldenCross").text = '有' if symbol_df['golden_cross'].iloc[-1] else '無'
        ET.SubElement(indicators_elem, "DeadCross").text = '有' if symbol_df['dead_cross'].iloc[-1] else '無'
        
        # AI推奨要素（存在する場合）
        if ai_recommendation:
            ai_elem = ET.SubElement(stock_elem, "AIRecommendation")
            
            # リスク評価
            risk_elem = ET.SubElement(ai_elem, "RiskAssessment")
            risk_elem.set("score", str(ai_recommendation.get('risk_score', 0)))
            risk_elem.set("level", ai_recommendation.get('risk_level', 'N/A'))
            
            # 収益評価
            return_elem = ET.SubElement(ai_elem, "ReturnAssessment")
            return_elem.set("score", str(ai_recommendation.get('return_score', 0)))
            return_elem.set("level", ai_recommendation.get('return_level', 'N/A'))
            
            # 総合評価
            ET.SubElement(ai_elem, "OverallRating").text = ai_recommendation.get('overall_rating', 'N/A')
            ET.SubElement(ai_elem, "Recommendation").text = ai_recommendation.get('recommendation', 'N/A')
            ET.SubElement(ai_elem, "Reasoning").text = ai_recommendation.get('reasoning', 'N/A')
        
        return ET.tostring(stock_elem, encoding='unicode')
    
    except Exception as e:
        print(f"XML生成エラー ({symbol}): {str(e)}")
        return None
