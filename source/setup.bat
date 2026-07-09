@echo off
rem 文字コードをWindows標準のShift-JISに明示的に設定
chcp 932 > nul

echo ====================================================
echo シフト自動調整管理アプリ - 環境構築セットアップ
echo ====================================================

rem パソコン内にPythonがあるかチェック
python --version > nul 2>&1
if errorlevel 1 goto NO_PYTHON

rem フォルダが存在するかチェック
if exist .venv goto VENV_EXISTS
echo 仮想環境 venv を作成しています...
python -m venv .venv
if errorlevel 1 goto VENV_ERROR
goto VENV_DONE

:VENV_EXISTS
echo 仮想環境 venv は既に存在します。

:VENV_DONE
rem ライブラリのインストール
echo pipの更新とライブラリのインストールを開始します...
call .venv\Scripts\activate.bat
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
echo 画面下部にある Add python.exe to PATH にチェックを入れて再インストールしてください。
pause
exit /b

:VENV_ERROR
echo [ERROR] 仮想環境 venv の作成に失敗しました。
pause
exit /b

:INSTALL_ERROR
echo [ERROR] ライブラリのインストールに失敗しました。
pause
exit /b