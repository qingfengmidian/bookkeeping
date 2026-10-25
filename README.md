# 记账本程序（跨平台桌面版）

本项目是一个简洁高效的跨平台桌面记账本程序（支持 Windows / macOS / Linux），支持收入/支出账单管理、可视化统计与数据导出。适合个人日常财务记录与分析。

## 功能简介

### 核心功能
- 添加收入/支出账单（支持分类、金额、日期、备注）
- 显示账单列表、统计总收入/支出
- 双击编辑账单记录
- 支持单条/批量删除记录
- 账单筛选（按日期、金额、类型、分类）

### 数据导入
- 标准 CSV 文件导入
- 支付宝账单导入（自动识别列映射）
- 微信账单导入（自动识别列映射）
- 导入预览与编辑功能

### 数据统计与可视化
- 月度账单统计
- 月度收支柱状图
- 单月分类饼图（支持切换月份）
- 双击查看当月明细

### 系统管理
- 多数据库文件管理（新建/打开/切换）
- 数据另存为
- 一键导出 CSV
- 状态栏显示当前数据库路径
- 应用日志记录（保存于 logs/ 目录）

## 项目结构说明

```text
windsurf/
├─ main.py                # 主入口，仅负责启动程序
├─ db/
│    └─ database.py       # 数据库相关操作（SQLite）
├─ model/
│    └─ record_model.py   # 数据模型与数据处理
├─ ui/
│    ├─ main_window.py    # 主窗口类（RecordBook）
│    ├─ dialogs.py        # 各种弹窗（筛选、编辑、导入映射、预览等）
│    └─ charts.py         # 图表绘制与嵌入
├─ utils/
│    ├─ constants.py      # 常量（分类、默认路径等）
│    └─ logger.py         # 日志配置模块
├─ test/                  # 单元测试
│    ├─ test_database.py
│    ├─ test_record_model.py
│    ├─ test_dialogs.py
│    ├─ test_main_window.py
│    ├─ test_charts.py
│    └─ test_ui_charts.py
├─ requirements.txt       # 依赖包
├─ README.md              # 项目说明
└─ docs/                  # 文档
     ├─ 软件设计说明书.md
     └─ 需求规格说明书.md
```

- `main.py` 只负责应用启动，集成日志系统。
- `db/database.py` 提供数据库操作，支持批量插入和索引优化。
- `model/record_model.py` 处理数据转换和统计计算。
- `ui/` 目录包含所有界面相关代码，主窗口使用分层架构。
- `utils/logger.py` 提供应用级别日志记录。
- `test/` 包含完整的单元测试覆盖。

## 导入数据

### CSV导入

导入的列包括：日期、类型、分类、金额、备注
示例格式

```
日期,类型,分类,金额,备注
2025-01-01,收入,工资,10000,无
2025-01-02,支出,吃饭,100,无
```

### 支付宝账单导入

支持支付宝账单 CSV 文件导入：
- 自动跳过前24行说明文字
- 自动识别中英文列名
- 自动映射字段（交易时间→日期，收/支→类型等）
- 支持导入预览和编辑

### 微信账单导入

支持微信账单 Excel 文件导入：
- 自动跳过前16行说明文字
- 自动去除金额中的 ¥ 符号
- 自动识别收入/支出类型
- 支持导入预览和编辑

## 运行

### 创建虚拟环境并安装依赖

Windows（PowerShell）：

```bash
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
```

macOS / Linux：

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

> Linux 需先安装 tkinter 系统包，如 Ubuntu/Debian：`sudo apt install python3-tk`。

### 运行程序

Windows：

```bash
.\venv\Scripts\python main.py
```

macOS / Linux：

```bash
./venv/bin/python main.py
```

程序启动后，日志将保存到 `logs/bookkeeping.log` 文件中。

### 执行测试用例

```bash
# Windows
.\venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
pytest
```

## 技术特点

- **安全性**：全部数据库写入使用参数化查询，防止 SQL 注入
- **性能**：数据库批量插入优化（executemany），自动创建索引
- **可维护性**：类型注解、文档字符串、模块化设计
- **可测试性**：完整的单元测试覆盖（43个测试用例）
- **用户体验**：精细化异常处理、操作反馈、状态栏显示

## 数据存储

数据默认存储在 `./database/root.db`（SQLite数据库），您可以通过菜单栏的「文件」→「打开/新建」来切换不同的数据库文件。

当前打开的数据库路径会显示在窗口底部状态栏右侧。

## 依赖要求

- Python 3.8+
- tkinter（内置）
- pandas >= 1.0
- matplotlib >= 3.0
- tkcalendar >= 1.6
- openpyxl >= 3.0
