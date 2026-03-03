"""Logging utilities for CLI runs."""

import logging
import sys
from pathlib import Path


def setup_logger(log_dir: str, level: str, model_alias: str) -> tuple[logging.Logger, Path]:
    """创建日志器，按模型固定日志文件名并在每次运行时覆盖旧日志。"""
    log_filename = f"qwen3_tts_{model_alias}.log"
    log_path = Path(log_dir).expanduser().resolve() / log_filename
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("qwen3_tts_cli")
    logger.setLevel(getattr(logging, level))
    logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    file_handler.setLevel(getattr(logging, level))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(getattr(logging, level))
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger, log_path

