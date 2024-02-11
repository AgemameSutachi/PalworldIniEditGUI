import os
import logging
from datetime import datetime
from logging import Formatter
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL, NOTSET
from rich.logging import RichHandler
from logging.handlers import RotatingFileHandler
import sys

# ストリームハンドラの設定
rich_handler = RichHandler(rich_tracebacks=True)
rich_handler.setLevel(INFO)
rich_handler.setFormatter(Formatter("%(message)s"))

# 保存先の有無チェック
if not os.path.isdir('./Log'):
    os.makedirs('./Log', exist_ok=True)
    
debug_handler = RotatingFileHandler("./Log/debug.log", "a", maxBytes=1000000, backupCount=10)
debug_handler.setLevel(DEBUG)
debug_handler.setFormatter(Formatter("%(asctime)s [%(levelname).4s] %(filename)s %(funcName)s %(lineno)d: %(message)s"))

# INFO ログ用のハンドラとフォーマッター
info_handler = RotatingFileHandler("./Log/info.log", "a", maxBytes=1000000, backupCount=10)
info_handler.setLevel(INFO)
info_handler.setFormatter(Formatter("%(asctime)s [%(levelname).4s] %(filename)s %(funcName)s %(lineno)d: %(message)s"))

# ルートロガーの設定
logging.basicConfig(level=NOTSET, handlers=[rich_handler, debug_handler,info_handler])

def getLogger():
    return logging.getLogger(__name__)


def log_decorator(logger):
    def _log_decorator(func):
        def wrapper(*args, **kwargs):
            try:
                logger.debug(f'start: {func.__name__}')
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f'error: {func.__name__}')
                raise e
            finally:
                logger.debug(f'  end: {func.__name__}')
        return wrapper
    return _log_decorator

