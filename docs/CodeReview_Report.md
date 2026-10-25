# 记账本项目代码审查报告

**审查日期**: 2026-05-23
**审查范围**: 源代码 + 测试用例 + 项目文档

---

## 1. 文档与代码不一致

| # | 不一致项 | 文档描述 | 代码实际 | 文件位置 |
|---|---------|---------|---------|----------|
| 1 | `edit_record` 方法缺失 | 设计说明书类图中 `RecordBook` 包含 `edit_record()` 方法 | 实际不存在该方法，编辑逻辑直接内联在 `on_tree_double_click` 事件处理中 | `ui/main_window.py:817` |
| 2 | 状态栏悬浮提示未实现 | 需求规格说明书 FR-019 要求"支持悬浮提示显示完整路径" | 仅设置了 `tooltip_text` 自定义属性，**未创建实际的 Tooltip 组件**，鼠标悬浮无任何效果 | `ui/main_window.py:701` |
| 3 | 微信导入文件过滤异常 | 需求 NFR-023 要求支持 `.xls` 和 `.xlsx` | `filetypes=[('Excel文件', '*.xls;*.xlsx')]`，该写法在部分 tkinter 版本中**无法正确过滤 `.xlsx` 文件** | `ui/main_window.py:362` |
| 4 | `load_data` 同名方法行为不一致 | `db/database.py` 的 `load_data` 返回不含 `id` 列的 DataFrame | `ui/main_window.py` 的同名 `load_data` 返回**包含 `id` 列**的 DataFrame，调用方需分别处理 | `db/database.py:38` vs `ui/main_window.py:404` |
| 5 | 表名常量未统一使用 | 设计说明书提到表名统一管理 | `db/database.py` 中 SQL 语句多处**硬编码字符串 `'records'`**，未使用 `utils/constants.py` 中定义的 `TABLE_NAME` 常量 | `db/database.py:51,75,84` |
| 6 | 设计说明书方法列表错误 | 类图/方法列表包含 `edit_record()` | 实际源码中不存在 | `docs/软件设计说明书.md` 4.1.1 |

---

## 2. 源代码优化建议

### 2.1 重大逻辑缺陷（必须修复）

#### 2.1.1 `charts.py` 污染传入的原始 DataFrame

**位置**: `ui/charts.py:48-49`

```python
# 当前代码（有缺陷）
df['日期'] = pd.to_datetime(df['日期'])
df['年月'] = df['日期'].dt.to_period('M').astype(str)
```

**问题**: 直接修改函数参数 `df`，会在调用方 DataFrame 上添加 `'年月'` 列，造成副作用。

**建议**:
```python
df = df.copy()
df['日期'] = pd.to_datetime(df['日期'])
df['年月'] = df['日期'].dt.to_period('M').astype(str)
```

---

#### 2.1.2 `charts.py` 图表内存泄漏

**位置**: `ui/charts.py:22`, `ui/charts.py:78`

**问题**: 每次调用 `plt.subplots()` 创建新的 Figure 对象，但从未调用 `plt.close(fig)` 释放。长期运行后内存持续增长。

**建议**: 在窗口关闭或重新绘图时调用 `plt.close(fig)`，或将 Figure 引用保存并在重绘时关闭旧对象。

---

#### 2.1.3 添加记录时重复弹窗

**位置**: `ui/main_window.py:638-642`

**问题**: 当金额格式错误时，会连续弹出两个错误对话框（`'输入错误'` 和 `'添加失败'`），用户需要点击两次才能继续。

**建议**: 保留一个错误提示即可，删除多余的第二次弹窗。

---

#### 2.1.4 强制退出过于粗暴

**位置**: `ui/main_window.py:939-965`

**问题**: `on_close` 中使用了 `sys.exit(0)` 和 `os._exit(0)` 强制终止进程。这会导致 tkinter 清理逻辑无法执行，可能产生资源泄漏或窗口残留。

**建议**: 仅调用 `self.master.destroy()` 让 Tkinter 主循环正常结束，移除 `sys.exit()` 和 `os._exit()`。

---

### 2.2 数据与性能问题

#### 2.2.1 `model/record_model.py` 列结构不稳定

**位置**: `model/record_model.py:28-30`

**问题**: `process_monthly` 返回的 DataFrame 列结构取决于输入数据——当只有"收入"或只有"支出"时，返回的列不同。下游代码（排序、导出、测试）需要处理不确定的列结构。

**建议**: 始终确保返回的 DataFrame 包含 `['收入', '支出', '总收入', '总支出']` 四列，缺失列填充 0：
```python
for col in ['收入', '支出', '总收入', '总支出']:
    if col not in monthly.columns:
        monthly[col] = 0
```

---

#### 2.2.2 `db/database.py` 数据库连接未安全关闭

**位置**: `db/database.py:38`, `db/database.py:60`

**问题**: `load_data` 和 `save_data` 中使用 `conn = sqlite3.connect(...)`，但如果在 `conn.close()` 之前发生异常，连接将不会被关闭。

**建议**: 使用 `with` 上下文管理器：
```python
with sqlite3.connect(db_path) as conn:
    # ... 操作 ...
```

---

#### 2.2.3 无效日期变成字符串 `'NaT'`

**位置**: `ui/main_window.py:240`

**问题**: `_parse_and_import` 中对日期做 `pd.to_datetime(..., errors='coerce').dt.strftime('%Y-%m-%d')`，无效日期会变成字符串 `'NaT'` 存入数据库。

**建议**: 在转换后过滤掉 NaT 值，或将其设为空字符串/默认值。

---

### 2.3 代码质量问题

#### 2.3.1 过度使用裸 `except Exception: pass`

**位置**: `ui/main_window.py` 多处（`_close_date_popup`, `_on_de_escape`, `_on_escape` 等）

**问题**: 大量代码使用裸异常捕获并静默忽略，真正的 bug 会被隐藏，调试困难。

**建议**: 至少记录日志：
```python
except Exception:
    logger.warning("关闭日期弹窗失败", exc_info=True)
    pass
```

---

#### 2.3.2 `RecordBook` 类过于庞大

**位置**: `ui/main_window.py`（965 行）

**问题**: `RecordBook` 类同时承担了 UI 渲染、事件处理、数据操作、导入导出、图表展示等过多职责，违反单一职责原则。

**建议**: 将以下职责拆分为独立模块/类：
- 数据库操作（CRUD） -> `db/database.py`（已存在，但 `main_window.py` 中有重复实现）
- 导入处理逻辑 -> 新建 `services/import_service.py`
- 统计/图表数据准备 -> 已有 `model/record_model.py`，可进一步扩展

---

#### 2.3.3 代码重复

**位置**: `ui/main_window.py`, `ui/charts.py`

**问题**:
- `show_monthly_bill` 和 `show_month_detail` 中的 Treeview 排序逻辑几乎相同，只是列映射不同。
- `charts.py` 中 matplotlib 字体设置在每个函数中重复。

**建议**: 提取公共工具函数。

---

## 3. 测试用例优化建议

### 3.1 测试结构问题

#### 3.1.1 测试代码高度冗余

**位置**: `test/test_main_window.py`, `test/test_charts.py`

**问题**:
- `test_main_window.py` 每个测试嵌套 8-10 层 `with patch(...)`，可读性极差。
- `test_charts.py` 中 `DummyWin`、`DummyCanvas`、`DummyFrame`、`DummyButton` 等 mock 类在每个测试中重复定义。

**建议**: 
- 将 mock 类提取为公共 fixture，放到 `conftest.py` 中。
- 使用 `@pytest.fixture` 包装 RecordBook 的初始化 mock 逻辑。

---

#### 3.1.2 `test_dialogs.py` mock 方式脆弱

**位置**: `test/test_dialogs.py`

**问题**: 通过操作 `sys.modules` 替换 tkinter，依赖导入顺序。如果其他测试先导入过 `ui.dialogs`，此测试会失败。

**建议**: 使用标准的 `@patch('ui.dialogs.tk.Toplevel')` / `@patch('ui.dialogs.ttk.Combobox')` 等 patch 装饰器，避免操作 `sys.modules`。

---

### 3.2 断言质量问题

#### 3.2.1 断言过于宽松

**位置**: `test/test_charts.py`

**问题**: 多个测试最后只 `assert True`，没有验证具体行为。例如 `test_draw_pie_normal_data` 仅验证"没抛异常"。

**建议**: 验证 mock 的调用：
```python
# 验证 pie() 被调用
mock_axs[0].pie.assert_called_once()
mock_axs[1].pie.assert_called_once()
```

---

### 3.3 覆盖率不足

以下关键场景当前**缺少测试覆盖**：

| 未覆盖场景 | 建议补充 |
|-----------|---------|
| `db/database.py` `save_data` 异常回滚 | mock `sqlite3.Error`，验证 `conn.rollback()` 被调用 |
| `ui/main_window.py` `on_close` 退出逻辑 | 模拟 `dirty=True` 和 `dirty=False` 的分支 |
| `ui/main_window.py` `show_chart` / `plot_trend` / `plot_category` | 空数据和非空数据场景，验证 Figure 返回 |
| `ui/charts.py` 月份导航边界 | 第一个月"上一月"按钮禁用，最后一个月"下一月"禁用 |
| `ui/dialogs.py` `_on_escape` / `_close_date_popup` | 日历弹窗关闭的正确性 |
| `_parse_and_import` 的异常分支 | 列映射不全、预览取消等场景 |
| `import_alipay_csv` / `import_wechat_excel` 的异常处理 | 文件不存在、编码错误、空文件、解析错误 |

---

### 3.4 测试组织建议

#### 3.4.1 使用参数化测试

**位置**: `test/test_record_model.py`

`process_monthly` 的多种输入情况（只有收入、只有支出、空数据、混合数据）可以用 `@pytest.mark.parametrize` 合并，减少重复代码。

#### 3.4.2 补充集成测试

当前测试全是单元测试，缺少模块间协作的验证。建议补充：

```
导入流程集成测试: 选择文件 -> 读取 -> 列映射 -> 预览编辑 -> 确认 -> 保存 -> 重新加载 -> 验证数据
```

---

## 4. 总结与优先级

### 4.1 问题统计

| 类别 | 数量 |
|------|------|
| 文档与代码不一致 | 6 项 |
| 源代码优化点 | 10 项 |
| 测试用例优化点 | 7 项 |

### 4.2 高优先级修复项（建议立即处理）

1. **[缺陷]** `ui/charts.py` 污染原始 DataFrame（`df.copy()`）
2. **[缺陷]** `ui/charts.py` 图表 Figure 未关闭导致内存泄漏（`plt.close(fig)`）
3. **[缺陷]** `ui/main_window.py` 强制退出导致 tkinter 资源泄漏（移除 `sys.exit`）
4. **[缺陷]** `ui/main_window.py` 添加记录时重复弹窗（删除多余 `messagebox`）
5. **[可维护性]** 提取 `test/test_charts.py` 和 `test/test_main_window.py` 中的公共 mock 类

### 4.3 中优先级优化项

6. `model/record_model.py` 列结构不稳定
7. `db/database.py` 数据库连接使用 `with` 上下文管理器
8. `test/test_dialogs.py` 改用标准 `@patch` 方式
9. 补充图表模块的月份导航边界测试
10. 补充 `_parse_and_import` 的异常分支测试

### 4.4 低优先级改进项

11. `RecordBook` 类职责拆分（长期重构）
12. 消除 `show_monthly_bill` / `show_month_detail` 中的排序重复代码
13. 补充导入流程的集成测试

---

*报告结束*
