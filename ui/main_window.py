import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font as tkfont
from ui.dialogs import FilterDialog, EditRecordDialog, ImportMappingDialog, PreviewDialog
from ui.charts import show_monthly_chart, show_single_month_pie, show_pie
from db.database import ensure_db, create_table, load_data, save_data
from model.record_model import process_monthly, process_detail
from ui.theme import pick_font_family, INCOME, EXPENSE, TOTAL_EXPENSE, ROW_STRIPE, TEXT_MUTED
from utils.constants import DB_DEFAULT, CATEGORIES, TABLE_RECORDS_SCHEMA, TABLE_NAME, CJK_FONT_FALLBACK
from utils.logger import get_logger
import pandas as pd
from tkcalendar import DateEntry
import os
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

logger = get_logger(__name__)

class RecordBook:
    def __init__(self, master):
        self.master = master
        self.master.title('记账本')
        self.master.geometry('960x640')
        # 设置全局字体
        self.default_font = tkfont.nametofont('TkDefaultFont')
        self.default_font.configure(size=self.default_font['size'] + 2)
        self.tree_font = tkfont.Font(family=pick_font_family(), size=12)
        self.db_path = DB_DEFAULT
        self.conn = None
        self.dirty = False  # 数据变更标志
        self.chart_window = None  # 图表窗口引用
        logger.info(f'初始化数据库: {self.db_path}')
        self.ensure_db()
        self.data = self.load_data()
        logger.info(f'加载了 {len(self.data)} 条记录')
        self.create_menu()
        self.create_widgets()
        self.refresh_table()
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_menu(self):
        menubar = tk.Menu(self.master)
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label='新建', command=self.new_db)
        file_menu.add_command(label='打开', command=self.open_db)
        file_menu.add_command(label='保存', command=self.save_data)
        file_menu.add_command(label='另存为', command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label='退出', command=self.on_close)
        menubar.add_cascade(label='文件', menu=file_menu)
        # 导入菜单
        import_menu = tk.Menu(menubar, tearoff=0)
        import_menu.add_command(label='CSV', command=self.import_csv)
        import_menu.add_command(label='导入支付宝账单', command=self.import_alipay_csv)
        import_menu.add_command(label='导入微信账单', command=self.import_wechat_excel)
        menubar.add_cascade(label='导入', menu=import_menu)
        # 导出菜单
        export_menu = tk.Menu(menubar, tearoff=0)
        export_menu.add_command(label='CSV', command=self.export_csv)
        menubar.add_cascade(label='导出', menu=export_menu)
        # 筛选菜单
        filter_menu = tk.Menu(menubar, tearoff=0)
        filter_menu.add_command(label='筛选账单', command=self.open_filter_dialog)
        menubar.add_cascade(label='筛选', menu=filter_menu)
        # 统计菜单
        stat_menu = tk.Menu(menubar, tearoff=0)
        stat_menu.add_command(label='月度账单', command=self.show_monthly_bill)
        # 统计图表二级菜单
        chart_menu = tk.Menu(stat_menu, tearoff=0)
        chart_menu.add_command(label='月度收支柱状图', command=lambda: show_monthly_chart(self.data, self.master))
        chart_menu.add_command(label='单月收支饼状图', command=lambda: show_single_month_pie(self.data, self.master))
        stat_menu.add_cascade(label='统计图表', menu=chart_menu)
        menubar.add_cascade(label='统计', menu=stat_menu)
        self.master.config(menu=menubar)


    def show_monthly_bill(self):
        # 按月统计收入、支出和汇总
        df = self.data.copy()
        if df.empty:
            messagebox.showinfo('无数据', '没有可统计的账单数据。')
            return
        df['日期'] = pd.to_datetime(df['日期'])
        df['年月'] = df['日期'].dt.to_period('M').astype(str)
        monthly = df.pivot_table(index='年月', columns='类型', values='金额', aggfunc='sum', fill_value=0)
        monthly['总收入'] = monthly.get('收入', 0)
        monthly['总支出'] = monthly.get('支出', 0)
        monthly = monthly[['收入', '支出', '总收入', '总支出']] if set(['收入','支出']).issubset(monthly.columns) else monthly
        # 弹窗展示表格
        win = tk.Toplevel(self.master)
        win.title('月度账单')
        win.geometry('500x400')
        tree = ttk.Treeview(win, columns=('month', 'income', 'expense', 'total_income', 'total_expense'), show='headings')
        tree.heading('month', text='月份')
        tree.heading('income', text='收入')
        tree.heading('expense', text='支出')
        tree.heading('total_income', text='总收入')
        tree.heading('total_expense', text='总支出')
        tree.column('month', width=80)
        tree.column('income', width=80)
        tree.column('expense', width=80)
        tree.column('total_income', width=100)
        tree.column('total_expense', width=100)
        # 插入数据
        for idx, row in monthly.iterrows():
            tree.insert('', 'end', values=(idx, row.get('收入', 0), row.get('支出', 0), row.get('总收入', 0), row.get('总支出', 0)))
        tree.pack(fill='both', expand=True)
        # 滚动条
        scrollbar = ttk.Scrollbar(win, orient='vertical', command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        # 表头排序功能
        sort_state = {'col': None, 'asc': True}
        def treeview_sort_column(col):
            nonlocal monthly
            # 排序并刷新表格
            asc = True if sort_state['col'] != col or not sort_state['asc'] else False
            sort_state['col'] = col
            sort_state['asc'] = asc
            # DataFrame排序
            df_sorted = monthly.sort_values(col, ascending=asc)
            # 清空并重插入
            for row in tree.get_children():
                tree.delete(row)
            for idx, row in df_sorted.iterrows():
                tree.insert('', 'end', values=(idx, row.get('收入', 0), row.get('支出', 0), row.get('总收入', 0), row.get('总支出', 0)))
        # 设置表头点击事件
        tree.heading('month', text='月份', command=lambda: treeview_sort_column('年月'))
        tree.heading('income', text='收入', command=lambda: treeview_sort_column('收入'))
        tree.heading('expense', text='支出', command=lambda: treeview_sort_column('支出'))
        tree.heading('total_income', text='总收入', command=lambda: treeview_sort_column('总收入'))
        tree.heading('total_expense', text='总支出', command=lambda: treeview_sort_column('总支出'))

        # 绑定双击事件，弹出该月明细
        def on_month_double_click(event):
            item = tree.selection()
            if not item:
                return
            month = tree.item(item[0], 'values')[0]
            self.show_month_detail(month)
        tree.bind('<Double-1>', on_month_double_click)

    def show_month_detail(self, month):
        # 展示指定月份的所有收支明细
        df = self.data.copy()
        if df.empty:
            messagebox.showinfo('无数据', '没有可展示的账单数据。')
            return
        df['日期'] = pd.to_datetime(df['日期'])
        df['年月'] = df['日期'].dt.to_period('M').astype(str)
        month_df = df[df['年月'] == month]
        if month_df.empty:
            messagebox.showinfo('无数据', f'{month} 无账单数据。')
            return
        win = tk.Toplevel(self.master)
        win.title(f'{month} 收支明细')
        win.geometry('700x400')
        # 使用Frame容器让滚动条在右侧
        frame = ttk.Frame(win)
        frame.pack(fill='both', expand=True)
        tree = ttk.Treeview(frame, columns=('date', 'type', 'cat', 'amount', 'note'), show='headings')
        # 排序状态存储
        sort_state = {'col': None, 'asc': True}
        # 列表头排序函数
        def treeview_sort_column(col):
            nonlocal month_df
            asc = True if sort_state['col'] != col or not sort_state['asc'] else False
            sort_state['col'] = col
            sort_state['asc'] = asc
            # DataFrame排序
            if col == 'date':
                df_sorted = month_df.sort_values('日期', ascending=asc)
            elif col == 'amount':
                df_sorted = month_df.sort_values('金额', ascending=asc)
            else:
                df_sorted = month_df.sort_values(col_map[col], ascending=asc)
            # 清空并重插入
            for row in tree.get_children():
                tree.delete(row)
            for _, row in df_sorted.iterrows():
                tree.insert('', 'end', values=(row['日期'].strftime('%Y-%m-%d'), row['类型'], row['分类'], row['金额'], row['备注']))
        # 表头映射
        col_map = {'date': '日期', 'type': '类型', 'cat': '分类', 'amount': '金额', 'note': '备注'}
        tree.heading('date', text='日期', command=lambda: treeview_sort_column('date'))
        tree.heading('type', text='类型', command=lambda: treeview_sort_column('type'))
        tree.heading('cat', text='分类', command=lambda: treeview_sort_column('cat'))
        tree.heading('amount', text='金额', command=lambda: treeview_sort_column('amount'))
        tree.heading('note', text='备注', command=lambda: treeview_sort_column('note'))
        tree.column('date', width=100)
        tree.column('type', width=60)
        tree.column('cat', width=100)
        tree.column('amount', width=80)
        tree.column('note', width=300)
        for _, row in month_df.iterrows():
            tree.insert('', 'end', values=(row['日期'].strftime('%Y-%m-%d'), row['类型'], row['分类'], row['金额'], row['备注']))
        tree.grid(row=0, column=0, sticky='nsew')
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)


    def _show_import_error(self, error_type: str, message: str):
        """显示导入错误对话框"""
        messagebox.showerror(error_type, message)
    
    def _parse_and_import(self, df: pd.DataFrame, default_map: dict, source_name: str, 
                          auto_transform: callable = None):
        """
        通用导入流程：列映射 -> 数据转换 -> 预览 -> 导入
        
        Args:
            df: 原始数据DataFrame
            default_map: 默认列映射
            source_name: 数据来源名称（用于提示信息）
            auto_transform: 自动数据转换函数（可选）
        """
        try:
            columns = list(df.columns)
            
            # 弹出列映射对话框
            dialog = ImportMappingDialog(self.master, columns, default_map, self.default_font)
            self.master.wait_window(dialog)
            if not dialog.result:
                return
            
            col_map = dialog.result
            if not all(col_map.get(field) in columns for field in ['日期','类型','分类','金额','备注']):
                self._show_import_error('映射错误', '请为所有字段选择对应的列')
                return
            
            # 字段重命名
            df = df.rename(columns={v: k for k, v in col_map.items()})
            
            # 应用自动转换（如支付宝/微信特殊处理），需在数据标准化之前处理原始字符串格式
            if auto_transform:
                df = auto_transform(df)
            
            # 数据标准化（放在转换之后，避免微信金额等原始格式被提前破坏）
            df['金额'] = pd.to_numeric(df['金额'], errors='coerce')
            df['日期'] = pd.to_datetime(df['日期'], errors='coerce').dt.strftime('%Y-%m-%d')
            
            # 弹出预览对话框
            preview_df = df[['日期', '类型', '分类', '金额', '备注']]
            preview_dialog = PreviewDialog(self.master, preview_df, self.default_font)
            self.master.wait_window(preview_dialog)
            
            # 如果用户确认导入，才进行实际导入
            if preview_dialog.result:
                final_df = preview_dialog.data[['日期', '类型', '分类', '金额', '备注']].copy()
                self.data = pd.concat([self.data, final_df], ignore_index=True)
                self.dirty = True
                self.refresh_table()
                messagebox.showinfo('导入成功', f'已从{source_name}导入 {len(final_df)} 条记录')
            else:
                messagebox.showinfo('取消导入', '已取消导入操作')
        except Exception as e:
            self._show_import_error('导入失败', f'导入过程中发生错误: {e}')

    def import_csv(self):
        file_path = filedialog.askopenfilename(title='选择CSV文件', filetypes=[('CSV文件', '*.csv')])
        if not file_path:
            return
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except FileNotFoundError:
            self._show_import_error('文件错误', '选择的文件不存在')
            return
        except UnicodeDecodeError:
            self._show_import_error('编码错误', '文件编码错误，请尝试使用UTF-8编码保存文件')
            return
        except pd.errors.EmptyDataError:
            messagebox.showinfo('空文件', '选择的文件没有数据')
            return
        except pd.errors.ParserError as e:
            self._show_import_error('解析错误', f'CSV解析失败: {e}')
            return
        except Exception as e:
            self._show_import_error('读取失败', f'无法读取文件: {e}')
            return
        
        # 构建默认映射
        columns = list(df.columns)
        default_map = {k: k for k in ['日期', '类型', '分类', '金额', '备注'] if k in columns}
        
        self._parse_and_import(df, default_map, 'CSV文件')

    def _build_alipay_mapping(self, columns: list) -> dict:
        """构建支付宝账单的默认列映射"""
        default_map = {}
        for std, alipay in zip(['日期','类型','分类','金额','备注'], ['交易时间','收/支','交易分类','金额','商品说明']):
            if alipay in columns:
                default_map[std] = alipay
        # 兼容英文账单
        alt_map = {'日期':'Date','类型':'In/Out','分类':'Product','金额':'Amount(¥)','备注':'Remark'}
        for std, alt in alt_map.items():
            if std not in default_map and alt in columns:
                default_map[std] = alt
        return default_map
    
    def _transform_alipay_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """支付宝数据自动转换"""
        df['类型'] = df['类型'].map(lambda x: '收入' if str(x).strip() == '收入' else '支出')
        df['分类'] = df['分类'].fillna('支付宝')
        df['备注'] = df['备注'].astype(str)
        return df

    def import_alipay_csv(self):
        file_path = filedialog.askopenfilename(title='选择支付宝账单CSV文件', filetypes=[('CSV文件', '*.csv')])
        if not file_path:
            return
        try:
            # 支付宝账单前24行为说明，从第25行开始为数据
            # 支付宝账单，编码格式为gbk
            df = pd.read_csv(file_path, encoding='gbk', skiprows=24, usecols=range(7))
        except FileNotFoundError:
            self._show_import_error('文件错误', '选择的文件不存在')
            return
        except UnicodeDecodeError:
            self._show_import_error('编码错误', '文件编码错误，支付宝账单通常使用GBK编码')
            return
        except pd.errors.EmptyDataError:
            messagebox.showinfo('空文件', '选择的文件没有数据')
            return
        except pd.errors.ParserError as e:
            self._show_import_error('解析错误', f'CSV解析失败，请确认是支付宝账单格式: {e}')
            return
        except Exception as e:
            self._show_import_error('读取失败', f'无法读取文件: {e}')
            return
        
        default_map = self._build_alipay_mapping(list(df.columns))
        self._parse_and_import(df, default_map, '支付宝账单', self._transform_alipay_data)

    def _build_wechat_mapping(self, columns: list) -> dict:
        """构建微信账单的默认列映射"""
        default_map = {}
        for std, wechat in zip(['日期','类型','分类','金额','备注'], ['交易时间','收/支','交易对方','金额(元)','商品']):
            if wechat in columns:
                default_map[std] = wechat
        # 兼容全角括号写法 金额（元）
        if '金额' not in default_map and '金额（元）' in columns:
            default_map['金额'] = '金额（元）'
        # 兼容英文账单
        alt_map = {'日期':'Date','类型':'Type','分类':'Category','金额':'Amount','备注':'Description'}
        for std, alt in alt_map.items():
            if std not in default_map and alt in columns:
                default_map[std] = alt
        return default_map
    
    def _transform_wechat_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """微信数据自动转换"""
        # 去除金额中的¥/￥符号并转数值（先转字符串，兼容已是数值类型的列）
        df['金额'] = df['金额'].astype(str).str.replace('¥', '', regex=False).str.replace('￥', '', regex=False)
        df['金额'] = pd.to_numeric(df['金额'], errors='coerce')
        df['类型'] = df['类型'].map(lambda x: '收入' if str(x).strip() == '收入' else '支出')
        df['分类'] = df['分类'].fillna('微信')
        df['备注'] = df['备注'].astype(str)
        return df

    def import_wechat_excel(self):
        file_path = filedialog.askopenfilename(title='选择微信账单Excel文件', filetypes=[('Excel文件', '*.xls *.xlsx')])
        if not file_path:
            return
        try:
            # 微信账单前16行为说明，第17行开始为数据
            df = pd.read_excel(file_path, header=16, usecols=[0, 2, 3, 4, 5])
        except FileNotFoundError:
            self._show_import_error('文件错误', '选择的文件不存在')
            return
        except pd.errors.EmptyDataError:
            messagebox.showinfo('空文件', '选择的文件没有数据')
            return
        except ValueError as e:
            self._show_import_error('格式错误', f'Excel格式错误或缺少必要列: {e}')
            return
        except Exception as e:
            self._show_import_error('读取失败', f'无法读取Excel文件: {e}')
            return
        
        default_map = self._build_wechat_mapping(list(df.columns))
        self._parse_and_import(df, default_map, '微信账单', self._transform_wechat_data)

    def ensure_db(self):
        # 检查默认db，不存在则自动创建
        if not os.path.exists(self.db_path):
            # 确保目录存在
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            # 提示用户将新建数据库
            messagebox.showinfo('初始化数据库', f'将在以下位置新建数据库文件：\n{self.db_path}')
        self.conn = sqlite3.connect(self.db_path)
        self.create_table()

    def create_table(self):
        # 创建账单表
        c = self.conn.cursor()
        c.execute(f'''CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            {TABLE_RECORDS_SCHEMA}
        )''')
        self.conn.commit()

    def load_data(self):
        # 从数据库读取账单
        c = self.conn.cursor()
        c.execute('SELECT id, 日期, 类型, 分类, 金额, 备注 FROM records')
        rows = c.fetchall()
        df = pd.DataFrame(rows, columns=['id', '日期', '类型', '分类', '金额', '备注'])
        if not df.empty:
            df['金额'] = pd.to_numeric(df['金额'], errors='coerce')
        return df

    def save_data(self):
        # 保存DataFrame到当前数据库（全量覆盖）
        try:
            c = self.conn.cursor()
            c.execute('DELETE FROM records')
            
            # 使用executemany批量插入，提升性能
            if not self.data.empty:
                data_tuples = [
                    (row['日期'], row['类型'], row['分类'], row['金额'], row['备注'])
                    for _, row in self.data.iterrows()
                ]
                c.executemany(
                    'INSERT INTO records (日期, 类型, 分类, 金额, 备注) VALUES (?, ?, ?, ?, ?)',
                    data_tuples
                )
            
            self.conn.commit()
            self.dirty = False
            logger.info(f'数据保存成功，共 {len(self.data)} 条记录')
            messagebox.showinfo('保存成功', '数据已成功保存！')
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f'保存数据时数据库错误: {e}')
            messagebox.showerror('保存失败', f'数据库错误: {e}')
        except Exception as e:
            self.conn.rollback()
            logger.exception('保存数据时发生错误')
            messagebox.showerror('保存失败', f'保存过程中发生错误: {e}')

    def save_as(self):
        # 另存为新db文件
        new_path = filedialog.asksaveasfilename(defaultextension='.db', filetypes=[('SQLite数据库', '*.db')])
        if not new_path:
            return
        new_conn = None
        try:
            # 新建数据库并写入数据
            new_conn = sqlite3.connect(new_path)
            c = new_conn.cursor()
            c.execute(f'''CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                {TABLE_RECORDS_SCHEMA}
            )''')
            # 使用executemany批量插入，提升性能
            if not self.data.empty:
                data_tuples = [
                    (row['日期'], row['类型'], row['分类'], row['金额'], row['备注'])
                    for _, row in self.data.iterrows()
                ]
                c.executemany(
                    f'INSERT INTO {TABLE_NAME} (日期, 类型, 分类, 金额, 备注) VALUES (?, ?, ?, ?, ?)',
                    data_tuples
                )
            new_conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror('保存失败', f'数据库错误: {e}')
            return
        except Exception as e:
            messagebox.showerror('保存失败', f'保存过程中发生错误: {e}')
            return
        finally:
            # 无论成功失败都关闭新库连接，避免连接泄漏
            if new_conn is not None:
                new_conn.close()
        self.db_path = new_path
        self.conn.close()
        self.conn = sqlite3.connect(self.db_path)
        messagebox.showinfo('另存为成功', f'数据已另存为 {self.db_path}')
        self.dirty = False
        self.data = self.load_data()
        self.refresh_table()
        self.update_db_path_display()

    def new_db(self):
        # 新建一个空数据库文件
        if self.dirty:
            res = messagebox.askyesnocancel('未保存更改', '当前数据尚未保存，是否先保存？')
            if res is None:
                return
            elif res:
                self.save_data()
        new_path = filedialog.asksaveasfilename(defaultextension='.db', filetypes=[('SQLite数据库', '*.db')])
        if not new_path:
            return
        # 关闭旧连接
        if self.conn:
            try:
                self.conn.close()
            except Exception:
                pass
        # 创建新数据库并初始化表
        self.db_path = new_path
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.create_table()
        # 清空当前数据并刷新界面
        self.data = self.load_data()
        self.dirty = False
        self.refresh_table()
        self.update_db_path_display()
        messagebox.showinfo('新建成功', f'已创建新的数据库：{self.db_path}')

    def open_db(self):
        # 打开并切换数据库文件，默认路径为database目录
        if self.dirty:
            res = messagebox.askyesnocancel('未保存更改', '当前数据尚未保存，是否先保存？')
            if res is None:
                return
            elif res:
                self.save_data()
        db_path = filedialog.askopenfilename(
            title='打开账单数据库',
            filetypes=[('SQLite数据库', '*.db')],
            initialdir=os.path.abspath('./database')
        )
        if not db_path:
            return
        try:
            # 先尝试连接新数据库，成功后再关闭旧连接，避免切换失败导致状态损坏
            new_conn = sqlite3.connect(db_path)
        except sqlite3.Error as e:
            logger.error(f'打开数据库失败: {e}')
            messagebox.showerror('打开失败', f'无法打开数据库：{e}')
            return
        if self.conn:
            self.conn.close()
        self.db_path = db_path
        self.conn = new_conn
        self.create_table()
        self.data = self.load_data()
        self.refresh_table()
        self.dirty = False
        self.update_db_path_display()
        messagebox.showinfo('打开成功', f'已打开数据库：{self.db_path}')

    def create_widgets(self):
        # 输入区：BG_SUBTLE 底平面面板，内部栅格统一 8px 间距（设计稿 4.1-1）
        input_frame = ttk.Frame(self.master, style='Subtle.TFrame')
        input_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(input_frame, text='日期:').grid(row=0, column=0, padx=8, pady=8)
        self.date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        self.date_entry = DateEntry(input_frame, textvariable=self.date_var, date_pattern='yyyy-mm-dd', width=12, font=self.default_font)
        self.date_entry.grid(row=0, column=1, padx=8, pady=8)
        try:
            self.date_entry.bind('<Escape>', lambda e: self._on_de_escape(self.date_entry), add='+')
        except Exception:
            pass

        ttk.Label(input_frame, text='类型:').grid(row=0, column=2, padx=8, pady=8)
        self.type_var = tk.StringVar(value='支出')
        self.type_combo = ttk.Combobox(input_frame, textvariable=self.type_var, values=['支出', '收入'], width=8, state='readonly')
        self.type_combo.grid(row=0, column=3, padx=8, pady=8)

        ttk.Label(input_frame, text='分类:').grid(row=0, column=4, padx=8, pady=8)
        self.cat_var = tk.StringVar(value=CATEGORIES[0])
        self.cat_combo = ttk.Combobox(input_frame, textvariable=self.cat_var, values=CATEGORIES, width=10, state='readonly')
        self.cat_combo.grid(row=0, column=5, padx=8, pady=8)

        ttk.Label(input_frame, text='金额:').grid(row=0, column=6, padx=8, pady=8)
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(input_frame, textvariable=self.amount_var, width=10)
        self.amount_entry.grid(row=0, column=7, padx=8, pady=8)

        ttk.Label(input_frame, text='备注:').grid(row=0, column=8, padx=8, pady=8)
        self.note_var = tk.StringVar()
        self.note_entry = ttk.Entry(input_frame, textvariable=self.note_var, width=15)
        self.note_entry.grid(row=0, column=9, padx=8, pady=8)

        self.add_btn = ttk.Button(input_frame, text='添加', style='Accent.TButton', command=self.add_record)
        self.add_btn.grid(row=0, column=10, padx=8, pady=8)

        # 设置输入区所有控件字体
        for child in input_frame.winfo_children():
            try:
                child.configure(font=self.default_font)
            except Exception:
                pass

        # （已移除导入导出按钮，统一放入菜单栏）

        # --- 表格区 ---
        table_frame = ttk.Frame(self.master)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        columns = ['日期', '类型', '分类', '金额', '备注']
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12, selectmode='extended')
        self.tree.bind('<Double-1>', self.on_tree_double_click)  # 双击行编辑
        for col in columns:
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_by_column(_col))
            # 金额列右对齐（设计稿 NUMERIC），其余列居中
            anchor = 'e' if col == '金额' else 'center'
            self.tree.column(col, width=90, anchor=anchor)
        self._sort_column = None  # 当前排序列
        self._sort_asc = True     # 当前排序方向
        # 斑马行与收支语义色标签（设计稿 4.1-2）
        self.tree.tag_configure('even', background=ROW_STRIPE)
        self.tree.tag_configure('income', foreground=INCOME)
        self.tree.tag_configure('expense', foreground=EXPENSE)
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        # 按钮区：删除类操作降为文字按钮，弱化误触（设计稿 4.1-3）
        btn_frame = ttk.Frame(self.master)
        btn_frame.pack(fill='x', padx=10, pady=(0,5))
        self.delete_btn = ttk.Button(btn_frame, text='删除选中账单', style='DangerText.TButton', command=self.delete_record)
        self.delete_btn.pack(side='left', padx=(0, 20))
        self.delete_all_btn = ttk.Button(btn_frame, text='删除全部', style='MutedText.TButton', command=self.delete_all_records)
        self.delete_all_btn.pack(side='left', padx=0)

        # 统计区：BG_SUBTLE 底栏，大数字 + CAPTION 说明（设计稿 4.1-4）
        stats_frame = ttk.Frame(self.master, style='Subtle.TFrame')
        stats_frame.pack(fill='x', padx=10, pady=5)

        # 左侧：总收入/总支出大数字（INCOME/EXPENSE 色）+ CAPTION 说明
        family = pick_font_family()
        income_frame = ttk.Frame(stats_frame, style='Subtle.TFrame')
        income_frame.pack(side='left', padx=(12, 24), pady=6)
        self.income_value_label = ttk.Label(income_frame, text='0.00', style='Subtle.TLabel',
                                            font=(family, 14), foreground=INCOME)
        self.income_value_label.pack(side='left')
        ttk.Label(income_frame, text=' 总收入', style='Subtle.TLabel',
                  font=(family, 11), foreground=TEXT_MUTED).pack(side='left')

        expense_frame = ttk.Frame(stats_frame, style='Subtle.TFrame')
        expense_frame.pack(side='left', padx=(0, 24), pady=6)
        self.expense_value_label = ttk.Label(expense_frame, text='0.00', style='Subtle.TLabel',
                                             font=(family, 14), foreground=TOTAL_EXPENSE)
        self.expense_value_label.pack(side='left')
        ttk.Label(expense_frame, text=' 总支出', style='Subtle.TLabel',
                  font=(family, 11), foreground=TEXT_MUTED).pack(side='left')

        # 右侧：当前数据库路径（10px TEXT_MUTED）
        self.db_path_label = ttk.Label(stats_frame, text='', style='Subtle.TLabel',
                                       font=(family, 10), foreground=TEXT_MUTED)
        self.db_path_label.pack(side='right', padx=12)
        self.update_db_path_display()

        # 已去除右下角显示图表按钮


    def add_record(self):
        date = self.date_var.get()
        type_ = self.type_var.get()
        cat = self.cat_var.get()
        amount = self.amount_var.get()
        note = self.note_var.get()
        try:
            amount = float(amount)
        except ValueError:
            logger.warning(f'添加记录失败：金额格式错误 - {amount}')
            messagebox.showerror('输入错误', '金额必须为数字')
            return
        if not date or not type_ or not cat:
            logger.warning('添加记录失败：信息不完整')
            messagebox.showerror('输入错误', '请填写完整信息')
            return
        try:
            # 日期格式化
            try:
                date_fmt = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
            except Exception:
                date_fmt = datetime.now().strftime("%Y-%m-%d")
            new_row = {'日期': date_fmt, '类型': type_, '分类': cat, '金额': amount, '备注': note}
            self.data = pd.concat([self.data, pd.DataFrame([new_row])], ignore_index=True)
            self.dirty = True
            self.refresh_table()
            self.clear_inputs()
            logger.info(f'添加记录成功：{type_} - {cat} - {amount}元')
            messagebox.showinfo('添加成功', '账单添加成功！')
        except Exception as e:
            logger.exception('添加记录失败')
            messagebox.showerror('添加失败', f'账单添加失败：{e}')

    def clear_inputs(self):
        self.amount_var.set('')
        self.note_var.set('')
        self.date_var.set(datetime.now().strftime('%Y-%m-%d'))
        self.type_var.set('支出')
        self.cat_var.set(CATEGORIES[0])

    def refresh_table(self, filtered_df=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        # 用于筛选和排序的数据
        df = filtered_df if filtered_df is not None else self.data
        for i, (idx, row) in enumerate(df.iterrows()):
            # 斑马行 even/odd + 收支语义色 income/expense（类型列文字着色）
            stripe_tag = 'even' if i % 2 == 0 else 'odd'
            type_tag = 'income' if row['类型'] == '收入' else 'expense'
            self.tree.insert('', 'end', iid=str(idx), values=(row['日期'], row['类型'], row['分类'], row['金额'], row['备注']),
                             tags=(stripe_tag, type_tag))
        self.update_stats()

    def update_stats(self):
        # 在局部副本上计算统计，避免把 NaN 改写为 0 污染 self.data 后被保存
        df = self.data.copy()
        df['金额'] = pd.to_numeric(df['金额'], errors='coerce').fillna(0)
        income = df[df['类型'] == '收入']['金额'].sum()
        expense = df[df['类型'] == '支出']['金额'].sum()
        self.income_value_label.config(text=f'{income:.2f}')
        self.expense_value_label.config(text=f'{expense:.2f}')

    def update_db_path_display(self):
        """更新当前数据库路径显示"""
        # 将路径转换为绝对路径显示，更直观
        abs_path = os.path.abspath(self.db_path)
        # 如果路径太长，显示后半部分
        max_len = 50
        if len(abs_path) > max_len:
            display_path = '...' + abs_path[-(max_len-3):]
        else:
            display_path = abs_path
        self.db_path_label.config(text=f'当前数据库: {display_path}')
        # 添加悬浮提示显示完整路径
        self.db_path_label.tooltip_text = abs_path

    # 存储当前筛选条件
    def apply_filter(self, filter_dict=None):
        df = self.data.copy()
        # 从 filter_dict 读取筛选条件
        if filter_dict is not None:
            self._current_filter = filter_dict
        else:
            filter_dict = getattr(self, '_current_filter', {})
        # 日期筛选
        start = filter_dict.get('start', '').strip()
        end = filter_dict.get('end', '').strip()
        if start:
            df = df[df['日期'] >= start]
        if end:
            df = df[df['日期'] <= end]
        # 金额筛选
        min_amt = filter_dict.get('min_amt', '').strip()
        max_amt = filter_dict.get('max_amt', '').strip()
        df['金额'] = pd.to_numeric(df['金额'], errors='coerce').fillna(0)
        if min_amt:
            try:
                df = df[df['金额'] >= float(min_amt)]
            except ValueError:
                messagebox.showerror('筛选错误', '最小金额必须为数字')
                return
        if max_amt:
            try:
                df = df[df['金额'] <= float(max_amt)]
            except ValueError:
                messagebox.showerror('筛选错误', '最大金额必须为数字')
                return
        # 类型筛选
        t = filter_dict.get('type', '')
        if t and t != '全部':
            df = df[df['类型'] == t]
        # 分类筛选
        c = filter_dict.get('cat', '')
        if c and c != '全部':
            df = df[df['分类'] == c]
        # 排序（如有）
        if self._sort_column:
            df = df.sort_values(self._sort_column, ascending=self._sort_asc)
        self.refresh_table(filtered_df=df)

    def clear_filter(self):
        self._current_filter = {}
        self.refresh_table()

    def open_filter_dialog(self):
        dialog = FilterDialog(self.master, getattr(self, '_current_filter', {}), self.default_font)
        self.master.wait_window(dialog)
        if dialog.result is not None:
            if dialog.result == '__clear__':
                self.clear_filter()
            else:
                self.apply_filter(dialog.result)

    def _close_date_popup(self, de: DateEntry):
        try:
            top = getattr(de, '_top_cal', None)
            if top is None:
                return
            if not top.winfo_exists():
                return
            try:
                top.event_generate('<Escape>')
            except Exception as e:
                logger.warning(f'关闭日期弹窗时出错: {e}')
            try:
                for child in top.winfo_children():
                    try:
                        child.event_generate('<Escape>')
                    except Exception as e:
                        logger.warning(f'关闭日期弹窗时出错: {e}')
            except Exception as e:
                logger.warning(f'关闭日期弹窗时出错: {e}')
            try:
                top.withdraw()
            except Exception as e:
                logger.warning(f'关闭日期弹窗时出错: {e}')
        except Exception as e:
            logger.warning(f'关闭日期弹窗时出错: {e}')

    def _on_de_escape(self, de: DateEntry):
        try:
            self._close_date_popup(de)
        except Exception:
            pass
        return 'break'

    def sort_by_column(self, col):
        # 切换排序方向
        if self._sort_column == col:
            self._sort_asc = not self._sort_asc
        else:
            self._sort_column = col
            self._sort_asc = True
        self.apply_filter()  # 排序与筛选结合

    def on_tree_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
        idx = int(item_id)
        # 筛选态下 iid 是原始索引标签，按标签取值防止 iloc 按位置错位
        if idx not in self.data.index:
            logger.warning(f'编辑记录失败：索引 {idx} 不在当前数据中，已取消编辑')
            return
        record = self.data.loc[idx].to_dict()
        dialog = EditRecordDialog(self.master, record, self.default_font)
        self.master.wait_window(dialog)
        if dialog.result:
            # 更新 DataFrame
            self.data.loc[idx, ['日期', '类型', '分类', '金额', '备注']] = [
                dialog.result['日期'],
                dialog.result['类型'],
                dialog.result['分类'],
                float(dialog.result['金额']),
                dialog.result['备注']
            ]
            self.dirty = True
            self.save_data()
            self.refresh_table()

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('未选中', '请先选中要删除的账单')
            return
        # 二次确认
        if not messagebox.askyesno('确认删除', f'确定要删除选中的 {len(selected)} 条账单吗？此操作不可撤销。'):
            return
        # 支持多选删除
        idxs = sorted([int(iid) for iid in selected], reverse=True)
        self.data = self.data.drop(index=idxs).reset_index(drop=True)
        self.dirty = True
        self.refresh_table()
        logger.info(f'删除记录成功：共 {len(idxs)} 条')
        messagebox.showinfo('删除成功', f'已删除 {len(idxs)} 条账单')

    def delete_all_records(self):
        if self.data.empty:
            messagebox.showinfo('无数据', '没有可删除的账单。')
            return
        if not messagebox.askyesno('确认删除全部', '确定要删除全部账单吗？此操作不可撤销。'):
            return
        self.data = self.data.iloc[0:0].copy()
        self.dirty = True
        self.refresh_table()
        logger.info('删除全部记录成功')
        messagebox.showinfo('删除成功', '已删除全部账单')

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV文件', '*.csv')])
        if file_path:
            self.data.to_csv(file_path, index=False, encoding='utf-8-sig')
            logger.info(f'导出CSV成功：{file_path}，共 {len(self.data)} 条记录')
            messagebox.showinfo('导出成功', f'数据已导出到 {file_path}')

    def show_chart(self):
        if self.chart_window and tk.Toplevel.winfo_exists(self.chart_window):
            self.chart_window.lift()
            return
        self.chart_window = tk.Toplevel(self.master)
        self.chart_window.title('图表统计')
        self.chart_window.geometry('700x500')
        tab_control = ttk.Notebook(self.chart_window)
        tab1 = ttk.Frame(tab_control)
        tab2 = ttk.Frame(tab_control)
        tab_control.add(tab1, text='收支趋势')
        tab_control.add(tab2, text='分类统计')
        tab_control.pack(expand=1, fill='both')
        # 收支趋势
        fig1 = self.plot_trend()
        canvas1 = FigureCanvasTkAgg(fig1, master=tab1)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill='both', expand=True)
        # 分类统计
        fig2 = self.plot_category()
        canvas2 = FigureCanvasTkAgg(fig2, master=tab2)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill='both', expand=True)
        # 图表窗口销毁时关闭 figure，防止 matplotlib figure 泄漏
        def on_chart_window_destroy(event):
            plt.close(fig1)
            plt.close(fig2)
        self.chart_window.bind('<Destroy>', on_chart_window_destroy)

    def plot_trend(self):
        # 设置中文字体，避免图表标题/坐标轴中文显示为方块
        plt.rcParams['font.sans-serif'] = CJK_FONT_FALLBACK  # 中文字体按平台回退选择
        plt.rcParams['axes.unicode_minus'] = False
        df = self.data.copy()
        if df.empty:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, '暂无数据', ha='center', va='center')
            return fig
        df['日期'] = pd.to_datetime(df['日期'])
        df = df.sort_values('日期')
        trend = df.groupby(['日期', '类型'])['金额'].sum().unstack(fill_value=0)
        fig, ax = plt.subplots(figsize=(6,4))
        trend.plot(ax=ax, marker='o')
        ax.set_title('每日收支趋势')
        ax.set_xlabel('日期')
        ax.set_ylabel('金额')
        ax.legend(['支出', '收入'])
        plt.tight_layout()
        return fig

    def plot_category(self):
        # 设置中文字体，避免图表标题中文显示为方块
        plt.rcParams['font.sans-serif'] = CJK_FONT_FALLBACK  # 中文字体按平台回退选择
        plt.rcParams['axes.unicode_minus'] = False
        df = self.data.copy()
        if df.empty:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, '暂无数据', ha='center', va='center')
            return fig
        expense = df[df['类型'] == '支出'].groupby('分类')['金额'].sum()
        income = df[df['类型'] == '收入'].groupby('分类')['金额'].sum()
        fig, axs = plt.subplots(1, 2, figsize=(10,4))
        # 支出分类
        if not expense.empty:
            axs[0].pie(expense, labels=expense.index, autopct='%1.1f%%')
            axs[0].set_title('支出分类')
        else:
            axs[0].text(0.5, 0.5, '无支出数据', ha='center', va='center')
        # 收入分类
        if not income.empty:
            axs[1].pie(income, labels=income.index, autopct='%1.1f%%')
            axs[1].set_title('收入分类')
        else:
            axs[1].text(0.5, 0.5, '无收入数据', ha='center', va='center')
        plt.tight_layout()
        return fig

    def on_close(self):
        try:
            if self.dirty:
                res = messagebox.askyesnocancel('未保存更改', '当前数据尚未保存，是否保存后退出？')
                if res is None:
                    logger.info('用户取消退出')
                    return  # 取消
                elif res:
                    logger.info('用户选择保存后退出')
                    self.save_data()
                else:
                    logger.info('用户选择不保存直接退出')
            # 关闭数据库连接
            if self.conn:
                try:
                    self.conn.close()
                    self.conn = None
                    logger.debug('数据库连接已关闭')
                except Exception as e:
                    logger.warning(f'关闭数据库连接时出错: {e}')
        except Exception as e:
            logger.error(f'退出清理时发生错误: {e}')
        finally:
            logger.info('应用窗口关闭')
            # 销毁窗口后 mainloop 会自然结束，不再强制退出进程
            try:
                self.master.destroy()
            except Exception as e:
                logger.warning(f'销毁窗口时出错: {e}')
