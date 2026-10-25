"""
日志配置模块

提供应用级别的日志配置和获取日志记录器功能。
"""
import logging
from pathlib import Path

# 日志格式
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# 默认日志级别
DEFAULT_LEVEL = logging.INFO

# 日志文件路径（基于项目根目录定位，避免依赖运行时工作目录）
LOG_DIR = Path(__file__).resolve().parent.parent / 'logs'
LOG_FILE = LOG_DIR / 'bookkeeping.log'


def setup_logging(level: int = DEFAULT_LEVEL) -> None:
    """
    配置应用日志，仅保存到文件，不输出到终端。
    
    Args:
        level: 日志级别，默认为INFO
    """
    # 确保日志目录存在
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # 配置根日志记录器，仅使用文件处理器
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[
            # 仅文件处理器，不输出到终端
            logging.FileHandler(LOG_FILE, encoding='utf-8', mode='a')
        ]
    )
    
    # 设置第三方库的日志级别
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器。
    
    Args:
        name: 日志记录器名称，通常使用__name__
        
    Returns:
        配置好的日志记录器
        
    Example:
        >>> from utils.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info('应用启动成功')
    """
    return logging.getLogger(name)
