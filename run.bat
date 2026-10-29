@echo off
setlocal enabledelayedexpansion

REM =====================================================================
REM CareerConnect Clone - Windows Launch Script
REM =====================================================================

REM 1. Change working directory to the directory containing run.bat
cd /d "%~dp0"

echo =====================================================================
echo   CareerConnect Clone - Local Development Server
echo =====================================================================
echo   Working Directory: %~dp0
echo.

REM 2. Check for Python (py launcher or python command)
set "PYTHON_CMD="

py -3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py -3"
    goto :python_detected
)

py --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py"
    goto :python_detected
)

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    goto :python_detected
)

REM If Python was not found, show clear error and halt
echo.
echo =====================================================================
echo  [ERROR] Python is not installed or not found in system PATH.
echo =====================================================================
echo  Neither the Windows Python launcher ('py') nor 'python' was found.
echo.
echo  To resolve this:
echo    1. Download Python 3.10+ from https://www.python.org/downloads/
echo    2. During installation, ensure you check:
echo       [x] "Add python.exe to PATH"
echo    3. Restart your terminal or command prompt and run run.bat again.
echo =====================================================================
echo.
pause
exit /b 1

:python_detected
echo [INFO] Detected Python command: !PYTHON_CMD!
!PYTHON_CMD! --version

REM 3. Create .venv if it does not exist
if exist ".venv\Scripts\python.exe" goto :venv_exists

echo.
echo [INFO] Virtual environment .venv not found.
echo [INFO] Creating Python virtual environment using !PYTHON_CMD!...
!PYTHON_CMD! -m venv .venv
if %errorlevel% neq 0 (
    echo.
    echo =====================================================================
    echo  [ERROR] Failed to create virtual environment in .venv.
    echo =====================================================================
    echo  Please verify:
    echo    - The Python standard library venv module is installed.
    echo    - You have write permissions for this folder.
    echo =====================================================================
    echo.
    pause
    exit /b 1
)
echo [INFO] Virtual environment created successfully.

:venv_exists
echo [INFO] Using virtual environment in .venv.

REM 4. Install requirements.txt using the virtual environment's Python
echo.
echo [INFO] Verifying dependencies from requirements.txt...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo =====================================================================
    echo  [ERROR] Dependency installation failed.
    echo =====================================================================
    echo  Failed to install required packages from requirements.txt.
    echo  Please check:
    echo    - Your internet connection to https://pypi.org
    echo    - File permissions in .venv
    echo =====================================================================
    echo.
    pause
    exit /b 1
)
echo [INFO] Dependencies verified successfully.

REM 5. Create default .env from .env.example if missing (preserves user settings)
if not exist ".env" (
    if exist ".env.example" (
        echo [INFO] Creating default .env configuration from .env.example...
        copy ".env.example" ".env" >nul 2>&1
    )
)

REM 6. Check for duplicate server processes on port 5000
set "PORT_PID="
for /f "tokens=5" %%a in ('netstat -ano -p tcp 2^>nul ^| findstr ":5000 "') do (
    set "PORT_PID=%%a"
)

if not defined PORT_PID goto :port_available

echo.
echo =====================================================================
echo  [WARNING] Port 5000 is already in use by process PID !PORT_PID!.
echo =====================================================================
echo  CareerConnectClone or another server is already active on this port.
echo  Starting a duplicate process would cause port binding conflicts.
echo.
echo  Options:
echo    - Enter 'Y' to open http://127.0.0.1:5000 in your browser.
echo    - Enter 'N' to exit.
echo =====================================================================
echo.
set /p "OPEN_URL=Open http://127.0.0.1:5000 in browser now? [Y/N]: "
if /i "!OPEN_URL!"=="Y" (
    start http://127.0.0.1:5000
)
echo.
echo Exiting to avoid duplicate server conflict.
pause
exit /b 0

:port_available

REM 7. Schedule browser launch once server initializes (~2 seconds)
echo [INFO] Scheduling browser launch for http://127.0.0.1:5000...
start "" cmd /c "ping 127.0.0.1 -n 3 >nul 2>&1 & start http://127.0.0.1:5000"

REM 8. Start Flask application using virtual environment's Python executable
echo.
echo =====================================================================
echo   CareerConnect Clone is running!
echo =====================================================================
echo   Local Address: http://127.0.0.1:5000/
echo.
echo   * The application will open in your default browser shortly.
echo   * TO STOP THE SERVER: Press Ctrl+C in this console window.
echo =====================================================================
echo.

".venv\Scripts\python.exe" app.py

REM 9. Keep console open after shutdown or errors
echo.
echo =====================================================================
echo   Server stopped.
echo =====================================================================
pause
