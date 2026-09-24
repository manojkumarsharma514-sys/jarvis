@echo off
setlocal
cd /d "%~dp0"

echo Starting Ollama in the background...
start "JARVIS Ollama" /min ollama serve

echo Waiting for Ollama to become ready...
for /l %%i in (1,1,15) do (
    powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:11434/api/tags' -UseBasicParsing -TimeoutSec 1; if ($r.StatusCode -eq 200) { exit 0 } } catch {} ; exit 1" >nul 2>&1
    if not errorlevel 1 goto ollama_ready
    timeout /t 1 /nobreak >nul
)

echo Ollama did not become ready. Make sure Ollama is installed and phi3:mini is downloaded.
pause
exit /b 1

:ollama_ready
echo Ollama is ready.
echo Starting JARVIS...
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" main.py --cli
) else (
    python main.py --cli
)

pause
endlocal
