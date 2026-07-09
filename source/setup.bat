@echo off
echo === SETUP START ===

python --version > nul 2>&1
if errorlevel 1 goto NO_PY

if exist .venv goto SKIP_VENV
echo Creating .venv...
python -m venv .venv
if errorlevel 1 goto NO_VENV

:SKIP_VENV
echo Activating and installing...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 goto NO_PIP

echo === SETUP SUCCESS! ===
echo Please close this window and run run.bat
pause
exit /b

:NO_PY
echo [ERROR] Python not found.
pause
exit /b

:NO_VENV
echo [ERROR] Failed to create .venv.
pause
exit /b

:NO_PIP
echo [ERROR] Failed to install pip or requirements.
pause
exit /b