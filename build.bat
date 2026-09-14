@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo.
echo ============================================================
echo              HTOOL NOVA - ANDROID APK BUILD
echo                 Windows + WSL2 / Ubuntu
echo ============================================================
echo.

where wsl.exe >nul 2>&1
if errorlevel 1 (
    echo [ERROR] WSL was not found.
    echo.
    echo Install WSL2 first from Administrator PowerShell:
    echo     wsl --install -d Ubuntu
    echo.
    pause
    exit /b 1
)

wsl.exe -l -q | findstr /i /r /c:"^Ubuntu$" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Ubuntu WSL distribution was not found.
    echo.
    echo Install it from Administrator PowerShell:
    echo     wsl --install -d Ubuntu
    echo.
    pause
    exit /b 1
)

echo [INFO] Starting Ubuntu WSL2 build...
echo [INFO] First build can take a long time because Android tools are downloaded.
echo.

wsl.exe -d Ubuntu -- bash -lc "bash \"$(wslpath -a '%~dp0')/build_wsl.sh\" \"%~dp0\""
if errorlevel 1 (
    echo.
    echo ============================================================
    echo [FAILED] APK build failed. Scroll up and copy the last error.
    echo ============================================================
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo [SUCCESS] APK was created in this project folder.
echo ============================================================
echo.

dir /b *.apk 2>nul
if errorlevel 1 echo [WARNING] APK was not visible from Windows. Check WSL output.

echo.
pause
exit /b 0
