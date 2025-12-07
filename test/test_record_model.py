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
