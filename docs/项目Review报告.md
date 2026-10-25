# 记账本项目 Review 报告

- **项目名称**：bookKeeping（Windows 桌面记账本）
- **技术栈**：Python 3.8+ / tkinter / SQLite / pandas / matplotlib
- **代码规模**：核心代码约 1600 行（ui/main_window.py ~965 行、ui/dialogs.py ~329 行、ui/charts.py ~120 行、db/database.py 93 行、model/record_model.py 58 行），测试 43 个用例
- **Review 日期**：2026-07-19
- **Review 范围**：架构、代码质量、Bug 隐患、测试、工程规范、文档

---

## 一、总体评价

这是一个完成度较高的单人小型项目：功能闭环完整（记账/筛选/统计/图表/第三方账单导入/多库管理），分层意识清晰（`db` / `model` / `ui` / `utils`），测试可 headless 运行，文档（需求规格、软件设计说明书）齐全，代码中能看到不少用心的设计（参数化查询、executemany 批量插入、导入流程四步抽象、删除二次确认等）。

主要问题集中在四个方面：**个别真实 Bug（P0）**、**资源管理与全局状态污染**、**测试断言薄弱**、**工程杂项（.pyc 入库、requirements 臃肿）**。

**质量评级：B+（功能完整、可运行；修复 P0/P1 问题后可到 A-）**

---

## 二、严重 Bug（P0，建议立即修复）

### 2.1 筛选状态下双击编辑会改错记录 ★★★★★

**位置**：`ui/main_window.py` L679 / L822-836

```python
# refresh_table 中，iid 用的是 DataFrame 的【索引标签】
self.tree.insert('', 'end', iid=str(idx), values=...)   # L679

# on_tree_double_click 中：
idx = int(item_id)                       # L822，拿到的是筛选后 df 的标签
record = self.data.iloc[idx].to_dict()   # L822，iloc 按【位置】取 —— 错位！
self.data.loc[idx, [...]] = ...          # L827，loc 按【标签】写
```

未筛选时索引恰好连续，两种取法结果一致；一旦经过 `apply_filter` 传入 `filtered_df`（L677），树中 iid 是原始数据的索引标签（如原始第 100 行），此时 `iloc[100]` 取到的是**筛选结果的第 100 行**——编辑筛选后的记录会写错到另一条原始记录上，随后自动 `save_data()` 落库，错误被持久化。

**修复建议**：统一使用标签索引（`self.data.loc[idx]` 读取），或让树 iid 始终映射到 `self.data.index` 并在写入时校验 `idx in self.data.index`。

### 2.2 `update_stats` 静默把 NaN 金额改写为 0 并污染待保存数据 ★★★★

**位置**：`ui/main_window.py` L684

```python
def update_stats(self):
    self.data['金额'] = pd.to_numeric(self.data['金额'], errors='coerce').fillna(0)
```

`refresh_table → update_stats` 在多处被调用。原始数据中的非法金额（NaN）会被静默改成 0；此后任何触发 `save_data()` 的操作（如双击编辑，见 2.1）都会把这份"被修复"的数据全量覆盖写库——用户未确认的数据修改被持久化，且无从察觉。

**修复建议**：统计时操作副本（`df = self.data.copy()`），展示层做容错，不反向写回 `self.data`。

---

## 三、重要问题（P1）

### 3.1 `charts.py` 原地修改调用方 DataFrame

**位置**：`ui/charts.py` L48

```python
def show_single_month_pie(df, master):
    df['日期'] = pd.to_datetime(df['日期'])   # 无 copy()，直接改 self.data
```

同文件 L15 的 `show_monthly_chart` 做了 `df.copy()`，此处遗漏。查看一次饼图后，`self.data['日期']` 列 dtype 被永久改变，后续 L715 的字符串日期比较等行为可能异常。

### 3.2 matplotlib figure 永不关闭，内存泄漏

- `ui/charts.py` L78：饼图月份导航每次点击"上一月/下一月"都 `plt.subplots(1, 2)` 新建 figure，旧 canvas 被 destroy 但 figure 对象留在 pyplot 全局 registry 中，连续翻月无限累积。
- `ui/main_window.py` L897-930：`plot_trend` / `plot_category` 创建的 figure 同样没有 `plt.close(fig)`。

**修复建议**：在窗口 destroy 回调或翻页逻辑里 `plt.close(fig)`；或改用纯 OOP 方式（`Figure` + `FigureCanvasTkAgg`），不经过 pyplot 全局状态。

### 3.3 单文件多连接混用，存在 `database is locked` 隐患

**位置**：`ui/main_window.py` L393（常驻连接 `self.conn`）vs `db/database.py` L48/L71（每次新开连接）

主窗口持有常驻连接跨多次 commit，`db/database.py` 的函数又各自新建连接访问同一文件。SQLite 同一时刻只允许一个写事务；tkinter 单线程下暂难触发，但常驻连接若处于未提交事务状态，`save_data` 的新连接会立即报 locked。此外 `open_db` 切换失败时旧连接已关闭但未置 None，后续操作会在已关闭连接上进行，状态不可恢复（L532-534）。

**修复建议**：全局只保留一个连接；`open_db` 失败时回滚 `self.conn` 状态。

### 3.4 `load_data` 异常路径泄漏数据库连接

**位置**：`db/database.py` L48-57

```python
conn = sqlite3.connect(db_path)
...
conn.close()   # L56，查询抛异常时执行不到
```

同文件 `save_data`（L92-93）已用 `finally: conn.close()`，`load_data` 与 `ensure_db` 却没有。建议统一改用 `with contextlib.closing(sqlite3.connect(db_path)) as conn:`。

### 3.5 耗时 IO 全部在主线程，界面冻结

微信账单 `pd.read_excel`（main_window.py L367）、CSV 解析、`save_data` 的全量 DELETE + executemany（L414-442）均在按钮回调中同步执行。导入几千行 Excel 时界面完全卡死无响应。项目无任何 `threading` / `after` 的使用。对小数据量可容忍，但作为产品体验缺陷值得记录。

### 3.6 重复的"双重错误弹窗"

**位置**：`ui/main_window.py` L641-642 / L646-647

金额非法时连续弹出"输入错误"和"添加失败"两个内容几乎相同的错误框，用户一次输错要点击 4 次。系重构残留，应合并。

---

## 四、中等问题（P2）

| # | 问题 | 位置 | 说明 |
|---|------|------|------|
| 1 | 大量裸 `except Exception: pass` | main_window.py L553/L583/L769-784；dialogs.py L31/L41/L104 | `_close_date_popup` 连续 4 层嵌套 try/except 把所有错误（含编程错误）全部吞掉，出问题无从排查 |
| 2 | `on_close` 使用 `os._exit(0)` | main_window.py L962-965 | 跳过 atexit、不 flush 日志，危险兜底；`import sys` 写在函数体内 |
| 3 | `save_as` 中 `new_conn` 泄漏 | main_window.py L455-471 | `executemany` 抛异常时 new_conn 无 finally close |
| 4 | `_current_filter` / `_sort_column` 靠调用顺序隐式初始化 | main_window.py L708/L597-598 | 属性存在与否取决于代码执行路径，逻辑顺序一变即 AttributeError |
| 5 | 收支判断用单字符包含 | main_window.py L306 / L356 | `'收入' if '入' in str(x) else '支出'`，异常值（空串、"转账"）一律归为"支出"，分类逻辑脆弱 |
| 6 | 日期解析未处理 NaT | model/record_model.py L26 | `pd.to_datetime` 对脏日期产生 NaT，`df['年月']` 混入异常月份行 |
| 7 | 月度表列筛选三元表达式无实际意义 | main_window.py L89 | 条件与结果逻辑矛盾，靠 L107 `row.get(..., 0)` 兜底 |
| 8 | 中文列名 + 中文表名贯穿全项目 | 全局 | SQLite 支持无碍，但 IDE 无法补全/重构，跨工具可移植性差，属风格权衡 |

---

## 五、代码重复（建议提取公共逻辑）

1. **三个 import 函数的异常处理块几乎相同**（main_window.py L267-283 / L315-333 / L365-379），约 15 行 × 3。
2. **树排序逻辑重复 4 处**：`show_monthly_bill.treeview_sort_column`（L116）、`show_month_detail`（L167）、`PreviewDialog._refresh_tree`（L272）、`RecordBook.sort_by_column`（L808）。且 PreviewDialog 有日期列临时排序处理（L280-284），其余三处没有，行为不一致。
3. **DateEntry Escape 兼容 hack 重复约 60 行**（main_window.py L760-806 与 dialogs.py L96-127）；且 main_window 的 `_on_escape`（L786）定义后**从未绑定任何事件，是死代码**。
4. **中文字体设置重复**（charts.py L10-11 vs L43-44），且 main_window 的图表函数（L897+）完全没设中文字体，月度图标题/图例会显示为方块（□□）。
5. **`data_tuples` 构建代码重复**（main_window.py L421-429 与 L461-469）。
6. **死代码**：`FilterDialog.split_date`（dialogs.py L69-76）无任何调用者；`db/database.py` 的 `ensure_db` 未被 ui 层引用；`utils/constants.py` 的 `ALLOWED_TABLES` 白名单仅在 `save_as` 中与另一个模块级常量互比，属无效防御（已于本次修复中移除，README 相关表述同步更正）。

## 六、架构层面观察

1. **上帝类**：`RecordBook` 单类 965 行，同时承担 UI 构建、数据库 IO、导入导出、筛选、统计、图表。`db/database.py` 本已存在且有同名函数，但 main_window 又自行实现了 `ensure_db/create_table/load_data/save_data`，形成两套并行实现，职责重叠/遮蔽。建议让 UI 层只持有 `db.database` 的句柄。
2. **交互逻辑不一致**：双击编辑后立即自动 `save_data()` 落库（L835），而 `add_record`/`delete_record` 只置 `self.dirty` 标志不保存（L624）。增、删、改三种操作的持久化策略应统一。
3. **相对路径依赖 CWD**：`DB_DEFAULT = './database/root.db'`（constants.py L4）与 `LOG_DIR = Path('./logs')`（logger.py L17）都依赖工作目录，打包成 exe 后 CWD 不固定会导致建库/日志位置漂移。建议改用 `Path(__file__).parent` 锚定。
4. **命名易混淆**：代码包 `db/` 与数据目录 `database/` 同名；`load_path/`（账单导入源目录）表意不清，建议 `imports/`；`test_env/` 是另一套虚拟环境，与 `venv/` 并存令人困惑。

---

## 七、测试评估

**总体**：43 个用例、不依赖真实 UI（Tk 全部 mock，可 headless 运行）、数据库测试用 `tmp_path` 隔离、数据层 roundtrip 断言扎实。属于"有骨架、缺肌肉"。

**主要薄弱点**：

1. **假断言**：`test_charts.py` 中 6 处直接 `assert True`（L91/L166/L241/L340/L386/L455），只验证"没抛异常"。
2. **统计测试未验证数值**：`test_main_window.py:54` 只断言 label.config 被调用，没断言"总收入 1000、总支出 80"的文本内容（注释里写了却没断言）。
3. **筛选测试只断言 mock 被调用**：`test_apply_filter_date_range` / `test_apply_filter_by_type` 只断言 `refresh_table` 被调用，**没有断言筛选结果行数/内容**——筛选逻辑全错也能通过。
4. **核心功能零测试**：微信/支付宝账单导入（`skiprows=24`/`header=16` 的列映射、收支转换）是本项目特色功能，却完全没有测试；数据库切换/保存确认流程无测试；`utils/logger.py`、`main.py`、`constants.py` 无测试。
5. **mock 姿势问题**：`test_main_window.py` 每个测试嵌套 8~12 层 `with patch(...)` 且重复样板代码，无共享 fixture；`test_dialogs.py:73/85` 直接改写 `sys.modules`，有全局状态污染风险；Dummy 类在 `test_charts.py` 中复制粘贴约 150 行。

---

## 八、工程规范问题

1. **9 个 `.pyc` 仍在 git 索引中**：提交 f9430c1 声称 "stop tracking compiled pyc files" 但未生效（`db/model/ui/utils` 各包的 `__pycache__` 内 cpython-311/313 双版本残留）。需 `git rm --cached` 清理。
2. **`.gitignore` 缺 `test_env/`**：目前靠 `test_env/.gitignore`（内容 `*`）兜底，内部文件一旦被删就会被提交。同时建议补 `.idea/`、`.vscode/`、`build/`、`dist/`。
3. **`.gitignore` 对 `load_path/` 的规则形同虚设**：`load_path/bill-1.csv`、`bill-2.csv` 已被跟踪，忽略规则不作用于已跟踪文件，需 `git rm --cached`。
4. **requirements.txt 是 `pip freeze` 全量输出**：18 个包中仅 5 个是直接依赖（`matplotlib`、`pandas`、`openpyxl`、`tkcalendar`、`pytest`）；`babel/contourpy/cycler/fonttools/kiwisolver/packaging/python-dateutil/pytz/tzdata/six/numpy/pillow` 均为传递依赖，`setuptools` 为构建工具——都不应出现在运行时 requirements 中。

---

## 九、亮点（值得保持的做法）

1. **导入流程抽象好**：`_parse_and_import`（main_window.py L210）统一"映射→标准化→预览→导入"四步，三个导入入口只做格式差异。
2. **数据库写入规范**：全项目参数化查询（`?` 占位符），`executemany` 批量插入，事务 commit/rollback/finally-close 三段式，高频查询列建了 3 个索引。
3. **防呆设计**：删除二次确认；未保存更改在 `new_db`/`open_db`/`on_close` 三处有一致的 askyesnocancel 流程。
4. **导入错误处理细致**：区分 FileNotFoundError / UnicodeDecodeError / EmptyDataError / ParserError，均有用户友好的中文提示。
5. **`PreviewDialog` 支持预览中双击编辑回写**并保留原索引，日期列有专门排序处理。
6. **日志系统完善**：UTF-8 文件 handler、第三方库降噪、关键操作分级记录、main.py 用 `logger.exception` 记完整堆栈。
7. **常量集中**：表结构 DDL、分类列表、默认路径抽在 `constants.py`；docstring 规范（含 Args/Returns/Example，部分含 doctest）。
8. **文档齐全**：需求规格说明书、软件设计说明书与实际代码基本一致（历史 review 文档已核对过一致性）。

---

## 十、修复优先级清单

| 优先级 | 事项 | 位置 |
|--------|------|------|
| P0 | 修复筛选态编辑错位（iloc/loc 混用） | main_window.py L679/L822-827 |
| P0 | `update_stats` 停止污染 `self.data` | main_window.py L684 |
| P1 | `show_single_month_pie` 加 `df.copy()` | charts.py L48 |
| P1 | matplotlib figure 使用后 `plt.close`；主窗口图表补中文字体 | charts.py / main_window.py |
| P1 | 统一为单一数据库连接；`open_db` 失败可恢复 | main_window.py L393/L516 |
| P1 | `load_data`/`ensure_db` 连接用 try/finally 关闭 | db/database.py L48 |
| P2 | 导入/保存 IO 移出主线程（threading + after） | main_window.py |
| P2 | 合并重复错误弹窗；收敛 `except: pass` | main_window.py L641-647 等 |
| P2 | 收支分类判断改精确匹配 | main_window.py L306/L356 |
| P3 | 提取公共逻辑（import 异常块、树排序、DateEntry hack）；删除死代码 | 多处 |
| P3 | 测试补强：假断言改真断言、补导入功能测试、共享 fixture | test/ |
| P3 | 工程清理：`git rm --cached` 9 个 pyc + 2 个 bill csv；`.gitignore` 加 `test_env/`；精简 requirements.txt | 根目录 |

---

*附：本报告基于 2026-07-19 工作区代码（HEAD 16423ca，另有 main.py 与 docs/CodeReview_Report.md 两处未提交变更）。报告中所有问题均经源码核实并附行号。*
