import os
import sys
from com import log_decorator
import configparser
from io import StringIO
from pandas import read_csv
import csv
from typing import Tuple
import unicodedata
import logging
from copy import deepcopy
logger = logging.getLogger(__name__)

fix_section="/Script/Pal.PalGameWorldSettings"
fix_key="OptionSettings"

class PalIniManager():
    """iniファイルを管理するクラス"""
    @log_decorator(logger)
    def __init__(self,config_path: str ="PalWorldSettings.ini"):
        self.default_ini_dic, self.default_detail_dic=self.read_default()
        self.config_path=config_path
        if not os.path.exists(self.config_path):
            logger.error("設定ファイルがないです: "+self.config_path)
            raise FileNotFoundError 
        logger.info("設定ファイル読み込み: "+self.config_path)
        main_config_dic=self.read(self.config_path)
        self.config_dic=deepcopy(self.default_ini_dic)
        self.detail_dic=deepcopy(self.default_detail_dic)
        for key in main_config_dic.keys():
            self.config_dic[key] = main_config_dic.get(key)
            if key not in self.default_detail_dic.keys():
                self.detail_dic[key]=self.default_setting_path+"に説明なし"
            logger.info(key+": "+str(self.detail_dic[key])+": "+str(self.config_dic[key]))
        self.before_config_dic=deepcopy(self.config_dic)
        self.before_detail_dic=deepcopy(self.detail_dic)
        return

    @log_decorator(logger)
    def read(self, config_path: str ="PalWorldSettings.ini") -> dict:
        """オリジナルのini読み込み関数"""
        config_temp = configparser.ConfigParser(allow_no_value=True)
        with open(config_path, mode="r", encoding="UTF-8") as config_file:
            config_temp.read_file(config_file)

        #セクション「"/Script/Pal.PalGameWorldSettings"」キー「"optionsettings"」に定義されているものを1文字目と最後の文字を除いて抜き出し、カンマ区切りのリストにする。
        #ただし、""で囲まれている区切り文字は無視
        string = config_temp[fix_section][fix_key]
        if string[0]=="(":string=string[1:]
        if string[-1]==")":string=string[:-1]
        main_config_list = read_csv(StringIO(string), sep=",", header=None, skipinitialspace=True).values[0].tolist()

        #=区切りの文字列を分割して1番目はキー、2番目以降は連結して値とする
        main_config_dic={}
        for i in main_config_list:
            templist=i.split("=")
            main_config_dic[templist[0]]="".join(templist[1:])
        return main_config_dic

    @log_decorator(logger)
    def write(self, config_path: str ="PalWorldSettings.ini"):
        """オリジナルのini書き込み関数"""
        templist=[]
        for key in self.config_dic.keys():
            templist.append(key+"="+str(self.config_dic[key]))
        value=",".join(templist)
        value="("+value+")"

        with open(config_path, 'w', encoding="UTF-8",newline="") as f:
            f.write("["+fix_section+"]\n")
            f.write(fix_key+"="+value+"\n\n")
        return

    @log_decorator(logger)
    def read_default(self, path:str="defaultsetting.csv") -> Tuple[dict,dict]:
        """説明保存csvを読む"""
        self.default_setting_path=path
        if not os.path.exists(path):
            with open(path, 'w', encoding="cp932",newline="") as f:
                writer = csv.writer(f,delimiter=",")
                writer.writerow(["key","value","detail"])
            logger.warning("デフォルト設定ファイルがないため、作成しました。: "+path)
        df=read_csv(path, sep=",", skipinitialspace=True, encoding="cp932")
        #key,value,detail
        default_ini_dic=dict(zip(df["key"], df["value"]))
        default_detail_dic=dict(zip(df["key"], df["detail"]))
        return default_ini_dic, default_detail_dic

    @log_decorator(logger)
    def write_default(self, path:str="defaultsetting.csv"):
        """説明保存csvを更新"""
        writelist=[]
        #デフォルトcsvにないものは設定値で更新
        for key in list(self.config_dic.keys()):
            if key not in list(self.default_ini_dic.keys()):
                writelist.append([key,self.config_dic[key],self.detail_dic[key]])
                logger.debug("設定値でデフォルト記述:"+key+":"+str(self.config_dic[key])+":"+self.detail_dic[key])
            else:
                writelist.append([key,self.default_ini_dic[key],self.detail_dic[key]])
                logger.debug("デフォルトの設定値は上書かない:"+key+":"+str(self.default_ini_dic[key])+":"+self.detail_dic[key])
        with open(path, 'w', encoding="cp932",newline="") as f:
            writer = csv.writer(f,delimiter=",")
            writer.writerow(["key","value","detail"])
            writer.writerows(writelist)
        return

    @log_decorator(logger)
    def get_keys(self) -> list:
        """キーのリストを取得"""
        return list(self.config_dic.keys())

    @log_decorator(logger)
    def get(self,key: str) -> str:
        """値を取得"""
        return self.config_dic.get(key)

    @log_decorator(logger)
    def get_detail(self,key: str) -> str:
        """説明文を取得"""
        return self.detail_dic.get(key)

    @log_decorator(logger)
    def update(self,key:str, val):
        """設定を更新する"""
        self.config_dic[key]=val

    @log_decorator(logger)
    def update_detail(self,key:str, detail):
        """説明を更新する"""
        self.detail_dic[key]=detail

    @log_decorator(logger)
    def discard(self,key:str=""):
        """更新した設定をもとに戻す"""
        if key=="":
            self.config_dic=self.before_config_dic
        else:
            self.config_dic[key]=self.before_config_dic[key]

    @log_decorator(logger)
    def discard_detail(self,key:str=""):
        """更新した説明をもとに戻す"""
        if key=="":
            self.detail_dic=self.before_detail_dic
        else:
            self.detail_dic[key]=self.before_detail_dic[key]

    @log_decorator(logger)
    def get_east_asian_width_count(self,text):
        """全角は2文字、ほかは1文字としてカウントする"""
        count = 0
        for c in text:
            if unicodedata.east_asian_width(c) in 'FWA':
                count += 2
            else:
                count += 1
        return count

    @log_decorator(logger)
    def get_maxlen(self):
        """設定の一番多い文字数のリストを取得"""
        maxlen_key=0
        maxlen_detail=self.get_east_asian_width_count(self.default_setting_path+"に説明なし")
        maxlen_value=0
        for key in self.config_dic.keys():
            len_key=self.get_east_asian_width_count(key)
            if len_key>maxlen_key:maxlen_key=len_key
            len_detail=self.get_east_asian_width_count(self.get_detail(key))
            if len_detail>maxlen_detail:maxlen_detail=len_detail
            len_value=self.get_east_asian_width_count(self.get(key))
            if len_value>maxlen_value:maxlen_value=len_value
        logger.debug(" maxlen_key:"+str(maxlen_key)+" maxlen_detail:"+str(maxlen_detail)+" maxlen_value:"+str(maxlen_value))
        return maxlen_key,maxlen_detail,maxlen_value
    
