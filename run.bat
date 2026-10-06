@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" run.py
) else (
  echo Run install.bat first, then this file.
  pause
  exit /b 1
)
