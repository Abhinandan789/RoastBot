@echo off
cd /d "%~dp0.."

if exist ".venv\Scripts\python.exe" (
    set VENV=.venv
) else if exist "venv\Scripts\python.exe" (
    set VENV=venv
) else (
    echo No virtual environment found.
    pause
    exit /b 1
)

call "%VENV%\Scripts\activate.bat"

:: Kill any existing pet_widget process to prevent duplicates
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *pet_widget*" >nul 2>&1

:: Run with visible console so you see errors, log to file
"%VENV%\Scripts\python.exe" -m src.pet_widget >> data\pet_widget.log 2>&1