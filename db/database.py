import contextlib
import sqlite3
import pandas as pd
import os
from utils.constants import TABLE_RECORDS_SCHEMA, TABLE_NAME


def ensure_db(db_path: str) -> None:
    """
    确保数据库文件存在，不存在则创建。
    
    Args:
        db_path: 数据库文件路径
    """
    if not os.path.exists(db_path):
        with contextlib.closing(sqlite3.connect(db_path)) as conn:
            create_table(conn)


def create_table(conn: sqlite3.Connection) -> None:
    """
    创建账单记录表。
    
    Args:
        conn: SQLite数据库连接对象
    """
    c = conn.cursor()
    c.execute(f'''CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        {TABLE_RECORDS_SCHEMA}
    )''')
    # 创建索引以提升查询性能
    c.execute(f'CREATE INDEX IF NOT EXISTS idx_date ON {TABLE_NAME}(日期)')
    c.execute(f'CREATE INDEX IF NOT EXISTS idx_type ON {TABLE_NAME}(类型)')
    c.execute(f'CREATE INDEX IF NOT EXISTS idx_category ON {TABLE_NAME}(分类)')
    conn.commit()


def load_data(db_path: str) -> pd.DataFrame:
    """
    从数据库加载所有记录。
    
    Args:
        db_path: 数据库文件路径
        
    Returns:
        包含所有记录的DataFrame，列为：日期、类型、分类、金额、备注
    """
    with contextlib.closing(sqlite3.connect(db_path)) as conn:
        create_table(conn)
        c = conn.cursor()
        c.execute(f'SELECT 日期, 类型, 分类, 金额, 备注 FROM {TABLE_NAME}')
        rows = c.fetchall()
        df = pd.DataFrame(rows, columns=['日期', '类型', '分类', '金额', '备注'])
        if not df.empty:
            df['金额'] = pd.to_numeric(df['金额'], errors='coerce')
    return df


def save_data(db_path: str, df: pd.DataFrame) -> None:
    """
    将DataFrame保存到数据库（全量覆盖）。
    
    Args:
        db_path: 数据库文件路径
        df: 要保存的DataFrame
        
    Raises:
        sqlite3.Error: 数据库操作失败时抛出
    """
    conn = sqlite3.connect(db_path)
    try:
        create_table(conn)
        c = conn.cursor()
        c.execute('DELETE FROM records')
        
        # 使用executemany批量插入，提升性能
        if not df.empty:
            data_tuples = [
                (row['日期'], row['类型'], row['分类'], row['金额'], row['备注'])
                for _, row in df.iterrows()
            ]
            c.executemany(
                'INSERT INTO records (日期, 类型, 分类, 金额, 备注) VALUES (?, ?, ?, ?, ?)',
                data_tuples
            )
        
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()
