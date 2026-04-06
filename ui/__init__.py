"""
UI 模块

提供图形界面组件，包括主窗口、对话框和图表。

注意：此模块中的组件涉及 GUI 初始化，请根据需要使用显式导入：
    from ui.main_window import RecordBook
    from ui.dialogs import FilterDialog
    from ui.charts import show_monthly_chart
"""

# 由于 GUI 组件依赖 tkinter 和 matplotlib，不在 __init__.py 中自动导入
# 请使用显式导入以避免在测试/mock 环境中触发真实 GUI 初始化
