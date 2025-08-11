import json
import os
from typing import Dict
from utils import setup_backend_logger

logger = setup_backend_logger(__name__)

def build_recommendation_prompt(params: Dict, data: Dict) -> str:
    """JSONテンプレートから推奨プロンプトを構築
    
    Args:
        params: ユーザー入力パラメータ
        data: 銘柄データ
        
    Returns:
        構築されたプロンプト文字列
    """
    try:
        prompt_path = os.path.abspath('prompts/recommendation_prompt.json')

        with open(prompt_path, encoding='utf-8') as f:
            template = json.load(f)
        
        prompt = (
            template['user_template'].format(
                principal=params.get('principal', 'N/A'),
                risk_tolerance=params.get('risk_tolerance', '中'),
                strategy=params.get('strategy', '成長株重視'),
                company_infos=json.dumps(data.get('company_infos', []), ensure_ascii=False),
                news=json.dumps(data.get('news', []), ensure_ascii=False),
                technical_indicators=json.dumps(data.get('technical_indicators', []), ensure_ascii=False),
                price_history=json.dumps(data.get('price_history', []), ensure_ascii=False)
            ) + "\n\n" +
            "output_format:" + template['output_format']
        )
        
        logger.debug(f"構築されたプロンプト: {prompt}")  # ログには先頭200文字のみ表示
        return prompt
        
    except Exception as e:
        logger.error(f"プロンプト構築エラー: {str(e)}")
        raise
