@echo off
chcp 65001 >nul

echo ==================================================
echo シフト自動調整管理アプリ - venv環境セットアップ
echo ==================================================

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Pythonが見つかりません。
    pause
    exit /b
)

if not exist ".venv" (
    echo 仮想環境を作成しています...
    python -m venv .venv
)

echo 依存ライブラリをインストールしています...

call ".venv\Scripts\activate.bat"

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo セットアップ完了
pause