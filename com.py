import os
import logging
import os
from datetime import datetime
import logging
from logging import Formatter
from logging import INFO, DEBUG, NOTSET
from rich.logging import RichHandler
from logging.handlers import RotatingFileHandler

# ストリームハンドラの設定
rich_handler: RichHandler = RichHandler(rich_tracebacks=True)
rich_handler.setLevel(INFO)
# rich_handler.setLevel(DEBUG)
rich_handler.setFormatter(Formatter("%(message)s"))

# 保存先の有無チェック
if not os.path.isdir('./Log'):
    os.makedirs('./Log', exist_ok=True)

# ファイルハンドラの設定
file_handler = RotatingFileHandler(f"./Log/{datetime.now():%Y-%m-%d}.log","a", maxBytes=1000000, backupCount=10)
file_handler.setLevel(DEBUG)
file_handler.setFormatter(
    # Formatter("%(asctime)s [%(levelname).4s] %(filename)s %(funcName)s %(lineno)d: %(message)s")
    Formatter("%(asctime)s [%(levelname)s] %(filename)s %(funcName)s %(lineno)d: %(message)s")
)

# ルートロガーの設定
logging.basicConfig(level=NOTSET, handlers=[rich_handler, file_handler])

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

