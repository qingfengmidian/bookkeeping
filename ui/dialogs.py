import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from utils.constants import CATEGORIES
import pandas as pd

class FilterDialog(tk.Toplevel):
    def __init__(self, master, filter_dict, font):
        super().__init__(master)
        self.title('筛选账单')
        self.geometry('480x360')
        self.result = None
        self.resizable(True, True)
        self.transient(master)
        self.grab_set()
        self.font = font

        # 日期选择器
        import datetime
        now = datetime.datetime.now()

        self.vars = {}
        # 起始日期
        tk.Label(self, text='起始日期:', font=self.font).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        start_val = filter_dict.get('start', '')
        self.start_var = tk.StringVar(value=start_val or now.strftime('%Y-%m-%d'))
        self.start_entry = DateEntry(self, textvariable=self.start_var, date_pattern='yyyy-mm-dd', width=12, font=self.font)
        self.start_entry.grid(row=0, column=1, padx=2, pady=10, sticky='w')
        try:
            self.start_entry.bind('<Escape>', lambda e: self._on_de_escape(self.start_entry), add='+')
        except Exception:
            pass
        # 结束日期
        tk.Label(self, text='结束日期:', font=self.font).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        end_val = filter_dict.get('end', '')
        self.end_var = tk.StringVar(value=end_val or now.strftime('%Y-%m-%d'))
        self.end_entry = DateEntry(self, textvariable=self.end_var, date_pattern='yyyy-mm-dd', width=12, font=self.font)
        self.end_entry.grid(row=1, column=1, padx=2, pady=10, sticky='w')
        try:
            self.end_entry.bind('<Escape>', lambda e: self._on_de_escape(self.end_entry), add='+')
        except Exception:
            pass
        # 其余筛选项
        # 金额区间
        tk.Label(self, text='最小金额:', font=self.font).grid(row=2, column=0, padx=10, pady=10, sticky='w')
        min_amt = filter_dict.get('min_amt', '')
        self.min_amt_var = tk.StringVar(value=min_amt)
        ttk.Entry(self, textvariable=self.min_amt_var, font=self.font, width=8).grid(row=2, column=1, columnspan=1, padx=2, pady=10, sticky='w')
        tk.Label(self, text='最大金额:', font=self.font).grid(row=3, column=0, padx=10, pady=10, sticky='w')
        max_amt = filter_dict.get('max_amt', '')
        self.max_amt_var = tk.StringVar(value=max_amt)
        ttk.Entry(self, textvariable=self.max_amt_var, font=self.font, width=8).grid(row=3, column=1, columnspan=1, padx=2, pady=10, sticky='w')
        # 类型
        tk.Label(self, text='类       型:', font=self.font).grid(row=4, column=0, padx=10, pady=10, sticky='w')
        type_val = filter_dict.get('type', '全部')
        self.type_var = tk.StringVar(value=type_val or '全部')
        ttk.Combobox(self, textvariable=self.type_var, values=['全部', '支出', '收入'], state='readonly', font=self.font, width=6).grid(row=4, column=1, padx=2, pady=10, sticky='w')
        # 分类
        tk.Label(self, text='分       类:', font=self.font).grid(row=5, column=0, padx=10, pady=10, sticky='w')
        cat_val = filter_dict.get('cat', '全部')
        self.cat_var = tk.StringVar(value=cat_val or '全部')
        ttk.Combobox(self, textvariable=self.cat_var, values=['全部'] + CATEGORIES, state='readonly', font=self.font, width=6).grid(row=5, column=1, padx=2, pady=10, sticky='w')
        # 应用和清除按钮纵向排布在起始日期下
        btn_apply = ttk.Button(self, text='应用筛选', command=self.on_ok)
        btn_apply.grid(row=6, column=1, columnspan=1, pady=10, sticky='w')
        btn_clear = ttk.Button(self, text='清除筛选', command=self.on_clear)
        btn_clear.grid(row=6, column=2, columnspan=1, pady=10, sticky='w')

    def on_ok(self):
        # 读取 DateEntry 的日期字符串（yyyy-mm-dd）
        start = self.start_var.get()
        end = self.end_var.get()
        result = {
            'start': start,
            'end': end,
            'min_amt': self.min_amt_var.get(),
            'max_amt': self.max_amt_var.get(),
            'type': self.type_var.get(),
            'cat': self.cat_var.get(),
        }
        self.result = result
        self.destroy()
    def on_clear(self):
        self.result = '__clear__'
        self.destroy()

    def _close_date_popup(self, de: DateEntry):
        try:
            top = getattr(de, '_top_cal', None)
            if not top:
                return
            if not top.winfo_exists():
                return
            top.withdraw()
        except Exception:
            pass

    def _on_escape(self, event=None):
        try:
            w = self.focus_get()
            if isinstance(w, DateEntry):
                self._close_date_popup(w)
                return 'break'
        except Exception:
            pass
        try:
            self._close_date_popup(self.start_entry)
            self._close_date_popup(self.end_entry)
        except Exception:
            pass
        return 'break'

    def _on_de_escape(self, de: DateEntry):
        try:
            self._close_date_popup(de)
        except Exception:
            pass
        return 'break'

class EditRecordDialog(tk.Toplevel):
    def __init__(self, master, record, font):
        super().__init__(master)
        self.title('编辑账单')
        self.geometry('350x300')
        self.result = None
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.font = font
        fields = ['日期', '类型', '分类', '金额', '备注']
        self.vars = {}
        for i, field in enumerate(fields):
            tk.Label(self, text=f'{field}:', font=self.font).grid(row=i, column=0, padx=10, pady=10, sticky='e')
            var = tk.StringVar(value=str(record.get(field, '')))
            if field == '类型':
                cb = ttk.Combobox(self, textvariable=var, values=['收入', '支出'], state='readonly', font=self.font)
                cb.grid(row=i, column=1, padx=10, pady=10, sticky='w')
                self.vars[field] = var
            elif field == '分类':
                cb = ttk.Combobox(self, textvariable=var, values=CATEGORIES, state='readonly', font=self.font)
                cb.grid(row=i, column=1, padx=10, pady=10, sticky='w')
                self.vars[field] = var
            else:
                entry = ttk.Entry(self, textvariable=var, font=self.font)
                entry.grid(row=i, column=1, padx=10, pady=10, sticky='w')
                self.vars[field] = var
        btn = ttk.Button(self, text='保存', command=self.on_ok)
        btn.grid(row=len(fields), column=0, columnspan=2, pady=20)
    def on_ok(self):
        # 校验金额为数字
        try:
            float(self.vars['金额'].get())
        except ValueError:
            messagebox.showerror('输入错误', '金额必须为数字')
            return
        self.result = {field: self.vars[field].get() for field in self.vars}
        self.destroy()

class ImportMappingDialog(tk.Toplevel):
    def __init__(self, master, columns, default_map, font):
        super().__init__(master)
        self.title('选择导入列对应关系')
        self.geometry('400x300')
        self.result = None
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.font = font
        self.vars = {}
        fields = ['日期', '类型', '分类', '金额', '备注']
        for i, field in enumerate(fields):
            tk.Label(self, text=f'{field}:', font=self.font).grid(row=i, column=0, padx=10, pady=10, sticky='e')
            var = tk.StringVar(value=default_map.get(field, columns[0] if columns else ''))
            cb = ttk.Combobox(self, textvariable=var, values=columns, state='readonly', font=self.font)
            cb.grid(row=i, column=1, padx=10, pady=10, sticky='w')
            self.vars[field] = var
        btn = ttk.Button(self, text='确定', command=self.on_ok)
        btn.grid(row=len(fields), column=0, columnspan=2, pady=20)
    def on_ok(self):
        self.result = {field: var.get() for field, var in self.vars.items()}
        self.destroy()


class PreviewDialog(tk.Toplevel):
    def __init__(self, master, data, font):
        """
        显示导入数据预览的对话框
        
        Args:
            master: 父窗口
            data: 要预览的DataFrame数据
            font: 字体设置
        """
        super().__init__(master)
        self.title('导入数据预览')
        self.geometry('800x500')  # 更大的窗口以显示更多数据
        self.result = False  # 默认不确认导入
        self.resizable(True, True)  # 允许调整大小
        self.transient(master)
        self.grab_set()
        self.font = font
        # 保存一份可编辑的数据副本
        self.data = data.copy()
        # 当前排序状态
        self._sort_state = {'col': None, 'asc': True}
        
        # 创建预览标签
        tk.Label(self, text='即将导入的数据预览（显示前10行）：', font=self.font).pack(pady=10)
        
        # 创建表格显示预览数据
        frame = ttk.Frame(self)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 创建Treeview显示数据
        self.columns = list(self.data.columns)
        self.tree = ttk.Treeview(frame, columns=self.columns, show='headings', height=10)
        
        # 设置列标题和宽度，并绑定点击排序
        for col in self.columns:
            self.tree.heading(col, text=col, command=lambda c=col: self._on_heading_click(c))
            self.tree.column(col, width=100, anchor='center')
        
        # 添加滚动条
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # 放置滚动条
        self.tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        
        # 配置frame的网格权重
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        # 显示数据（最多显示前10行）
        self._refresh_tree()
        
        # 显示总行数信息
        total_rows = len(data)
        tk.Label(self, text=f'总记录数: {total_rows}', font=self.font).pack(pady=5)
        
        # 绑定双击编辑事件
        self.tree.bind('<Double-1>', self._on_tree_double_click)

        # 按钮区域
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        # 确认和取消按钮
        ttk.Button(btn_frame, text='确认导入', command=self.on_confirm).pack(side='left', padx=10)
        ttk.Button(btn_frame, text='取消', command=self.on_cancel).pack(side='right', padx=10)
    
    def on_confirm(self):
        self.result = True
        self.destroy()
    
    def on_cancel(self):
        self.result = False
        self.destroy()

    def _refresh_tree(self):
        # 根据当前排序状态刷新Treeview内容
        for item in self.tree.get_children():
            self.tree.delete(item)
        df = self.data
        col = self._sort_state.get('col')
        if col:
            asc = self._sort_state.get('asc', True)
            if col == '日期':
                # 日期列按时间排序
                df = df.copy()
                df['__tmp_date__'] = pd.to_datetime(df['日期'], errors='coerce')
                df = df.sort_values('__tmp_date__', ascending=asc).drop(columns=['__tmp_date__'])
            else:
                df = df.sort_values(col, ascending=asc)
        # 保持使用原索引作为iid，方便编辑回写
        for idx, row in df.iterrows():
            values = [row.get(col, '') for col in self.columns]
            self.tree.insert('', 'end', iid=str(idx), values=values)

    def _on_heading_click(self, col):
        # 列表头点击切换排序状态
        if self._sort_state['col'] == col:
            self._sort_state['asc'] = not self._sort_state['asc']
        else:
            self._sort_state['col'] = col
            self._sort_state['asc'] = True
        self._refresh_tree()

    def _on_tree_double_click(self, event):
        # 双击行进行编辑
        item_id = self.tree.focus()
        if not item_id:
            return
        try:
            row_idx = int(item_id)
        except ValueError:
            return
        if row_idx not in self.data.index:
            return
        # 仅在具备标准字段时启用编辑
        fields = ['日期', '类型', '分类', '金额', '备注']
        record = {field: self.data.loc[row_idx].get(field, '') for field in fields if field in self.data.columns}
        if set(fields).issubset(self.data.columns):
            dialog = EditRecordDialog(self, record, self.font)
            self.wait_window(dialog)
            if dialog.result:
                # 回写修改
                for field in fields:
                    self.data.at[row_idx, field] = dialog.result.get(field, self.data.at[row_idx, field])
                # 金额列转为数字
                if '金额' in self.data.columns:
                    try:
                        self.data['金额'] = pd.to_numeric(self.data['金额'], errors='coerce')
                    except Exception:
                        pass
                self._refresh_tree()

