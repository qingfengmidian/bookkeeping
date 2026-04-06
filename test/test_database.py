import os
import sqlite3
import pandas as pd

from db.database import ensure_db, create_table, load_data, save_data
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


def test_load_data_empty_db(tmp_path):
    """测试从空数据库加载数据"""
    db_path = tmp_path / "empty.db"
    ensure_db(str(db_path))
    
    loaded = load_data(str(db_path))
    
    # 应返回空 DataFrame
    assert loaded.empty
    assert list(loaded.columns) == ['日期', '类型', '分类', '金额', '备注']


def test_save_data_empty_df(tmp_path):
    """测试保存空 DataFrame"""
    db_path = tmp_path / "empty_save.db"
    empty_df = pd.DataFrame(columns=['日期', '类型', '分类', '金额', '备注'])
    
    save_data(str(db_path), empty_df)
    
    # 重新加载应得到空数据
    loaded = load_data(str(db_path))
    assert loaded.empty


def test_create_table_directly(tmp_path):
    """测试直接调用 create_table 函数"""
    db_path = tmp_path / "direct_create.db"
    conn = sqlite3.connect(db_path)
    
    # 直接创建表
    create_table(conn)
    
    # 验证表存在
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='records'")
    row = cur.fetchone()
    conn.close()
    
    assert row is not None


def test_load_data_with_invalid_amount(tmp_path):
    """测试加载包含无效金额的数据"""
    db_path = tmp_path / "invalid_amount.db"
    ensure_db(str(db_path))
    
    # 手动插入包含非数字金额的数据
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("INSERT INTO records (日期, 类型, 分类, 金额, 备注) VALUES (?, ?, ?, ?, ?)",
                ("2025-01-01", "支出", "餐饮", "invalid", "test"))
    conn.commit()
    conn.close()
    
    # 加载时应处理无效金额
    loaded = load_data(str(db_path))
    assert len(loaded) == 1
    # 无效金额应被转换为 NaN
    assert pd.isna(loaded.iloc[0]['金额'])


def test_save_data_overwrite(tmp_path):
    """测试 save_data 会覆盖已有数据"""
    db_path = tmp_path / "overwrite.db"
    
    # 第一次保存
    df1 = pd.DataFrame([
        {"日期": "2025-01-01", "类型": "收入", "分类": "工资", "金额": 1000.0, "备注": "first"},
    ])
    save_data(str(db_path), df1)
    
    # 第二次保存（应覆盖）
    df2 = pd.DataFrame([
        {"日期": "2025-02-01", "类型": "支出", "分类": "餐饮", "金额": 100.0, "备注": "second"},
    ])
    save_data(str(db_path), df2)
    
    # 验证只有第二次的数据
    loaded = load_data(str(db_path))
    assert len(loaded) == 1
    assert loaded.iloc[0]['日期'] == '2025-02-01'
    assert loaded.iloc[0]['备注'] == 'second'
