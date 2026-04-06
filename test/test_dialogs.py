"""
测试 ui/dialogs.py 中的对话框类
关键：必须在导入 ui.dialogs 之前 mock tkinter，否则导入时会初始化真实 Tkinter
"""
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch, ANY


def create_mock_tkinter():
    """创建可以安全继承的 tkinter mock"""
    
    # 创建 mock messagebox 子模块
    mock_messagebox = MagicMock()
    
    # 创建 DummyToplevel 类，可以被安全地继承
    class DummyToplevel:
        def __init__(self, master=None, **kwargs):
            self.master = master
            self.tk = MagicMock()
            self._children = []
            self._title = ''
            self._geometry = ''
        
        def title(self, title=None):
            if title is not None:
                self._title = title
            return self._title
        
        def geometry(self, geom=None):
            if geom is not None:
                self._geometry = geom
            return self._geometry
        
        def resizable(self, width=None, height=None):
            pass
        
        def transient(self, master=None):
            pass
        
        def grab_set(self):
            pass
        
        def destroy(self):
            pass
        
        def winfo_children(self):
            return self._children
        
        def grid(self, **kwargs):
            pass
        
        def pack(self, **kwargs):
            pass
        
        def bind(self, event, callback, add=None):
            pass
        
        def focus_get(self):
            return None
    
    # 创建 mock tkinter 模块
    mock_tk = MagicMock()
    mock_tk.Toplevel = DummyToplevel
    mock_tk.StringVar = MagicMock
    mock_tk.Label = MagicMock
    mock_tk.DoubleVar = MagicMock
    mock_tk.Frame = MagicMock
    mock_tk.messagebox = mock_messagebox  # 添加 messagebox 作为 tkinter 的子模块
    
    # 重要：将 messagebox 也添加到 sys.modules 中，这样 from tkinter import messagebox 会使用这个 mock
    import sys
    sys.modules['tkinter.messagebox'] = mock_messagebox
    
    return mock_tk, mock_messagebox


@pytest.fixture
def mock_dialogs():
    """在导入 ui.dialogs 之前完成所有 mock"""
    import importlib
    import sys
    
    # 如果 dialogs 模块及其相关模块已经被导入，先移除它们
    modules_to_remove = [k for k in sys.modules.keys() if k == 'ui.dialogs' or k.startswith('ui.dialogs.')]
    for mod in modules_to_remove:
        del sys.modules[mod]
    
    mock_tk, mock_msg = create_mock_tkinter()
    mock_ttk = MagicMock()
    mock_tkcalendar = MagicMock()
    
    with patch.dict('sys.modules', {
        'tkinter': mock_tk,
        'tkinter.ttk': mock_ttk,
        'tkinter.messagebox': mock_msg,
        'tkcalendar': mock_tkcalendar,
    }):
        # 现在导入 dialogs
        from ui import dialogs
        # 验证 messagebox 是否正确 mock
        assert hasattr(dialogs, 'messagebox')
        yield dialogs, mock_tk, mock_ttk, mock_msg, mock_tkcalendar


class TestFilterDialog:
    """测试筛选对话框"""
    
    def test_filter_dialog_init(self, mock_dialogs):
        """测试筛选对话框初始化"""
        dialogs, mock_tk, mock_ttk, mock_msg, mock_tkcalendar = mock_dialogs
        
        mock_master = MagicMock()
        mock_font = MagicMock()
        
        mock_tkcalendar.DateEntry = MagicMock()
        
        # 创建对话框
        filter_dict = {'start': '2025-01-01', 'end': '2025-12-31', 'type': '支出'}
        dialog = dialogs.FilterDialog(mock_master, filter_dict, mock_font)
        
        # 验证窗口属性设置
        assert hasattr(dialog, 'result')
        
    def test_filter_dialog_on_ok(self, mock_dialogs):
        """测试筛选对话框确认操作"""
        dialogs, mock_tk, mock_ttk, mock_msg, mock_tkcalendar = mock_dialogs
        
        mock_master = MagicMock()
        mock_font = MagicMock()
        
        mock_tkcalendar.DateEntry = MagicMock()
        
        # 设置模拟值
        dialog = dialogs.FilterDialog(mock_master, {}, mock_font)
        dialog.start_var = MagicMock()
        dialog.start_var.get.return_value = '2025-01-01'
        dialog.end_var = MagicMock()
        dialog.end_var.get.return_value = '2025-12-31'
        dialog.min_amt_var = MagicMock()
        dialog.min_amt_var.get.return_value = '100'
        dialog.max_amt_var = MagicMock()
        dialog.max_amt_var.get.return_value = '1000'
        dialog.type_var = MagicMock()
        dialog.type_var.get.return_value = '支出'
        dialog.cat_var = MagicMock()
        dialog.cat_var.get.return_value = '餐饮'
        dialog.destroy = MagicMock()
        
        # 调用 on_ok
        dialog.on_ok()
        
        # 验证结果
        assert dialog.result is not None
        assert dialog.result['start'] == '2025-01-01'
        assert dialog.result['end'] == '2025-12-31'
        assert dialog.result['min_amt'] == '100'
        assert dialog.result['max_amt'] == '1000'
        assert dialog.result['type'] == '支出'
        assert dialog.result['cat'] == '餐饮'

    def test_filter_dialog_on_clear(self, mock_dialogs):
        """测试筛选对话框清除操作"""
        dialogs, mock_tk, mock_ttk, mock_msg, mock_tkcalendar = mock_dialogs
        
        mock_master = MagicMock()
        mock_font = MagicMock()
        mock_tkcalendar.DateEntry = MagicMock()
        
        dialog = dialogs.FilterDialog(mock_master, {}, mock_font)
        dialog.destroy = MagicMock()
        
        # 调用 on_clear
        dialog.on_clear()
        
        # 验证结果为清除标记
        assert dialog.result == '__clear__'


class TestEditRecordDialog:
    """测试编辑对话框"""
    
    def test_edit_dialog_init(self, mock_dialogs):
        """测试编辑对话框初始化"""
        dialogs, mock_tk, mock_ttk, mock_msg, mock_tkcalendar = mock_dialogs
        
        mock_master = MagicMock()
        mock_font = MagicMock()
        
        record = {
            '日期': '2025-01-01',
            '类型': '支出',
            '分类': '餐饮',
            '金额': '50.00',
            '备注': '午餐'
        }
        
        dialog = dialogs.EditRecordDialog(mock_master, record, mock_font)
        
        # 验证窗口创建和属性
        assert hasattr(dialog, 'result')
        assert hasattr(dialog, 'vars')

    def test_edit_dialog_on_ok_valid(self, mock_dialogs):
        """测试编辑对话框确认 - 有效金额"""
        dialogs, mock_tk, mock_ttk, mock_msg, mock_tkcalendar = mock_dialogs
        
        mock_master = MagicMock()
        mock_font = MagicMock()
        
        dialog = dialogs.EditRecordDialog(mock_master, {}, mock_font)
        
        # 创建模拟的 StringVar
        vars_dict = {
            '日期': MagicMock(get=lambda: '2025-01-01'),
            '类型': MagicMock(get=lambda: '支出'),
            '分类': MagicMock(get=lambda: '餐饮'),
            '金额': MagicMock(get=lambda: '100.50'),
            '备注': MagicMock(get=lambda: '晚餐'),
        }
        dialog.vars = vars_dict
        dialog.result = None
        dialog.destroy = MagicMock()
        
        dialog.on_ok()
        
        # 验证结果
        assert dialog.result is not None
        assert dialog.result['金额'] == '100.50'

    def test_edit_dialog_on_ok_invalid_amount(self, mock_dialogs):
        """测试编辑对话框确认 - 无效金额"""
        dialogs, mock_tk, mock_ttk, mock_msg, mock_tkcalendar = mock_dialogs
        
        mock_master = MagicMock()
        mock_font = MagicMock()
        
        dialog = dialogs.EditRecordDialog(mock_master, {}, mock_font)
        
        vars_dict = {
            '日期': MagicMock(get=lambda: '2025-01-01'),
            '类型': MagicMock(get=lambda: '支出'),
            '分类': MagicMock(get=lambda: '餐饮'),
            '金额': MagicMock(get=lambda: 'invalid'),  # 无效金额
            '备注': MagicMock(get=lambda: '晚餐'),
        }
        dialog.vars = vars_dict
        dialog.result = None
        
        dialog.on_ok()
        
        # 验证显示错误提示（使用 dialogs.messagebox 来检查调用）
        dialogs.messagebox.showerror.assert_called_once()
        assert dialog.result is None  # 结果应为空


class TestImportMappingDialog:
    """测试导入映射对话框"""
    
    def test_import_mapping_dialog(self, mock_dialogs):
        """测试导入映射对话框"""
        dialogs, mock_tk, mock_ttk, mock_msg, mock_tkcalendar = mock_dialogs
        
        mock_master = MagicMock()
        mock_font = MagicMock()
        
        columns = ['日期', '类型', '分类', '金额', '备注']
        default_map = {'日期': '日期', '类型': '类型'}
        
        dialog = dialogs.ImportMappingDialog(mock_master, columns, default_map, mock_font)
        
        # 验证窗口创建
        assert hasattr(dialog, 'result')
        assert hasattr(dialog, 'vars')


class TestPreviewDialog:
    """测试预览对话框"""
    
    def test_preview_dialog_init(self, mock_dialogs):
        """测试预览对话框初始化"""
        dialogs, mock_tk, mock_ttk, mock_msg, mock_tkcalendar = mock_dialogs
        
        mock_master = MagicMock()
        mock_font = MagicMock()
        
        # 创建测试数据
        data = pd.DataFrame([
            {"日期": "2025-01-01", "类型": "支出", "分类": "餐饮", "金额": 50.0, "备注": "午餐"},
            {"日期": "2025-01-02", "类型": "支出", "分类": "交通", "金额": 20.0, "备注": "地铁"},
        ])
        
        dialog = dialogs.PreviewDialog(mock_master, data, mock_font)
        
        # 验证数据副本已创建
        assert hasattr(dialog, 'data')
        assert hasattr(dialog, '_sort_state')

    def test_preview_dialog_on_confirm(self, mock_dialogs):
        """测试预览对话框确认"""
        dialogs, mock_tk, mock_ttk, mock_msg, mock_tkcalendar = mock_dialogs
        
        mock_master = MagicMock()
        mock_font = MagicMock()
        
        data = pd.DataFrame([
            {"日期": "2025-01-01", "类型": "支出", "分类": "餐饮", "金额": 50.0, "备注": "午餐"},
        ])
        
        dialog = dialogs.PreviewDialog(mock_master, data, mock_font)
        dialog.destroy = MagicMock()
        dialog.on_confirm()
        
        assert dialog.result is True
        dialog.destroy.assert_called_once()

    def test_preview_dialog_on_cancel(self, mock_dialogs):
        """测试预览对话框取消"""
        dialogs, mock_tk, mock_ttk, mock_msg, mock_tkcalendar = mock_dialogs
        
        mock_master = MagicMock()
        mock_font = MagicMock()
        
        data = pd.DataFrame([
            {"日期": "2025-01-01", "类型": "支出", "分类": "餐饮", "金额": 50.0, "备注": "午餐"},
        ])
        
        dialog = dialogs.PreviewDialog(mock_master, data, mock_font)
        dialog.destroy = MagicMock()
        dialog.on_cancel()
        
        assert dialog.result is False
        dialog.destroy.assert_called_once()
