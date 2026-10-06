@echo off
setlocal
cd /d "%~dp0"
title SIGNAL TERMINAL - Windows Build

echo ========================================
echo  SIGNAL TERMINAL - Windows EXE Builder
echo ========================================
echo.
where py >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python launcher was not found.
  echo Install Python 3.11 x64 from python.org and enable the Python launcher.
  pause
  exit /b 1
)

py -3.11 --version
if errorlevel 1 (
  echo ERROR: Python 3.11 was not found. Install Python 3.11 x64 first.
  pause
  exit /b 1
)

if not exist ".build-venv\Scripts\python.exe" (
  py -3.11 -m venv .build-venv
  if errorlevel 1 goto failed
)
call ".build-venv\Scripts\activate.bat"
python -m pip install --upgrade pip
if errorlevel 1 goto failed
python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto failed

echo.
echo Building Windows application folder...
python -m PyInstaller --noconfirm --clean --windowed --name SIGNAL_TERMINAL --collect-all PySide6 --collect-all pyqtgraph run.py
if errorlevel 1 goto failed

echo.
echo SUCCESS: dist\SIGNAL_TERMINAL\SIGNAL_TERMINAL.exe
echo You can now compile installer.iss using Inno Setup 6.
echo Installer output: Output\SIGNAL_TERMINAL_Setup.exe
pause
exit /b 0

:failed
echo.
echo BUILD FAILED. Read the error messages above and share them for troubleshooting.
pause
exit /b 1
