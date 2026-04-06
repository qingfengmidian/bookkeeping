from pathlib import Path

# 默认数据库路径
DB_DEFAULT: str = './database/root.db'

# 预定义分类列表
CATEGORIES: list[str] = ['餐饮', '交通', '购物', '娱乐', '医疗', '住房', '学习', '工资', '其他']

# 数据库表结构定义
TABLE_RECORDS_SCHEMA: str = '''
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    日期 TEXT,
    类型 TEXT,
    分类 TEXT,
    金额 REAL,
    备注 TEXT
'''

# 数据库表名
TABLE_NAME: str = 'records'

# 允许的表名（防止SQL注入）
ALLOWED_TABLES: list[str] = ['records']
