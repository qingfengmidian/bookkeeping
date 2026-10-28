from pathlib import Path
import sys

# 项目根目录：源码运行按文件位置定位；PyInstaller 打包后按 exe 所在目录定位
#（打包环境 __file__ 指向临时解压根目录，直接用它会导致数据库/日志每次运行被丢弃）
if getattr(sys, 'frozen', False):
    PROJECT_ROOT = Path(sys.executable).resolve().parent
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 默认数据库路径（基于项目根目录定位，避免依赖运行时工作目录）
DB_DEFAULT: str = str(PROJECT_ROOT / 'database' / 'root.db')

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

# matplotlib 图表中文字体回退链：按列表顺序选用当前平台第一个可用字体，
# 保证图表中文在 Windows / macOS / Linux 上都能正常显示（找不到时逐个回退）
CJK_FONT_FALLBACK: list[str] = [
    'Microsoft YaHei',      # Windows 微软雅黑
    'SimHei',               # Windows 黑体（兜底）
    'PingFang SC',          # macOS 苹方
    'Hiragino Sans GB',     # macOS 冬青黑体（兜底）
    'Noto Sans CJK SC',     # Linux 常见发行版
    'WenQuanYi Micro Hei',  # Linux 文泉驿（兜底）
    'sans-serif',
]
