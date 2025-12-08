import pandas as pd

from ui import charts


def test_show_monthly_chart_empty_df(monkeypatch):
    """空 DataFrame 时应提示无数据并立即返回，不创建窗口。"""
    called = {}

    def fake_showinfo(title, message):  # noqa: D401
        called["args"] = (title, message)

    monkeypatch.setattr(charts.messagebox, "showinfo", fake_showinfo)

    df = pd.DataFrame()

    # 不应抛出异常
    charts.show_monthly_chart(df, master=None)

    assert "args" in called
    title, message = called["args"]
    assert "无数据" in title
    assert "没有可统计的账单数据" in message


def test_show_single_month_pie_empty_df(monkeypatch):
    """空 DataFrame 时应提示无数据并立即返回，不创建窗口。"""
    called = {}

    def fake_showinfo(title, message):  # noqa: D401
        called["args"] = (title, message)

    monkeypatch.setattr(charts.messagebox, "showinfo", fake_showinfo)

    df = pd.DataFrame()

    charts.show_single_month_pie(df, master=None)

    assert "args" in called
    title, message = called["args"]
    assert "无数据" in title
    assert "没有可统计的账单数据" in message


def test_show_monthly_chart_only_expense_no_income(monkeypatch):
    """只有支出或只有收入时，内部应能正常处理，不抛异常。"""

    # mock 掉 Tk 相关类，避免真实创建窗口
    class DummyWin:
        def __init__(self, master=None):  # noqa: D401
            self.master = master

        def title(self, _):  # noqa: D401
            pass

        def geometry(self, _):  # noqa: D401
            pass

        def winfo_children(self):  # noqa: D401
            return []

    class DummyWidget:
        def pack(self, *_, **__):  # noqa: D401
            pass

    class DummyCanvas:
        def __init__(self, fig, master=None):  # noqa: D401
            self.fig = fig
            self.master = master

        def draw(self):  # noqa: D401
            pass

        def get_tk_widget(self):  # noqa: D401
            return DummyWidget()

    monkeypatch.setattr(charts.tk, "Toplevel", DummyWin)
    monkeypatch.setattr(charts, "FigureCanvasTkAgg", DummyCanvas)

    # 只有支出数据
    df = pd.DataFrame(
        [
            {"日期": "2025-01-01", "类型": "支出", "分类": "餐饮", "金额": 50.0},
            {"日期": "2025-01-02", "类型": "支出", "分类": "交通", "金额": 20.0},
        ]
    )

    charts.show_monthly_chart(df, master=None)

    # 只有收入数据
    df_income = pd.DataFrame(
        [
            {"日期": "2025-02-01", "类型": "收入", "分类": "工资", "金额": 1000.0},
            {"日期": "2025-02-05", "类型": "收入", "分类": "奖金", "金额": 200.0},
        ]
    )

    charts.show_monthly_chart(df_income, master=None)
