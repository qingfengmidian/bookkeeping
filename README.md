# 记账本程序（Windows 桌面版）

本项目是一个简洁高效的 Windows 桌面记账本程序，支持收入/支出账单管理、可视化统计与数据导出。适合个人日常财务记录与分析。

## 功能简介
- 添加收入/支出账单（支持分类、金额、日期、备注）
- 显示账单列表、统计总收入/支出
- 图表统计（收支趋势、分类饼图等）
- 一键导出 CSV 文件

## 项目结构说明

```text
windsurf/
├─ main.py                # 主入口，仅负责启动程序
├─ db/
│    └─ database.py       # 数据库相关操作
├─ model/
│    └─ record_model.py   # 数据模型与数据处理
├─ ui/
│    ├─ main_window.py    # 主窗口类（RecordBook）
│    ├─ dialogs.py        # 各种弹窗（筛选、编辑、导入映射等）
│    └─ charts.py         # 图表绘制与嵌入
├─ utils/
│    └─ constants.py      # 常量（分类、默认路径等）
├─ requirements.txt       # 依赖包
├─ README.md              # 项目说明
```

- `main.py` 只负责应用启动。
- 业务逻辑全部分布在 `ui`、`db`、`model`、`utils` 等子模块中。
- 结构清晰，便于维护和扩展。

## 导入数据

### csv导入

导入的列包括：日期、类型、分类、金额、备注
示例格式

```
日期,类型,分类,金额,备注
2025-01-01,收入,工资,10000,无
2025-01-02,支出,吃饭,100,无
```

### 微信账单导入


### 支付宝账单导入

## 运行

如何创建虚拟环境并安装依赖

```
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
```


如何在虚拟环境中运行此程序

```
.\venv\Scripts\python main.py
```
