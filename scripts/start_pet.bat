@echo off
cd /d "%~dp0.."

if exist ".venv\Scripts\pythonw.exe" (
    set VENV=.venv
) else if exist "venv\Scripts\pythonw.exe" (
    set VENV=venv
) else (
    echo No virtual environment found.
    pause
    exit /b 1
)

call "%VENV%\Scripts\activate.bat"
start "" "%VENV%\Scripts\pythonw.exe" -m src.pet_widget