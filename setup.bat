@echo off
setlocal
cd /d "%~dp0"

echo Creating virtual environment...
if not exist ".venv\Scripts\python.exe" (
    py -3 -m venv .venv
    if errorlevel 1 (
        echo Failed to create the virtual environment.
        pause
        exit /b 1
    )
)

echo Installing Python dependencies...
call ".venv\Scripts\python.exe" -m pip install --upgrade pip
call ".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo Dependency installation failed.
    pause
    exit /b 1
)

echo.
echo Setup complete.
echo.
echo Next steps:
echo   1. Install Ollama from https://ollama.com if it is not installed.
echo   2. Open a separate terminal and run: ollama serve
 echo  3. In another terminal, run: ollama pull phi3:mini
 echo  4. Start JARVIS with: .venv\Scripts\python.exe main.py --cli
 echo.
pause
endlocal
