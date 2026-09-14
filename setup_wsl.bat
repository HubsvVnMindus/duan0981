@echo off
setlocal
cd /d "%~dp0"
where wsl.exe >nul 2>&1
if errorlevel 1 (
    echo WSL is not installed.
    echo Run this in Administrator PowerShell:
    echo     wsl --install -d Ubuntu
    pause
    exit /b 1
)
echo Opening Ubuntu WSL2...
wsl.exe -d Ubuntu
