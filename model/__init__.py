"""
数据模型模块

提供账单数据的处理和分析功能。
"""

from .record_model import process_monthly, process_detail

__all__ = ['process_monthly', 'process_detail']
