rem @echo off
python -m venv C:\Users\hdur3\temp\env
call C:\Users\hdur3\temp\env\Scripts\Activate.bat
cd F:\GoogleDrive\develop\working\PalworldIniEditGUI
pip install -r .\requirements.txt
pyinstaller iniEditGUI.spec
call deactivate
rmdir /s /q C:\Users\hdur3\temp\env
rmdir /s /q build
pause