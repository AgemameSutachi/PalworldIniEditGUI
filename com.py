import os
import logging
import os
from datetime import datetime
import logging
from logging import Formatter
from logging import INFO, DEBUG, NOTSET
from rich.logging import RichHandler
from logging.handlers import RotatingFileHandler

# Trueで日付、Falseでdebugとinfoのログファイル名
# 起動しっぱなしはFalseにする
flag_datelog = True

# ストリームハンドラの設定
rich_handler: RichHandler = RichHandler(rich_tracebacks=True)
rich_handler.setLevel(INFO)
# rich_handler.setLevel(DEBUG)
rich_handler.setFormatter(Formatter("%(message)s"))

# 保存先の有無チェック
if not os.path.isdir("./Log"):
    os.makedirs("./Log", exist_ok=True)

# ファイルハンドラの設定
if flag_datelog:
    file_handler = RotatingFileHandler(
        f"./Log/{datetime.now():%Y-%m-%d}.log", "a", maxBytes=1000000, backupCount=10
    )
    file_handler.setLevel(DEBUG)
    file_handler.setFormatter(
        # Formatter("%(asctime)s [%(levelname).4s] %(filename)s %(funcName)s %(lineno)d: %(message)s")
        Formatter(
            "%(asctime)s [%(levelname)s] %(filename)s %(funcName)s %(lineno)d: %(message)s"
        )
    )

    # ルートロガーの設定
    logging.basicConfig(level=NOTSET, handlers=[rich_handler, file_handler])
else:
    file_handler_debug = RotatingFileHandler(
        f"./Log/debug.log", "a", maxBytes=1000000, backupCount=10
    )
    file_handler_debug.setLevel(DEBUG)
    file_handler_debug.setFormatter(
        # Formatter("%(asctime)s [%(levelname).4s] %(filename)s %(funcName)s %(lineno)d: %(message)s")
        Formatter(
            "%(asctime)s [%(levelname)s] %(filename)s %(funcName)s %(lineno)d: %(message)s"
        )
    )
    file_handler_info = RotatingFileHandler(
        f"./Log/info.log", "a", maxBytes=1000000, backupCount=10
    )
    file_handler_info.setLevel(INFO)
    file_handler_info.setFormatter(
        # Formatter("%(asctime)s [%(levelname).4s] %(filename)s %(funcName)s %(lineno)d: %(message)s")
        Formatter(
            "%(asctime)s [%(levelname)s] %(filename)s %(funcName)s %(lineno)d: %(message)s"
        )
    )
    # ルートロガーの設定
    logging.basicConfig(
        level=NOTSET, handlers=[rich_handler, file_handler_debug, file_handler_info]
    )


def log_decorator(logger):
    def _log_decorator(func):
        def wrapper(*args, **kwargs):
            local_args = locals()
            try:
                logger.debug(f"start: {func.__name__}  args: {str(local_args)}")
                return_val = func(*args, **kwargs)
                # logger.debug(f'  end: {func.__name__}  ret: {str(return_val)}')
                logger.debug(f"  end: {func.__name__}")
                return return_val
            except Exception as e:
                logger.error(f"error: {func.__name__}")
                raise e

        return wrapper

    return _log_decorator
