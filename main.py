"""
记账本程序 - 主入口模块

本模块是记账本应用程序的入口点，负责初始化日志系统和启动主窗口。

功能:
    - 初始化应用日志系统
    - 创建并启动 Tkinter 主窗口
    - 异常处理和日志记录

使用方式:
    直接运行: python main.py
    或在虚拟环境中: .\venv\Scripts\python main.py

日期: 2026-04-06
"""

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
