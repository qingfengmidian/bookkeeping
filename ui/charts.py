import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pandas as pd

from ui.theme import (BORDER, TEXT, TEXT_MUTED, INCOME, EXPENSE,
                      CHART_PALETTE, MPL_FONT_FALLBACK)
from utils.i18n import _, _t


def __getattr__(name):
    """延迟加载 matplotlib：仅在实际绘图时才导入，显著加快应用启动"""
    if name == 'plt':
        import matplotlib.pyplot as plt
        globals()['plt'] = plt
        return plt
    if name == 'FigureCanvasTkAgg':
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        globals()['FigureCanvasTkAgg'] = FigureCanvasTkAgg
        return FigureCanvasTkAgg
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def _setup_matplotlib():
    """图表中文字体与负号设置（设计稿 4.3）：字体取 matplotlib 专用的跨平台回退链"""
    import matplotlib
    matplotlib.rcParams['font.sans-serif'] = MPL_FONT_FALLBACK
    matplotlib.rcParams['axes.unicode_minus'] = False  # 正常显示负号


def _style_axes(ax, grid=True):
    """图表装饰统一（设计稿 4.3）：白底、隐藏上/右边框，网格线仅 Y 轴、虚线、BORDER 色"""
    ax.set_facecolor('white')
    # 隐藏上/右边框，剩余边框用 BORDER 暖灰发丝线
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(BORDER)
    ax.spines['bottom'].set_color(BORDER)
    ax.tick_params(colors=TEXT_MUTED, labelsize=10)
    if grid:
        ax.yaxis.grid(True, linestyle='--', linewidth=0.8, color=BORDER)
        ax.xaxis.grid(False)
        ax.set_axisbelow(True)  # 网格线置于柱体之下


def show_monthly_chart(df, master):
    _setup_matplotlib()
    if df.empty:
        messagebox.showinfo(_('无数据'), _('没有可统计的账单数据。'))
        return
    df = df.copy()
    df['日期'] = pd.to_datetime(df['日期'])
    df['年月'] = df['日期'].dt.to_period('M').astype(str)
    monthly = df.pivot_table(index='年月', columns='类型', values='金额', aggfunc='sum', fill_value=0)
    months = monthly.index.tolist()
    income = monthly['收入'] if '收入' in monthly.columns else [0]*len(months)
    expense = monthly['支出'] if '支出' in monthly.columns else [0]*len(months)
    fig, ax = plt.subplots(figsize=(8,5))
    fig.patch.set_facecolor('white')  # 图表背景与窗口协调（设计稿 4.3）：纯白底
    x = range(len(months))
    # 收入柱=INCOME 橄榄绿、支出柱=EXPENSE 墨色（设计稿 4.3）
    ax.bar(x, income, width=0.4, label=_('收入'), align='center', color=INCOME)
    ax.bar([i+0.4 for i in x], expense, width=0.4, label=_('支出'), align='center', color=EXPENSE)
    ax.set_xticks([i+0.2 for i in x])
    ax.set_xticklabels(months, rotation=45)
    _style_axes(ax, grid=True)
    ax.set_ylabel(_('金额'), color=TEXT_MUTED)
    # 标题 14px 左对齐（设计稿 4.3）
    ax.set_title(_('每月收入与支出变化'), fontsize=14, loc='left', color=TEXT)
    ax.legend(frameon=False)
    plt.tight_layout()
    win = tk.Toplevel(master)
    win.title(_('每月收支柱状图'))
    win.geometry('700x500')
    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)


def show_single_month_pie(df, master):
    # 选择月份，绘制该月的收入/支出分类饼状图
    _setup_matplotlib()
    if df.empty:
        messagebox.showinfo(_('无数据'), _('没有可统计的账单数据。'))
        return
    df = df.copy()
    df['日期'] = pd.to_datetime(df['日期'])
    df['年月'] = df['日期'].dt.to_period('M').astype(str)
    months = sorted(df['年月'].unique())
    # 弹窗选择月份（下拉选择框）
    sel_win = tk.Toplevel(master)
    sel_win.title(_('选择月份'))
    sel_win.geometry('250x140')
    tk.Label(sel_win, text=_('请选择月份：')).pack(pady=10)
    month_var = tk.StringVar()
    cb = ttk.Combobox(sel_win, textvariable=month_var, values=months, state='readonly')
    cb.pack(pady=5)
    if months:
        cb.current(0)
        month_var.set(months[0])
    btn = ttk.Button(sel_win, text=_('确定'), style='Accent.TButton',
                     command=lambda: show_pie(month_var.get(), df, master, sel_win))
    btn.pack(pady=(10, 0), ipadx=12, ipady=2, anchor='center')


    # 画饼状图窗口，带左右切换
def draw_pie(month, df, master, win=None):
    if win is None:
        win = tk.Toplevel(master)
    win.title(f"{month} {_('收支分类饼状图')}")
    win.geometry('750x480')
    # 关闭上一次绘制的 figure，防止切换月份时 matplotlib figure 泄漏
    old_fig = getattr(win, '_pie_fig', None)
    if old_fig is not None:
        plt.close(old_fig)
        win._pie_fig = None
    # 清空内容
    for widget in win.winfo_children():
        widget.destroy()
    month_df = df[df['年月'] == month].copy()
    # 确保金额为数值且非空
    month_df['金额'] = pd.to_numeric(month_df['金额'], errors='coerce').fillna(0)
    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    fig.patch.set_facecolor('white')  # 图表背景与窗口协调（设计稿 4.3）：纯白底
    for ax in axs:
        ax.set_facecolor('white')
    # 支出分类
    expense = month_df[month_df['类型'] == '支出'].groupby('分类')['金额'].sum()
    if not expense.empty and expense.sum() > 0:
        try:
            # 分类饼图统一用低饱和暖系色板（设计稿 4.3），替换 matplotlib 默认彩色
            axs[0].pie(expense, labels=expense.index, autopct='%1.1f%%', colors=CHART_PALETTE)
            axs[0].set_title(f"{month} {_('支出分类')}", fontsize=14, loc='left', color=TEXT)
        except Exception as e:
            axs[0].text(0.5, 0.5, _t('绘图错误: {e}').format(e=e), ha='center', va='center', color=TEXT_MUTED)
    else:
        axs[0].text(0.5, 0.5, _('无支出数据'), ha='center', va='center', color=TEXT_MUTED)
    # 收入分类
    income = month_df[month_df['类型'] == '收入'].groupby('分类')['金额'].sum()
    if not income.empty and income.sum() > 0:
        try:
            axs[1].pie(income, labels=income.index, autopct='%1.1f%%', colors=CHART_PALETTE)
            axs[1].set_title(f"{month} {_('收入分类')}", fontsize=14, loc='left', color=TEXT)
        except Exception as e:
            axs[1].text(0.5, 0.5, _t('绘图错误: {e}').format(e=e), ha='center', va='center', color=TEXT_MUTED)
    else:
        axs[1].text(0.5, 0.5, _('无收入数据'), ha='center', va='center', color=TEXT_MUTED)
    plt.tight_layout()
    win._pie_fig = fig  # 保存引用，供切换月份时关闭旧图、窗口销毁时释放
    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
    # 窗口销毁时关闭当前 figure，防止泄漏
    def _on_pie_win_destroy(event, _win=win):
        fig = getattr(_win, '_pie_fig', None)
        if fig is not None:
            plt.close(fig)
            _win._pie_fig = None
    if not getattr(win, '_pie_destroy_bound', False):
        win.bind('<Destroy>', _on_pie_win_destroy)
        win._pie_destroy_bound = True
    # 底部左右按钮
    nav_frame = ttk.Frame(win)
    nav_frame.pack(fill='x', pady=8)
    months = sorted(df['年月'].unique())
    idx = months.index(month)
    btn_prev = ttk.Button(nav_frame, text=_('← 上一月'), command=lambda: draw_pie(months[idx-1], df, master, win))
    btn_prev.pack(side='left', padx=15, ipadx=12, ipady=4)
    btn_next = ttk.Button(nav_frame, text=_('下一月 →'), command=lambda: draw_pie(months[idx+1], df, master, win))
    btn_next.pack(side='right', padx=15, ipadx=12, ipady=4)
    if idx == 0:
        btn_prev.state(['disabled'])
    if idx == len(months)-1:
        btn_next.state(['disabled'])


def show_pie(selected_month, df, master, sel_win):
    sel_win.destroy()
    draw_pie(selected_month, df, master)
