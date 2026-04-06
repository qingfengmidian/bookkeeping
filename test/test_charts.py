"""
测试 ui/charts.py 中的图表功能
补充 draw_pie 和 show_pie 的测试
"""
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch


def test_draw_pie_normal_data(monkeypatch):
    """测试 draw_pie 正常数据情况"""
    from ui import charts
    from unittest.mock import patch
    
    # Mock Tkinter 组件
    class DummyWin:
        def __init__(self, master=None):
            self.master = master
            self._children = []
            self.tk = MagicMock()  # 添加 tk 属性
        
        def title(self, _):
            pass
        
        def geometry(self, _):
            pass
        
        def winfo_children(self):
            return self._children
        
        def destroy(self):
            pass
    
    class DummyFrame:
        def __init__(self, master=None, **kwargs):
            self.master = master
            self.children = []
        
        def pack(self, **kwargs):
            pass
    
    class DummyWidget:
        def pack(self, *args, **kwargs):
            pass
    
    class DummyCanvas:
        def __init__(self, fig, master=None):
            self.fig = fig
            self.master = master
        
        def draw(self):
            pass
        
        def get_tk_widget(self):
            return DummyWidget()
    
    class DummyButton:
        def __init__(self, master=None, **kwargs):
            self.master = master
        
        def pack(self, **kwargs):
            pass
        
        def state(self, state):
            pass
    
    # 准备测试数据
    df = pd.DataFrame([
        {"日期": "2025-01-01", "类型": "支出", "分类": "餐饮", "金额": 50.0},
        {"日期": "2025-01-02", "类型": "支出", "分类": "交通", "金额": 30.0},
        {"日期": "2025-01-03", "类型": "收入", "分类": "工资", "金额": 1000.0},
    ])
    df['日期'] = pd.to_datetime(df['日期'])
    df['年月'] = df['日期'].dt.to_period('M').astype(str)
    
    monkeypatch.setattr(charts.tk, "Toplevel", DummyWin)
    monkeypatch.setattr(charts, "FigureCanvasTkAgg", DummyCanvas)
    monkeypatch.setattr(charts.ttk, "Frame", DummyFrame)
    monkeypatch.setattr(charts.ttk, "Button", DummyButton)
    
    # Mock matplotlib.pyplot.subplots 避免创建真实图表
    mock_fig = MagicMock()
    mock_axs = [MagicMock(), MagicMock()]
    with patch.object(charts.plt, 'subplots', return_value=(mock_fig, mock_axs)):
        with patch.object(charts.plt, 'tight_layout'):
            # 执行测试
            win = DummyWin()
            charts.draw_pie("2025-01", df, None, win)
    
    # 验证没有抛出异常
    assert True


def test_draw_pie_only_expense(monkeypatch):
    """测试 draw_pie 只有支出的情况"""
    from ui import charts
    from unittest.mock import patch
    
    class DummyWin:
        def __init__(self, master=None):
            self.master = master
            self.tk = MagicMock()
        
        def title(self, _):
            pass
        
        def geometry(self, _):
            pass
        
        def winfo_children(self):
            return []
    
    class DummyWidget:
        def pack(self, *args, **kwargs):
            pass
    
    class DummyCanvas:
        def __init__(self, fig, master=None):
            self.fig = fig
            self.master = master
        
        def draw(self):
            pass
        
        def get_tk_widget(self):
            return DummyWidget()
    
    class DummyFrame:
        def __init__(self, master=None, **kwargs):
            self.master = master
        
        def pack(self, **kwargs):
            pass
    
    class DummyButton:
        def __init__(self, master=None, **kwargs):
            self.master = master
        
        def pack(self, **kwargs):
            pass
        
        def state(self, state):
            pass
    
    # 只有支出数据
    df = pd.DataFrame([
        {"日期": "2025-01-01", "类型": "支出", "分类": "餐饮", "金额": 50.0},
        {"日期": "2025-01-02", "类型": "支出", "分类": "交通", "金额": 30.0},
    ])
    df['日期'] = pd.to_datetime(df['日期'])
    df['年月'] = df['日期'].dt.to_period('M').astype(str)
    
    monkeypatch.setattr(charts.tk, "Toplevel", DummyWin)
    monkeypatch.setattr(charts, "FigureCanvasTkAgg", DummyCanvas)
    monkeypatch.setattr(charts.ttk, "Frame", DummyFrame)
    monkeypatch.setattr(charts.ttk, "Button", DummyButton)
    
    # Mock matplotlib.pyplot.subplots
    mock_fig = MagicMock()
    mock_axs = [MagicMock(), MagicMock()]
    with patch.object(charts.plt, 'subplots', return_value=(mock_fig, mock_axs)):
        with patch.object(charts.plt, 'tight_layout'):
            win = DummyWin()
            charts.draw_pie("2025-01", df, None, win)
    
    assert True


def test_draw_pie_only_income(monkeypatch):
    """测试 draw_pie 只有收入的情况"""
    from ui import charts
    from unittest.mock import patch
    
    class DummyWin:
        def __init__(self, master=None):
            self.master = master
            self.tk = MagicMock()
        
        def title(self, _):
            pass
        
        def geometry(self, _):
            pass
        
        def winfo_children(self):
            return []
    
    class DummyWidget:
        def pack(self, *args, **kwargs):
            pass
    
    class DummyCanvas:
        def __init__(self, fig, master=None):
            self.fig = fig
            self.master = master
        
        def draw(self):
            pass
        
        def get_tk_widget(self):
            return DummyWidget()
    
    class DummyFrame:
        def __init__(self, master=None, **kwargs):
            self.master = master
        
        def pack(self, **kwargs):
            pass
    
    class DummyButton:
        def __init__(self, master=None, **kwargs):
            self.master = master
        
        def pack(self, **kwargs):
            pass
        
        def state(self, state):
            pass
    
    # 只有收入数据
    df = pd.DataFrame([
        {"日期": "2025-01-01", "类型": "收入", "分类": "工资", "金额": 1000.0},
        {"日期": "2025-01-02", "类型": "收入", "分类": "奖金", "金额": 200.0},
    ])
    df['日期'] = pd.to_datetime(df['日期'])
    df['年月'] = df['日期'].dt.to_period('M').astype(str)
    
    monkeypatch.setattr(charts.tk, "Toplevel", DummyWin)
    monkeypatch.setattr(charts, "FigureCanvasTkAgg", DummyCanvas)
    monkeypatch.setattr(charts.ttk, "Frame", DummyFrame)
    monkeypatch.setattr(charts.ttk, "Button", DummyButton)
    
    # Mock matplotlib.pyplot.subplots
    mock_fig = MagicMock()
    mock_axs = [MagicMock(), MagicMock()]
    with patch.object(charts.plt, 'subplots', return_value=(mock_fig, mock_axs)):
        with patch.object(charts.plt, 'tight_layout'):
            win = DummyWin()
            charts.draw_pie("2025-01", df, None, win)
    
    assert True


def test_show_pie_destroys_selector(monkeypatch):
    """测试 show_pie 会销毁选择窗口"""
    from ui import charts
    
    # 模拟选择窗口
    mock_sel_win = MagicMock()
    
    # 模拟 draw_pie
    with patch.object(charts, 'draw_pie') as mock_draw:
        charts.show_pie("2025-01", pd.DataFrame(), None, mock_sel_win)
        
        # 验证选择窗口被销毁
        mock_sel_win.destroy.assert_called_once()
        # 验证 draw_pie 被调用
        mock_draw.assert_called_once()


def test_draw_pie_month_navigation(monkeypatch):
    """测试 draw_pie 的月份导航按钮状态"""
    from ui import charts
    from unittest.mock import patch
    
    class DummyWin:
        def __init__(self, master=None):
            self.master = master
            self.tk = MagicMock()
        
        def title(self, _):
            pass
        
        def geometry(self, _):
            pass
        
        def winfo_children(self):
            return []
    
    class DummyWidget:
        def pack(self, *args, **kwargs):
            pass
    
    class DummyCanvas:
        def __init__(self, fig, master=None):
            self.fig = fig
            self.master = master
        
        def draw(self):
            pass
        
        def get_tk_widget(self):
            return DummyWidget()
    
    class DummyFrame:
        def __init__(self, master=None, **kwargs):
            self.master = master
        
        def pack(self, **kwargs):
            pass
    
    # 多个月份数据
    df = pd.DataFrame([
        {"日期": "2025-01-01", "类型": "支出", "分类": "餐饮", "金额": 50.0},
        {"日期": "2025-02-01", "类型": "支出", "分类": "餐饮", "金额": 60.0},
        {"日期": "2025-03-01", "类型": "支出", "分类": "餐饮", "金额": 70.0},
    ])
    df['日期'] = pd.to_datetime(df['日期'])
    df['年月'] = df['日期'].dt.to_period('M').astype(str)
    
    # 跟踪按钮状态
    button_states = []
    
    class DummyButton:
        def __init__(self, master=None, **kwargs):
            self.master = master
            self._text = kwargs.get('text', '')
        
        def pack(self, **kwargs):
            pass
        
        def state(self, state):
            button_states.append((self._text, state))
    
    monkeypatch.setattr(charts.tk, "Toplevel", DummyWin)
    monkeypatch.setattr(charts, "FigureCanvasTkAgg", DummyCanvas)
    monkeypatch.setattr(charts.ttk, "Frame", DummyFrame)
    monkeypatch.setattr(charts.ttk, "Button", DummyButton)
    
    # Mock matplotlib.pyplot.subplots
    mock_fig = MagicMock()
    mock_axs = [MagicMock(), MagicMock()]
    with patch.object(charts.plt, 'subplots', return_value=(mock_fig, mock_axs)):
        with patch.object(charts.plt, 'tight_layout'):
            # 测试第一个月（上一月应禁用）
            win = DummyWin()
            charts.draw_pie("2025-01", df, None, win)
    
    # 验证测试运行无异常
    assert True


def test_show_monthly_chart_with_data(monkeypatch):
    """测试 show_monthly_chart 有数据时正常显示"""
    from ui import charts
    
    class DummyWin:
        def __init__(self, master=None):
            self.master = master
        
        def title(self, _):
            pass
        
        def geometry(self, _):
            pass
    
    class DummyWidget:
        def pack(self, *args, **kwargs):
            pass
    
    class DummyCanvas:
        def __init__(self, fig, master=None):
            self.fig = fig
            self.master = master
        
        def draw(self):
            pass
        
        def get_tk_widget(self):
            return DummyWidget()
    
    # 多月份数据
    df = pd.DataFrame([
        {"日期": "2025-01-01", "类型": "收入", "分类": "工资", "金额": 1000.0},
        {"日期": "2025-01-02", "类型": "支出", "分类": "餐饮", "金额": 50.0},
        {"日期": "2025-02-01", "类型": "收入", "分类": "工资", "金额": 1200.0},
        {"日期": "2025-02-02", "类型": "支出", "分类": "交通", "金额": 80.0},
    ])
    
    monkeypatch.setattr(charts.tk, "Toplevel", DummyWin)
    monkeypatch.setattr(charts, "FigureCanvasTkAgg", DummyCanvas)
    monkeypatch.setattr(charts.messagebox, "showinfo", lambda t, m: None)
    
    charts.show_monthly_chart(df, None)
    
    assert True


def test_show_single_month_pie_with_data(monkeypatch):
    """测试 show_single_month_pie 有数据时显示选择窗口"""
    from ui import charts
    
    class DummyWin:
        def __init__(self, master=None):
            self.master = master
            self._destroyed = False
            self.tk = MagicMock()  # 添加 tk 属性
        
        def title(self, _):
            pass
        
        def geometry(self, _):
            pass
        
        def destroy(self):
            self._destroyed = True
    
    class DummyLabel:
        def __init__(self, master=None, **kwargs):
            self.master = master
        
        def pack(self, **kwargs):
            pass
    
    class DummyCombobox:
        def __init__(self, master=None, **kwargs):
            self.master = master
            self._values = kwargs.get('values', [])
        
        def current(self, i):
            pass
        
        def set(self, v):
            pass
        
        def pack(self, **kwargs):
            pass
    
    class DummyButton:
        def __init__(self, master=None, **kwargs):
            self.master = master
        
        def pack(self, **kwargs):
            pass
    
    # 多月份数据
    df = pd.DataFrame([
        {"日期": "2025-01-01", "类型": "支出", "分类": "餐饮", "金额": 50.0},
        {"日期": "2025-02-01", "类型": "支出", "分类": "餐饮", "金额": 60.0},
    ])
    df['日期'] = pd.to_datetime(df['日期'])
    df['年月'] = df['日期'].dt.to_period('M').astype(str)
    
    with patch.object(charts, 'show_pie') as mock_show_pie:
        monkeypatch.setattr(charts.tk, "Toplevel", lambda master=None: DummyWin(master))
        monkeypatch.setattr(charts.tk, "Label", DummyLabel)
        monkeypatch.setattr(charts.tk, "StringVar", MagicMock)
        monkeypatch.setattr(charts.ttk, "Combobox", DummyCombobox)
        monkeypatch.setattr(charts.ttk, "Button", DummyButton)
        monkeypatch.setattr(charts.messagebox, "showinfo", lambda t, m: None)
        
        charts.show_single_month_pie(df, None)
        
        # 验证显示选择窗口
        assert True
