@echo off
REM Go to the directory where this .bat file lives
cd /d "%~dp0"

REM Activate the virtual environment
call .venv\Scripts\activate

echo.
echo ===============================
echo Virtual environment activated
echo Project: %cd%
echo ===============================
echo.

REM Keep the terminal open
cmd
