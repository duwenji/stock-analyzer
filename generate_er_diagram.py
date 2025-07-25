import os
import sqlite3

def generate_er_diagram():
    # docsディレクトリ作成
    os.makedirs("docs", exist_ok=True)
    
    # データベース接続
    conn = sqlite3.connect('stock_data.db')
    cursor = conn.cursor()
    
    # テーブル情報取得
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    # Mermaid記法でER図生成
    er_content = "```mermaid\nerDiagram\n"
    
    # テーブルごとのカラム情報取得
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        er_content += f"    {table_name} {{\n"
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            er_content += f"        {col_type} {col_name}\n"
        er_content += "    }\n"
    
    # リレーションシップ情報取得
    cursor.execute("PRAGMA foreign_key_list(stock_prices);")
    relations = cursor.fetchall()
    
    for rel in relations:
        from_table = "stock_prices"
        to_table = "companies"
        er_content += f"    {from_table} ||--o| {to_table} : \"FK_company_ticket\"\n"
    
    er_content += "```"
    
    # ER.mdファイルに保存
    with open("docs/ER.md", "w", encoding="utf-8") as f:
        f.write("# 株価分析システム ER図\n\n")
        f.write(er_content)
    
    conn.close()
    print("ER図を docs/ER.md に生成しました")

if __name__ == "__main__":
    generate_er_diagram()
