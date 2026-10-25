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

                                                        # 验证统计标签被调用一次，且文本包含正确的总收入/总支出
                                                        rb.stats_label.config.assert_called_once()
                                                        text = rb.stats_label.config.call_args.kwargs.get('text', '')
                                                        assert '1000' in text  # 总收入 1000 元
                                                        assert '80' in text    # 总支出 80 元（50 + 30）


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
                                                        # apply_filter 将筛选结果作为 filtered_df 传给 refresh_table，self.data 保持不变
                                                        filtered = mock_refresh.call_args.kwargs['filtered_df']
                                                        assert len(filtered) == 1
                                                        assert filtered.iloc[0]['日期'] == '2025-02-01'
                                                        assert filtered.iloc[0]['类型'] == '支出'
                                                        assert filtered.iloc[0]['金额'] == 60.0
                                                        # 原始数据未被修改
                                                        assert len(rb.data) == 3

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
                                                        # apply_filter 将筛选结果作为 filtered_df 传给 refresh_table
                                                        filtered = mock_refresh.call_args.kwargs['filtered_df']
                                                        assert len(filtered) == 1
                                                        assert filtered.iloc[0]['类型'] == '收入'
                                                        assert filtered.iloc[0]['分类'] == '工资'
                                                        assert filtered.iloc[0]['金额'] == 1000.0
                                                        # 原始数据未被修改
                                                        assert len(rb.data) == 2

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


class TestImportTransforms:
    """测试支付宝/微信账单的自动数据转换（_transform_alipay_data / _transform_wechat_data）"""

    def _make_record_book(self):
        """绕过 __init__ 构造 RecordBook 实例（转换函数不依赖实例状态）"""
        from ui.main_window import RecordBook
        return object.__new__(RecordBook)

    def test_transform_alipay_data(self):
        """支付宝：' 收入 ' 带空格值 strip 后判为收入，分类空值填充为'支付宝'"""
        rb = self._make_record_book()
        # 模拟列映射重命名后的支付宝账单（原始'收/支'列已映射到'类型'列）
        df = pd.DataFrame({
            '交易时间': ['2025-07-01 12:00:00', '2025-07-02 08:30:00', '2025-07-03 18:00:00'],
            '类型': ['收入', ' 收入 ', '不计收支'],
            '分类': ['工资', None, '餐饮'],
            '金额': [1000.0, 200.0, 50.0],
            '备注': ['工资到账', '奖金', '午餐'],
        })

        result = rb._transform_alipay_data(df)

        # 类型映射：'收入'和带空格的' 收入 '都判为收入，其余值一律判为支出
        assert result['类型'].tolist() == ['收入', '收入', '支出']
        # 分类空值填充为'支付宝'
        assert result['分类'].tolist() == ['工资', '支付宝', '餐饮']
        # 备注转为字符串
        assert result['备注'].tolist() == ['工资到账', '奖金', '午餐']
        # 未被转换引用的列（交易时间、金额）保持原样
        assert result['交易时间'].tolist() == ['2025-07-01 12:00:00', '2025-07-02 08:30:00', '2025-07-03 18:00:00']
        assert result['金额'].tolist() == [1000.0, 200.0, 50.0]

    def test_transform_wechat_data(self):
        """微信：金额去除¥符号转数值，类型映射正确，分类空值填充为'微信'"""
        rb = self._make_record_book()
        # 模拟列映射重命名后的微信账单（原始'收/支'列已映射到'类型'列，金额含¥符号）
        df = pd.DataFrame({
            '交易时间': ['2025-07-01 12:00:00', '2025-07-02 18:00:00'],
            '类型': ['收入', '支出'],
            '分类': [None, '餐饮'],
            '金额': ['¥100.50', '¥50.00'],
            '备注': ['红包', '晚餐'],
        })

        result = rb._transform_wechat_data(df)

        # 金额去除¥符号并转为数值
        assert result['金额'].tolist() == [100.5, 50.0]
        # 类型映射正确
        assert result['类型'].tolist() == ['收入', '支出']
        # 分类空值填充为'微信'
        assert result['分类'].tolist() == ['微信', '餐饮']
        # 备注保持字符串
        assert result['备注'].tolist() == ['红包', '晚餐']


class TestWechatImportFixes:
    """回归测试：微信账单导入的两个历史 bug（金额列映射半角/全角、¥符号被提前数值化）"""

    def _make_record_book(self):
        """绕过 __init__ 构造 RecordBook 实例"""
        from ui.main_window import RecordBook
        return object.__new__(RecordBook)

    def test_build_wechat_mapping_half_width_amount(self):
        """真实微信账单表头为半角 金额(元)，默认映射必须包含金额列"""
        rb = self._make_record_book()
        columns = ['交易时间', '交易类型', '交易对方', '商品', '收/支', '金额(元)',
                   '支付方式', '当前状态', '交易单号', '商户单号', '备注']
        m = rb._build_wechat_mapping(columns)
        assert m.get('金额') == '金额(元)'
        assert m.get('日期') == '交易时间'
        assert m.get('类型') == '收/支'
        assert m.get('分类') == '交易对方'
        assert m.get('备注') == '商品'

    def test_build_wechat_mapping_full_width_fallback(self):
        """全角 金额（元）写法仍能映射（向后兼容）"""
        rb = self._make_record_book()
        m = rb._build_wechat_mapping(['交易时间', '收/支', '交易对方', '商品', '金额（元）'])
        assert m.get('金额') == '金额（元）'

    def test_transform_wechat_numeric_amount(self):
        """金额列已是数值类型时不抛异常，值保持不变"""
        rb = self._make_record_book()
        df = pd.DataFrame({
            '金额': [14.91, 20.0],
            '类型': ['支出', '收入'],
            '分类': [None, None],
            '备注': ['a', 'b'],
        })
        result = rb._transform_wechat_data(df)
        assert result['金额'].tolist() == [14.91, 20.0]

    def test_transform_wechat_full_width_yen(self):
        """全角￥符号同样能被去除"""
        rb = self._make_record_book()
        df = pd.DataFrame({
            '金额': ['￥100.50'],
            '类型': ['支出'],
            '分类': [None],
            '备注': ['a'],
        })
        result = rb._transform_wechat_data(df)
        assert result['金额'].tolist() == [100.5]

    def test_parse_and_import_wechat_yen_end_to_end(self):
        """端到端：含¥金额的微信数据经完整导入流程后金额为数值而非 NaN"""
        rb = self._make_record_book()
        rb.master = MagicMock()
        rb.default_font = None
        rb.data = pd.DataFrame(columns=['日期', '类型', '分类', '金额', '备注'])
        rb.dirty = False

        df = pd.DataFrame({
            '交易时间': ['2025-07-01 12:00:00', '2025-07-02 18:00:00'],
            '交易类型': ['商户消费', '转账'],
            '交易对方': ['某快餐店', '张三'],
            '商品': ['午餐', '红包'],
            '收/支': ['支出', '收入'],
            '金额(元)': ['¥14.91', '¥100.00'],
        })
        default_map = rb._build_wechat_mapping(list(df.columns))
        assert '金额' in default_map  # 半角表头下默认映射完整，无需用户手动补金额列

        captured = {}
        def fake_preview(master, preview_df, font):
            dlg = MagicMock()
            dlg.result = True
            dlg.data = preview_df
            captured['df'] = preview_df
            return dlg

        with patch('ui.main_window.ImportMappingDialog') as mock_map_dialog, \
                patch('ui.main_window.PreviewDialog', side_effect=fake_preview), \
                patch('ui.main_window.messagebox'), \
                patch.object(rb, 'refresh_table'):
            mock_map_dialog.return_value.result = default_map
            rb._parse_and_import(df, default_map, '微信账单', rb._transform_wechat_data)

        preview = captured['df']
        # 关键回归断言：¥ 金额被正确转换为数值，而不是在转换前被数值化成 NaN
        assert preview['金额'].tolist() == [14.91, 100.0]
        assert preview['类型'].tolist() == ['支出', '收入']
        assert preview['日期'].tolist() == ['2025-07-01', '2025-07-02']
        # 数据真正进入了账本
        assert len(rb.data) == 2
        assert rb.dirty is True
        assert rb.data['金额'].tolist() == [14.91, 100.0]


class TestEditDeleteRegression:
    """回归测试：双击编辑（iloc/loc 错位 P0）与单条删除"""

    def _make_record_book(self):
        from ui.main_window import RecordBook
        rb = object.__new__(RecordBook)
        rb.master = MagicMock()
        rb.default_font = None
        return rb

    def test_double_click_edit_non_contiguous_index(self):
        """删除记录后索引不连续（如 [0,1,3]），双击 iid='3' 必须编辑标签3的记录"""
        rb = self._make_record_book()
        rb.data = pd.DataFrame([
            {"日期": "2025-01-01", "类型": "支出", "分类": "餐饮", "金额": 50.0, "备注": "a"},
            {"日期": "2025-01-02", "类型": "支出", "分类": "交通", "金额": 30.0, "备注": "b"},
            {"日期": "2025-01-03", "类型": "支出", "分类": "购物", "金额": 80.0, "备注": "c"},
        ], index=[0, 1, 3])  # 模拟删除一条后的非连续索引
        rb.dirty = False
        rb.tree = MagicMock()
        rb.tree.identify_row.return_value = '3'

        with patch('ui.main_window.EditRecordDialog') as mock_dlg, \
                patch.object(rb, 'save_data') as mock_save, \
                patch.object(rb, 'refresh_table'):
            mock_dlg.return_value.result = {
                '日期': '2025-01-03', '类型': '支出', '分类': '购物', '金额': '99.9', '备注': '改后'
            }
            rb.on_tree_double_click(MagicMock(y=10))

        # 标签3的记录被修改，其余记录不受影响（旧实现 iloc[3] 会越界或改错行）
        assert rb.data.loc[3, '金额'] == 99.9
        assert rb.data.loc[3, '备注'] == '改后'
        assert rb.data.loc[0, '金额'] == 50.0
        assert rb.data.loc[1, '金额'] == 30.0
        mock_save.assert_called_once()

    def test_double_click_invalid_index_guarded(self):
        """iid 不在索引中时安全返回，不弹编辑对话框"""
        rb = self._make_record_book()
        rb.data = pd.DataFrame([
            {"日期": "2025-01-01", "类型": "支出", "分类": "餐饮", "金额": 50.0, "备注": "a"},
        ])
        rb.tree = MagicMock()
        rb.tree.identify_row.return_value = '99'

        with patch('ui.main_window.EditRecordDialog') as mock_dlg:
            rb.on_tree_double_click(MagicMock(y=10))
        mock_dlg.assert_not_called()

    def test_delete_record_single(self):
        """删除单条记录：确认后该行被移除，其余保留"""
        rb = self._make_record_book()
        rb.data = pd.DataFrame([
            {"日期": "2025-01-01", "类型": "支出", "分类": "餐饮", "金额": 50.0, "备注": "a"},
            {"日期": "2025-01-02", "类型": "支出", "分类": "交通", "金额": 30.0, "备注": "b"},
            {"日期": "2025-01-03", "类型": "收入", "分类": "工资", "金额": 100.0, "备注": "c"},
        ])
        rb.dirty = False
        rb.tree = MagicMock()
        rb.tree.selection.return_value = ('1',)

        with patch('ui.main_window.messagebox') as mock_msg, \
                patch.object(rb, 'refresh_table'):
            mock_msg.askyesno.return_value = True
            rb.delete_record()

        assert len(rb.data) == 2
        assert 'b' not in rb.data['备注'].tolist()
        assert rb.dirty is True
