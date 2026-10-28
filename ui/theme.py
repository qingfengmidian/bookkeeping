"""
界面主题模块

集中定义设计稿《界面美化设计方案》中的配色系统与跨平台字体栈，
并通过 apply_theme(root) 基于 ttk/clam 主题统一配置全局样式，
避免色值与 style.configure 散落在各窗口代码中。

配色与组件规格对应设计稿第二、三、四节；
色板经评审调整为暖纸陶土系（原冷蓝系弃用）。
"""

import tkinter as tk
from tkinter import ttk, font as tkfont

# ===== 配色系统（暖纸陶土系） =====
BG = '#FAF9F6'            # 窗口主背景（米白暖底）
BG_SUBTLE = '#EFEBE3'     # 输入区/统计区背景（明显暖一档，与主背景拉开对比）
BORDER = '#D8D3C7'        # 输入框、表格描边（可见的暖灰发丝线）
TEXT = '#1C1B1A'          # 主文字（暖墨黑）
TEXT_MUTED = '#8C8880'    # 次要文字（表头、提示、数据库路径）
ACCENT = '#1C1B1A'        # 墨色：输入框聚焦边框等强调用途；全界面不使用红/橙
ACCENT_HOVER = '#44403A'  # 墨色悬停层级（备用）
INCOME = '#4D7C0F'        # 收入金额（橄榄绿）
EXPENSE = '#1C1B1A'       # 支出金额（墨色，与主文字一致；表格/图表不用红色）
TOTAL_EXPENSE = '#B91C1C' # 统计栏"总支出"大数字专用砖红（记账惯例，红绿对应）
ROW_STRIPE = '#F1EEE6'    # 表格斑马行（可见的暖米间隔）
ROW_SELECTED = '#E7E2D6'  # 表格选中行（暖灰米，中性无彩色）

# 跨平台字体栈（设计稿第三节，替代写死的"微软雅黑"）
FONT_FAMILY = ['Helvetica Neue', 'PingFang SC', 'Microsoft YaHei', 'Microsoft YaHei UI', '微软雅黑', 'Noto Sans CJK SC', 'sans-serif']


def pick_font_family():
    """从字体栈中选出第一个当前系统可用的字体族名，全部不可用时兜底 'sans-serif'"""
    try:
        available = tkfont.families()
    except Exception:
        return 'sans-serif'
    for family in FONT_FAMILY:
        if family in available:
            return family
    return 'sans-serif'


def configure_text_button(root, style_name, foreground, background=BG):
    """配置无边框文字按钮样式，前景色参数化（用于删除类弱化的操作按钮）

    设计稿 4.1-3：无边框、无底色、悬停加底色，弱化误触。
    """
    style = ttk.Style(root)
    style.configure(style_name,
                    foreground=foreground,
                    background=background,
                    borderwidth=0,
                    relief='flat',
                    padding=(6, 4),
                    font=(pick_font_family(), 11))
    style.map(style_name,
              foreground=[('active', foreground), ('pressed', foreground)],
              background=[('active', BG_SUBTLE), ('pressed', BG_SUBTLE)])


def apply_theme(root):
    """将极简主题应用到给定根窗口（clam 是唯一可深度定制的内置 ttk 主题）"""
    family = pick_font_family()
    body_font = (family, 13)    # BODY 层级
    caption_font = (family, 11)  # CAPTION 层级（表头、说明）

    style = ttk.Style(root)
    style.theme_use('clam')

    # 基础容器与文字：TFrame/TLabel 背景 BG、文字 TEXT
    style.configure('TFrame', background=BG)
    style.configure('TLabel', background=BG, foreground=TEXT)

    # 低一档明度的分区背景，用于输入区/统计区（无描边，靠明度差分区）
    style.configure('Subtle.TFrame', background=BG_SUBTLE)
    style.configure('Subtle.TLabel', background=BG_SUBTLE, foreground=TEXT)

    # 输入控件：白底、BORDER 边框、聚焦时 ACCENT（clam 可用的 fieldbackground/bordercolor/focuscolor）
    style.configure('TEntry', fieldbackground=BG, bordercolor=BORDER, focuscolor=ACCENT)
    style.configure('TCombobox', fieldbackground=BG, bordercolor=BORDER, focuscolor=ACCENT, arrowcolor=TEXT_MUTED)

    # 主按钮：白底、细墨边、墨字（悬停铺暖底色）——低调清晰，不用沉重的实心黑块
    style.configure('Accent.TButton',
                    background=BG,
                    foreground=TEXT,
                    bordercolor=TEXT,
                    borderwidth=1,
                    relief='flat',
                    padding=(16, 8),
                    font=body_font)
    style.map('Accent.TButton',
              background=[('active', BG_SUBTLE), ('pressed', BG_SUBTLE)],
              foreground=[('active', TEXT), ('pressed', TEXT)])

    # 文字按钮：无边框无背景，前景色参数化（删除选中=EXPENSE、删除全部=TEXT_MUTED）
    configure_text_button(root, 'DangerText.TButton', EXPENSE)
    configure_text_button(root, 'MutedText.TButton', TEXT_MUTED)

    # 表格：白底、行高 32；clam 下选中色需经 style.map 的 selected 状态生效
    style.configure('Treeview',
                    background=BG,
                    fieldbackground=BG,
                    bordercolor=BORDER,
                    borderwidth=1,
                    rowheight=32,
                    font=body_font,
                    selectbackground=ROW_SELECTED,
                    selectforeground=TEXT)
    style.map('Treeview',
              background=[('selected', ROW_SELECTED)],
              selectbackground=[('selected', ROW_SELECTED)],
              selectforeground=[('selected', TEXT)])
    # 表头：CAPTION 11px、TEXT_MUTED、无边框（排序功能由 main_window 表头命令实现）
    style.configure('Treeview.Heading',
                    background=BG,
                    foreground=TEXT_MUTED,
                    font=caption_font,
                    relief='flat',
                    borderwidth=0,
                    padding=(6, 4))
