@echo off
chcp 65001 >nul

cd /d "%~dp0"

echo.
echo ==============================================
echo シフト自動調整管理アプリを起動します
echo ==============================================
echo.

if not exist ".venv\Scripts\python.exe" goto NOVENV

call ".venv\Scripts\activate.bat"

python -m streamlit run app.py

pause
exit /b

:NOVENV
echo.
echo [ERROR] 仮想環境(.venv)がありません。
echo setup.bat を最初に実行してください。
echo.
pause