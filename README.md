# パルワールドサーバー管理プログラム

このプログラムは、パルワールドサーバーのini変更をサポートするためのツールです。以下に、主な機能と使用法を示します。

時間ができ次第、readmeは改善する予定です。

## 注意点

- windowsです
- rconが有効化されていることが前提です
- rconがあまり安定していません
- palserver_monitorのserverend.exeを使用することが前提です(rcon等設定済み)

## 使用法

1. dist/iniEditGUI.iniを確認し、必要に応じて調整します。
2. dist/iniEditGUI.exeを実行

## 設定

プログラムの設定は、`dist/iniEditGUI.ini`ファイルを編集することで可能です。設定ファイルには以下の項目が含まれます。

- inipath = C:\Users\aaaa\temp\steamcmd\steamapps\common\PalServer\Pal\Saved\Config\WindowsServer\PalWorldSettings.ini
  - パルワールドのiniファイルを指定
- shutdownexepath = serverend.exe
  - シャットダウンさせるexe(palserver_monitorのserverend.exeを指定)
- startexepath = C:\Users\aaaa\temp\steamcmd\steamapps\common\PalServer\PalServer.exe
  - 起動するプログラム(パルワールドのexeを指定)
