@echo off
rem 文字コードをWindows標準(Shift-JIS)に強制設定して文字化けを完全に防ぐ
chcp 932 > nul

echo ==================================================
echo シフト自動調整管理アプリを起動しています...
echo ==================================================

rem 仮想環境の存在チェック
if not exist .venv goto NO_VENV

rem 仮想環境を有効化してアプリを起動
call .venv\Scripts\activate
streamlit run app.py
exit /b

:NO_VENV
echo [ERROR] 仮想環境 (.venv) が見つかりません。
echo 最初に setup.bat を実行して環境構築を完了させてください。
pause
exit /b