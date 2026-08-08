"""
日志工具 - 基于 loguru
开发环境: 彩色控制台 + 可读文本文件
生产环境: 彩色控制台 + JSON 格式文件(便于 ELK/Loki 采集)
"""

import sys
from pathlib import Path

from loguru import logger

from app.config.settings import settings


def setup_logger():
    """配置全局日志"""
    logger.remove()

    # 控制台输出 (彩色 — 开发和生产都启用)
    logger.add(
        sys.stderr,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        level=settings.LOG_LEVEL,
        colorize=True,
    )

    # 文件输出
    log_dir = settings.BASE_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    if settings.is_production:
        # JSON 行格式 — 适合日志采集管线
        logger.add(
            log_dir / "app_{time:YYYY-MM-DD}.jsonl",
            format=(
                '{{"time":"{time:YYYY-MM-DD HH:mm:ss.SSS}","level":"{level}",'
                '"name":"{name}","function":"{function}","line":{line},'
                '"message":"{message}"}}'
            ),
            level="INFO",
            rotation="1 day",
            retention="30 days",
            compression="gz",
        )
    else:
        # 可读文本格式
        logger.add(
            log_dir / "app_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="1 day",
            retention="7 days",
            compression="gz",
        )

    return logger


# 初始化
logger = setup_logger()
