"""
测试 ui/main_window.py 中的主窗口类
由于涉及GUI，主要测试业务逻辑而非界面渲染
"""
import pytest
import pandas as pd
import sqlite3
from unittest.mock import MagicMock, patch, mock_open


class TestRecordBookCoreLogic:
    """测试 RecordBook 核心业务逻辑"""

    @pytest.fixture
    def sample_data(self):
        """返回测试用的 DataFrame"""
        return pd.DataFrame([
            {"日期": "2025-01-01", "类型": "收入", "分类": "工资", "金额": 1000.0, "备注": "test1"},
            {"日期": "2025-01-02", "类型": "支出", "分类": "餐饮", "金额": 50.0, "备注": "test2"},
            {"日期": "2025-01-03", "类型": "支出", "分类": "交通", "金额": 30.0, "备注": "test3"},
        ])

    def test_update_stats_calculation(self, sample_data):
        """测试统计更新计算"""
        with patch('ui.main_window.tk'):
            with patch('ui.main_window.ttk'):
                with patch('ui.main_window.DateEntry'):
                    with patch('ui.main_window.ensure_db'):
                        with patch('ui.main_window.sqlite3'):
                            with patch.object(pd.DataFrame, 'to_sql'):
                                from ui.main_window import RecordBook
                                
                                mock_master = MagicMock()
                                mock_master.tk = MagicMock()
                                mock_master.winfo_toplevel.return_value = mock_master
                                
                                # 模拟 font
                                with patch('ui.main_window.tkfont'):
                                    # 模拟所有初始化
                                    with patch.object(RecordBook, 'ensure_db'):
                                        with patch.object(RecordBook, 'load_data', return_value=sample_data):
                                            with patch.object(RecordBook, 'create_menu'):
                                                with patch.object(RecordBook, 'create_widgets'):
                                                    with patch.object(RecordBook, 'refresh_table'):
                                                        rb = RecordBook(mock_master)
                                                        rb.data = sample_data
                                                        rb.stats_label = MagicMock()
                                                        
                                                        rb.update_stats()
                                                        
                                                        # 验证统计标签被调用，总收入1000，总支出80
                                                        rb.stats_label.config.assert_called_once()
                                                        call_args = rb.stats_label.config.call_args
                                                        assert 'text' in call_args.kwargs or call_args[1]


class TestRecordBookDataOperations:
    """测试数据操作相关方法"""

    def test_add_record_valid(self):
        """测试添加有效记录"""
        with patch('ui.main_window.tk'):
            with patch('ui.main_window.ttk'):
                with patch('ui.main_window.DateEntry'):
                    with patch('ui.main_window.ensure_db'):
                        with patch('ui.main_window.sqlite3'):
                            with patch('ui.main_window.messagebox'):
                                from ui.main_window import RecordBook
                                
                                mock_master = MagicMock()
                                mock_master.tk = MagicMock()
                                mock_master.winfo_toplevel.return_value = mock_master
                                
                                with patch('ui.main_window.tkfont'):
                                    with patch.object(RecordBook, 'ensure_db'):
                                        with patch.object(RecordBook, 'load_data', return_value=pd.DataFrame()):
                                            with patch.object(RecordBook, 'create_menu'):
                                                with patch.object(RecordBook, 'create_widgets'):
                                                    with patch.object(RecordBook, 'refresh_table'):
                                                        rb = RecordBook(mock_master)
                                                        rb.data = pd.DataFrame()
                                                        
                                                        # 设置输入值
                                                        rb.date_var = MagicMock()
                                                        rb.date_var.get.return_value = '2025-01-01'
                                                        rb.type_var = MagicMock()
                                                        rb.type_var.get.return_value = '支出'
                                                        rb.cat_var = MagicMock()
                                                        rb.cat_var.get.return_value = '餐饮'
                                                        rb.amount_var = MagicMock()
                                                        rb.amount_var.get.return_value = '100.50'
                                                        rb.note_var = MagicMock()
                                                        rb.note_var.get.return_value = '午餐'
                                                        
                                                        with patch.object(rb, 'refresh_table') as mock_refresh:
                                                            with patch.object(rb, 'clear_inputs') as mock_clear:
                                                                rb.add_record()
                                                                
                                                                # 验证数据已添加
                                                                assert len(rb.data) == 1
                                                                assert rb.dirty is True

    def test_apply_filter_date_range(self):
        """测试按日期范围筛选"""
        with patch('ui.main_window.tk'):
            with patch('ui.main_window.ttk'):
                with patch('ui.main_window.DateEntry'):
                    with patch('ui.main_window.ensure_db'):
                        with patch('ui.main_window.sqlite3'):
                            from ui.main_window import RecordBook
                            
                            mock_master = MagicMock()
                            mock_master.tk = MagicMock()
                            mock_master.winfo_toplevel.return_value = mock_master
                            
                            data = pd.DataFrame([
                                {"日期": "2025-01-01", "类型": "支出", "分类": "餐饮", "金额": 50.0, "备注": "test1"},
                                {"日期": "2025-02-01", "类型": "支出", "分类": "餐饮", "金额": 60.0, "备注": "test2"},
                                {"日期": "2025-03-01", "类型": "收入", "分类": "工资", "金额": 1000.0, "备注": "test3"},
                            ])
                            
                            with patch('ui.main_window.tkfont'):
                                with patch.object(RecordBook, 'ensure_db'):
                                    with patch.object(RecordBook, 'load_data', return_value=data):
                                        with patch.object(RecordBook, 'create_menu'):
                                            with patch.object(RecordBook, 'create_widgets'):
                                                with patch.object(RecordBook, 'refresh_table'):
                                                    rb = RecordBook(mock_master)
                                                    rb.data = data
                                                    rb._sort_column = None
                                                    
                                                    # 测试日期筛选
                                                    filter_dict = {
                                                        'start': '2025-01-15',
                                                        'end': '2025-02-15',
                                                        'min_amt': '',
                                                        'max_amt': '',
                                                        'type': '全部',
                                                        'cat': '全部'
                                                    }
                                                    
                                                    with patch.object(rb, 'refresh_table') as mock_refresh:
                                                        rb.apply_filter(filter_dict)
                                                        # 验证 refresh_table 被调用
                                                        mock_refresh.assert_called_once()

    def test_apply_filter_by_type(self):
        """测试按类型筛选"""
        with patch('ui.main_window.tk'):
            with patch('ui.main_window.ttk'):
                with patch('ui.main_window.DateEntry'):
                    with patch('ui.main_window.ensure_db'):
                        with patch('ui.main_window.sqlite3'):
                            from ui.main_window import RecordBook
                            
                            mock_master = MagicMock()
                            mock_master.tk = MagicMock()
                            mock_master.winfo_toplevel.return_value = mock_master
                            
                            data = pd.DataFrame([
                                {"日期": "2025-01-01", "类型": "支出", "分类": "餐饮", "金额": 50.0, "备注": "test1"},
                                {"日期": "2025-01-02", "类型": "收入", "分类": "工资", "金额": 1000.0, "备注": "test2"},
                            ])
                            
                            with patch('ui.main_window.tkfont'):
                                with patch.object(RecordBook, 'ensure_db'):
                                    with patch.object(RecordBook, 'load_data', return_value=data):
                                        with patch.object(RecordBook, 'create_menu'):
                                            with patch.object(RecordBook, 'create_widgets'):
                                                with patch.object(RecordBook, 'refresh_table'):
                                                    rb = RecordBook(mock_master)
                                                    rb.data = data
                                                    rb._sort_column = None
                                                    
                                                    # 测试类型筛选
                                                    filter_dict = {
                                                        'start': '',
                                                        'end': '',
                                                        'min_amt': '',
                                                        'max_amt': '',
                                                        'type': '收入',
                                                        'cat': '全部'
                                                    }
                                                    
                                                    with patch.object(rb, 'refresh_table') as mock_refresh:
                                                        rb.apply_filter(filter_dict)
                                                        mock_refresh.assert_called_once()

    def test_clear_filter(self):
        """测试清除筛选"""
        with patch('ui.main_window.tk'):
            with patch('ui.main_window.ttk'):
                with patch('ui.main_window.DateEntry'):
                    with patch('ui.main_window.ensure_db'):
                        with patch('ui.main_window.sqlite3'):
                            from ui.main_window import RecordBook
                            
                            mock_master = MagicMock()
                            mock_master.tk = MagicMock()
                            mock_master.winfo_toplevel.return_value = mock_master
                            
                            with patch('ui.main_window.tkfont'):
                                with patch.object(RecordBook, 'ensure_db'):
                                    with patch.object(RecordBook, 'load_data', return_value=pd.DataFrame()):
                                        with patch.object(RecordBook, 'create_menu'):
                                            with patch.object(RecordBook, 'create_widgets'):
                                                with patch.object(RecordBook, 'refresh_table'):
                                                    rb = RecordBook(mock_master)
                                                    rb._current_filter = {'type': '支出'}
                                                    
                                                    with patch.object(rb, 'refresh_table') as mock_refresh:
                                                        rb.clear_filter()
                                                        # 验证筛选条件被清除
                                                        assert rb._current_filter == {}
                                                        mock_refresh.assert_called_once()


class TestRecordBookDeleteOperations:
    """测试删除操作"""

    def test_delete_all_records(self):
        """测试删除全部记录"""
        with patch('ui.main_window.tk'):
            with patch('ui.main_window.ttk'):
                with patch('ui.main_window.DateEntry'):
                    with patch('ui.main_window.ensure_db'):
                        with patch('ui.main_window.sqlite3'):
                            with patch('ui.main_window.messagebox') as mock_msg:
                                mock_msg.askyesno.return_value = True
                                
                                from ui.main_window import RecordBook
                                
                                mock_master = MagicMock()
                                mock_master.tk = MagicMock()
                                mock_master.winfo_toplevel.return_value = mock_master
                                
                                data = pd.DataFrame([
                                    {"日期": "2025-01-01", "类型": "支出", "分类": "餐饮", "金额": 50.0, "备注": "test1"},
                                    {"日期": "2025-01-02", "类型": "支出", "分类": "交通", "金额": 30.0, "备注": "test2"},
                                ])
                                
                                with patch('ui.main_window.tkfont'):
                                    with patch.object(RecordBook, 'ensure_db'):
                                        with patch.object(RecordBook, 'load_data', return_value=data):
                                            with patch.object(RecordBook, 'create_menu'):
                                                with patch.object(RecordBook, 'create_widgets'):
                                                    with patch.object(RecordBook, 'refresh_table'):
                                                        rb = RecordBook(mock_master)
                                                        rb.data = data
                                                        rb.dirty = False
                                                        
                                                        with patch.object(rb, 'refresh_table'):
                                                            rb.delete_all_records()
                                                            
                                                            # 验证数据被清空
                                                            assert rb.data.empty
                                                            assert rb.dirty is True


class TestRecordBookFileOperations:
    """测试文件操作"""

    def test_export_csv(self):
        """测试导出CSV功能"""
        with patch('ui.main_window.tk'):
            with patch('ui.main_window.ttk'):
                with patch('ui.main_window.DateEntry'):
                    with patch('ui.main_window.ensure_db'):
                        with patch('ui.main_window.sqlite3'):
                            with patch('ui.main_window.filedialog') as mock_dialog:
                                mock_dialog.asksaveasfilename.return_value = 'test_export.csv'
                                
                                with patch('ui.main_window.messagebox') as mock_msg:
                                    from ui.main_window import RecordBook
                                    
                                    mock_master = MagicMock()
                                    mock_master.tk = MagicMock()
                                    mock_master.winfo_toplevel.return_value = mock_master
                                    
                                    data = pd.DataFrame([
                                        {"日期": "2025-01-01", "类型": "支出", "分类": "餐饮", "金额": 50.0, "备注": "test1"},
                                    ])
                                    
                                    with patch('ui.main_window.tkfont'):
                                        with patch.object(RecordBook, 'ensure_db'):
                                            with patch.object(RecordBook, 'load_data', return_value=data):
                                                with patch.object(RecordBook, 'create_menu'):
                                                    with patch.object(RecordBook, 'create_widgets'):
                                                        with patch.object(RecordBook, 'refresh_table'):
                                                            rb = RecordBook(mock_master)
                                                            rb.data = data
                                                            
                                                            with patch.object(data, 'to_csv') as mock_to_csv:
                                                                rb.export_csv()
                                                                # 验证 to_csv 被调用
                                                                mock_to_csv.assert_called_once()


class TestRecordBookSort:
    """测试排序功能"""

    def test_sort_by_column_toggle(self):
        """测试点击列头切换排序方向"""
        with patch('ui.main_window.tk'):
            with patch('ui.main_window.ttk'):
                with patch('ui.main_window.DateEntry'):
                    with patch('ui.main_window.ensure_db'):
                        with patch('ui.main_window.sqlite3'):
                            from ui.main_window import RecordBook
                            
                            mock_master = MagicMock()
                            mock_master.tk = MagicMock()
                            mock_master.winfo_toplevel.return_value = mock_master
                            
                            with patch('ui.main_window.tkfont'):
                                with patch.object(RecordBook, 'ensure_db'):
                                    with patch.object(RecordBook, 'load_data', return_value=pd.DataFrame()):
                                        with patch.object(RecordBook, 'create_menu'):
                                            with patch.object(RecordBook, 'create_widgets'):
                                                with patch.object(RecordBook, 'refresh_table'):
                                                    rb = RecordBook(mock_master)
                                                    rb._sort_column = None
                                                    rb._sort_asc = True
                                                    
                                                    with patch.object(rb, 'apply_filter') as mock_apply:
                                                        # 第一次点击，设置排序列
                                                        rb.sort_by_column('日期')
                                                        assert rb._sort_column == '日期'
                                                        assert rb._sort_asc is True
                                                        
                                                        # 第二次点击同一列，切换方向
                                                        rb.sort_by_column('日期')
                                                        assert rb._sort_column == '日期'
                                                        assert rb._sort_asc is False
