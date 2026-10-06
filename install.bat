@echo off
cd /d "%~dp0"
echo SIGNAL TERMINAL — installing into a local virtual environment
python -m venv .venv
if errorlevel 1 (
  echo Python was not found. Install Python 3.11+ from python.org and tick "Add Python to PATH".
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r "%~dp0requirements.txt"
echo.
echo Done. Next: double-click run.bat
pause
