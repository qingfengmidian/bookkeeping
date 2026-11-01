"""界面语言支持：数据层（数据库字段、收支类型、分类）保持中文不变，仅翻译界面文案。

用法：from utils.i18n import _
     _('筛选账单')  # 英文模式下返回 'Filter Bills'，中文模式下原样返回
带变量的文案使用命名占位符模板：_t('已导入 {n} 条记录').format(n=5)
"""
import os

_LANG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'i18n.lang')

_current = None

EN = {
    # 主窗口标题与菜单
    '记账本': 'Bookkeeping',
    '文件': 'File',
    '新建': 'New',
    '打开': 'Open',
    '保存': 'Save',
    '另存为': 'Save As',
    '退出': 'Exit',
    '导入': 'Import',
    '导入支付宝账单': 'Import Alipay Bill',
    '导入微信账单': 'Import WeChat Bill',
    '导出': 'Export',
    '筛选': 'Filter',
    '筛选账单': 'Filter Bills',
    '统计': 'Statistics',
    '月度账单': 'Monthly Bill',
    '统计图表': 'Charts',
    '月度收支柱状图': 'Monthly Income/Expense Bar Chart',
    '每月收支柱状图': 'Monthly Income/Expense Bar Chart',
    '单月收支饼状图': 'Single Month Pie Chart',
    '语言': 'Language',
    '设置': 'Settings',
    '菜单字号': 'Menu Font Size',
    '界面字号': 'UI Font Size',
    '跟随界面': 'Follow UI',
    '默认': 'Default',
    # 通用对话框
    '无数据': 'No Data',
    '没有可统计的账单数据。': 'No bill data to analyze.',
    '没有可展示的账单数据。': 'No bill data to display.',
    '没有可删除的账单。': 'No bills to delete.',
    '无支出数据': 'No expense data',
    '无收入数据': 'No income data',
    '暂无数据': 'No data yet',
    '未保存更改': 'Unsaved Changes',
    '当前数据尚未保存，是否先保存？': 'You have unsaved changes. Save first?',
    '当前数据尚未保存，是否保存后退出？': 'You have unsaved changes. Save before exiting?',
    '输入错误': 'Input Error',
    '金额必须为数字': 'Amount must be a number',
    '请填写完整信息': 'Please fill in all required fields',
    '文件错误': 'File Error',
    '选择的文件不存在': 'The selected file does not exist',
    '编码错误': 'Encoding Error',
    '文件编码错误，请尝试使用UTF-8编码保存文件': 'Invalid file encoding. Please save the file as UTF-8.',
    '文件编码错误，支付宝账单通常使用GBK编码': 'Invalid encoding. Alipay bills usually use GBK encoding.',
    '空文件': 'Empty File',
    '选择的文件没有数据': 'The selected file has no data',
    '解析错误': 'Parse Error',
    '读取失败': 'Read Failed',
    '无法读取文件: ': 'Unable to read file: ',
    '无法读取Excel文件: ': 'Unable to read Excel file: ',
    '格式错误': 'Format Error',
    'Excel格式错误或缺少必要列: ': 'Invalid Excel format or missing required columns: ',
    '保存成功': 'Save Successful',
    '数据已成功保存！': 'Data saved successfully!',
    '保存失败': 'Save Failed',
    '数据库错误: ': 'Database error: ',
    '保存过程中发生错误: ': 'An error occurred while saving: ',
    '另存为成功': 'Save As Successful',
    '打开失败': 'Open Failed',
    '无法打开数据库：': 'Unable to open database: ',
    '打开成功': 'Open Successful',
    '已打开数据库：': 'Opened database: ',
    '新建成功': 'Created',
    '已创建新的数据库：': 'Created new database: ',
    '初始化数据库': 'Initialize Database',
    '添加成功': 'Added',
    '账单添加成功！': 'Bill added successfully!',
    '添加失败': 'Add Failed',
    '账单添加失败：': 'Failed to add bill: ',
    '添加': 'Add',
    '删除成功': 'Deleted',
    '删除选中账单': 'Delete Selected',
    '删除全部': 'Delete All',
    '未选中': 'Nothing Selected',
    '请先选中要删除的账单': 'Please select bills to delete first',
    '确认删除': 'Confirm Deletion',
    '此操作不可撤销。': 'This cannot be undone.',
    '确认删除全部': 'Confirm Delete All',
    '导出成功': 'Export Successful',
    '取消导入': 'Import Cancelled',
    '已取消导入操作': 'Import operation cancelled.',
    '导入成功': 'Import Successful',
    '导入失败': 'Import Failed',
    '映射错误': 'Mapping Error',
    '请为所有字段选择对应的列': 'Please select a column for every field',
    '筛选错误': 'Filter Error',
    '最小金额必须为数字': 'Min amount must be a number',
    '最大金额必须为数字': 'Max amount must be a number',
    '全部': 'All',
    # 输入区与表格
    '日期:': 'Date:',
    '类型:': 'Type:',
    '分类:': 'Category:',
    '金额:': 'Amount:',
    '备注:': 'Note:',
    '总收入': 'Total Income',
    '总支出': 'Total Expense',
    '收支明细': 'Bills Detail',
    '月份': 'Month',
    '收入': 'Income',
    '支出': 'Expense',
    # 文件对话框
    '选择CSV文件': 'Select CSV File',
    'CSV文件': 'CSV File',
    '选择支付宝账单CSV文件': 'Select Alipay Bill CSV',
    '选择微信账单Excel文件': 'Select WeChat Bill Excel',
    'Excel文件': 'Excel File',
    'SQLite数据库': 'SQLite Database',
    '打开账单数据库': 'Open Bill Database',
    # 图表
    '图表统计': 'Chart Statistics',
    '收支趋势': 'Income & Expense Trend',
    '分类统计': 'Category Statistics',
    '每日收支趋势': 'Daily Income & Expense Trend',
    '金额': 'Amount',
    '支出分类': 'Expense by Category',
    '收入分类': 'Income by Category',
    '每月收入与支出变化': 'Monthly Income & Expense',
    '选择月份': 'Select Month',
    '请选择月份：': 'Please select a month:',
    '收支分类饼状图': 'Income & Expense Pie',
    '绘图错误: ': 'Plot error: ',
    '← 上一月': '← Prev',
    '下一月 →': 'Next →',
    # 筛选/编辑/导入对话框
    '编辑账单': 'Edit Bill',
    '起始日期': 'Start Date',
    '结束日期': 'End Date',
    '最小金额': 'Min Amount',
    '最大金额': 'Max Amount',
    '类型': 'Type',
    '分类': 'Category',
    '清除筛选': 'Clear Filters',
    '应用筛选': 'Apply Filter',
    '保存': 'Save',
    '选择导入列对应关系': 'Map Import Columns',
    '确定': 'OK',
    '导入数据预览': 'Import Preview',
    '即将导入的数据预览（显示前10行）：': 'Preview of data to import (first 10 rows):',
    '确认导入': 'Confirm Import',
    '取消': 'Cancel',
    # 数据列显示名（内部数据仍使用中文字段名）
    '日期': 'Date',
    '备注': 'Note',
}

# 带变量的文案模板
EN_TEMPLATES = {
    '已导入 {n} 条记录': 'Imported {n} records',
    '已从{source}导入 {n} 条记录': 'Imported {n} records from {source}',
    '确定要删除选中的 {n} 条账单吗？': 'Delete the selected {n} bill(s)?',
    '确定要删除全部账单吗？': 'Delete all bills?',
    '已删除 {n} 条账单': 'Deleted {n} bill(s)',
    '已删除全部账单': 'All bills deleted',
    '将在以下位置新建数据库文件：\n{path}': 'A new database file will be created at:\n{path}',
    '数据已另存为 {path}': 'Data saved as {path}',
    '数据已导出到 {path}': 'Data exported to {path}',
    '总记录数: {n}': 'Total records: {n}',
    '当前数据库: {path}': 'Current DB: {path}',
    '导入过程中发生错误: {e}': 'Error during import: {e}',
    'CSV解析失败: {e}': 'Failed to parse CSV: {e}',
    'CSV解析失败，请确认是支付宝账单格式: {e}': 'Failed to parse CSV. Please confirm Alipay bill format: {e}',
}

_REV = {v: k for k, v in EN.items()}


def get_lang():
    """当前语言：'zh' 或 'en'，首次调用时从配置文件读取"""
    global _current
    if _current is not None:
        return _current
    lang = 'zh'
    try:
        if os.path.exists(_LANG_FILE):
            with open(_LANG_FILE, 'r', encoding='utf-8') as f:
                lang = f.read().strip() or 'zh'
    except Exception:
        pass
    _current = lang
    return lang


def set_lang(lang):
    """切换语言并持久化到配置文件"""
    global _current
    _current = lang
    try:
        os.makedirs(os.path.dirname(_LANG_FILE), exist_ok=True)
        with open(_LANG_FILE, 'w', encoding='utf-8') as f:
            f.write(lang)
    except Exception:
        pass


def _(text):
    """翻译界面文案：英文模式查表，中文模式或缺失时原样返回"""
    if get_lang() == 'en':
        return EN.get(text, text)
    return text


def _t(template):
    """取带命名占位符的文案模板，调用处自行 .format(...)"""
    if get_lang() == 'en':
        return EN_TEMPLATES.get(template, template)
    return template


def to_zh(text):
    """把英文界面值映射回内部中文值（用于筛选对话框下拉框等）"""
    if get_lang() != 'en':
        return text
    return _REV.get(text, text)
