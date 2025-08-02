import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# 彩色输出 ANSI 码
COLOR_RESET = "\033[0m"
COLOR_RED = "\033[31m"
COLOR_YELLOW = "\033[33m"
COLOR_GREEN = "\033[32m"
COLOR_BLUE = "\033[34m"

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "PV-server.log"


class ColorFormatter(logging.Formatter):
    def format(self, record):
        log_msg = super().format(record)
        if record.levelno == logging.ERROR:
            return f"{COLOR_RED}{log_msg}{COLOR_RESET}"
        elif record.levelno == logging.WARNING:
            return f"{COLOR_YELLOW}{log_msg}{COLOR_RESET}"
        elif record.levelno == logging.INFO:
            return f"{COLOR_GREEN}{log_msg}{COLOR_RESET}"
        elif record.levelno == logging.DEBUG:
            return f"{COLOR_BLUE}{log_msg}{COLOR_RESET}"
        return log_msg


def get_logger(name: str = "media_server", level=logging.INFO):
    """返回一个同时输出到终端和彩色文件的 logger"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        # 1️⃣ 终端彩色输出
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(
            ColorFormatter(
                "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

        # 2️⃣ 文件输出（自动按大小轮转）
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,  # 保留 5 个历史日志
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
