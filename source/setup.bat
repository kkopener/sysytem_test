@echo off
rem 文字コードをWindows標準(Shift-JIS)に明示的に設定
chcp 932 > nul

echo ====================================================
echo シフト自動調整管理アプリ - 環境構築セットアップ
echo ====================================================

rem 1. Pythonの存在チェック
python --version > nul 2>&1
if errorlevel 1 goto NO_PYTHON

rem 2. 仮想環境(.venv)の作成
if exist .venv goto VENV_EXISTS
echo 仮想環境 (.venv) を作成しています...
python -m venv .venv
if errorlevel 1 goto VENV_ERROR
goto VENV_DONE

:VENV_EXISTS
echo 仮想環境 (.venv) は既に存在します。

:VENV_DONE
rem 3. ライブラリのインストール
echo pipの更新とライブラリのインストールを開始します...
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 goto INSTALL_ERROR

echo ====================================================
echo セットアップが正常に完了しました！
echo この画面を閉じ、run.bat をダブルクリックして起動してください。
echo ====================================================
pause
exit /b

:NO_PYTHON
echo [ERROR] Pythonがパソコンで見つかりません！
echo.
echo 原因として以下の2つが考えられます：
echo 1. Pythonがまだパソコンにインストールされていない
echo 2. インストール時に「Add python.exe to PATH」にチェックを入れ忘れた
echo.
echo 【対処法】
echo Pythonのインストーラ（python-3.12.x.exeなど）をもう一度起動し、
echo 画面下部にある「Add python.exe to PATH」に必ずチェックを入れて
echo 再インストール（またはModify）を行ってください。
echo.
pause
exit /b

:VENV_ERROR
echo [ERROR] 仮想環境(.venv)の作成に失敗しました。
pause
exit /b

:INSTALL_ERROR
echo [ERROR] ライブラリのインストールに失敗しました。
echo requirements.txt が同じフォルダ内にあるか確認してください。
pause
exit /b