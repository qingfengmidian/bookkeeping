import pandas as pd

from model.record_model import process_monthly, process_detail


def _sample_df():
    return pd.DataFrame([
        {"日期": "2025-01-01", "类型": "收入", "分类": "工资", "金额": 1000.0, "备注": "test1"},
        {"日期": "2025-01-02", "类型": "支出", "分类": "餐饮", "金额": 50.0, "备注": "test2"},
        {"日期": "2025-02-01", "类型": "收入", "分类": "工资", "金额": 1200.0, "备注": "test3"},
    ])


def test_process_monthly_basic():
    df = _sample_df()

    monthly = process_monthly(df)

    # 应该有两个月份
    assert set(monthly.index) == {"2025-01", "2025-02"}

    # 检查 2025-01 的收入和支出
    jan = monthly.loc["2025-01"]
    assert jan["收入"] == 1000.0
    assert jan["支出"] == 50.0

    # 检查汇总列是否存在
    assert "总收入" in monthly.columns
    assert "总支出" in monthly.columns


def test_process_detail_filters_by_month():
    df = _sample_df()

    jan_df = process_detail(df, "2025-01")
    feb_df = process_detail(df, "2025-02")

    assert not jan_df.empty
    assert not feb_df.empty

    # 将日期列统一格式化为字符串再比较，避免 Timestamp 与字符串直接比较
    jan_dates = pd.to_datetime(jan_df["日期"]).dt.strftime("%Y-%m-%d")
    feb_dates = pd.to_datetime(feb_df["日期"]).dt.strftime("%Y-%m-%d")

    assert set(jan_dates) == {"2025-01-01", "2025-01-02"}
    assert set(feb_dates) == {"2025-02-01"}


def test_process_monthly_empty_df():
    """测试空 DataFrame 的月度处理"""
    empty_df = pd.DataFrame(columns=['日期', '类型', '分类', '金额', '备注'])
    
    result = process_monthly(empty_df)
    
    # 应返回空 DataFrame
    assert result.empty


def test_process_detail_empty_df():
    """测试空 DataFrame 的明细筛选"""
    empty_df = pd.DataFrame(columns=['日期', '类型', '分类', '金额', '备注'])
    
    result = process_detail(empty_df, "2025-01")
    
    # 应返回空 DataFrame
    assert result.empty


def test_process_detail_nonexistent_month():
    """测试筛选不存在的月份"""
    df = _sample_df()
    
    result = process_detail(df, "2024-12")  # 不存在的月份
    
    # 应返回空 DataFrame
    assert result.empty


def test_process_monthly_only_income():
    """测试只有收入数据的情况"""
    df = pd.DataFrame([
        {"日期": "2025-01-01", "类型": "收入", "分类": "工资", "金额": 1000.0, "备注": "test1"},
        {"日期": "2025-01-15", "类型": "收入", "分类": "奖金", "金额": 500.0, "备注": "test2"},
    ])
    
    monthly = process_monthly(df)
    
    assert len(monthly) == 1
    assert monthly.loc["2025-01", "收入"] == 1500.0
    assert monthly.loc["2025-01", "总支出"] == 0  # 没有支出应为0


def test_process_monthly_only_expense():
    """测试只有支出数据的情况"""
    df = pd.DataFrame([
        {"日期": "2025-01-01", "类型": "支出", "分类": "餐饮", "金额": 100.0, "备注": "test1"},
        {"日期": "2025-01-15", "类型": "支出", "分类": "交通", "金额": 50.0, "备注": "test2"},
    ])
    
    monthly = process_monthly(df)
    
    assert len(monthly) == 1
    assert monthly.loc["2025-01", "支出"] == 150.0
    assert monthly.loc["2025-01", "总收入"] == 0  # 没有收入应为0


def test_process_detail_preserves_data():
    """测试明细筛选是否保留原始数据完整性"""
    df = _sample_df()

    jan_df = process_detail(df, "2025-01")

    # 验证筛选后的数据完整性
    assert '日期' in jan_df.columns
    assert '类型' in jan_df.columns
    assert '分类' in jan_df.columns
    assert '金额' in jan_df.columns
    assert '备注' in jan_df.columns

    # 验证金额正确
    assert jan_df['金额'].sum() == 1050.0  # 1000 + 50


def test_process_monthly_dirty_dates():
    """测试 process_monthly 丢弃脏日期行，合法行（含混合格式）正常汇总"""
    df = pd.DataFrame([
        {"日期": "2025-07-01 12:00:00", "类型": "收入", "分类": "工资", "金额": 1000.0, "备注": "t1"},
        {"日期": "not-a-date", "类型": "支出", "分类": "餐饮", "金额": 50.0, "备注": "t2"},
        {"日期": "2025-07-15", "类型": "支出", "分类": "交通", "金额": 30.0, "备注": "t3"},
        {"日期": "", "类型": "收入", "分类": "奖金", "金额": 200.0, "备注": "t4"},
    ])

    monthly = process_monthly(df)

    # 非法日期行被丢弃，仅剩 2025-07 一个月的合法数据
    assert set(monthly.index) == {"2025-07"}
    assert monthly.loc["2025-07", "收入"] == 1000.0
    assert monthly.loc["2025-07", "支出"] == 30.0
    # 原始 DataFrame 未被修改
    assert len(df) == 4


def test_process_detail_dirty_dates():
    """测试 process_detail 丢弃脏日期行，合法行正常按月筛选"""
    df = pd.DataFrame([
        {"日期": "2025-07-01 12:00:00", "类型": "收入", "分类": "工资", "金额": 1000.0, "备注": "t1"},
        {"日期": "not-a-date", "类型": "支出", "分类": "餐饮", "金额": 50.0, "备注": "t2"},
        {"日期": "2025-08-01", "类型": "支出", "分类": "餐饮", "金额": 60.0, "备注": "t3"},
    ])

    july_df = process_detail(df, "2025-07")

    # 只有一条合法记录属于 2025-07，脏日期行被丢弃
    assert len(july_df) == 1
    assert july_df.iloc[0]["金额"] == 1000.0
    assert july_df.iloc[0]["类型"] == "收入"
    # 原始 DataFrame 未被修改
    assert len(df) == 3
