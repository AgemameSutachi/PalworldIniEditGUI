from com import log_decorator
import os
import configparser
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

default_config_dic = {
    "key1": "val1",
    "key2": "val2",
}


class ConfigManager:
    """設定ファイルを管理するクラス"""

    @log_decorator(logger)
    def __init__(
        self,
        default_dic: dict = default_config_dic,
        config_path: str = os.path.basename(os.getcwd()) + ".ini",
        encoding: str = "cp932",
    ):
        self.config_dic = default_dic
        self.config_path = str(Path(config_path).absolute())
        self.encoding = encoding
        if not os.path.exists(config_path):
            logger.info("設定ファイルがないのでテンプレートを作成: " + self.config_path)
            self.config_generator()
        else:
            logger.info("設定ファイル読み込み: " + self.config_path)
        config_ini = configparser.ConfigParser()
        config_ini.read(config_path, encoding=self.encoding)
        read_default = config_ini["DEFAULT"]
        for key in self.config_dic.keys():
            self.config_dic[key] = read_default.get(key, self.config_dic[key])
            logger.info(key + ": " + str(self.config_dic[key]))

    @log_decorator(logger)
    def config_generator(self):
        try:
            if os.path.dirname(self.config_path) != "":
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            config = configparser.ConfigParser()
            config["DEFAULT"] = self.config_dic
            with open(self.config_path, "w", encoding=self.encoding) as configfile:
                config.write(configfile)
        except:
            logger.error("設定ファイル作成失敗: " + self.config_path)
            raise

    @log_decorator(logger)
    def get(self, key: str, default: str = ""):
        if default == "":
            return self.config_dic.get(key)
        else:
            return self.config_dic.get(key, default)

    @log_decorator(logger)
    def set(self, key: str, value):
        self.config_dic[key] = value
        return

    @log_decorator(logger)
    def save(self):
        config = configparser.ConfigParser()
        config["DEFAULT"] = self.config_dic
        with open(self.config_path, "w", encoding=self.encoding) as configfile:
            config.write(configfile)
