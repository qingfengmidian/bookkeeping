import tkinter as tk
from tkinter import ttk, messagebox
from utils.constants import CATEGORIES

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

        # 年月日下拉选项
        import datetime
        now = datetime.datetime.now()
        years = list(range(2000, now.year + 1))
        months = list(range(1, 13))
        days = list(range(1, 32))

        self.vars = {}
        # 起始日期
        tk.Label(self, text='起始日期:', font=self.font).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        start_val = filter_dict.get('start', '')
        s_year, s_month, s_day = self.split_date(start_val, now.year, 1, 1)
        self.s_year_var = tk.IntVar(value=s_year)
        self.s_month_var = tk.IntVar(value=s_month)
        self.s_day_var = tk.IntVar(value=s_day)
        ttk.Combobox(self, textvariable=self.s_year_var, values=years, width=6, font=self.font, state='readonly').grid(row=0, column=1, padx=2, pady=10, sticky='w')
        ttk.Combobox(self, textvariable=self.s_month_var, values=months, width=4, font=self.font, state='readonly').grid(row=0, column=2, padx=2, pady=10, sticky='w')
        ttk.Combobox(self, textvariable=self.s_day_var, values=days, width=4, font=self.font, state='readonly').grid(row=0, column=3, padx=2, pady=10, sticky='w')
        # 结束日期
        tk.Label(self, text='结束日期:', font=self.font).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        end_val = filter_dict.get('end', '')
        e_year, e_month, e_day = self.split_date(end_val, now.year, 12, 31)
        self.e_year_var = tk.IntVar(value=e_year)
        self.e_month_var = tk.IntVar(value=e_month)
        self.e_day_var = tk.IntVar(value=e_day)
        ttk.Combobox(self, textvariable=self.e_year_var, values=years, width=6, font=self.font, state='readonly').grid(row=1, column=1, padx=2, pady=10, sticky='w')
        ttk.Combobox(self, textvariable=self.e_month_var, values=months, width=4, font=self.font, state='readonly').grid(row=1, column=2, padx=2, pady=10, sticky='w')
        ttk.Combobox(self, textvariable=self.e_day_var, values=days, width=4, font=self.font, state='readonly').grid(row=1, column=3, padx=2, pady=10, sticky='w')
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

    def split_date(self, date_str, default_year, default_month, default_day):
        try:
            parts = [int(x) for x in date_str.split('-')]
            if len(parts) == 3:
                return parts[0], parts[1], parts[2]
        except Exception:
            pass
        return default_year, default_month, default_day

    def on_ok(self):
        # 组装日期
        start = f"{self.s_year_var.get():04d}-{self.s_month_var.get():02d}-{self.s_day_var.get():02d}"
        end = f"{self.e_year_var.get():04d}-{self.e_month_var.get():02d}-{self.e_day_var.get():02d}"
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
            tk.Label(self, text=f'{field} 对应列:', font=self.font).grid(row=i, column=0, padx=10, pady=10, sticky='e')
            var = tk.StringVar(value=default_map.get(field, columns[0] if columns else ''))
            cb = ttk.Combobox(self, textvariable=var, values=columns, state='readonly', font=self.font)
            cb.grid(row=i, column=1, padx=10, pady=10, sticky='w')
            self.vars[field] = var
        btn = ttk.Button(self, text='确定', command=self.on_ok)
        btn.grid(row=len(fields), column=0, columnspan=2, pady=20)
    def on_ok(self):
        self.result = {field: var.get() for field, var in self.vars.items()}
        self.destroy()
