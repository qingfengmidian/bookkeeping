import sqlite3
import pandas as pd
import os

def ensure_db(db_path):
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        create_table(conn)
        conn.close()

def create_table(conn):
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        日期 TEXT,
        类型 TEXT,
        分类 TEXT,
        金额 REAL,
        备注 TEXT
    )''')
    conn.commit()

def load_data(db_path):
    conn = sqlite3.connect(db_path)
    create_table(conn)
    c = conn.cursor()
    c.execute('SELECT 日期, 类型, 分类, 金额, 备注 FROM records')
    rows = c.fetchall()
    df = pd.DataFrame(rows, columns=['日期', '类型', '分类', '金额', '备注'])
    if not df.empty:
        df['金额'] = pd.to_numeric(df['金额'], errors='coerce')
    conn.close()
    return df

def save_data(db_path, df):
    conn = sqlite3.connect(db_path)
    create_table(conn)
    c = conn.cursor()
    c.execute('DELETE FROM records')
    for _, row in df.iterrows():
        c.execute('INSERT INTO records (日期, 类型, 分类, 金额, 备注) VALUES (?, ?, ?, ?, ?)',
                  (row['日期'], row['类型'], row['分类'], row['金额'], row['备注']))
    conn.commit()
    conn.close()
