import logging
from pathlib import Path
from logger_rewrite.logger import setup_logging


def setup_log(save_dir='./', name_exp='train'):
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    setup_logging(save_dir)
    logger = get_logger(name_exp)
    return logger


def get_logger(name):
    logger = logging.getLogger(name=name)
    logger.setLevel(logging.DEBUG)
    return logger
