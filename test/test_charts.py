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
    canvas_instances = []  # 记录创建的画布实例，便于断言

    class DummyWin:
        def __init__(self, master=None):
            self.master = master
            self._children = []
            self.titles = []  # 记录 title 调用
            self.tk = MagicMock()  # 添加 tk 属性

        def title(self, t):
            self.titles.append(t)

        def geometry(self, _):
            pass

        def bind(self, event, callback, add=None):
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
            canvas_instances.append(self)

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

    # 画布被创建一次，且挂载的 figure 就是 subplots 返回的 mock_fig、宿主是目标窗口
    assert len(canvas_instances) == 1
    assert canvas_instances[0].fig is mock_fig
    assert canvas_instances[0].master is win
    # 窗口标题为 "2025-01 收支分类饼状图"
    assert win.titles == ['2025-01 收支分类饼状图']
    # 支出、收入两个子图都绘制了饼图（mock axs 上可验证）
    mock_axs[0].pie.assert_called_once()
    mock_axs[1].pie.assert_called_once()
    # figure 引用被保存到窗口上，供切换月份时关闭旧图
    assert win._pie_fig is mock_fig


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
        
        def bind(self, event, callback, add=None):
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

    # 只有支出：支出子图绘制饼图，收入子图不绘制
    mock_axs[0].pie.assert_called_once()
    mock_axs[1].pie.assert_not_called()
    # 收入子图显示"无收入数据"占位文本
    mock_axs[1].text.assert_called_once()
    assert mock_axs[1].text.call_args[0][2] == '无收入数据'
    # figure 引用被保存到窗口上
    assert win._pie_fig is mock_fig


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
        
        def bind(self, event, callback, add=None):
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

    # 只有收入：收入子图绘制饼图，支出子图不绘制
    mock_axs[1].pie.assert_called_once()
    mock_axs[0].pie.assert_not_called()
    # 支出子图显示"无支出数据"占位文本
    mock_axs[0].text.assert_called_once()
    assert mock_axs[0].text.call_args[0][2] == '无支出数据'
    # figure 引用被保存到窗口上
    assert win._pie_fig is mock_fig


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
        
        def bind(self, event, callback, add=None):
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

    # 第一个月：上一月按钮被禁用，下一月按钮未禁用
    assert ('← 上一月', ['disabled']) in button_states
    assert ('下一月 →', ['disabled']) not in button_states


def test_show_monthly_chart_with_data(monkeypatch):
    """测试 show_monthly_chart 有数据时正常显示"""
    from ui import charts

    canvas_instances = []  # 记录创建的画布实例，便于断言

    class DummyWin:
        def __init__(self, master=None):
            self.master = master
            self.titles = []  # 记录 title 调用

        def title(self, t):
            self.titles.append(t)

        def geometry(self, _):
            pass

        def bind(self, event, callback, add=None):
            pass

    class DummyWidget:
        def pack(self, *args, **kwargs):
            pass

    class DummyCanvas:
        def __init__(self, fig, master=None):
            self.fig = fig
            self.master = master
            canvas_instances.append(self)

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

    mock_showinfo = MagicMock()
    monkeypatch.setattr(charts.tk, "Toplevel", DummyWin)
    monkeypatch.setattr(charts, "FigureCanvasTkAgg", DummyCanvas)
    monkeypatch.setattr(charts.messagebox, "showinfo", mock_showinfo)

    charts.show_monthly_chart(df, None)

    # 画布被创建一次，挂载的是 show_monthly_chart 内部创建的真实 matplotlib Figure
    from matplotlib.figure import Figure
    assert len(canvas_instances) == 1
    assert isinstance(canvas_instances[0].fig, Figure)
    assert canvas_instances[0].master is not None
    # 窗口标题为"每月收支柱状图"
    assert canvas_instances[0].master.titles == ['每月收支柱状图']
    # 有数据时不应弹出"无数据"提示
    mock_showinfo.assert_not_called()


def test_show_single_month_pie_with_data(monkeypatch):
    """测试 show_single_month_pie 有数据时显示选择窗口"""
    from ui import charts

    created_wins = []  # 记录创建的窗口实例，便于断言
    created_cbs = []  # 记录创建的下拉框实例，便于断言

    class DummyWin:
        def __init__(self, master=None):
            self.master = master
            self._destroyed = False
            self.titles = []  # 记录 title 调用
            self.tk = MagicMock()  # 添加 tk 属性

        def title(self, t):
            self.titles.append(t)

        def geometry(self, _):
            pass

        def bind(self, event, callback, add=None):
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
            created_cbs.append(self)

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

    def _make_win(master=None):
        w = DummyWin(master)
        created_wins.append(w)
        return w

    with patch.object(charts, 'show_pie') as mock_show_pie:
        monkeypatch.setattr(charts.tk, "Toplevel", _make_win)
        monkeypatch.setattr(charts.tk, "Label", DummyLabel)
        monkeypatch.setattr(charts.tk, "StringVar", MagicMock)
        monkeypatch.setattr(charts.ttk, "Combobox", DummyCombobox)
        monkeypatch.setattr(charts.ttk, "Button", DummyButton)
        monkeypatch.setattr(charts.messagebox, "showinfo", lambda t, m: None)

        charts.show_single_month_pie(df, None)

        # 弹出了月份选择窗口，标题为"选择月份"
        assert len(created_wins) == 1
        assert created_wins[0].titles == ['选择月份']
        # 下拉框的月份选项来自数据中的两个月份
        assert len(created_cbs) == 1
        assert list(created_cbs[0]._values) == ['2025-01', '2025-02']
        # 仅弹出选择窗口，show_pie 只有点击确定按钮后才会被调用
        mock_show_pie.assert_not_called()
