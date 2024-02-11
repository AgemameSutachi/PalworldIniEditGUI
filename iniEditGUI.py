from com import log_decorator
import logging
import sys
from configmanager import ConfigManager
Cl_Con=ConfigManager()
from palinimanager import PalIniManager
logger = logging.getLogger(__name__)
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import os
import threading
import subprocess
import traceback
import psutil

#現在のアプリバージョン
VERSION="1.0"

#標準出力フラグ(デバッグ用)
flag_print=False

process_name_to_check = Cl_Con.get("StartExePath")

def is_process_running(process_name):
    logger.debug("start: "+str(sys._getframe().f_code.co_name))
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == process_name:
            return True
    return False

class GUI:
    @log_decorator(logger)
    def __init__(self) -> None:
        self.inipath=Cl_Con.get("inipath")
        self.shutdownExePath=Cl_Con.get("ShutdownExePath")
        self.startExePath=Cl_Con.get("StartExePath")
        if self.inicherk():
            self.flag_shutdown=True
        else:
            self.flag_shutdown=False
            self.Cl_Pal=PalIniManager(self.inipath)
            self.keys=self.Cl_Pal.get_keys()

    @log_decorator(logger)
    def inicherk(self):
        if not os.path.exists(self.inipath):
            messagebox.showerror("設定エラー", "設定ファイルが見つかりません、設定を見直してください\nファイル名: "+Cl_Con.config_path+"\nキー名: inipath")
            return 1
        if not os.path.exists(self.shutdownExePath):
            messagebox.showerror("設定エラー", "シャットダウンexeが見つかりません、設定を見直してください\nファイル名: "+Cl_Con.config_path+"\nキー名: ShutdownExePath")
            return 1
        if not os.path.exists(self.startExePath):
            messagebox.showerror("設定エラー", "起動exeが見つかりません、設定を見直してください\nファイル名: "+Cl_Con.config_path+"\nキー名: StartExePath")
            return 1
        return 0


    @log_decorator(logger)
    def update_ini(self,key,val):
        """一時的に更新"""
        self.Cl_Pal.update(key,val)
        return
    
    @log_decorator(logger)
    def update_detail(self,key,detail):
        """一時的に更新"""
        self.Cl_Pal.update_detail(key,detail)
        return
    
    @log_decorator(logger)
    def discard_ini(self,key=""):
        """一時的に更新したものをiniだけ戻す。keyなしで全て戻す"""
        self.Cl_Pal.discard(key)
        return

    @log_decorator(logger)
    def discard_detail(self,key=""):
        """一時的に更新したものを説明だけ戻す。keyなしで全て戻す"""
        self.Cl_Pal.discard_detail(key)
        return

    @log_decorator(logger)
    def discard_all(self,key=""):
        """一時的に更新したものをini、説明両方戻す。keyなしで全て戻す"""
        self.Cl_Pal.discard(key)
        self.Cl_Pal.discard_detail(key)
        return
    
    @log_decorator(logger)
    def write_ini(self):
        """iniを更新"""
        self.Cl_Pal.write(self.inipath)
        return
    
    @log_decorator(logger)
    def write_default(self):
        """説明を更新"""
        self.Cl_Pal.write_default()
        return

    @log_decorator(logger)
    def click_progress_close(self):
        """ウィンドウの閉じるボタンクリック時に、確認ダイアログを出し、okの場合終了する"""
        if self.flag_update:
            ret=messagebox.askokcancel("確認", "更新を強制中断してもよろしいですか？")
            if ret:
                self.dlg_progress.destroy()
        else:
            self.dlg_progress.destroy()

    @log_decorator(logger)
    def click_btn_progress_close(self):
        """閉じるボタンクリック時に終了する"""
        self.dlg_progress.destroy()

    @log_decorator(logger)
    def create_progress_window(self):
        """設定更新中画面を表示"""
        self.dlg_progress = tk.Toplevel(self.root)
        self.dlg_progress.withdraw()
        self.dlg_progress.title("設定更新中") # ウィンドウタイトル
        lw=300 #幅
        lh=200 #高さ

        #中心に表示する
        ww=self.dlg_progress.winfo_screenwidth()
        wh=self.dlg_progress.winfo_screenheight()
        self.dlg_progress.geometry(str(lw)+"x"+str(lh)+"+"+str(int(ww/2-lw/2))+"+"+str(int(wh/2-lh/2)) )

        # モーダルにする設定
        self.dlg_progress.grab_set()        # モーダルにする
        self.dlg_progress.focus_set()       # フォーカスを新しいウィンドウをへ移す
        self.dlg_progress.transient(self.root)   # タスクバーに表示しない

        self.progress_str_list=[]
        self.progress_lbl_list=[]
        for num,i in enumerate(["1. デフォルトファイル更新","2. サーバーシャットダウン","3. 設定ファイル更新","4. サーバー起動"]):
            progress_str = tk.StringVar()
            progress_str.set(i)
            self.progress_str_list.append(progress_str)
            label=ttk.Label(self.dlg_progress, textvariable=progress_str)
            label.grid(row=num, column=0,sticky=tk.NSEW,padx=10,pady=10)
            self.progress_lbl_list.append(label)

        self.btn_progress_close=ttk.Button(self.dlg_progress,text="閉じる",command=self.click_btn_progress_close)
        self.btn_progress_close.grid(row=4,column=0,sticky=tk.SE,padx=10,pady=10)
        self.btn_progress_close.config(state="disabled")
        self.dlg_progress.protocol("WM_DELETE_WINDOW", self.click_progress_close)
        self.dlg_progress.columnconfigure(0, weight=1)
        self.dlg_progress.deiconify()
        self.dlg_progress.update()

    @log_decorator(logger)
    def btn_update_click(self):
        self.thread_update = threading.Thread(target = self.btn_update_click_main)
        self.thread_update.start()

    @log_decorator(logger)
    def btn_update_click_main(self):
        """更新を確定し、サーバー再起動する"""
        ret=messagebox.askokcancel("確認", "設定の更新のために、サーバーを再起動してもよろしいですか？")
        if not ret:return
        self.flag_update=True
        self.create_progress_window()
        try:
            try:
                for num,key in enumerate(self.keys):
                    self.update_detail(key,self.table_string_list[num+1][1].get())
                    self.update_ini(key,self.table_string_list[num+1][2].get())
                self.Cl_Pal.write_default()
            except:
                logger.exception("デフォルトファイル更新中にエラー発生")
                self.progress_str_list[0].set(self.progress_str_list[0].get()+"…エラー")
                return
            self.progress_str_list[0].set(self.progress_str_list[0].get()+"…完了")
            self.dlg_progress.update()
            
            try:
                res=subprocess.run([self.shutdownExePath,"1"])
                # if res.returncode:
                #     logger.error("サーバーシャットダウン中にエラー発生")
                #     self.progress_str_list[1].set(self.progress_str_list[1].get()+"…エラー")
                #     return
                if is_process_running(self.startExePath):
                    logger.error("サーバーをシャットダウンできませんでした")
                    self.progress_str_list[1].set(self.progress_str_list[1].get()+"…エラー")
                    return
            except Exception as e:
                logger.info("エラー")
                errortxt = ", ".join(list(traceback.TracebackException.from_exception(e).format()))
                logger.exception(e)
                self.progress_str_list[1].set(self.progress_str_list[1].get()+"…エラー")
                return
            self.progress_str_list[1].set(self.progress_str_list[1].get()+"…完了")
            self.dlg_progress.update()
            
            try:
                self.Cl_Pal.write(self.inipath)
            except:
                logger.exception("設定ファイル更新中にエラー発生")
                self.progress_str_list[2].set(self.progress_str_list[2].get()+"…エラー")
                return
            self.progress_str_list[2].set(self.progress_str_list[2].get()+"…完了")
            self.dlg_progress.update()
            
            try:
                subprocess.Popen(self.startExePath)
                logger.info(f"{self.startExePath} を起動しました。")
            except Exception as e:
                logger.info("エラー")
                errortxt = ", ".join(list(traceback.TracebackException.from_exception(e).format()))
                logger.exception(e)
                self.progress_str_list[3].set(self.progress_str_list[3].get()+"…エラー")
                return
            self.progress_str_list[3].set(self.progress_str_list[3].get()+"…完了")
            self.dlg_progress.update()
        finally:
            # ダイアログが閉じられるまで待つ
            self.flag_update=False
            self.btn_progress_close.config(state="normal")
            self.dlg_progress.update()
            self.root.wait_window(self.dlg_progress)

    @log_decorator(logger)
    def btn_output_click(self):
        try:
            for num,key in enumerate(self.keys):
                self.update_detail(key,self.table_string_list[num+1][1].get())
                self.update_ini(key,self.table_string_list[num+1][2].get())
            self.Cl_Pal.write_default()
        except:
            logger.exception("デフォルトファイル更新中にエラー発生")
            self.progress_str_list[0].set(self.progress_str_list[0].get()+"…エラー")
            return
        f_type = [('ini', '*.ini')]

        file_path = filedialog.asksaveasfilename(
            title = "名前を付けて保存",
            filetypes=f_type, 
            initialfile="PalWorldSettings.ini",
            initialdir="./",
            defaultextension="ini"
            )
        
        if file_path != "":
            self.Cl_Pal.write(file_path)
        return

    @log_decorator(logger)
    def readkeys(self):
        ret_list=[]
        for i in self.keys:
            ret_list.append([i,self.Cl_Pal.get_detail(i),self.Cl_Pal.get(i)])
        return ret_list
        
    @log_decorator(logger)
    def click_close(self):
        """ウィンドウの閉じるボタンクリック時に、確認ダイアログを出し、okの場合説明を更新する"""
        flag_unsave=False
        for num,key in enumerate(self.keys):
            if self.table_string_list[num+1][1].get()!=self.Cl_Pal.get_detail(key):
                flag_unsave=True
                break
        if flag_unsave:
            #説明の変更あり
            ret=messagebox.askyesnocancel("確認", "終了します。\n説明文の変更を保存しますか？")
            if ret is not None:
                if ret:
                    for num,key in enumerate(self.keys):
                        self.update_detail(key,self.table_string_list[num+1][1].get())
                    self.write_default()
                self.root.destroy()
        else:
            #説明の変更なし
            ret=messagebox.askokcancel("確認", "終了してもよろしいですか？")
            if ret:
                self.root.destroy()

    @log_decorator(logger)
    def btn_discard_click(self,index):
        """各行の元に戻すボタンクリック時に説明と値を戻す"""
        def inner():
            key=self.keys[index]
            self.discard_all(key)
            self.table_string_list[index+1][1].set(self.Cl_Pal.get_detail(key))
            self.table_string_list[index+1][2].set(self.Cl_Pal.get(key))
        return inner

    @log_decorator(logger)
    def change_entry_width_key(self,index):
        """キーのエントリーの横幅を変更する→変更されないので未使用"""
        def inner(var, index_, mode):
            txtlen=self.Cl_Pal.get_east_asian_width_count(self.table_string_list[index][0].get())
            if self.maxlen_key<txtlen:
                if txtlen+self.maxlen_detail+self.maxlen_value>220:
                    txtlen=220-self.maxlen_detail-self.maxlen_value
                logger.debug("説明欄を拡張: "+str(self.maxlen_key+2)+" → "+str(txtlen+2))
                self.maxlen_key=txtlen
                for i in self.table_entry_list:
                    i[0].config(width = self.maxlen_key+2)
        return inner

    @log_decorator(logger)
    def change_entry_width_detail(self,index):
        """説明のエントリーの横幅を変更する"""
        def inner(var, index_, mode):
            txtlen=self.Cl_Pal.get_east_asian_width_count(self.table_string_list[index][1].get())
            if self.maxlen_detail<txtlen:
                if txtlen+self.maxlen_key+self.maxlen_value>220:
                    txtlen=220-self.maxlen_key-self.maxlen_value
                logger.debug("説明欄を拡張: "+str(self.maxlen_detail+2)+" → "+str(txtlen+2))
                self.maxlen_detail=txtlen
                for i in self.table_entry_list:
                    i[1].config(width = self.maxlen_detail+2)
        return inner

    @log_decorator(logger)
    def change_entry_width_value(self,index):
        """設定値のエントリーの横幅を変更する"""
        def inner(var, index_, mode):
            txtlen=self.Cl_Pal.get_east_asian_width_count(self.table_string_list[index][2].get())
            if self.maxlen_value<txtlen:
                if txtlen+self.maxlen_key+self.maxlen_detail>220:
                    txtlen=220-self.maxlen_key-self.maxlen_detail
                logger.debug("設定欄を拡張: "+str(self.maxlen_value+2)+" → "+str(txtlen+2))
                self.maxlen_value=txtlen
                for i in self.table_entry_list:
                    i[2].config(width = self.maxlen_value+2)
        return inner

    @log_decorator(logger)
    def guimain(self):
        """画面作成"""
        self.root = tk.Tk()
        self.root.title(u"ini設定ツール"+"  Ver:"+VERSION)
        self.style = ttk.Style()
        self.style.configure('.', font = ('', 12))   # Ttk Widget のフォントの大きさを 12 に変更
        self.style.configure("office.TButton", font = ('', 10))

        # self.fr = ttk.Frame(self.root)
        self.fr = ttk.LabelFrame(self.root, text = 'ini設定ツール')

        #iniの表作成
        self.canvas = tk.Canvas(self.fr,highlightthickness=0)#,bg='#000fff000')
        self.canvas.bind(
            "<MouseWheel>", 
            lambda e: self.canvas.yview_scroll(int(-1*(e.delta/abs(e.delta))), "units")
        )
        self.canvas.bind(
            "<Shift-MouseWheel>", 
            lambda e: self.canvas.xview_scroll(int(-1*(e.delta/abs(e.delta))), "units")
        )

        self.fr2 = tk.Frame(self.canvas,padx=0,pady=0,highlightthickness=0)#,bg='#000000FFF')
        self.fr2.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.fr2.bind(
            "<MouseWheel>", 
            lambda e: self.canvas.yview_scroll(int(-1*(e.delta/abs(e.delta))), "units")
        )
        self.fr2.bind(
            "<Shift-MouseWheel>", 
            lambda e: self.canvas.xview_scroll(int(-1*(e.delta/abs(e.delta))), "units")
        )

        self.table_string_list=[]
        self.table_entry_list=[]
        self.table_discard_list=[]
        self.maxlen_key,self.maxlen_detail,self.maxlen_value=self.Cl_Pal.get_maxlen()
        for num,i in enumerate([['キー', '説明', '設定値']]+self.readkeys()):
            logger.debug(i)
            #key
            string_key = tk.StringVar()
            string_key.set(i[0])
            string_key.trace_add('write',self.change_entry_width_key(len(self.table_entry_list)))
            entry_key=ttk.Entry(self.fr2, width = self.maxlen_key+2,textvariable=string_key)#, validate="focusout", validatecommand=self.change_entry_width_key(len(self.table_entry_list)))
            entry_key.grid(row=num, column=0,sticky=tk.N+tk.S)
            entry_key.configure(state='readonly')
            entry_key.bind(
                "<MouseWheel>", 
                lambda e: self.canvas.yview_scroll(int(-1*(e.delta/abs(e.delta))), "units")
            )
            entry_key.bind(
                "<Shift-MouseWheel>", 
                lambda e: self.canvas.xview_scroll(int(-1*(e.delta/abs(e.delta))), "units")
            )

            #detail
            string_detail = tk.StringVar()
            string_detail.set(i[1])
            string_detail.trace_add('write',self.change_entry_width_detail(len(self.table_entry_list)))
            entry_detail=ttk.Entry(self.fr2, width = self.maxlen_detail+2,textvariable=string_detail)#, validate="focusout", validatecommand=self.change_entry_width_detail(len(self.table_entry_list)))
            entry_detail.grid(row=num, column=1,sticky=tk.N+tk.S)
            if num==0:
                entry_detail.configure(state='readonly')
            else:
                entry_detail.configure(state='normal')
            entry_detail.bind(
                "<MouseWheel>", 
                lambda e: self.canvas.yview_scroll(int(-1*(e.delta/abs(e.delta))), "units")
            )
            entry_key.bind(
                "<Shift-MouseWheel>", 
                lambda e: self.canvas.xview_scroll(int(-1*(e.delta/abs(e.delta))), "units")
            )

            #value
            string_value = tk.StringVar()
            string_value.set(i[2])       
            string_value.trace_add('write',self.change_entry_width_value(len(self.table_entry_list)))
            entry_value=ttk.Entry(self.fr2, width = self.maxlen_value+2,textvariable=string_value)#, validate="focusout", validatecommand=self.change_entry_width_value(len(self.table_entry_list)))
            entry_value.grid(row=num, column=2,sticky=tk.N+tk.S)
            if num==0:
                entry_value.configure(state='readonly')
            else:
                entry_value.configure(state='normal')
            entry_value.bind(
                "<MouseWheel>", 
                lambda e: self.canvas.yview_scroll(int(-1*(e.delta/abs(e.delta))), "units")
            )
            entry_value.bind(
                "<Shift-MouseWheel>", 
                lambda e: self.canvas.xview_scroll(int(-1*(e.delta/abs(e.delta))), "units")
            )

            self.table_string_list.append([string_key,string_detail,string_value])
            self.table_entry_list.append([entry_key,entry_detail,entry_value])

            #もとに戻すボタン
            if num!=0:
                btn_discard=ttk.Button(self.fr2,text="元に戻す", width = 10,command=self.btn_discard_click(len(self.table_discard_list)))
                btn_discard.grid(row=num, column=3,sticky=tk.N+tk.S,padx=10)
                self.table_discard_list.append([entry_key,entry_detail,entry_value])

        # #スクロールバー
        self.scrollbar = tk.Scrollbar(
            self.fr, orient=tk.VERTICAL, command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.fr2.grid(row=0, column=0,sticky=tk.NSEW)
        self.scrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.canvas.grid(row=0, column=0,sticky=tk.NSEW,padx=10,pady=10)
        self.canvas.create_window((0, 0), window=self.fr2, anchor="nw")

        self.fr.grid(row=0, column=0,sticky=tk.NSEW,padx=10,pady=10)

        #更新ボタンを配置するフレーム
        self.fr3 = ttk.Frame(self.root)
        btn_update=ttk.Button(self.fr3,text="設定を適用(サーバーが再起動します)",command=self.btn_update_click)
        btn_update.pack(anchor="se",padx=10,pady=10,side=tk.RIGHT)
        btn_output=ttk.Button(self.fr3,text="設定ファイルの出力",command=self.btn_output_click)
        btn_output.pack(anchor="se",padx=10,pady=10)
        self.fr3.grid(row=1, column=0,sticky=tk.NSEW,padx=10,pady=10)

        self.fr2.columnconfigure(0, weight=1)
        self.canvas.columnconfigure(0, weight=1)
        self.fr.columnconfigure(0, weight=1)
        self.fr.columnconfigure(1, weight=0)
        self.fr.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        
        self.root.minsize(width=700, height=250)
        self.root.maxsize(width=1920, height=1080)
        self.root.state("zoomed")
        self.root.protocol("WM_DELETE_WINDOW", self.click_close)
        self.root.mainloop()
        return 0

if __name__ == '__main__':
    cl_GUI=GUI()
    if not cl_GUI.flag_shutdown:
        cl_GUI.guimain()
