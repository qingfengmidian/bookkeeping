

import tkinter as tk
from ui.main_window import RecordBook
from utils.logger import setup_logging, get_logger

# 初始化日志系统
setup_logging()
logger = get_logger(__name__)


def main():
    """应用主入口"""
    logger.info('记账本应用启动')
    try:
        root = tk.Tk()
        app = RecordBook(root)
        logger.info('主窗口初始化完成')
        root.mainloop()
    except Exception as e:
        logger.exception('应用运行出错')
        raise
    finally:
        logger.info('记账本应用退出')


if __name__ == '__main__':
    main()
