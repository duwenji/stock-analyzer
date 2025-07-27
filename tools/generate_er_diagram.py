import os
from sqlalchemy import inspect
from ..backend.utils import get_db_engine

def generate_er_diagram():
    # docsディレクトリ作成
    os.makedirs("docs", exist_ok=True)
    
    # PostgreSQLデータベース接続
    engine = get_db_engine()
    inspector = inspect(engine)
    
    # Mermaid記法でER図生成
    er_content = "```mermaid\nerDiagram\n"
    
    # テーブル一覧取得
    tables = inspector.get_table_names()
    
    # テーブルごとのカラム情報取得
    for table_name in tables:
        columns = inspector.get_columns(table_name)
        
        er_content += f"    {table_name} {{\n"
        for col in columns:
            er_content += f"        {col['type']} {col['name']}\n"
        er_content += "    }\n"
    
    # リレーションシップ情報取得
    relationships = []
    for table_name in tables:
        fks = inspector.get_foreign_keys(table_name)
        for fk in fks:
            from_table = table_name
            to_table = fk['referred_table']
            relationships.append(f"    {from_table} ||--o| {to_table} : \"{fk['name']}\"\n")
    
    # リレーションシップを追加（重複排除）
    er_content += ''.join(set(relationships))
    
    er_content += "```"
    
    # ER.mdファイルに保存
    with open("docs/ER.md", "w", encoding="utf-8") as f:
        f.write("# 株価分析システム ER図\n\n")
        f.write(er_content)
    
    print("ER図を docs/ER.md に生成しました")

if __name__ == "__main__":
    generate_er_diagram()
