import os
import sqlite3
import pandas as pd

from db.database import ensure_db, load_data, save_data
from utils.constants import DB_DEFAULT


def test_ensure_db_creates_file(tmp_path):
    db_path = tmp_path / "test.db"
    assert not db_path.exists()

    ensure_db(str(db_path))

    # 数据库文件应被创建
    assert db_path.exists()

    # 且包含 records 表
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='records'")
    row = cur.fetchone()
    conn.close()
    assert row is not None


def test_save_and_load_roundtrip(tmp_path):
    db_path = tmp_path / "test_roundtrip.db"
    # 构造一个简单的 DataFrame
    df = pd.DataFrame([
        {"日期": "2025-01-01", "类型": "收入", "分类": "工资", "金额": 1000.0, "备注": "test1"},
        {"日期": "2025-01-02", "类型": "支出", "分类": "餐饮", "金额": 50.5, "备注": "test2"},
    ])

    save_data(str(db_path), df)

    loaded = load_data(str(db_path))

    # 按金额排序后比较，避免顺序差异
    df_sorted = df.sort_values(["日期", "金额"]).reset_index(drop=True)
    loaded_sorted = loaded.sort_values(["日期", "金额"]).reset_index(drop=True)

    pd.testing.assert_frame_equal(df_sorted, loaded_sorted)
