@echo off
echo === STARTING APP ===

if not exist .venv goto NO_VENV

echo Activating .venv and running the app...
call .venv\Scripts\activate.bat
streamlit run app.py
exit /b

:NO_VENV
echo [ERROR] .venv not found.
echo Please run setup.bat first.
pause
exit /b